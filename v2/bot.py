"""
TORTINMANG.UZ v2.0 — UltraBotV2
==============================
v1 UltraOrchestrator ustiga qurilgan mustaqil savdo tizimi:

  Pog'ona tizimi (BRONZE→DIAMOND) + Risk Desk + Gatekeeper
  + AI Kengash (veto) + Learning Core (DNA/kNN/soat xaritasi)
  + Bozor Nafasi + Whale Trap + Liquidity Magnet + Trade Manager

Har daqiqa: tahlil → darvoza → kengash → sizing → savdo → boshqaruv.
"""
import os
import time
import asyncio
from datetime import datetime, date

from core.orchestrator import UltraOrchestrator, TradingDecision
from core.config import config
from core.logger import logger

from v2.tiers import TierEngine
from v2.riskdesk import RiskDesk
from v2.gatekeeper import SignalGate
from v2.learning import LearningCore
from v2.council import AICouncil
from v2.breath import MarketBreath
from v2.manager import TradeManagerV2


class UltraBotV2(UltraOrchestrator):
    VERSION = "2.0.0"

    def __init__(self):
        super().__init__()
        self.tier_engine = TierEngine()
        self.riskdesk = RiskDesk()
        self.gate = SignalGate()
        self.learning = LearningCore()
        self.council: AICouncil | None = None      # initialize() da yaratiladi
        self.breath = MarketBreath()
        self.manager = TradeManagerV2()
        self._v2_open_vec: dict[int, list] = {}
        self._v2_open_hour: dict[int, int] = {}
        self._daily_target_done = None             # kunlik maqsad erishilgan sana
        self._profit_lock_notified = False
        self._drift_notified = False

    # ─── INIT ─────────────────────────────────────────────────────

    async def initialize(self) -> bool:
        ok = await super().initialize()
        if ok:
            self.council = AICouncil(self.ai)
            logger.info(f"🚀 TORTINMANG.UZ v{self.VERSION} tayyor — pog'ona dvigateli yoqilgan")
        return ok

    # ─── STATE (v2 komponentlar bilan) ────────────────────────────

    def _save_state(self):
        super()._save_state()
        try:
            import json
            path = getattr(self, "_state_file", "tortinmang_state.json")
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        data["v2"] = {
            "tiers": self.tier_engine.get_state(),
            "riskdesk": self.riskdesk.get_state(),
            "learning": self.learning.get_state(),
            "council": self.council.get_state() if self.council else {},
        }
        try:
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            os.replace(tmp, path)     # atomar yozish (#107)
        except Exception as e:
            logger.debug(f"v2 state saqlash: {e}")

    def _load_state(self):
        super()._load_state()
        try:
            import json
            path = getattr(self, "_state_file", "tortinmang_state.json")
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            v2 = data.get("v2", {})
            self.tier_engine.load_state(v2.get("tiers", {}))
            self.riskdesk.load_state(v2.get("riskdesk", {}))
            self.learning.load_state(v2.get("learning", {}))
            if self.council:
                self.council.load_state(v2.get("council", {}))
            logger.info(f"📦 v2 state yuklandi: pog'ona={self.tier_engine.current().name}")
        except Exception:
            pass

    # ─── ASOSIY SIKL (v2 pipeline) ────────────────────────────────

    async def run_cycle(self):
        self._cycle_count += 1
        try:
            account = await self._get_account()
            balance = float(account.get("balance", 0))
            equity = float(account.get("equity", 0) or balance)

            if balance < 1:
                if self._cycle_count % 30 == 0:
                    logger.warning(f"⚠️ Balans ${balance:.2f} — kuzatuv rejimi")
                return

            today = date.today().isoformat()

            # 1. POG'ONA DVIGATELI (#127)
            tier, event = self.tier_engine.tick(balance, today)
            if event == "PROMOTED":
                await self.telegram.send(
                    f"🎉 <b>POG'ONA OSHDI!</b>\n{self.tier_engine.passport(balance)}")
            elif event == "DEMOTED":
                await self.telegram.send(
                    f"⬇️ <b>Pog'ona tushdi</b> — himoya qoidalari kuchaydi.\n"
                    f"{self.tier_engine.passport(balance)}")

            # Profit lock zonasi (#133)
            if self.tier_engine.profit_lock_breached(balance):
                if not self._profit_lock_notified:
                    self._profit_lock_notified = True
                    n = await self.manager.emergency_flat(self, "PROFIT_LOCK")
                    self.riskdesk.emergency_stop = True
                    self.riskdesk.emergency_reason = "Profit lock zonasi buzildi"
                    await self.telegram.send(
                        f"🔒 <b>PROFIT LOCK</b>: himoyalangan kapital zonaga tushdi. "
                        f"{n} pozitsiya yopildi, savdolar to'xtadi. /start bilan qayta boshlash.")
                return

            # 2. RISK DESK tick
            self.riskdesk.tick(balance, equity)

            # 3. Paper pozitsiyalar monitoringi (SL/TP)
            closed_papers = await self.paper.update_prices()
            for cp in closed_papers:
                await self._v2_on_close(
                    cp["ticket"], cp["symbol"], cp["side"],
                    cp["entry"], cp["close_price"], cp["profit"],
                    cp["reason"] + " [PAPER]")

            # 4. MT5 yopilgan pozitsiyalarni sinxronlash (v2 hooks bilan)
            await self._v2_sync_closed()

            # 5. Ochiq pozitsiyalarni boshqarish: partial TP + BE + trailing
            await self._manage_positions(balance)

            # 6. Time-stop + Juma himoyasi
            for pos in await self.manager.time_stop(self):
                pass  # _v2_close_position ichida hamma narsa qilinadi
            await self.manager.weekend_close(self)

            # 7. Learning: drift + self-tuning
            if self.learning.drift_alert() and not self._drift_notified:
                self._drift_notified = True
                self._auto_mode = False
                await self.telegram.send(
                    "🩺 <b>DRIFT ANIQLANDI</b>: oxirgi 20 savdoda 15+ zarar. "
                    "Bot xavfsizlik uchun MANUAL rejimga o'tdi. "
                    "/auto bilan qayta yoqasiz, /backtest bilan strategiyani tekshiring.")
            self.learning.tune_confidence()

            # 8. Bozor Nafasi + ma'lumot yig'ish
            active = self._get_active_symbols(balance)
            market_data = await self._scan_market_data(active)
            scan = None
            if market_data:
                for sym, df in market_data.items():
                    self.breath.compute(sym, df)

                # 9. SKANER
                scan = await self.scanner.scan_all(market_data, balance)

                # Yangilik dvigateli (v1) — sentiment yangilash + blackout
                try:
                    if self._cycle_count % 20 == 0:
                        await self.news.get_sentiment(
                            [s.replace("USD", "") for s in active[:4]])
                    nb, nb_reason = self.news.is_blackout()
                    if nb:
                        logger.warning(f"⏸️ News blackout: {nb_reason}")
                        scan.best_signals = []
                except Exception as _e:
                    logger.debug(f"News check: {_e}")

                if self._auto_mode and scan.best_signals:
                    # Risk Desk darvozasi (#29-35)
                    can, why = self.riskdesk.can_trade(
                        tier, balance, equity, len(self._get_positions()))
                    if not can:
                        if self._cycle_count % 15 == 0:
                            logger.info(f"⏸️ Yangi savdo yo'q: {why}")
                        scan.best_signals = []

                if self._auto_mode and scan.best_signals:
                    # Kunlik maqsad qulfi (#47)
                    if self.riskdesk.daily_target_reached(equity, tier.daily_target_usd):
                        if self._daily_target_done != today:
                            self._daily_target_done = today
                            await self.telegram.send(
                                f"🎯 <b>KUNLIK MAQSAD YIG'ILDI!</b> "
                                f"+${equity - self.riskdesk.daily_start_balance:.2f} "
                                f"(maqsad ${tier.daily_target_usd:.0f}) — bugun savdo yopiladi. 🛡️")
                    else:
                        for signal in scan.best_signals[:2]:
                            await self._v2_process_signal(signal, account, tier, market_data)
                        # Dogon — faqat ruxsat etilgan pog'onalarda
                        if tier.dogon_allowed:
                            await self._dogon_check(scan, account)

            # 10. SL mavjudligini tekshirish (#36)
            if self._cycle_count % 10 == 0:
                await self._runtime_sl_check()

            # 11. Soatlik heartbeat (#103) — tier passport + nafas
            if self._cycle_count % 60 == 0:
                await self._v2_heartbeat(account)

            # 12. Whale monitoring
            if market_data and self._cycle_count % 5 == 0:
                await self._check_whale_alerts(market_data, balance)

            # 13. State saqlash
            if self._cycle_count % 30 == 0:
                self._save_state()

        except Exception as e:
            logger.error(f"v2 sikl xatosi: {e}", exc_info=True)

    # ─── SIGNAL → SAVDO (v2 pipeline) ─────────────────────────────

    async def _v2_process_signal(self, signal, account: dict, tier, market_data: dict):
        symbol = signal.symbol
        balance = float(account.get("balance", 0))
        positions = self._get_positions()

        # duplicate + symbol limiti
        same = [p for p in positions if p.get("symbol") == symbol]
        if len(same) >= tier.max_per_symbol:
            return

        # SL cooldown
        if symbol in self._sl_cooldown:
            elapsed = time.time() - self._sl_cooldown[symbol]
            if elapsed < 1800:
                return
            del self._sl_cooldown[symbol]

        df = market_data.get(symbol)
        if df is None or len(df) < 30:
            return

        tick = self.market.get_tick(symbol) or {}
        bid = float(tick.get("bid", 0) or signal.entry)
        ask = float(tick.get("ask", 0) or signal.entry)
        spread = abs(ask - bid) if ask and bid else 0.0
        price = bid if signal.signal == "SELL" else (ask or bid)

        # ATR + gatekeeper darvozasi
        atr = float(df["atr"].iloc[-1]) if "atr" in df.columns else 0.0
        ok, why = self.gate.check(symbol, signal, atr, price or signal.entry, spread)
        if not ok:
            logger.debug(f"🚪 {symbol} gate: {why}")
            return

        # Entry drift (#23)
        if not self.gate.entry_drift_ok(signal.entry, price or signal.entry):
            return

        # Whale trap bonus (#116)
        trap = self.breath.whale_trap(df)
        trap_boost = 0.0
        if trap["trap"] == "bull" and signal.signal == "BUY" and trap["strength"] > 50:
            trap_boost = 5.0
        elif trap["trap"] == "bear" and signal.signal == "SELL" and trap["strength"] > 50:
            trap_boost = 5.0

        # META va Signal DNA (#83)
        from engines.market_scanner import MultiMarketScanner
        try:
            adx = MultiMarketScanner._calc_adx(df)
        except Exception:
            adx = 0.0
        rsi = float(df["rsi"].iloc[-1]) if "rsi" in df.columns else 50.0
        atr_pct = float(df["atr_pct"].iloc[-1]) if "atr_pct" in df.columns else 0.0
        ema20 = df["ema20"] if "ema20" in df.columns else df["close"]
        mom = float((ema20.iloc[-1] / ema20.iloc[-6] - 1) * 100) if len(ema20) > 6 else 0.0
        hour = datetime.now().hour
        meta = {"rsi": round(rsi, 1), "adx": round(adx, 1), "atr_pct": round(atr_pct, 3),
                "mom": round(mom, 3), "trend": str(pd_series(df)), "hour": hour}

        # Soat xaritasi filtri (#92)
        if not self.learning.hour_ok(symbol, hour):
            logger.debug(f"⏰ {symbol}: bu soatda tarix zaif — o'tkazildi")
            return

        vector = LearningCore.make_vector(signal, meta, hour)
        boost = self.learning.pattern_boost(vector, symbol) + trap_boost
        conf = float(signal.confidence) + boost + self.learning.confidence_offset

        threshold = config.risk.min_confidence
        if conf < threshold:
            logger.debug(f"📉 {symbol}: ishonch {conf:.1f}% < {threshold}% (boost {boost:+.1f})")
            return

        # AI KENGASH + risk-ofitser VETO (#61, #62)
        vote = {"decision": signal.signal, "confidence": conf, "veto": False, "reason": ""}
        if self.council and (tier.ai_veto_required or config.deepseek.api_key):
            vote = await self.council.vote(signal, meta)
            if vote["veto"]:
                logger.info(f"🛑 AI VETO {symbol}: {vote['reason']}")
                await self.telegram.send(
                    f"🛑 <b>AI VETO</b> {symbol} {signal.signal}\n{vote['reason']}")
                return
            if vote["decision"] == "WAIT":
                logger.debug(f"⏸️ Kengash WAIT: {symbol}")
                return
            # DIQQAT: yo'nalishni ALMASHTIRMAYMIZ — SL/TP signallar
            # aniq yo'nalish uchun hisoblangan. Kengash rozi bo'lmasa — o'tamiz.
            if vote["decision"] != signal.signal:
                logger.info(
                    f"🔁 Kengash rozi emas ({signal.signal} → {vote['decision']}) — "
                    f"{symbol} o'tkazildi")
                return

        # ── RISK DESK sizing (#26) ───────────────────────────────
        sl_dist = abs(signal.entry - signal.stop_loss)
        lot, actual_risk = self.riskdesk.calc_lot(balance, symbol, sl_dist, tier)
        lot *= self.riskdesk.anti_tilt_lot_factor()
        lot = round(max(0.01, min(lot, tier.lot_max)), 2)

        if sl_dist <= 0:
            return

        # HALOL RISK CHEGARASI: minimal lotning o'zi ruxsat etilgan riskdan
        # oshsa (kichik balans + katta kontrakt) — savdo OCHILMAYDI.
        # Masalan $10 balansda XAUUSD 0.01 lot = ~$5 risk = 50% → blok.
        max_actual = float(os.getenv("MAX_ACTUAL_RISK_PCT", "3.0"))
        if actual_risk > max_actual:
            logger.info(
                f"🚫 {symbol}: min lot risk {actual_risk:.1f}% > {max_actual}% "
                f"chegara — o'tkazildi (balans ${balance:.0f} hali kichik)")
            return

        rr = abs(signal.take_profit - signal.entry) / max(sl_dist, 1e-10)
        self.riskdesk.audit({
            "event": "open", "symbol": symbol, "side": signal.signal,
            "balance": balance, "lot": lot, "sl_dist": round(sl_dist, 5),
            "risk_pct": round(actual_risk, 3), "conf": round(conf, 1),
            "boost": round(boost, 1), "veto": vote.get("veto", False),
            "breath": self.breath.get(symbol).get("score"),
        })

        decision = TradingDecision(
            action=signal.signal,
            symbol=symbol,
            market_type=getattr(signal, "market_type", "forex"),
            confidence=min(99.0, conf),
            lot=lot,
            entry=signal.entry,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            rr_ratio=round(rr, 2),
            tier=tier.name,
            reason=f"v2 | {signal.reason} | boost{boost:+.0f} | {vote.get('reason', '')}"[:200],
            whale_involved=bool(getattr(signal, "whale_activity", None)),
            timestamp=datetime.utcnow().isoformat(),
            cluster_score=getattr(signal, "cluster_score", 0.0),
            cluster_type=getattr(signal, "cluster_type", ""),
            poc=getattr(signal, "poc", 0.0),
            cvd_trend=getattr(signal, "cvd_trend", ""),
        )

        await self.history.save_signal({
            "symbol": symbol, "market_type": decision.market_type,
            "signal": signal.signal, "confidence": conf,
            "entry": signal.entry, "sl": signal.stop_loss,
            "tp": signal.take_profit, "rr": rr, "tier": tier.name,
            "reason": decision.reason, "executed": True,
        })

        before = len(self._get_positions())
        await self._execute_trade(decision)
        if len(self._get_positions()) > before:
            self.riskdesk.on_trade_opened()
            # yangi ticket ni topib, DNA uchun belgilash
            for p in self._get_positions():
                t = p.get("ticket")
                if t not in self._v2_open_vec:
                    self._v2_open_vec[t] = vector
                    self._v2_open_hour[t] = hour
                    self.manager.mark_open(t)
            logger.info(
                f"✅ v2 SAVDO: {signal.signal} {symbol} lot={lot} risk={actual_risk:.2f}% "
                f"conf={conf:.0f}% breath={self.breath.get(symbol).get('score')}")

    # ─── MT5/BINANCE YOPILGAN SAVDOLAR (v2 hooks) ────────────────

    async def _v2_sync_closed(self):
        """
        v1 _sync_closed_positions ni chaqiradi (tarix/stats/telegram),
        keyin v2 hooklarini qo'shadi: riskdesk + Signal DNA + AI dars.
        """
        if not self._open_ticket_map:
            return
        current = {p["ticket"] for p in self._get_positions()}
        closing = {t: dict(info) for t, info in self._open_ticket_map.items()
                   if t not in current}
        await self._sync_closed_positions()

        for ticket, info in closing.items():
            entry, tp, sl = info["entry"], info["tp"], info["sl"]
            side = info["side"]
            qty = float(info.get("qty", 1.0))
            if abs(entry - tp) < abs(entry - sl):
                profit = abs(tp - entry) * qty * (1 if side == "BUY" else -1)
                reason = "TAKE_PROFIT"
            else:
                profit = -abs(entry - sl) * qty * (1 if side == "BUY" else -1)
                reason = "STOP_LOSS"
            self.riskdesk.on_trade_closed(profit)
            self.riskdesk.audit({"event": "close_mt5", "ticket": ticket,
                                 "symbol": info["symbol"],
                                 "profit": round(profit, 2), "reason": reason})
            vec = self._v2_open_vec.pop(ticket, None)
            if vec:
                hr = self._v2_open_hour.pop(ticket, datetime.now().hour)
                self.learning.record(vec, profit, info["symbol"], hr)
            self.manager.unmark(ticket)
            if profit < -0.5 and self.council:
                asyncio.create_task(self.council.learn_from_loss({
                    "symbol": info["symbol"], "side": side, "entry": entry,
                    "profit": round(profit, 2), "reason": reason,
                }))

    # ─── SAVDO YOPILISHI (learning + risk + telegram) ─────────────

    async def _v2_on_close(self, ticket, symbol, side, entry, close_price, profit, reason):
        await self.history.save_close(
            ticket=ticket, close_price=close_price, profit=profit, reason=reason)
        self._record_stat(symbol, profit)
        try:
            self.risk.record_trade_result(profit)
        except Exception:
            pass
        self.riskdesk.on_trade_closed(profit)
        self.riskdesk.audit({"event": "close", "ticket": ticket, "symbol": symbol,
                             "profit": round(profit, 2), "reason": reason})

        # Signal DNA ga yozish (#83)
        vec = self._v2_open_vec.pop(ticket, None)
        if vec:
            hour = self._v2_open_hour.pop(ticket, datetime.now().hour)
            self.learning.record(vec, profit, symbol, hour)
        self.manager.unmark(ticket)
        self._open_ticket_map.pop(ticket, None)

        # Zarar bo'lsa — AI dars (#65)
        if profit < -0.5 and self.council:
            asyncio.create_task(self.council.learn_from_loss({
                "symbol": symbol, "side": side, "entry": entry,
                "close": close_price, "profit": round(profit, 2), "reason": reason,
                "breath": self.breath.get(symbol),
            }))

        await self.telegram.send_trade_close(
            symbol=symbol, side=side, entry=entry, close_price=close_price,
            profit=profit, reason=reason, ticket=ticket)

    async def _v2_close_position(self, pos: dict, reason: str) -> bool:
        """Paper/MT5/Binance pozitsiyani yopish (manager ishlatadi)"""
        try:
            ticket = pos.get("ticket")
            if pos.get("is_paper") or ticket in self.paper._positions:
                p = self.paper._positions.get(ticket)
                if p is None:
                    return False
                profit = p.paper_profit
                self.paper._positions.pop(ticket, None)
                await self._v2_on_close(ticket, p.symbol, p.side, p.entry_price,
                                        p.current_price, profit, reason)
                return True
            elif self._mode == self.MODE_BINANCE and self.binance_exec:
                res = await self.binance_exec.close_position(ticket)
                return bool(getattr(res, "success", res))
            elif self.execution:
                # DIQQAT: close_position(ticket, lot) — 2-arg LOT, reason emas!
                res = self.execution.close_position(ticket)
                return bool(getattr(res, "success", False))
        except Exception as e:
            logger.debug(f"v2 close #{pos.get('ticket')}: {e}")
        return False

    # ─── HEARTBEAT (#103) ─────────────────────────────────────────

    async def _v2_heartbeat(self, account: dict):
        try:
            balance = float(account.get("balance", 0))
            equity = float(account.get("equity", 0) or balance)
            positions = self._get_positions()
            breath_lines = []
            for sym in self._get_active_symbols(balance)[:4]:
                b = self.breath.get(sym)
                breath_lines.append(f"  {sym}: {b.get('score', '?')}/100 {b.get('label', '')}")
            pnl = self.riskdesk.daily_pnl
            text = (
                f"💓 <b>TORTINMANG.UZ v2 — soatlik holat</b>\n\n"
                f"{self.tier_engine.passport(balance)}\n\n"
                f"💰 Balans: ${balance:.2f} | Equity: ${equity:.2f}\n"
                f"📈 Bugungi P&L: {pnl:+.2f}$ | Savdolar: {self.riskdesk.daily_trades}\n"
                f"📊 Ochiq: {len(positions)} pozitsiya\n"
                f"🫁 Bozor nafasi:\n" + "\n".join(breath_lines)
            )
            await self.telegram.send(text)
        except Exception as e:
            logger.debug(f"Heartbeat: {e}")

    # ─── TAVSIF (status uchun) ────────────────────────────────────

    def v2_status(self) -> str:
        return (f"v{self.VERSION} | pog'ona={self.tier_engine.current().name} | "
                f"darslar={len(self.council.lessons) if self.council else 0} | "
                f"DNA={len(self.learning.dna)}")


def pd_series(df):
    """adx_trend yo'q bo'lsa zaxira qiymat"""
    try:
        return df["adx_trend"].iloc[-1]
    except Exception:
        return "?"
