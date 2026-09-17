"""
v2 Pog'ona Tizimi (Tier Engine) — g'oya #127-136
=================================================
Balansga qarab 5 pog'ona profili avtomatik qo'llanadi:
  BRONZE ($10-100) → SILVER ($100-500) → GOLD ($500-2000)
  → PLATINUM ($2000-5000) → DIAMOND ($5000+)

Professional prinsip: balans oshgani sari risk% KAMAYADI —
kichik hisob o'sish uchun, katta hisob himoya uchun ishlaydi.
"""
import os
from dataclasses import dataclass, field


@dataclass
class TierProfile:
    name: str
    emoji: str
    min_balance: float
    lot_min: float
    lot_max: float
    risk_pct_xau: float          # XAUUSD savdo riski (%)
    risk_pct_eth: float          # ETHUSD savdo riski (%)
    daily_loss_pct: float        # kunlik zarar limiti (%)
    weekly_loss_pct: float       # haftalik zarar limiti (%)
    drawdown_stop_pct: float     # umumiy drawdown stop (%)
    max_positions: int
    max_per_symbol: int
    max_trades_day: int
    daily_target_usd: float      # yig'ilsa kun yopiladi
    style: str
    dogon_allowed: bool = True
    ai_veto_required: bool = False   # katta hisoblarda AI risk-desk veto
    iceberg_splits: int = 1          # katta lotni bo'lib yuborish

    def risk_pct(self, symbol: str) -> float:
        if "XAU" in symbol.upper() or "GOLD" in symbol.upper():
            return self.risk_pct_xau
        return self.risk_pct_eth


# ── Pog'onalar matritsa (IDEALAR.md 0A-bo'lim) ───────────────────
TIERS = [
    TierProfile(
        name="BRONZE", emoji="🥉", min_balance=0,
        lot_min=0.01, lot_max=0.03,
        risk_pct_xau=1.8, risk_pct_eth=1.0,
        daily_loss_pct=3.0, weekly_loss_pct=7.0, drawdown_stop_pct=20.0,
        max_positions=2, max_per_symbol=1, max_trades_day=6,
        daily_target_usd=5.0,
        style="Scalp + intraday (London/NY)", dogon_allowed=True,
    ),
    TierProfile(
        name="SILVER", emoji="🥈", min_balance=100,
        lot_min=0.03, lot_max=0.10,
        risk_pct_xau=1.5, risk_pct_eth=1.0,
        daily_loss_pct=2.5, weekly_loss_pct=6.0, drawdown_stop_pct=18.0,
        max_positions=3, max_per_symbol=1, max_trades_day=8,
        daily_target_usd=10.0,
        style="Intraday + qisqa swing", dogon_allowed=True,
    ),
    TierProfile(
        name="GOLD", emoji="🥇", min_balance=500,
        lot_min=0.05, lot_max=0.30,
        risk_pct_xau=1.0, risk_pct_eth=0.75,
        daily_loss_pct=2.0, weekly_loss_pct=5.0, drawdown_stop_pct=15.0,
        max_positions=4, max_per_symbol=2, max_trades_day=10,
        daily_target_usd=20.0,
        style="Swing asosiy (H1-H4) + scalp", dogon_allowed=False,
        ai_veto_required=True,
    ),
    TierProfile(
        name="PLATINUM", emoji="💎", min_balance=2000,
        lot_min=0.10, lot_max=0.50,
        risk_pct_xau=0.75, risk_pct_eth=0.5,
        daily_loss_pct=1.5, weekly_loss_pct=4.0, drawdown_stop_pct=12.0,
        max_positions=5, max_per_symbol=2, max_trades_day=10,
        daily_target_usd=40.0,
        style="70% swing (H4-D1), 30% intraday", dogon_allowed=False,
        ai_veto_required=True, iceberg_splits=2,
    ),
    TierProfile(
        name="DIAMOND", emoji="👑", min_balance=5000,
        lot_min=0.20, lot_max=1.0,
        risk_pct_xau=0.5, risk_pct_eth=0.3,
        daily_loss_pct=1.0, weekly_loss_pct=3.0, drawdown_stop_pct=10.0,
        max_positions=6, max_per_symbol=2, max_trades_day=12,
        daily_target_usd=80.0,
        style="Portfel: ko'p timeframe parallel", dogon_allowed=False,
        ai_veto_required=True, iceberg_splits=3,
    ),
]


class TierEngine:
    """
    Pog'ona dvigateli: balans → profil, promotion/demotion (5 kun barqarorlik),
    profit-lock zonalari, pasport matni. Holat dict ga saqlanadi.
    """
    PROMOTION_DAYS = int(os.getenv("TIER_PROMO_DAYS", "5"))

    def __init__(self):
        self._state = {
            "tier": "BRONZE",
            "above_days": 0,          # yuqori pog'ona chegarasidan yuqori ketma-ket kunlar
            "pending_tier": None,
            "profit_lock": None,      # himoyalangan kapital chegarasi
            "tier_history": [],       # [(sana, tier)]
        }

    # ── asosiy ───────────────────────────────────────────────────
    @staticmethod
    def tier_for_balance(balance: float) -> TierProfile:
        chosen = TIERS[0]
        for t in TIERS:
            if balance >= t.min_balance:
                chosen = t
        return chosen

    def current(self) -> TierProfile:
        for t in TIERS:
            if t.name == self._state["tier"]:
                return t
        return TIERS[0]

    def tick(self, balance: float, today: str) -> tuple[TierProfile, str]:
        """
        Har siklda chaqiriladi. Qaytarish: (profil, hodisa)
        hodisa: "" | "PROMOTED" | "DEMOTED"
        """
        event = ""
        target = self.tier_for_balance(balance)
        cur = self._state["tier"]

        # ── Demotion: balans orqaga tushsa DARHOL (hech qanday kutish yo'q)
        if target.min_balance < self.tier_min(cur):
            self._state["tier"] = target.name
            self._state["above_days"] = 0
            self._state["pending_tier"] = None
            self._state["promo_day"] = None
            self._state["profit_lock"] = None
            self._state["tier_history"].append((today, target.name))
            return target, "DEMOTED"

        # ── Promotion: 5 KUN ketma-ket chegaradan yuqori bo'lsagina.
        #    tick() har siklda (har daqiqa) chaqiriladi — shuning uchun
        #    kun sanagichi faqat KUN almashganda oshishi shart!
        if target.name != cur:
            counted_today = self._state.get("promo_day") == today
            if self._state["pending_tier"] == target.name:
                if not counted_today:
                    self._state["above_days"] += 1
                    self._state["promo_day"] = today
            else:
                self._state["pending_tier"] = target.name
                self._state["above_days"] = 1
                self._state["promo_day"] = today
            if self._state["above_days"] >= self.PROMOTION_DAYS:
                self._state["tier"] = target.name
                self._state["pending_tier"] = None
                self._state["above_days"] = 0
                self._state["promo_day"] = None
                # Profit lock: yangi pog'onada oldingi pog'ona chegarasi himoyalanadi
                prev_min = self.tier_min(cur)
                self._state["profit_lock"] = max(prev_min, balance * 0.85)
                self._state["tier_history"].append((today, target.name))
                return target, "PROMOTED"
        else:
            self._state["above_days"] = 0
            self._state["pending_tier"] = None
            self._state["promo_day"] = None

        return self.current(), event

    @staticmethod
    def tier_min(name: str) -> float:
        for t in TIERS:
            if t.name == name:
                return t.min_balance
        return 0.0

    def profit_lock_breached(self, balance: float) -> bool:
        """Himoyalangan kapital zonasiga tushib ketdimi?"""
        lock = self._state.get("profit_lock")
        return bool(lock and balance < lock)

    # ── pasport (Telegram /status uchun) ─────────────────────────
    def passport(self, balance: float) -> str:
        t = self.current()
        idx = TIERS.index(t)
        if idx < len(TIERS) - 1:
            nxt = TIERS[idx + 1]
            progress = min(100, int((balance - t.min_balance) /
                                    max(1, nxt.min_balance - t.min_balance) * 100))
            next_line = f"Keyingi: {nxt.emoji} {nxt.name} (${nxt.min_balance:.0f}) — {progress}%"
        else:
            next_line = "Eng yuqori pog'onada 👑"
        lock = self._state.get("profit_lock")
        lock_line = f"🔒 Profit lock: ${lock:.0f}\n" if lock else ""
        return (f"{t.emoji} <b>{t.name}</b> | ${balance:.2f}\n"
                f"{lock_line}"
                f"{next_line}\n"
                f"Uslub: {t.style}\n"
                f"Lot: {t.lot_min}-{t.lot_max} | Risk: ETH {t.risk_pct_eth}% / XAU {t.risk_pct_xau}%")

    # ── state ────────────────────────────────────────────────────
    def get_state(self) -> dict:
        return dict(self._state)

    def load_state(self, data: dict):
        if isinstance(data, dict):
            self._state.update(data)
