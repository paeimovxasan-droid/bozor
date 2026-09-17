"""
TORTINMANG.UZ — Integration test (tarmoqsiz, to'liq sikl simulyatsiyasi)
======================================================================
Barcha asosiy oqimlarni birga sinaydi:
  initialize → run_cycle (signal → savdo) → _manage_positions (partial TP)
  → _dogon_check → _sync_closed_positions → _daily_report

Foydalanish:  python tests_integration.py
"""
import os
import sys
import asyncio
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-integration-test")
os.environ.setdefault("FOCUS_MARKETS", "XAUUSD,ETHUSD")

import numpy as np
import pandas as pd

PASSED = []


def check(name, cond):
    PASSED.append((name, bool(cond)))
    print(f"  [{'OK' if cond else 'XX'}] {name}")


async def main():
    from core.orchestrator import UltraOrchestrator

    bot = UltraOrchestrator()
    bot._mode = "mt5"

    # ── Tashqi dunyoni neytrallashtirish ─────────────────────────
    rng = np.random.default_rng(11)
    n = 220
    t = np.arange(n)
    close = 2500 + t * 0.8 + rng.normal(0, 1.5, n)
    open_ = np.concatenate([[close[0]], close[:-1]])
    high = np.maximum(open_, close) + 1.0
    low = np.minimum(open_, close) - 1.0
    idx = pd.date_range("2026-09-01", periods=n, freq="15min")
    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                       "volume": 5000 + rng.normal(0, 200, n)}, index=idx)
    df.index.name = "time"

    from engines.market_data import MultiMarketDataEngine
    df_ind = MultiMarketDataEngine()._add_indicators(df.copy())

    bot.market.mt5_connected = False
    bot.market.get_account_info = lambda: {"balance": 10.0, "equity": 10.0}
    bot.paper.is_paper_mode = lambda b: True   # test uchun paper rejim majburiy
    bot.market.get_tick = lambda s: {"bid": 2500.0, "ask": 2500.5}
    async def scan_list(symbols):
        return {s: df_ind.copy() for s in symbols}
    bot.market.scan_all_markets_list = scan_list
    async def ohlc(symbol, tf="M15", bars=200):
        return df_ind.copy()
    bot.market.get_ohlc_async = ohlc

    # Telegram neytral
    for m in ("send", "send_signal", "send_trade_close", "send_whale_alert",
              "send_risk_alert", "send_startup_ultra"):
        async def _ok(*a, **kw):
            return True
        setattr(bot.telegram, m, _ok)
    bot.telegram.poll_once = _ok
    bot.telegram.init_polling = _ok

    # DeepSeek neytral
    async def fake_review(*a, **kw):
        return "AI test sharhi"
    async def fake_report(ctx):
        return "Test hisobot: XAUUSD yaxshi"
    bot.ai.quick_review = fake_review
    bot.ai.daily_report = fake_report

    # ── 1. initialize ────────────────────────────────────────────
    ok = await bot.initialize()
    check("initialize() True", ok)
    check("fokus = XAUUSD,ETHUSD", bot._get_active_symbols(50) == ["XAUUSD", "ETHUSD"])

    # ── 2. run_cycle: signal → paper savdo ───────────────────────
    # Scanner ni deterministik signal beradigan qilib almashtiramiz
    async def fake_scan(market_data, balance):
        sig = types.SimpleNamespace(
            symbol="XAUUSD", signal="BUY", market_type="commodity",
            confidence=60.0, entry=float(df_ind["close"].iloc[-1]),
            stop_loss=float(df_ind["close"].iloc[-1]) - 10,
            take_profit=float(df_ind["close"].iloc[-1]) + 20,
            reason="integration test", whale_activity=None,
            rr_ratio=2.0, cluster_score=0.0, cluster_type="", poc=0.0, cvd_trend="")
        return types.SimpleNamespace(best_signals=[sig], total_signals=1,
                                     total_scanned=2, scan_time_ms=5,
                                     market_overview={"sentiment": "RISK_ON",
                                                      "by_market_type": {}})
    bot.scanner.scan_all = fake_scan

    # Signal filter o'tkazsin
    async def filter_ok(**kw):
        return True, "ok"
    bot.sig_filter.check = filter_ok

    await bot.run_cycle()
    positions = bot._get_positions()
    check("paper savdo ochildi", len(positions) == 1)

    # ── 3. _manage_positions (partial TP / BE — paper xavfsiz) ───
    await bot._manage_positions(50.0)
    check("manage_positions crash yo'q", True)

    # ── 4. dogon: zarar simulyatsiyasi + tasdiq signal ───────────
    for p in bot.paper._positions.values():
        p.paper_profit = -0.04   # ~1% zarar ($4 balans)
        p.current_price = p.entry_price - 4
    async def fake_scan2(market_data, balance):
        sig = types.SimpleNamespace(
            symbol="XAUUSD", signal="BUY", market_type="commodity",
            confidence=70.0, entry=float(df_ind["close"].iloc[-1]) - 5,
            stop_loss=float(df_ind["close"].iloc[-1]) - 15,
            take_profit=float(df_ind["close"].iloc[-1]) + 15,
            reason="dogon test", whale_activity=None,
            rr_ratio=2.0, cluster_score=0.0, cluster_type="", poc=0.0, cvd_trend="")
        return types.SimpleNamespace(best_signals=[sig], total_signals=1,
                                     total_scanned=2, scan_time_ms=5,
                                     market_overview={})
    bot.scanner.scan_all = fake_scan2
    await bot._dogon_check(await fake_scan2({}, 50), {"balance": 50.0})
    check("dogon qo'shildi", len(bot._get_positions()) == 2)

    # ── 5. statistika + kunlik hisobot ───────────────────────────
    bot._record_stat("XAUUSD", 3.5)
    bot._record_stat("XAUUSD", -1.0)
    bot._record_stat("ETHUSD", 2.0)
    await bot._daily_report({"balance": 50.0})
    check("kunlik hisobot crash yo'q", True)

    # ── 6. state saqlash/yuklash ─────────────────────────────────
    bot._save_state()
    st = bot._sym_stats
    bot2 = UltraOrchestrator()
    bot2._state_file = bot._state_file
    bot2._load_state()
    check("state: sym_stats qayta yuklandi", bot2._sym_stats.get("XAUUSD", {}).get("trades") == 2)

    # ── Xulosa ───────────────────────────────────────────────────
    failed = [name for name, okk in PASSED if not okk]
    print()
    if failed:
        print(f"❌ {len(failed)} test yiqildi: {failed}")
        sys.exit(1)
    print(f"✅ BARCHA {len(PASSED)} INTEGRATION TEST O'TDI")


if __name__ == "__main__":
    asyncio.run(main())
