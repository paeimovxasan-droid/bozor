"""
v2 Risk Desk — g'oya #26-40
===========================
• Fixed-fractional sizing: lot = balans × risk% ÷ (SL masofasi × kontrakt hajmi)
• Hard lot cap, kunlik/haftalik zarar limiti, drawdown stop
• Anti-tilt: 2 zarar → lot 50%, 3 zarar → 2 soat pauza
• Equity Guardian: peak dan 5% tushsa yangi savdolar to'xtaydi
• Har savdo risk hisobi audit jurnaliga yoziladi
"""
import os
import json
from datetime import datetime, date, timedelta

# Kontrakt hajmlari (1 lot uchun): XAUUSD=100 oz, ETHUSD=1 ETH
# Libertex/ForexClub CFD da odatda ETH 1 lot = 1 ETH. Broker boshqacha
# bo'lsa .env da CONTRACT_ETH / CONTRACT_XAU bilan o'zgartiring.
CONTRACT_SIZE = {
    "XAUUSD": float(os.getenv("CONTRACT_XAU", "100")),
    "ETHUSD": float(os.getenv("CONTRACT_ETH", "1")),
}
DEFAULT_CONTRACT = float(os.getenv("CONTRACT_DEFAULT", "10"))

AUDIT_FILE = os.getenv("RISK_AUDIT_FILE", "risk_audit.jsonl")


def contract_size(symbol: str) -> float:
    s = symbol.upper()
    for k, v in CONTRACT_SIZE.items():
        if k in s:
            return v
    return DEFAULT_CONTRACT


class RiskDesk:
    def __init__(self, min_lot: float = 0.01):
        self.min_lot = min_lot
        self._today = date.today().isoformat()
        self._week = self._iso_week()
        self.daily_start_balance = 0.0
        self.week_start_balance = 0.0
        self.peak_equity = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.paused_until = None            # datetime — anti-tilt pauza
        self.manual_pause = False           # Telegram /pause
        self.emergency_stop = False         # /stop yoki drawdown stop
        self.emergency_reason = ""
        self.daily_pnl = 0.0
        self._lock_notified = False

    @staticmethod
    def _iso_week() -> str:
        d = date.today()
        return f"{d.isocalendar()[0]}-W{d.isocalendar()[1]}"

    # ── har sikl boshida ─────────────────────────────────────────
    def tick(self, balance: float, equity: float):
        """Sana/hafta almashishini nazorat qiladi, peak yangilaydi."""
        today = date.today().isoformat()
        if today != self._today:
            self._today = today
            self.daily_start_balance = balance
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self._lock_notified = False
        wk = self._iso_week()
        if wk != self._week:
            self._week = wk
            self.week_start_balance = balance
        if equity > self.peak_equity:
            self.peak_equity = equity
        if self.daily_start_balance <= 0:
            self.daily_start_balance = balance
        if self.week_start_balance <= 0:
            self.week_start_balance = balance

    # ── lot hisoblash (fixed-fractional) ─────────────────────────
    def calc_lot(self, balance: float, symbol: str, sl_distance: float,
                 tier) -> tuple[float, float]:
        """
        Qaytarish: (lot, haqiqiy_risk_pct)
        tier — TierProfile. Har doim tier lot diapazonida cheklanadi.
        """
        if sl_distance <= 0:
            return 0.0, 0.0
        risk_pct = tier.risk_pct(symbol) / 100.0
        risk_amount = balance * risk_pct
        cs = contract_size(symbol)
        raw_lot = risk_amount / (sl_distance * cs)
        lot = max(self.min_lot, min(raw_lot, tier.lot_max))
        lot = round(lot, 2)
        actual_risk_pct = (lot * sl_distance * cs) / max(balance, 0.01) * 100
        return lot, actual_risk_pct

    # ── savdo oldidan tekshiruv ──────────────────────────────────
    def can_trade(self, tier, balance: float, equity: float,
                  positions_count: int) -> tuple[bool, str]:
        if self.emergency_stop:
            return False, f"🛑 Emergency stop: {self.emergency_reason}"
        if self.manual_pause:
            return False, "⏸️ Qo'lda to'xtatilgan (/resume bilan davom)"
        now = datetime.now()
        if self.paused_until and now < self.paused_until:
            left = int((self.paused_until - now).total_seconds() / 60)
            return False, f"😤 Anti-tilt pauza ({left} daq qoldi)"
        # kunlik zarar limiti
        if self.daily_start_balance > 0:
            dl = (self.daily_start_balance - equity) / self.daily_start_balance * 100
            if dl >= tier.daily_loss_pct:
                return False, f"🔴 Kunlik zarar limiti: -{dl:.1f}% (max {tier.daily_loss_pct}%)"
        # haftalik zarar limiti
        if self.week_start_balance > 0:
            wl = (self.week_start_balance - equity) / self.week_start_balance * 100
            if wl >= tier.weekly_loss_pct:
                return False, f"🔴 Haftalik zarar limiti: -{wl:.1f}% (max {tier.weekly_loss_pct}%)"
        # umumiy drawdown stop
        if self.peak_equity > 0:
            dd = (self.peak_equity - equity) / self.peak_equity * 100
            if dd >= tier.drawdown_stop_pct:
                self.emergency_stop = True
                self.emergency_reason = f"Drawdown {dd:.1f}% (max {tier.drawdown_stop_pct}%)"
                return False, f"🛑 {self.emergency_reason}"
        # equity guardian: peak dan 5%+ tushsa yangi savdolar to'xtaydi
        if self.peak_equity > 0 and equity < self.peak_equity * 0.95:
            return False, "🛡️ Equity Guardian: peak dan 5%+ past — kuzatuv rejimi"
        # limitlar
        if self.daily_trades >= tier.max_trades_day:
            return False, f"⏳ Kunlik savdo limiti: {tier.max_trades_day}"
        if positions_count >= tier.max_positions:
            return False, f"📊 Pozitsiya limiti: {tier.max_positions}"
        return True, "ok"

    # ── hodisalar ────────────────────────────────────────────────
    def on_trade_opened(self):
        self.daily_trades += 1

    def on_trade_closed(self, profit: float):
        self.daily_pnl += profit
        if profit < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= 3:
                self.paused_until = datetime.now() + timedelta(hours=2)
                self.consecutive_losses = 0
        else:
            self.consecutive_losses = 0

    def anti_tilt_lot_factor(self) -> float:
        """2 ketma-ket zarar bo'lsa lot 50% kamayadi (#32)"""
        return 0.5 if self.consecutive_losses >= 2 else 1.0

    def daily_target_reached(self, equity: float, target_usd: float) -> bool:
        """Kunlik foyda maqsadi yig'ildimi? (#47)"""
        if target_usd <= 0:
            return False
        if self.daily_start_balance <= 0:
            return False
        return (equity - self.daily_start_balance) >= target_usd

    # ── audit jurnal (#40) ───────────────────────────────────────
    def audit(self, record: dict):
        try:
            record["ts"] = datetime.now().isoformat(timespec="seconds")
            with open(AUDIT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass

    # ── state ────────────────────────────────────────────────────
    def get_state(self) -> dict:
        return {
            "daily_start_balance": self.daily_start_balance,
            "week_start_balance": self.week_start_balance,
            "peak_equity": self.peak_equity,
            "daily_trades": self.daily_trades,
            "consecutive_losses": self.consecutive_losses,
            "daily_pnl": self.daily_pnl,
            "today": self._today,
        }

    def load_state(self, data: dict):
        if not isinstance(data, dict):
            return
        self.daily_start_balance = data.get("daily_start_balance", 0.0)
        self.week_start_balance = data.get("week_start_balance", 0.0)
        self.peak_equity = data.get("peak_equity", 0.0)
        self.daily_trades = data.get("daily_trades", 0)
        self.consecutive_losses = data.get("consecutive_losses", 0)
        self.daily_pnl = data.get("daily_pnl", 0.0)
        if data.get("today") and data["today"] != date.today().isoformat():
            # eski kun ma'lumotlari — yangi kun uchun reset
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self.daily_start_balance = 0.0
