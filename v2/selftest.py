"""
v2 Self-test — barcha modullarni 10 sekundda tekshiradi (#114)
Foydalanish:  python run_v2.py --test
"""
import asyncio
import types
from datetime import datetime, date

import numpy as np
import pandas as pd

PASS = []


def check(name: str, cond: bool):
    PASS.append((name, bool(cond)))
    mark = "✅" if cond else "❌"
    print(f"  {mark} {name}")


def synth_df(n=120, trend=0.5, seed=7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 2500 + np.arange(n) * trend + rng.normal(0, 2, n)
    open_ = np.concatenate([[close[0]], close[:-1]])
    high = np.maximum(open_, close) + rng.uniform(0.2, 1.5, n)
    low = np.minimum(open_, close) - rng.uniform(0.2, 1.5, n)
    idx = pd.date_range("2026-09-01", periods=n, freq="15min")
    df = pd.DataFrame({"open": open_, "high": high, "low": low,
                       "close": close, "volume": 5000 + rng.normal(0, 100, n)}, index=idx)
    from engines.market_data import MultiMarketDataEngine
    return MultiMarketDataEngine()._add_indicators(df)


async def run_selftest() -> bool:
    print("\n🧪 TORTINMANG.UZ v2 — SELF-TEST\n" + "─" * 42)

    # ── 1. Pog'ona tizimi ────────────────────────────────────────
    print("\n[1/7] Pog'ona tizimi (TierEngine)")
    from v2.tiers import TierEngine, TIERS

    # REGRESSION: bir kunda 100 marta tick bo'lsa ham promotion 5 KUN kutadi
    te_same = TierEngine()
    for _ in range(100):
        _, ev_same = te_same.tick(150, "2026-09-01")
    check("Bir kunda 100 tick → promotion YO'Q", ev_same != "PROMOTED")
    check("above_days=1 da qoldi (kun sanagichi)", te_same._state["above_days"] == 1)

    te = TierEngine()
    t = te.tier_for_balance(10)
    check("$10 → BRONZE", t.name == "BRONZE")
    check("$150 → SILVER", te.tier_for_balance(150).name == "SILVER")
    check("$800 → GOLD", te.tier_for_balance(800).name == "GOLD")
    check("$3000 → PLATINUM", te.tier_for_balance(3000).name == "PLATINUM")
    check("$9000 → DIAMOND", te.tier_for_balance(9000).name == "DIAMOND")
    # promotion 5 kundan keyin
    events = []
    for i in range(6):
        _, ev = te.tick(150, f"2026-09-{i+1:02d}")
        events.append(ev)
    check("5 kundan keyin PROMOTED", "PROMOTED" in events)
    check("Profit lock o'rnatildi", te._state.get("profit_lock") is not None)
    # demotion darhol
    _, ev = te.tick(50, "2026-09-10")
    check("Balans tushsa darhol DEMOTED", ev == "DEMOTED")
    check("Bronze lot cap 0.03", TIERS[0].lot_max == 0.03)

    # ── 2. Risk Desk ─────────────────────────────────────────────
    print("\n[2/7] Risk Desk")
    from v2.riskdesk import RiskDesk, contract_size
    rd = RiskDesk()
    rd.tick(100, 100)
    bronze = TIERS[0]
    lot, risk = rd.calc_lot(100, "ETHUSD", 10.0, bronze)
    # 100*1% = $1 risk; SL $10 → nazariy 0.1 lot, lekin BRONZE cap 0.03
    check("ETH sizing: lot cap 0.03", abs(lot - 0.03) < 1e-9)
    check("Risk ≤ 1.02%", risk <= 1.02 + 1e-6)
    # kichik balans: $10, SL $8 → 0.01 lot = 0.8% risk ✓
    lot_s, risk_s = rd.calc_lot(10, "ETHUSD", 8.0, bronze)
    check("$10 balans: risk 1.02% dan oshmaydi", risk_s <= 1.02 + 1e-6)
    lot2, _ = rd.calc_lot(1000, "XAUUSD", 3.0, TIERS[2])
    check("XAU sizing lot cap da", lot2 <= TIERS[2].lot_max + 1e-9)
    check("Kontrakt XAU=100", contract_size("XAUUSD") == 100)
    # kunlik zarar bloki
    rd2 = RiskDesk()
    rd2.tick(100, 100)
    ok, why = rd2.can_trade(bronze, 100, 96.5, 0)   # -3.5%
    check("Kunlik zarar limiti bloklaydi", not ok)
    # anti-tilt
    rd.on_trade_closed(-1); rd.on_trade_closed(-1)
    check("2 zarar → lot 50%", rd.anti_tilt_lot_factor() == 0.5)
    rd.on_trade_closed(-1)
    check("3 zarar → pauza", rd.paused_until is not None)
    ok, why = rd.can_trade(bronze, 100, 100, 0)
    check("Pauza paytida savdo yo'q", not ok)
    # daily target
    rd3 = RiskDesk(); rd3.tick(10, 10)
    check("Kunlik maqsad +$5 aniqlanadi", rd3.daily_target_reached(15.2, 5.0))

    # ── 3. Gatekeeper ────────────────────────────────────────────
    print("\n[3/7] Gatekeeper")
    from v2.gatekeeper import SignalGate
    g = SignalGate()
    ny = datetime(2026, 9, 15, 16, 0)     # seshanba 16:00 TST — London ochiq
    check("London sessiyasi ochiq (16:00)", g.session_ok("XAUUSD", ny))
    night = datetime(2026, 9, 15, 7, 0)
    check("Tongda sessiya yopiq (07:00)", not g.session_ok("XAUUSD", night))
    nfp = datetime(2026, 9, 4, 17, 30)    # birinchi juma → NFP
    nb, reason = g.news_blackout(nfp)
    check("NFP blackout ishlaydi", nb)
    check("Volatillik darvozasi (o'lik bozor)", not g.volatility_ok(0.1, 2500))
    check("Volatillik darvozasi (normal)", g.volatility_ok(8.0, 2500))
    check("Drift 0.1% ok", g.entry_drift_ok(2500, 2502))
    check("Drift 0.5% blok", not g.entry_drift_ok(2500, 2515))

    # ── 4. Learning ──────────────────────────────────────────────
    print("\n[4/7] Learning (DNA + kNN + soat xaritasi)")
    from v2.learning import LearningCore
    lc = LearningCore()
    vec = [0.6, 0.5, 0.5, 0.1, 0.2, 0.66, 1.0]
    for i in range(15):
        lc.record(vec, 1.0, "XAUUSD", 16)   # hammasi g'olib
    lc.record([0.1, 0.9, 0.1, 0.9, -0.5, 0.3, 0.0], -2.0, "XAUUSD", 3)
    boost = lc.pattern_boost(vec, "XAUUSD")
    check("G'olib pattern → bonus", boost > 0)
    check("Soat 16 yaxshi", lc.hour_ok("XAUUSD", 16))
    for i in range(20):
        lc.recent.append(-1.0)
    check("Drift detection (15+ zarar)", lc.drift_alert())
    lc.recent = lc.recent[-20:]
    off = lc.tune_confidence()
    check("Self-tuning offset ≤ 5", abs(off) <= 5.0)

    # ── 5. Bozor Nafasi + detektorlar ────────────────────────────
    print("\n[5/7] Bozor Nafasi + Whale Trap + Liquidity")
    from v2.breath import MarketBreath
    mb = MarketBreath()
    df = synth_df(trend=1.2)
    res = mb.compute("XAUUSD", df)
    check(f"Nafas hisoblandi ({res['score']}/100)", 0 <= res["score"] <= 100)
    check("Trend yuqoriga", res["direction"] == "UP")
    trap = mb.whale_trap(df)
    check("Whale trap funksiyasi ishlaydi", isinstance(trap, dict))
    levels = mb.liquidity_levels(df)
    check("Liquidity darajalar topildi", isinstance(levels, list))

    # ── 6. AI Kengash (fallback) ─────────────────────────────────
    print("\n[6/7] AI Kengash (AI yo'q bo'lsa fallback)")
    from v2.council import AICouncil

    class FakeAgent:
        async def _request(self, *a, **kw):
            raise RuntimeError("offline")

    council = AICouncil(FakeAgent())
    sig = types.SimpleNamespace(signal="BUY", symbol="XAUUSD", confidence=60.0,
                                entry=2500, stop_loss=2495, take_profit=2510)
    vote = await council.vote(sig, {"rsi": 55, "adx": 30, "atr_pct": 0.3,
                                    "trend": "UP", "hour": 16})
    check("Offline fallback: decision=BUY", vote["decision"] == "BUY")
    check("Offline veto yo'q", vote["veto"] is False)

    # ── 7. Trade Manager ─────────────────────────────────────────
    print("\n[7/7] Trade Manager (time-stop mantiqiy tekshiruv)")
    from v2.manager import TradeManagerV2
    import time as _t
    tm = TradeManagerV2()
    tm.mark_open(12345)
    tm.open_ts[12345] = _t.time() - 100 * 60   # 100 daqiqa oldin
    check("Time-stop belgilandi", 12345 in tm.open_ts)
    tm.unmark(12345)
    check("Time-stop tozalandi", 12345 not in tm.open_ts)

    # ── Xulosa ───────────────────────────────────────────────────
    print("\n" + "═" * 42)
    failed = [n for n, okk in PASS if not okk]
    if failed:
        print(f"❌ {len(failed)} ta test yiqildi: {failed}")
        return False
    print(f"✅ BARCHA {len(PASS)} TA SELF-TEST O'TDI — v2 TAYYOR!")
    return True


if __name__ == "__main__":
    import sys
    sys.exit(0 if asyncio.run(run_selftest()) else 1)
