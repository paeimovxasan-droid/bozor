"""
v2 AI Kengash (Council) — g'oya #61, #62, #65, #66
===================================================
Bitta DeepSeek chaqiruvida 3 persona ovoz beradi:
  1. Trendchi (H1-H4 yo'nalish)
  2. Skalpchi (M5-M15 entry)
  3. Risk-ofitser — VETO huquqiga ega (#62)

AI ishlamasa — texnik signal o'zi yetarli (fallback), hech narsa to'xtamaydi.
"""
import os
import json
from datetime import date


class AICouncil:
    def __init__(self, agent):
        self.agent = agent
        self.enabled = os.getenv("AI_COUNCIL", "true").lower() == "true"
        self.max_calls = int(os.getenv("AI_COUNCIL_CALLS", "30"))
        self._calls_today = 0
        self._day = date.today().isoformat()
        self.lessons: list[str] = []       # AI darslar bazasi (#66)

    def _tick_day(self):
        today = date.today().isoformat()
        if today != self._day:
            self._day = today
            self._calls_today = 0

    async def vote(self, signal, meta: dict) -> dict:
        """
        Qaytarish: {decision, confidence, veto, reason}
        """
        self._tick_day()
        base = {
            "decision": getattr(signal, "signal", "WAIT"),
            "confidence": float(getattr(signal, "confidence", 0)),
            "veto": False,
            "reason": "texnik signal",
        }
        if (not self.enabled) or self._calls_today >= self.max_calls:
            return base

        prompt = (
            "Sen savdo kengashisan: 3 mutaxassis — TRENDCHI, SKALPCHI, RISK-OFITSER.\n"
            f"Signal: {signal.signal} {signal.symbol}, ishonch {signal.confidence:.0f}%, "
            f"entry {signal.entry}, SL {signal.stop_loss}, TP {signal.take_profit}.\n"
            f"Kontekst: RSI {meta.get('rsi', '?')}, ADX {meta.get('adx', '?')}, "
            f"ATR% {meta.get('atr_pct', '?')}, trend {meta.get('trend', '?')}, "
            f"soat {meta.get('hour', '?')}.\n"
        )
        if self.lessons:
            prompt += "Oldingi darslar: " + " | ".join(self.lessons[-5:]) + "\n"
        prompt += (
            'Faqat JSON: {"trend":"BUY|SELL|WAIT","scalp":"BUY|SELL|WAIT",'
            '"risk":"APPROVE|VETO","conf":0-100,"reason":"1 gap"}'
        )

        try:
            self._calls_today += 1
            raw = await self.agent._request(
                [{"role": "user", "content": prompt}],
                max_tokens=220, temperature=0.2, json_mode=True,
            )
            data = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return base

        try:
            trend = str(data.get("trend", "WAIT")).upper()
            scalp = str(data.get("scalp", "WAIT")).upper()
            risk = str(data.get("risk", "APPROVE")).upper()
            conf = float(data.get("conf", base["confidence"]))
            reason = str(data.get("reason", ""))[:120]

            votes = [trend, scalp, base["decision"]]
            buy_n = votes.count("BUY")
            sell_n = votes.count("SELL")
            decision = "BUY" if buy_n >= 2 else "SELL" if sell_n >= 2 else "WAIT"

            # Risk-ofitser VETO (#62)
            veto = risk == "VETO"
            if veto:
                decision = "WAIT"
            return {
                "decision": decision,
                "confidence": min(conf, 95),
                "veto": veto,
                "reason": reason or base["reason"],
            }
        except Exception:
            return base

    async def learn_from_loss(self, trade: dict) -> str:
        """Zarar savdodan dars chiqarish (#65)"""
        if (not self.enabled) or self._calls_today >= self.max_calls:
            return ""
        try:
            self._calls_today += 1
            raw = await self.agent._request(
                [{"role": "user", "content":
                  f"Zarar savdo tahlili: {json.dumps(trade, ensure_ascii=False)}. "
                  "Bir gapda asosiy dars/sababni yoz (o'zbekcha, max 20 so'z)."}],
                max_tokens=60, temperature=0.3,
            )
            lesson = str(raw).strip()[:150]
            if lesson:
                self.lessons.append(lesson)
                if len(self.lessons) > 30:
                    del self.lessons[: len(self.lessons) - 30]
            return lesson
        except Exception:
            return ""

    def get_state(self) -> dict:
        return {"lessons": self.lessons[-30:], "calls": self._calls_today, "day": self._day}

    def load_state(self, data: dict):
        if isinstance(data, dict):
            self.lessons = data.get("lessons", [])
