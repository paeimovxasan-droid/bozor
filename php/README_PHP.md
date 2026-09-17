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
