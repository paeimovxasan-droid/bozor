# 🐘 TORTINMANG.UZ PHP Lite — 100% HOSTING, kompyuter kerak emas

**Kompyuter, Python, Windows, VPS — hech biri kerak emas.** Bot to'liq
arzon shared hostingda ishlaydi: cron har daqiqa siklni yurgizadi,
Libertex MT5 ga **MetaApi.cloud** bulut ko'prigi orqali ulanadi,
DeepSeek AI va Telegram ham HTTP orqali — hammasi hosting ichida.
Siz faqat telefoningizdan `admin.php` va Telegram orqali kuzatasiz.

## ✅ Hostingda nimalar avtomatik ishlaydi

| Vazifa | Qayerda ishlaydi |
|--------|------------------|
| Savdo sikli (har daqiqa) | Hosting cron |
| Libertex MT5 savdolari | MetaApi buluti (MetaTrader serveri) |
| DeepSeek AI tahlil | HTTP so'rov hostingdan |
| Telegram signallar/buyruqlar | getUpdates polling hostingdan |
| Balans/jurnal saqlash | MySQL (yoki json fayl) hostingda |
| Hisob ulash | admin.php — brauzerdan (telefon bo'ladimi!) |
| Avto savdo yoqish/o'chirish | admin.php tugmasi |

## 📦 Tarkib

| Fayl | Vazifa |
|------|--------|
| `index.php` | **Bosh sahifa** — barcha panellarga havolalar |
| `install.php` | **Web o'rnatuvchi** — brauzerda forma, config.php yozadi |
| `check.php` | **Ulanish tekshiruvi** — MetaApi/DeepSeek/Telegram ✅❌ |
| `test.php` | **Dvigatel self-test** — indikator/risk/jurnal logikasi |
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
   forma (MetaApi **token**, DeepSeek, Telegram, **DB host/name/user/pass**,
   admin parol) → Saqlash → "MySQL jadvallari yaratildi 🗄️" ko'rinsin.
   Sahifada **CRON URL** ko'rsatiladi — nusxalab oling.

5. **Hisob ulash:** `admin.php` → parol bilan kiring → Libertex MT5
   login/parol/server kiriting → **"Hisobni ulash"** tugmasi — hisob
   avtomatik yaratilib ulanadi. **Avto savdo** ni yoqing.

6. **Tekshiruv:** `check.php` (ulanishlar) va `test.php` (dvigatel logikasi) —
   hammasi yashil ✅ bo'lsin.

7. **Cron (3 usuldan biri, qarang crontab.txt):**
   - **CLI (eng ishonchli):** ISPmanager → *Cron jobs* → qo'shish:
     ```
     * * * * *  /usr/bin/php  /home/USERNAME/www/domen.uz/tortinmang/cycle.php
     ```
   - **HTTP (wget):** CLI ruxsat bo'lmasa — CRON URL ni wget bilan chaqirish:
     ```
     * * * * * wget -q -O /dev/null "https://domen.uz/tortinmang/cycle.php?key=CRON_KEY"
     ```
   - **Tashqi servis:** cron-job.org da bepul hisob → CRON URL, 60 sek interval.

8. **Xavfsizlik:** `install.php` ni **o'chiring**; `.htaccess` state/log/
   journal/config ni tashqaridan yopib qo'ygan.

9. **Kuzatish:** `status.php` (Saqlash: **MySQL** ko'rinadi), `admin.php`
   va Telegram — hammasi telefonda ham ochiladi. Kompyuter kerak emas!

> Eslatma: DB sozlanmasa ham bot ishlayveradi — json fayl rejimida.

## 📱 Telegram buyruqlari (har daqiqa javob beradi)

`/status` `/positions` `/closeall` `/close ID` `/pause` `/resume`
`/stats` `/history` `/risk` `/help`

## 🛠️ Admin panel (admin.php)

Parol bilan kiriladi (install.php da o'rnatilgan `ADMIN_PASS`). Imkoniyatlar:

- **🏦 Libertex hisobni panel orqali ulash** — MT5 login/parol/server kiritasiz,
  panel MetaApi provisioning API orqali hisobni **o'zi yaratib ulaydi**
  (yoki tayyor Account ID kiritish ham mumkin)
- **🤖 Avto savdo tugmasi** — yoqilgan bo'lsa bot o'zi signal topadi,
  savdo ochadi, partial TP + BE + trailing bilan **foydani qulflab yopadi**
- **📂 Jonli pozitsiyalar** — har birini yoki hammasini bir tugma bilan yopish
- **🛡️ Risk sozlamalari** — risk %, lot cap, kunlik maqsad/limit — brauzerdan
- **📈 Statistika va jurnal** — WR/PF, oxirgi savdolar jadvali

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
