"""
v2 Gatekeeper — g'oya #9-11, 14, 17, 18, 21, 23
================================================
Signal savdoga aylanishidan oldin darvozadan o'tadi:
  1. Sessiya filtri (London/NY — TST UTC+5)
  2. Yangilik blackout (NFP/CPI/FOMC taxminiy kalendar + qo'lda sana)
  3. Volatillik darvozasi (ATR juda past/yuqori emas)
  4. Signal TTL (3 daqiqa umr)
  5. Spread sniffer (o'rtachadan 1.5x keng bo'lsa kutish)
  6. Entry drift (signal narxidan uzoqlashsa bekor)
"""
import os
import json
from datetime import datetime, date

SIGNAL_TTL_SEC = int(os.getenv("SIGNAL_TTL_SEC", "180"))
ENTRY_DRIFT_PCT = float(os.getenv("ENTRY_DRIFT_PCT", "0.3"))
SPREAD_MULT = float(os.getenv("SPREAD_MULT", "1.5"))

# Savdo oynalari (TST = UTC+5). XAU: London+NY; ETH: kechki likvid soatlar
WINDOWS = {
    "XAUUSD": [(14, 24)],          # 14:00-00:00 TST
    "ETHUSD": [(14, 24), (0, 2)],  # kripto kechqurun eng faol
}


class SignalGate:
    def __init__(self):
        self._spread_hist: dict[str, list[float]] = {}
        self._custom_blackout = self._load_custom_blackout()
        self.news_blackout_until = None      # runtime blackout
        self.news_blackout_reason = ""

    # ── 1. sessiya ───────────────────────────────────────────────
    def session_ok(self, symbol: str, now: datetime = None) -> bool:
        now = now or datetime.now()
        h = now.hour + now.minute / 60
        for start, end in WINDOWS.get(symbol.upper(), [(0, 24)]):
            if start < end:
                if start <= h < end:
                    return True
            else:  # tundan o'tish
                if h >= start or h < end:
                    return True
        return False

    # ── 2. yangilik blackout (#14) ───────────────────────────────
    def _load_custom_blackout(self) -> list:
        """news_calendar.json — foydalanuvchi qo'shgan sanalar"""
        try:
            with open("news_calendar.json", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _recurring_news_events(self, d: date) -> list:
        """Takrorlanuvchi muhim yangiliklar (taxminiy, ehtiyotkor)"""
        ev = []
        # NFP — har oyning birinchi jumasi, ~17:30 TST
        if d.weekday() == 4 and d.day <= 7:
            ev.append(("NFP", 17, 30))
        # CPI — oy o'rtasi (10-15 kun oralig'i), ~17:30 TST
        if 10 <= d.day <= 15:
            ev.append(("CPI (taxminiy)", 17, 30))
        return ev

    def news_blackout(self, now: datetime = None) -> tuple[bool, str]:
        now = now or datetime.now()
        # runtime blackout (whale alert va h.k.)
        if self.news_blackout_until and now < self.news_blackout_until:
            return True, self.news_blackout_reason
        d = now.date()
        # qo'lda kalendar
        for item in self._custom_blackout:
            try:
                ed = date.fromisoformat(item.get("date", ""))
                if ed == d:
                    return True, f"📅 {item.get('name', 'Yangilik')}"
            except Exception:
                continue
        # takrorlanuvchi — hodisa atrofi ±60 daqiqa qora ro'yxat
        for name, hh, mm in self._recurring_news_events(d):
            ev_min = hh * 60 + mm
            now_min = now.hour * 60 + now.minute
            if abs(now_min - ev_min) <= 60:
                return True, f"📰 {name} (±60 daq)"
        return False, ""

    # ── 3. volatillik darvozasi (#11) ────────────────────────────
    def volatility_ok(self, atr: float, price: float) -> bool:
        if price <= 0 or atr <= 0:
            return False
        atr_pct = atr / price * 100
        # juda o'lik (chop) yoki juda xaosli bozor — savdo yo'q
        return 0.02 <= atr_pct <= 2.5

    # ── 4+6. TTL va drift ────────────────────────────────────────
    def entry_fresh(self, signal_ts: float, now_ts: float) -> bool:
        return (now_ts - signal_ts) <= SIGNAL_TTL_SEC

    def entry_drift_ok(self, signal_price: float, current_price: float) -> bool:
        if signal_price <= 0:
            return False
        drift = abs(current_price - signal_price) / signal_price * 100
        return drift <= ENTRY_DRIFT_PCT

    # ── 5. spread sniffer (#21) ──────────────────────────────────
    def spread_ok(self, symbol: str, spread: float) -> bool:
        h = self._spread_hist.setdefault(symbol, [])
        h.append(spread)
        if len(h) > 300:
            del h[: len(h) - 300]
        if len(h) < 10:
            return True
        avg = sum(h) / len(h)
        return spread <= max(avg * SPREAD_MULT, 1e-9)

    # ── umumiy darvoza ───────────────────────────────────────────
    def check(self, symbol: str, signal, atr: float, price: float,
              spread: float) -> tuple[bool, str]:
        if not self.session_ok(symbol):
            return False, "sessiya tashqarisi"
        nb, reason = self.news_blackout()
        if nb:
            return False, reason
        if not self.volatility_ok(atr, price):
            return False, "volatillik darvozasi"
        if not self.spread_ok(symbol, spread):
            return False, "spread juda keng"
        return True, "ok"

    # ── state ────────────────────────────────────────────────────
    def get_state(self):
        return {}

    def load_state(self, data):
        pass
