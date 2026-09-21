"""
v2 Trade Manager — g'oya #45, #47, #49, #50, #52
=================================================
• Time-stop: 90 daqiqada natija bo'lmasa pozitsiya yopiladi
• Weekend close: juma 20:00 dan keyin barcha pozitsiyalar yopiladi
• Emergency flat: bitta chaqiruvda hammasini yopish
(Partial TP / BE / trailing — v1 _manage_positions da qoladi, u yaxshi ishlaydi)
"""
import time
from datetime import datetime

TIME_STOP_MIN = 90          # daqiqa
WEEKEND_CLOSE_HOUR = 20     # juma soat 20:00 dan keyin


class TradeManagerV2:
    def __init__(self):
        self.open_ts: dict[int, float] = {}    # ticket → ochilgan vaqt
        self._weekend_closed_today = None

    def mark_open(self, ticket: int):
        self.open_ts[ticket] = time.time()

    def unmark(self, ticket: int):
        self.open_ts.pop(ticket, None)

    async def time_stop(self, bot) -> list:
        """90 daqiqa davomida foyda/zarar sezilarli bo'lmasa yopish (#45)"""
        closed = []
        now = time.time()
        for pos in list(bot._get_positions()):
            ticket = pos.get("ticket")
            ts = self.open_ts.get(ticket)
            if not ts:
                # oldingi sessiyadan qolgan pozitsiya — hozir belgilaymiz
                self.open_ts[ticket] = now
                continue
            age_min = (now - ts) / 60
            profit = float(pos.get("profit", 0) or 0)
            if age_min >= TIME_STOP_MIN and abs(profit) < 0.3:
                ok = await bot._v2_close_position(pos, reason="TIME_STOP")
                if ok:
                    closed.append(pos)
        return closed

    async def weekend_close(self, bot):
        """Juma 20:00 dan keyin hammasini yopish — gap himoyasi (#49)"""
        now = datetime.now()
        if now.weekday() != 4 or now.hour < WEEKEND_CLOSE_HOUR:
            return
        today = now.date().isoformat()
        if self._weekend_closed_today == today:
            return
        positions = bot._get_positions()
        if not positions:
            self._weekend_closed_today = today
            return
        for pos in list(positions):
            await bot._v2_close_position(pos, reason="WEEKEND_CLOSE")
        self._weekend_closed_today = today
        await bot.telegram.send(
            "🛡️ <b>Juma himoyasi</b>: weekend gap riskidan himoyalanish uchun "
            "barcha pozitsiyalar yopildi."
        )

    async def emergency_flat(self, bot, reason: str) -> int:
        """Hammasini darhol yopish (#52)"""
        count = 0
        for pos in list(bot._get_positions()):
            if await bot._v2_close_position(pos, reason=reason):
                count += 1
        return count
