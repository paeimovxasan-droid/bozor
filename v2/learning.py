"""
v2 Learning Core — g'oya #83-92, 92
===================================
• Signal DNA: har savdo indikatorlar vektori sifatida saqlanadi
• Pattern Memory (kNN): o'tgan G'ALABAlarga o'xshash holat → ishonch +bonus
• Soat xaritasi: o'z tarixidan eng foydali soatlarni o'rganadi
• Drift detection: WR tushsa avtomatik paper rejim taklifi
• Self-tuning: statistika asosida MIN_CONFIDENCE ±5 sozlanadi
"""
import math
from collections import defaultdict
from datetime import datetime

MAX_DNA = 400          # saqlanadigan savdo vektori
MIN_HOUR_SAMPLES = 8   # soat xaritasi ishlashi uchun minimal namuna


class LearningCore:
    def __init__(self):
        self.dna: list[dict] = []            # Signal DNA ombori
        self.hour_stats: dict = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0.0})
        self.recent: list[float] = []        # oxirgi savdolar P&L (drift uchun)
        self.confidence_offset = 0.0         # self-tuning natijasi

    # ── Signal DNA yozish (#83) ──────────────────────────────────
    @staticmethod
    def make_vector(sig, df_meta: dict, hour: int) -> list:
        """Signalni raqamli "DNK" ga aylantirish"""
        return [
            float(getattr(sig, "confidence", 0)) / 100.0,
            float(df_meta.get("rsi", 50)) / 100.0,
            float(df_meta.get("adx", 0)) / 50.0,
            float(df_meta.get("atr_pct", 0)),
            float(df_meta.get("mom", 0)),
            hour / 23.0,
            1.0 if getattr(sig, "signal", "") == "BUY" else 0.0,
        ]

    def record(self, vector: list, profit: float, symbol: str, hour: int):
        self.dna.append({"v": vector, "p": profit, "s": symbol})
        if len(self.dna) > MAX_DNA:
            del self.dna[: len(self.dna) - MAX_DNA]
        key = (symbol, hour)
        st = self.hour_stats[key]
        st["total"] += 1
        st["pnl"] += profit
        if profit > 0:
            st["wins"] += 1
        self.recent.append(profit)
        if len(self.recent) > 40:
            del self.recent[: len(self.recent) - 40]

    # ── Pattern Memory kNN (#84) ─────────────────────────────────
    def pattern_boost(self, vector: list, symbol: str, k: int = 7) -> float:
        """
        O'tgan savdolardan eng o'xshash k ta topiladi.
        G'oliblar ulushi yuqori bo'lsa +10 gacha bonus, aks holda -10.
        """
        pool = [d for d in self.dna if d["s"] == symbol]
        if len(pool) < 10:
            return 0.0
        dists = []
        for d in pool:
            dd = math.sqrt(sum((a - b) ** 2 for a, b in zip(vector, d["v"])))
            dists.append((dd, d["p"]))
        dists.sort()
        top = dists[:k]
        wins = sum(1 for _, p in top if p > 0)
        win_rate = wins / len(top)
        if win_rate >= 0.7:
            return +10.0
        if win_rate >= 0.55:
            return +5.0
        if win_rate <= 0.3:
            return -10.0
        return 0.0

    # ── Soat xaritasi (#24, #92) ─────────────────────────────────
    def hour_ok(self, symbol: str, hour: int) -> bool:
        st = self.hour_stats.get((symbol, hour))
        if not st or st["total"] < MIN_HOUR_SAMPLES:
            return True   # hali ma'lumot yetarli emas — ruxsat
        wr = st["wins"] / st["total"]
        return wr >= 0.30 or st["pnl"] > 0

    def best_hours(self, symbol: str, top: int = 5) -> list:
        rows = [(h, s) for (s, h), s_ in
                [(k, v) for k, v in self.hour_stats.items()]
                for s, h in [k] if s == symbol and s_["total"] >= MIN_HOUR_SAMPLES]
        rows.sort(key=lambda x: x[1]["pnl"], reverse=True)
        return [h for h, _ in rows[:top]]

    # ── Drift detection (#88) ────────────────────────────────────
    def drift_alert(self) -> bool:
        """Oxirgi 20 savdoda 15+ zarar → tizim "kasal", paper rejimga"""
        last = self.recent[-20:]
        if len(last) < 20:
            return False
        losses = sum(1 for p in last if p < 0)
        return losses >= 15

    # ── Self-tuning (#87) ────────────────────────────────────────
    def tune_confidence(self) -> float:
        """
        Oxirgi natijalarga qarab ishonch chegarasini ±5 siljitadi.
        Qaytarish: offset (-5..+5)
        """
        if len(self.recent) < 20:
            return 0.0
        last = self.recent[-20:]
        wins = sum(1 for p in last if p > 0)
        if wins <= 7:
            self.confidence_offset = min(self.confidence_offset + 2.5, 5.0)
        elif wins >= 13:
            self.confidence_offset = max(self.confidence_offset - 2.5, -5.0)
        return self.confidence_offset

    # ── state ────────────────────────────────────────────────────
    def get_state(self) -> dict:
        return {
            "dna": self.dna[-200:],
            "hour_stats": {f"{s}|{h}": v for (s, h), v in self.hour_stats.items()},
            "recent": self.recent[-40:],
            "confidence_offset": self.confidence_offset,
        }

    def load_state(self, data: dict):
        if not isinstance(data, dict):
            return
        self.dna = data.get("dna", [])
        self.recent = data.get("recent", [])
        self.confidence_offset = data.get("confidence_offset", 0.0)
        raw = data.get("hour_stats", {})
        self.hour_stats = defaultdict(lambda: {"wins": 0, "total": 0, "pnl": 0.0})
        for k, v in raw.items():
            try:
                s, h = k.split("|")
                self.hour_stats[(s, int(h))] = v
            except Exception:
                continue
