"""
v2 Bozor Nafasi va maxsus detektorlar — g'oya #115, #116, #117
================================================================
• Bozor Nafasi (0-100): trend kuchi + volatillik + hajm bitta indeksda
• Whale Trap Detection: stop-hunt shamini aniqlash → teskariga savdo imkoniyati
• Liquidity Magnet: teng cho'qqi/tublar — narx "tortiladigan" darajalar
"""
import numpy as np
import pandas as pd


class MarketBreath:
    def __init__(self):
        self._last: dict[str, dict] = {}

    # ── Bozor Nafasi indeksi (#115) ──────────────────────────────
    def compute(self, symbol: str, df: pd.DataFrame) -> dict:
        """
        0-100 indeks: 50 = neytral.
        >65 — trend nafas chuqur (trend savdolari);
        <35 — bozor uyquda/chop (ehtiyot);
        45-55 — noaniq.
        """
        try:
            close = df["close"].values[-60:]
            if len(close) < 30:
                return {"score": 50, "label": "ma'lumot yetarli emas"}
            ema20 = pd.Series(close).ewm(span=20).mean().values
            ema50 = pd.Series(close).ewm(span=50).mean().values \
                if len(close) >= 50 else pd.Series(close).ewm(span=min(len(close) - 1, 20)).mean().values
            price = close[-1]

            # trend kuchi: narx ema dan qancha uzoqda + ema qiyaligi
            trend_score = 50 + np.clip((price / ema20[-1] - 1) * 2000, -25, 25)
            slope = (ema20[-1] / ema20[-6] - 1) * 100
            trend_score += np.clip(slope * 8, -10, 10)

            # volatillik darajasi
            rets = np.diff(close) / close[:-1]
            vol_pct = np.std(rets) * 100
            vol_score = np.clip(vol_pct * 40, 0, 20) if np.abs(np.mean(rets)) > 0 else -5

            # hajm trendi
            if "volume" in df.columns and len(df) > 10:
                v = df["volume"].values[-10:]
                vol_trend = 5 if v[-1] > np.mean(v[:-1]) else -5
            else:
                vol_trend = 0

            score = int(np.clip(trend_score + vol_score + vol_trend, 0, 100))
            if score >= 65:
                label = "🔥 Nafas chuqur — trend kuchli"
            elif score >= 55:
                label = "📈 Nafas oshmoqda"
            elif score <= 35:
                label = "😴 Bozor uyquda/chop"
            else:
                label = "⚖️ Noaniq"
            res = {"score": score, "label": label,
                   "direction": "UP" if price > ema20[-1] else "DOWN"}
            self._last[symbol] = res
            return res
        except Exception:
            return {"score": 50, "label": "xato"}

    def get(self, symbol: str) -> dict:
        return self._last.get(symbol, {"score": 50, "label": "?"})

    # ── Whale Trap Detection (#116) ──────────────────────────────
    @staticmethod
    def whale_trap(df: pd.DataFrame, lookback: int = 12) -> dict:
        """
        Oxirgi sham oldingi ekstremumni YALANG'och fitil bilan buzib,
        qaytib ichkarida yopilsa — bu stop-hunt (tuzoq).
        Qaytarish: {"trap": "bull"|"bear"|None, "strength": 0-100}
        """
        try:
            if len(df) < lookback + 2:
                return {"trap": None, "strength": 0}
            h = df["high"].values
            l = df["low"].values
            c = df["close"].values
            prev_high = h[-lookback - 1:-1].max()
            prev_low = l[-lookback - 1:-1].min()
            last_h, last_l, last_c = h[-1], l[-1], c[-1]
            body = abs(last_c - df["open"].values[-1])

            # Ayiq tuzog'i: yuqoriga stop-hunt → pastda yopish (BUY imkoniyati)
            if last_h > prev_high and last_c < prev_high and last_c < df["open"].values[-1]:
                wick = last_h - max(last_c, df["open"].values[-1])
                strength = int(min(100, (wick / max(body, 1e-9)) * 25))
                return {"trap": "bull", "strength": strength}
            # Buqa tuzog'i: pastga stop-hunt → yuqorida yopish (SELL imkoniyati)
            if last_l < prev_low and last_c > prev_low and last_c > df["open"].values[-1]:
                wick = min(last_c, df["open"].values[-1]) - last_l
                strength = int(min(100, (wick / max(body, 1e-9)) * 25))
                return {"trap": "bear", "strength": strength}
            return {"trap": None, "strength": 0}
        except Exception:
            return {"trap": None, "strength": 0}

    # ── Liquidity Magnet darajalari (#117) ───────────────────────
    @staticmethod
    def liquidity_levels(df: pd.DataFrame, tol_pct: float = 0.05) -> list:
        """
        Teng cho'qqi/tublar (likvidlik hovuzlari) — narx odatda shu
        darajalarga "tortiladi". Qaytarish: [{"level": x, "touches": n, "side": "high"|"low"}]
        """
        try:
            if len(df) < 20:
                return []
            highs = df["high"].values[-50:]
            lows = df["low"].values[-50:]
            levels = []

            def cluster(vals, side):
                pts = sorted(vals)
                used = set()
                out = []
                for i, p in enumerate(pts):
                    if i in used:
                        continue
                    grp = [i]
                    for j in range(i + 1, len(pts)):
                        if j in used:
                            continue
                        if abs(pts[j] - p) / p * 100 <= tol_pct:
                            grp.append(j)
                            used.add(j)
                    if len(grp) >= 2:
                        out.append({"level": float(np.mean([pts[g] for g in grp])),
                                    "touches": len(grp), "side": side})
                return out

            levels += cluster(highs, "high")
            levels += cluster(lows, "low")
            levels.sort(key=lambda x: x["touches"], reverse=True)
            return levels[:6]
        except Exception:
            return []
