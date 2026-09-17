"""
TORTINMANG.UZ — Backtest rejimi
==============================
Strategiyani TARIXIY ma'lumotda sinash — real pul tikmasdan.

Foydalanish:
    python backtest.py                          # XAUUSD,ETHUSD | 30 kun | M15
    python backtest.py --symbols XAUUSD --days 60
    python backtest.py --symbols BTCUSD,ETHUSD --days 90

Ma'lumot manbai:
  • MT5 o'rnatilgan bo'lsa (Windows) — ForexClub tarixiy barlari (barcha bozorlar)
  • Aks holda — Binance public klines: crypto to'g'ridan-to'g'ri,
    XAUUSD esa PAXGUSDT (gold token) orqali taxminiy.

Hisobot: savdolar soni, win-rate, profit-factor, max drawdown, yakuniy balans.
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─── MA'LUMOT ──────────────────────────────────────────────────────

GOLD_PROXY = {"XAUUSD": "PAXGUSDT"}   # Binance da oltin proxisi


async def fetch_binance_klines(symbol: str, days: int) -> "pd.DataFrame":
    """Binance public klines — M15, keys 1000 bar"""
    import aiohttp
    import pandas as pd

    bn_sym = symbol if symbol.endswith("USDT") else symbol.replace("USD", "USDT")
    end_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    start_ms = end_ms - days * 86400_000
    rows = []
    try:
        async with aiohttp.ClientSession() as s:
            while start_ms < end_ms:
                url = (f"https://api.binance.com/api/v3/klines?symbol={bn_sym}"
                       f"&interval=15m&startTime={start_ms}&limit=1000")
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                    if r.status != 200:
                        break
                    data = await r.json()
                if not data:
                    break
                rows += data
                start_ms = data[-1][0] + 1
    except Exception as e:
        print(f"  [!] Binance dan ma'lumot olinmadi: {e}")
    if not rows:
        return None
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbb", "tqb", "ignore"])
    df["time"] = pd.to_datetime(df["open_time"], unit="ms")
    df = df.set_index("time")
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = df[c].astype(float)
    df = df[["open", "high", "low", "close", "volume"]].rename(columns={"volume": "tick_volume"})
    return df


def fetch_mt5_history(symbol: str, days: int):
    """MT5 tarixiy barlari (Windows da)"""
    try:
        import MetaTrader5 as mt5
        import pandas as pd
    except ImportError:
        return None
    if not mt5.initialize():
        return None
    end = datetime.now()
    start = end - timedelta(days=days)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, start, end)
    mt5.shutdown()
    if rates is None or len(rates) < 250:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df.set_index("time")
    df = df[["open", "high", "low", "close", "tick_volume"]].copy()
    return df


# ─── SIMULYATSIYA ──────────────────────────────────────────────────

async def run_backtest(symbols: list, days: int, risk_pct: float):
    import pandas as pd
    from engines.market_data import MultiMarketDataEngine
    from engines.market_scanner import MultiMarketScanner

    mde = MultiMarketDataEngine()
    scanner = MultiMarketScanner()

    # Backtest da LIVE manbalar o'chiriladi — faqat tarixiy M15 ishlatiladi
    async def _h1_neutral(symbol, market_type):
        return "NEUTRAL", 0.0

    async def _ob_zero(symbol, price, market_type):
        return 0.0

    async def _fund_zero(symbol, signal):
        return 0.0

    class _ClusterZero:
        cluster_score = 0.0
        reason = "backtest"

        async def analyze_with_m5(self, *a, **kw):
            return self

    scanner._h1_trend = _h1_neutral
    scanner._orderbook_imbalance = _ob_zero
    scanner._get_funding_score = _fund_zero
    scanner.cluster = _ClusterZero()

    print("=" * 62)
    print("  TORTINMANG.UZ — BACKTEST (M15, tarixiy ma'lumot)")
    print("=" * 62)

    grand = {"trades": 0, "wins": 0, "gross_win": 0.0, "gross_loss": 0.0}

    for symbol in symbols:
        df = fetch_mt5_history(symbol, days)
        src = "MT5"
        if df is None:
            proxy = GOLD_PROXY.get(symbol)
            bn = proxy or (symbol if symbol.endswith("USDT") else None)
            label = symbol
            if proxy:
                label = f"{symbol} (PAXGUSDT proksi)"
            df = await fetch_binance_klines(proxy or symbol.replace("USD", "USDT"), days)
            src = f"Binance {label}"
        if df is None or len(df) < 300:
            print(f"\n[{symbol}] ma'lumot topilmadi (MT5 yo'q va Binance mavjud emas)")
            continue

        if "tick_volume" in df.columns:
            df = df.rename(columns={"tick_volume": "volume"})
        df = mde._add_indicators(df)
        n = len(df)
        print(f"\n▶ {symbol} [{src}] | {n} bar | "
              f"{df.index[0]:%Y-%m-%d} → {df.index[-1]:%Y-%m-%d}")

        balance = 1000.0
        peak = 1000.0
        max_dd = 0.0
        trades = wins = 0
        gross_win = gross_loss = 0.0
        WINDOW, STEP, HORIZON = 200, 4, 48

        for i in range(WINDOW, n - 1, STEP):
            window = df.iloc[i - WINDOW:i]
            signal = await scanner._scan_symbol(symbol, window.copy(), balance)
            if signal is None:
                continue

            entry = signal.entry
            sl = signal.stop_loss
            tp = signal.take_profit
            side = signal.signal

            # Natijani keyingi barlarda aniqlaymiz (SL birinchi tekshiriladi — konservativ)
            outcome, exit_price = None, None
            for j in range(i, min(i + HORIZON, n)):
                bar = df.iloc[j]
                if side == "BUY":
                    if bar["low"] <= sl:
                        outcome, exit_price = "LOSS", sl
                        break
                    if bar["high"] >= tp:
                        outcome, exit_price = "WIN", tp
                        break
                else:
                    if bar["high"] >= sl:
                        outcome, exit_price = "LOSS", sl
                        break
                    if bar["low"] <= tp:
                        outcome, exit_price = "WIN", tp
                        break
            if outcome is None:
                exit_price = float(df.iloc[min(i + HORIZON, n) - 1]["close"])
                gained = (exit_price - entry) if side == "BUY" else (entry - exit_price)
                outcome = "WIN" if gained > 0 else "LOSS"

            risk_amount = balance * risk_pct / 100
            rr = abs(tp - entry) / max(abs(entry - sl), 1e-10)
            pnl = risk_amount * rr if outcome == "WIN" else -risk_amount

            trades += 1
            if outcome == "WIN":
                wins += 1
                gross_win += pnl
            else:
                gross_loss += abs(pnl)
            balance += pnl
            peak = max(peak, balance)
            max_dd = max(max_dd, (peak - balance) / peak * 100)

        wr = wins / trades * 100 if trades else 0
        pf = gross_win / gross_loss if gross_loss > 0 else float("inf")
        print(f"   Savdolar: {trades} | Win-rate: {wr:.1f}% | "
              f"Profit-factor: {pf:.2f}")
        print(f"   $1000 → ${balance:.2f} | Max drawdown: {max_dd:.1f}%")
        grand["trades"] += trades
        grand["wins"] += wins
        grand["gross_win"] += gross_win
        grand["gross_loss"] += gross_loss

    print("\n" + "=" * 62)
    if grand["trades"]:
        wr = grand["wins"] / grand["trades"] * 100
        pf = grand["gross_win"] / grand["gross_loss"] if grand["gross_loss"] else float("inf")
        print(f"  JAMI: {grand['trades']} savdo | Win-rate {wr:.1f}% | PF {pf:.2f}")
        verdict = "🟢 Strategiya +EV ko'rinyapti" if (wr >= 45 and pf >= 1.3) else \
                  "🟡 O'rtacha — sozlamalarni sinang" if pf >= 1.0 else \
                  "🔴 Manfiy — real pulda ehtiyot bo'ling!"
        print(f"  Xulosa: {verdict}")
    else:
        print("  Signal hosil bo'lmadi — kunlar sonini oshiring yoki")
        print("  SIGNAL_STRENGTH/MIN_CONFIDENCE ni pasaytirib sinang.")
    print("=" * 62)


def main():
    parser = argparse.ArgumentParser(description="Tortinmang backtest")
    parser.add_argument("--symbols", default="XAUUSD,ETHUSD")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--risk", type=float, default=0.5,
                        help="Har savdoga risk %% (default 0.5)")
    args = parser.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    asyncio.run(run_backtest(symbols, args.days, args.risk))


if __name__ == "__main__":
    main()
