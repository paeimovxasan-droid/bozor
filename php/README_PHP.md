# 🐘 TORTINMANG.UZ PHP Lite — Hostingda 24/7 (Libertex MT5)

Python/Windows/VPS **kerak emas** — istalgan PHP hostingda (cPanel cron)
ishlaydigan to'liq savdo dvigateli. Libertex MT5 hisobga **MetaApi.cloud**
bulut ko'prigi orqali ulanadi.

## 📦 Tarkib

| Fayl | Vazifa |
|------|--------|
| `index.php` | **Bosh sahifa** — barcha panellarga havolalar |
| `install.php` | **Web o'rnatuvchi** — brauzerda forma, config.php yozadi |
| `check.php` | **Ulanish tekshiruvi** — MetaApi/DeepSeek/Telegram ✅❌ |
| `status.php` | **Jonli panel** — balans, P&L, pog'ona, statistika (60s) |
| `cycle.php` | Asosiy sikl (cron har daqiqa) + 10 Telegram buyrug'i |
| `metaapi.php` | Libertex MT5 ko'prigi (savdo/shamlar/pozitsiya) |
| `lib.php` | Indikatorlar, risk, pog'ona, Telegram, DeepSeek |
| `config.example.php` | Sozlamalar namunasi |
| `.htaccess` | Xavfsizlik (state/log/config tashqariga yopiq) |
| `crontab.txt` | Cron namunasi |

## 🖥️ ISPmanager shared hosting (PHP 8.4 + MySQL) — batafsil

1. **Papka:** ISPmanager → *Fayl menejeri* → domeningiz `www/` (yoki
   `public_html/`) ichida **`tortinmang`** papka yarating →
   **TORTINMANG-PHP.zip** ni yuklab, shu yerga **oching (extract)**.

2. **PHP versiyasi:** ISPmanager → *Sozlamalar / PHP versiyasi* (yoki
   "Veb-sozlamalar → PHP") → domenga **PHP 8.4** tanlang.
   `curl` va `pdo_mysql` kengaytmalari odatda yoqilgan bo'ladi.

3. **MySQL:** ISPmanager → *Ma'lumot bazalari* → yangi baza yarating
   (masalan `tm_bot` + foydalanuvchi + parol). Ma'lumotlarni yozib oling —
   ularni install.php formasiga kiritasiz. Jadvallarni **install.php o'zi
   yaratadi** (yoki qo'lda: *phpMyAdmin → Import → schema.sql*).

4. **O'rnatish:** brauzerda `https://domen.uz/tortinmang/install.php` →
   forma (MetaApi token/account, DeepSeek, Telegram, **DB host/name/user/pass**)
   → Saqlash → "MySQL jadvallari yaratildi 🗄️" ko'rinsin.

5. **Tekshiruv:** `check.php` — hamma qator yashil ✅ bo'lsin.

6. **Cron:** ISPmanager → *Cron (rejali vazifalar)* → qo'shish:
   ```
   * * * * *  /usr/bin/php  /home/USERNAME/www/domen.uz/tortinmang/cycle.php
   ```
   PHP yo'li hostingda boshqacha bo'lishi mumkin (`php8.4`,
   `/usr/local/bin/php`) — ISPmanager "PHP yo'llari" bo'limida yoki
   qo'llab-quvvatlashdan aniqlang. `>> /dev/null 2>&1` qo'shish unutilmasin.

7. **Xavfsizlik:** `install.php` ni **o'chiring**; `.htaccess` state/log/
   journal/config ni tashqaridan yopib qo'ygan.

8. **Kuzatish:** `status.php` (Saqlash: **MySQL** ko'rinadi) va Telegram.

> Eslatma: DB sozlanmasa ham bot ishlayveradi — json fayl rejimida.

## 🚀 O'rnatish — 4 qadam

### 1. MetaApi hisob (5 daqiqa)
1. https://app.metaapi.cloud → ro'yxatdan o'ting
2. **Accounts** → Add account: broker **ForexClub/Libertex**, MT5 login/parol,
   server `ForexClub-MT5 Real Server`
3. **Token** va **Account ID** ni ko'chirib oling (bepul tarif yetarli)

### 2. Hostingga yuklash
`php/` papka ichidagini hosting `public_html/tortinmang/` ga yuklang
(FTP yoki file manager; **TORTINMANG-PHP.zip** ni ochib tashlang).

### 3. Web o'rnatuvchi
Brauzerda oching: `https://saytingiz.uz/tortinmang/install.php`
→ formani to'ldiring → Saqlash → `check.php` da hammasi yashil bo'lsin →
**install.php ni o'chiring!**

### 4. Cron
cPanel → Cron Jobs:
```
* * * * * /usr/bin/php /home/USER/public_html/tortinmang/cycle.php >> /dev/null 2>&1
```

TAYYOR!  `status.php` panel va Telegram xabarlari orqali kuzating.

## 📱 Telegram buyruqlari (har daqiqa javob beradi)

`/status` `/positions` `/closeall` `/close ID` `/pause` `/resume`
`/stats` `/history` `/risk` `/help`

## 🧠 Professional qatlamlar

- **Savdo jurnali** (`journal.json`) — har yopilgan savdo yoziladi, WR/PF hisoblanadi
- **Kunlik AI hisobot** — ertalab DeepSeek kechagi kunga xulosa yozadi
- **Anti-tilt** — 2 zarar: lot 50%; 3 zarar: 2 soat avtopauza
- **SL xavfsizligi** — broker tomonda SL yo'qolsa darhol tiklanadi
- **H1 multi-timeframe tasdiq** — katta trend qarshi bo'lsa savdo yo'q
- **Yangilik blackout** — NFP/CPI atrofi ±60 daqiqa savdo to'xtaydi
- **Juma himoyasi** — 20:00 dan keyin barcha pozitsiyalar yopiladi
- **Pog'ona tizimi** — balans o'ssa lot/risk avtomatik o'zgaradi

## ⚙️ Strategiya (Lite yadro)

- M15: EMA20/50 trend + RSI filtr + ATR volatillik darvozasi + spread sniffer
- Konflyuens ball ≥55; SL = 1.5×ATR, TP = 3×ATR (R:R 2.0)
- Risk: ETH 1% / XAU 1.8% + pog'ona risk-cap (BRONZE→DIAMOND avto)
- Min lot risk cap 3% — kichik balansda oltin halol bloklanadi
- Kunlik −3% stop | Haftalik −7% stop | +$5 maqsad lock
- Max 2 pozitsiya, 6 savdo/kun, 14:00–24:00 sessiya
- Partial TP +1R (50% + BE) | Time-stop 90 daq
- DeepSeek AI veto (kalit bo'lsa)

## ⚠️ Muhim

1. Birinchi hafta **DEMO Libertex hisob** bilan sinang!
2. `install.php` ni saqlagach **albatta o'chiring**.
3. PHP Lite = yengil dvigatel. To'liq "miya" (SMC, Signal DNA, AI Kengash)
   Python v2 da — ikkalasi parallel yurishi mumkin.
