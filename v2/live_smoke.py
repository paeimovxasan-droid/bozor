"""UltraBotV2 jonli sikl smoke-test (tarmoqsiz simulyatsiya)"""
import os
import sys
import asyncio
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-smoke-test")

import numpy as np
import pandas as pd


async def main():
    from v2.bot import UltraBotV2

    bot = UltraBotV2()
    bot._mode = "mt5"

    rng = np.random.default_rng(5)
    n = 220
    close = 2500 + np.arange(n) * 0.9 + rng.normal(0, 1.5, n)
    open_ = np.concatenate([[close[0]], close[:-1]])
    high = np.maximum(open_, close) + 1.2
    low = np.minimum(open_, close) - 1.2
    idx = pd.date_range("2026-09-01", periods=n, freq="15min")
    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                       "volume": 5000 + rng.normal(0, 200, n)}, index=idx)
    from engines.market_data import MultiMarketDataEngine
    df_ind = MultiMarketDataEngine()._add_indicators(df)

    bot.market.mt5_connected = False
    bot.market.get_account_info = lambda: {"balance": 10.0, "equity": 10.0}
    bot.market.get_tick = lambda s: {"bid": float(close[-1]), "ask": float(close[-1]) + 0.4}

    async def scan_list(symbols):
        return {s: df_ind.copy() for s in symbols}
    bot.market.scan_all_markets_list = scan_list

    async def ohlc(symbol, tf="M15", bars=200):
        return df_ind.copy()
    bot.market.get_ohlc_async = ohlc

    async def _ok(*a, **kw):
        return True
    for m in ("send", "send_signal", "send_trade_close", "send_whale_alert",
              "send_risk_alert", "send_startup_ultra", "send_tier_upgrade"):
        setattr(bot.telegram, m, _ok)
    bot.telegram.poll_once = _ok
    bot.telegram.init_polling = _ok

    async def fake_review(*a, **kw):
        return "ok"
    async def fake_report(ctx):
        return "ok"
    bot.ai.quick_review = fake_review
    bot.ai.daily_report = fake_report
    bot.ai._request = fake_review

    ok = await bot.initialize()
    assert ok, "initialize muvaffaqiyatsiz"
    bot._load_state()

    # signal beradigan scanner
    async def fake_scan(market_data, balance):
        sig = types.SimpleNamespace(
            symbol="ETHUSD", signal="BUY", market_type="crypto",
            confidence=70.0, entry=float(close[-1]),
            stop_loss=float(close[-1]) - 8,
            take_profit=float(close[-1]) + 16,
            reason="smoke", whale_activity=None, rr_ratio=2.0,
            cluster_score=0.0, cluster_type="", poc=0.0, cvd_trend="")
        return types.SimpleNamespace(best_signals=[sig], total_signals=1,
                                     total_scanned=2, scan_time_ms=5,
                                     market_overview={})
    bot.scanner.scan_all = fake_scan

    async def filter_ok(**kw):
        return True, "ok"
    bot.sig_filter.check = filter_ok

    # Test deterministik bo'lishi uchun: sessiya ochiq + paper rejim
    bot.gate.session_ok = lambda *a, **kw: True
    bot.gate.news_blackout = lambda *a, **kw: (False, "")
    bot.paper.is_paper_mode = lambda b: True

    # 3 sikl ishlatsak — crash yo'qligini tekshiramiz
    for i in range(3):
        await bot.run_cycle()
        print(f"  ✅ sikl {i+1} OK | pozitsiya={len(bot._get_positions())} | "
              f"tier={bot.tier_engine.current().name} | "
              f"breath={bot.breath.get('ETHUSD').get('score')}")

    bot._save_state()
    print("\n✅ UltraBotV2 LIVE SMOKE TEST O'TDI — crash yo'q, state saqlandi")


if __name__ == "__main__":
    asyncio.run(main())
