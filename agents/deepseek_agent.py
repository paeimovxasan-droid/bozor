"""
TORTINMANG.UZ — DeepSeek AI Agent
Rasmiy DeepSeek API docs asosida yozilgan: https://api-docs.deepseek.com

API spetsifikatsiya (2026-09 holatiga):
  • Endpoint : POST {base_url}/chat/completions   (base_url = https://api.deepseek.com)
  • Autentifikatsiya : Authorization: Bearer sk-...
  • Modellar : deepseek-flash  — DeepSeek-V4.1-Flash (arzon, tez, kundalik ish uchun)
               deepseek-v4-pro — chuqur reasoning, qimmatroq
  • DIQQAT   : eski `deepseek-chat` va `deepseek-reasoner` nomlari 2026-07-24 da
               TO'LIQ o'chirilgan. Ularga so'rov "Model Not Exist" bilan qaytadi.
  • Thinking : `reasoning_effort` parametri bilan boshqariladi
               (none | low | high | max). Trading botda "none" ishlatiladi —
               tez (1–3s) va token tejaydi.
  • JSON     : response_format={"type":"json_object"} — kafolatlangan JSON javob.

Xato kodlari (docs bo'yicha):
  401 Authentication Fails   — API key noto'g'ri/formati buzilgan
  402 Insufficient Balance   — hisobda mablag' yetarli emas
  404 Model Not Exist        — model nomi noto'g'ri (eski nom ham shu xatoga kiradi)
  429 Rate Limit Reached     — limit oshdi, biroz kutish kerak
  5xx Server Error           — DeepSeek tomonidagi vaqtinchalik xato
"""

import asyncio
import json
import re
import time
from typing import Optional

import aiohttp

from core.config import config
from core.logger import logger


class DeepSeekAPIError(Exception):
    """DeepSeek API xatosi — foydalanuvchiga tushunarli xabar bilan"""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")


# Model nomi noto'g'ri bo'lsa (404) navbat bilan sinab ko'riladigan zaxira nomlar.
# deepseek-v4-flash — deepseek-flash ning hali qabul qilinadigan eski sinonimi.
_FALLBACK_MODELS = ["deepseek-flash", "deepseek-v4-flash", "deepseek-v4-pro"]

_RETRY_STATUSES = {408, 429, 500, 502, 503, 504}


class DeepSeekAgent:
    """DeepSeek API orqali bozorni AI tahlil qilish (yagona AI provayder)"""

    def __init__(self):
        self.api_key = config.deepseek.api_key
        self.model = config.deepseek.model
        self.base_url = config.deepseek.base_url.rstrip("/")
        self.max_tokens = config.deepseek.max_tokens
        self.temperature = config.deepseek.temperature
        self.reasoning_effort = config.deepseek.reasoning_effort
        self.timeout = config.deepseek.timeout
        self._endpoint = f"{self.base_url}/chat/completions"
        # Oxirgi muvaffaqiyatli model (fallback ishlaganda yangilanadi)
        self._active_model = self.model
        # Statistika
        self.total_calls = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    # ─── YORDAMCHI ─────────────────────────────────────────────────

    @staticmethod
    def _error_message(status: int, body: str) -> str:
        """HTTP status → foydalanuvchiga tushunarli xabar (DeepSeek docs asosida)"""
        snippet = (body or "")[:200]
        if status == 401:
            return (
                "API key noto'g'ri yoki yaroqsiz (Authentication Fails). "
                ".env faylidagi DEEPSEEK_API_KEY ni tekshiring — kalit 'sk-' bilan "
                "boshlanishi va platform.deepseek.com/api_keys dan olingan bo'lishi kerak."
            )
        if status == 402:
            return (
                "DeepSeek hisobida mablag' yetarli emas (Insufficient Balance). "
                "platform.deepseek.com → Top up orqali balansni to'ldiring."
            )
        if status == 404:
            return (
                "Model topilmadi (Model Not Exist). Model nomi 'deepseek-flash' yoki "
                "'deepseek-v4-pro' bo'lishi kerak. Eski 'deepseek-chat' nomi 2026-07-24 dan "
                "o'chirilgan. Xabar: " + snippet
            )
        if status == 429:
            return "So'rovlar limiti oshdi (Rate Limit Reached). Bir oz kutib qayta urinilmoqda..."
        if status == 400:
            return "So'rov formatida xato (Invalid Request Body): " + snippet
        if 500 <= status < 600:
            return f"DeepSeek server xatosi ({status}). Qayta urinilmoqda..."
        return f"Kutilmagan xato ({status}): {snippet}"

    async def _request(
        self,
        messages: list,
        max_tokens: int = 400,
        temperature: Optional[float] = None,
        reasoning_effort: Optional[str] = None,
        json_mode: bool = False,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """
        DeepSeek Chat Completions ga markaziy so'rov (docs: api-docs.deepseek.com).
        429/5xx da avtomatik qayta urinish, 404 da zaxira modellarga o'tish.
        Javob matnini qaytaradi; xato bo'lsa DeepSeekAPIError ko'taradi.
        """
        if not self.api_key:
            raise DeepSeekAPIError(0, "DEEPSEEK_API_KEY o'rnatilmagan (.env fayliga kiriting)")

        payload = {
            "model": self._active_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": self.temperature if temperature is None else temperature,
            # Thinking rejimi: trading botda odatda "none" (tez va arzon)
            "reasoning_effort": reasoning_effort or self.reasoning_effort,
            "stream": False,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        models_to_try = [self._active_model] + [
            m for m in _FALLBACK_MODELS if m != self._active_model
        ]

        last_error: Optional[DeepSeekAPIError] = None

        for model in models_to_try:
            payload["model"] = model
            for attempt in range(3):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            self._endpoint,
                            headers=headers,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=timeout or self.timeout),
                        ) as resp:
                            body = await resp.text()

                            if resp.status == 200:
                                data = json.loads(body)
                                choice = data.get("choices") or [{}]
                                content = (choice[0].get("message") or {}).get("content")
                                if content is None:
                                    raise DeepSeekAPIError(
                                        resp.status, "Javobda content maydoni yo'q"
                                    )
                                self._track_usage(data)
                                if model != self._active_model:
                                    logger.info(
                                        f"🤖 DeepSeek: zaxira modelga o'tildi → {model}"
                                    )
                                    self._active_model = model
                                return content.strip()

                            # ── Xato kodlari ──
                            if resp.status == 404 and attempt == 0:
                                # Model nomi xato — keyingi nomoz modelni sinaymiz
                                logger.warning(
                                    f"DeepSeek: '{model}' topilmadi (404) — zaxira model sinovda"
                                )
                                last_error = DeepSeekAPIError(
                                    resp.status, self._error_message(resp.status, body)
                                )
                                break  # retry sikldan chiqib keyingi modelga o'tish

                            if resp.status in _RETRY_STATUSES and attempt < 2:
                                wait = min(float(resp.headers.get("Retry-After", 0) or 0), 5.0)
                                wait = wait or (1.0 * (attempt + 1))
                                logger.warning(
                                    f"DeepSeek HTTP {resp.status} — {wait:.0f}s dan keyin "
                                    f"{attempt + 2}-urinish..."
                                )
                                await asyncio.sleep(wait)
                                last_error = DeepSeekAPIError(
                                    resp.status, self._error_message(resp.status, body)
                                )
                                continue

                            raise DeepSeekAPIError(
                                resp.status, self._error_message(resp.status, body)
                            )

                except DeepSeekAPIError:
                    raise
                except (aiohttp.ClientError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                    last_error = DeepSeekAPIError(0, f"Tarmoq xatosi: {e}")
                    if attempt < 2:
                        await asyncio.sleep(1.0 * (attempt + 1))
                        continue
                    raise last_error from e

        # Barcha modellar muvaffaqiyatsiz
        raise last_error or DeepSeekAPIError(0, "DeepSeek so'rovi muvaffaqiyatsiz tugadi")

    def _track_usage(self, data: dict):
        """Token sarfini hisoblab borish (xarajat nazorati uchun)"""
        self.total_calls += 1
        usage = data.get("usage") or {}
        self.total_prompt_tokens += int(usage.get("prompt_tokens") or 0)
        self.total_completion_tokens += int(usage.get("completion_tokens") or 0)
        logger.debug(
            f"DeepSeek usage: in={usage.get('prompt_tokens')} "
            f"out={usage.get('completion_tokens')} model={data.get('model')}"
        )

    # ─── ULANISH TESTI ─────────────────────────────────────────────

    async def test_connection(self) -> dict:
        """
        API kalit va ulanishni tekshirish (run.py --test va test_deepseek.py uchun).
        Qaytaradi: {ok, model, message, latency_ms, usage}
        """
        if not self.api_key:
            return {
                "ok": False,
                "model": self._active_model,
                "message": "DEEPSEEK_API_KEY o'rnatilmagan — .env fayliga kalitni kiriting",
                "latency_ms": 0,
                "usage": {},
            }
        t0 = time.time()
        try:
            before = (self.total_prompt_tokens, self.total_completion_tokens)
            content = await self._request(
                messages=[
                    {"role": "system", "content": "You are a connectivity test. Reply exactly: OK"},
                    {"role": "user", "content": "ping"},
                ],
                max_tokens=16,
                temperature=0.0,
                reasoning_effort="none",
                timeout=20,
            )
            ms = int((time.time() - t0) * 1000)
            used_in = self.total_prompt_tokens - before[0]
            used_out = self.total_completion_tokens - before[1]
            return {
                "ok": True,
                "model": self._active_model,
                "message": f"Javob olindi: \"{content[:40]}\"",
                "latency_ms": ms,
                "usage": {"prompt_tokens": used_in, "completion_tokens": used_out},
            }
        except DeepSeekAPIError as e:
            return {
                "ok": False,
                "model": self._active_model,
                "message": e.message,
                "latency_ms": int((time.time() - t0) * 1000),
                "usage": {},
            }

    # ─── ASOSIY FUNKSIYALAR ────────────────────────────────────────

    async def quick_review(self, scan_summary: dict, account: dict) -> str:
        """Bozor holatini tezkor AI tahlili (har 10 siklda chaqiriladi)"""
        if not self.api_key:
            logger.debug("DeepSeek API key yo'q — skip")
            return ""

        balance = account.get("balance", 0)
        equity = account.get("equity", 0)
        best_sym = scan_summary.get("best_symbol", "N/A")
        best_conf = scan_summary.get("best_confidence", 0)
        sentiment = scan_summary.get("sentiment", "N/A")
        scanned = scan_summary.get("scanned", 0)
        signals = scan_summary.get("signals", 0)
        by_type = scan_summary.get("market_types", {})

        prompt = (
            f"You are a professional trading analyst. Briefly analyse:\n\n"
            f"Account: Balance=${balance:.2f}, Equity=${equity:.2f}\n"
            f"Scan: {scanned} markets scanned, {signals} signals found\n"
            f"Best opportunity: {best_sym} ({best_conf:.1f}% confidence)\n"
            f"Market sentiment: {sentiment}\n"
            f"Signals by type: {by_type}\n\n"
            f"Give a 2-3 sentence risk-aware trading recommendation. "
            f"Should we trade now? What is the main risk?"
        )

        try:
            review = await self._request(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                reasoning_effort="none",  # tezkor tahlil — thinking kerak emas
                timeout=20,
            )
            logger.info(f"🤖 DeepSeek AI sharhi: {review[:120]}...")
            return review
        except DeepSeekAPIError as e:
            logger.warning(f"DeepSeek quick_review: {e.message}")
            return ""

    async def trading_chat(self, user_message: str, context: dict = None) -> str:
        """
        Foydalanuvchi bilan suhbat — faqat trading mavzulari.
        Telegram /ask buyrug'i yoki oddiy xabar orqali chaqiriladi.
        """
        if not self.api_key:
            return (
                "⚠️ DeepSeek API kaliti yo'q — AI chat ishlamaydi.\n"
                ".env fayliga DEEPSEEK_API_KEY kiriting (platform.deepseek.com/api_keys)."
            )

        ctx = ""
        if context:
            balance = context.get("balance", 0)
            positions = context.get("positions", [])
            pos_text = ""
            for p in positions[:3]:
                try:
                    pos_text += (
                        f"\n  • {p.get('symbol')} {p.get('type')} "
                        f"@ {float(p.get('open_price') or 0):.4f} | "
                        f"P/L: {float(p.get('profit') or 0):+.4f}"
                    )
                except (TypeError, ValueError):
                    pos_text += f"\n  • {p.get('symbol')}"
            ctx = (
                f"\nHozirgi holat:\n"
                f"  Balans: ${float(balance or 0):.2f}\n"
                f"  Ochiq pozitsiyalar: {len(positions)}{pos_text}\n"
            )

        system_prompt = (
            "You are TORTINMANG.UZ's AI trading assistant for forex, crypto, stocks and commodities.\n"
            "You ONLY answer questions about:\n"
            "- Trading, technical analysis, price action, market trends\n"
            "- Risk management, position sizing, stop loss placement\n"
            "- Support/resistance, trading strategies, portfolio management\n\n"
            "RULES:\n"
            "1. For non-trading questions respond ONLY: \"Men faqat trading savollariga javob beraman.\"\n"
            "2. Keep answers concise (3-5 sentences max)\n"
            "3. Answer in the SAME LANGUAGE as the user's question (Uzbek/Russian/English)\n"
            "4. Always mention risk management when suggesting trades\n"
            "5. Never guarantee profits — speak in probabilities\n"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{ctx}\nSavol: {user_message}"},
        ]

        try:
            answer = await self._request(
                messages=messages,
                max_tokens=600,
                temperature=0.3,
                reasoning_effort="none",
                timeout=25,
            )
            return f"🤖 <b>TORTINMANG.UZ AI:</b>\n\n{answer}"
        except DeepSeekAPIError as e:
            logger.warning(f"DeepSeek chat xato: {e.message}")
            return f"⚠️ AI javob berolmadi.\n{e.message}"

    async def analyze_signal(self, signal_data: dict) -> dict:
        """
        Bitta signal uchun AI tekshiruvi — JSON javob (response_format=json_object).
        Qaytaradi: {"approved": bool, "reason": str}
        """
        if not self.api_key:
            return {"approved": True, "reason": "AI tahlilsiz — approve"}

        prompt = (
            f"Signal: {signal_data.get('signal')} {signal_data.get('symbol')}\n"
            f"Confidence: {signal_data.get('confidence')}%\n"
            f"Entry: {signal_data.get('entry')}, SL: {signal_data.get('stop_loss')}, "
            f"TP: {signal_data.get('take_profit')}\n"
            f"R:R: {signal_data.get('rr_ratio')}\n"
            f"Reason: {signal_data.get('reason')}\n\n"
            f"Should this trade be executed? Respond with a JSON object only, "
            f'in the exact format: {{"approved": true/false, "reason": "brief reason"}}'
        )

        try:
            content = await self._request(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1,
                reasoning_effort="none",
                json_mode=True,  # kafolatlangan JSON (DeepSeek JSON Output)
                timeout=15,
            )
            parsed = self._parse_json(content)
            if parsed is not None and "approved" in parsed:
                return {
                    "approved": bool(parsed.get("approved")),
                    "reason": str(parsed.get("reason", ""))[:300],
                }
            return {"approved": True, "reason": "AI javobi tahlil qilinmadi"}
        except DeepSeekAPIError as e:
            logger.debug(f"DeepSeek signal tahlil xatosi: {e.message}")
            return {"approved": True, "reason": f"AI xato: {e.message[:120]}"}

    async def daily_report(self, context: dict) -> str:
        """
        Kunlik statistika bo'yicha AI xulosa — Telegram hisoboti uchun.
        O'zbek tilida, 4-6 qator, aniq va risk-xabardor.
        """
        if not self.api_key:
            return ""
        by_symbol = "\n".join(f"  • {line}" for line in context.get("by_symbol", []))
        prompt = (
            "Sen professional trading menejerisan. Quyidagi statistika bo'yicha "
            "O'ZBEK tilida qisqa (4-6 qator) kunlik hisobot yoz:\n\n"
            f"Sana: {context.get('date')}\n"
            f"Balans: ${context.get('balance', 0):.2f}\n"
            f"Bugungi savdolar: {context.get('trades_today')}\n"
            f"Umumiy win-rate: {context.get('win_rate', 0):.1f}%\n"
            f"Jami P/L: {context.get('total_profit', 0):+.2f}\n"
            f"Fokus bozorlar: {', '.join(context.get('focus_symbols', []))}\n"
            f"Symbol bo'yicha:\n{by_symbol}\n\n"
            "Talablar: 1) eng yaxshi va eng yomon symbolni ayt; "
            "2) fokus ro'yxatga taklif ber (qaysi symbolni olib tashlash/qo'shish mumkin); "
            "3) risk eslatmasi bilan yakunla. Faqat matn, sarlavhasiz."
        )
        try:
            return await self._request(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3,
                reasoning_effort="none",
                timeout=25,
            )
        except DeepSeekAPIError as e:
            logger.debug(f"Daily report xato: {e.message}")
            return ""

    @staticmethod
    def _parse_json(text: str) -> Optional[dict]:
        """JSON javobni mustahkam parse qilish (markdown fence ham bo'lishi mumkin)"""
        if not text:
            return None
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        return None
