# 🚀 TORTINMANG.UZ v2.0 — Libertex Edition
## Pog'ona tizimi • AI Kengash • Risk Desk | ForexClub / Libertex via MT5

---

## ⚡ v2.0 — 3 TA BOSISHDA ISHGA TUSHIRISH (Windows)

| Fayl | Vazifa |
|------|--------|
| 🟢 **`ORNATISH.bat`** | Hammasini avtomatik o'rnatadi (Python kutubxonalar, .env, test) — **birinchi shu** |
| 🔵 **`START_BOT.bat`** | Botni ishga tushiradi |
| 🟡 **`TEST_BOT.bat`** | 38 ta self-test — tizim sog'lomligini tekshiradi |
| 🟣 **`BACKTEST.bat`** | Oxirgi 30 kunlik tarixda strategiya testi |

Terminal orqali ham mumkin:
```bash
python run_v2.py            # bot (hech qanday flag kerak emas!)
python run_v2.py --test     # self-test
python run_v2.py --backtest # tarixiy test (--days 90 --symbols XAUUSD)
python run_v2.py --check    # muhit tekshiruvi
```

### v2.0 yangiliklari (136 g'oya asosida)
- 🏦 **Pog'ona tizimi**: BRONZE ($10)→SILVER→GOLD→PLATINUM→DIAMOND ($5000+) — balansga qarab lot/risk/limitlar AVTO almashadi
- 🛡️ **Risk Desk**: har savdoda aniq risk formula, kunlik/haftalik limitlar, anti-tilt, equity guardian, audit jurnal
- 🧠 **AI Kengash**: 3 DeepSeek persona (Trendchi, Skalpchi, Risk-ofitser VETO)
- 🧬 **Learning**: Signal DNA + Pattern Memory (kNN) + Soat xaritasi + Drift detection + Self-tuning
- 🫁 **Bozor Nafasi** indeksi + 🐋 Whale Trap detektori + 🧲 Liquidity magnetlar
- 🚪 **Gatekeeper**: sessiya filtri, yangilik blackout (NFP/CPI), volatillik darvozasi, spread sniffer
- ⏱️ **Trade Manager**: partial TP ladder, break-even, trailing, time-stop, juma himoyasi, kunlik maqsad qulfi
- 📲 Telegram: /status da pog'ona pasporti, soatlik heartbeat

> Eski v1: `python run.py` (saqlanib qolgan)

---

## 🐘 PHP Lite — hostingda 24/7 (Windows/VPS kerak emas!)

Libertex MT5 ga **MetaApi.cloud** ko'prigi orqali ulanadigan yengil dvigatel —
istalgan PHP hostingda (cPanel cron) ishlaydi. Batafsil: [`php/README_PHP.md`](./php/README_PHP.md)

```
php/cycle.php  — har daqiqa cron: tahlil → risk → savdo → boshqaruv
php/config.php — MetaApi token + Libertex hisob + Telegram + DeepSeek
```

---

> 📖 **Batafsil o'rnatish va ishlatish qo'llanmasi:** [`QO'LLANMA.md`](./QO'LLANMA.md) — 18 bob, step-by-step, Windows/Linux, Telegram, xatolar yechimi

> **Broker:** ForexClub (Libertex) — `ForexClub-MT5 Real Server`
> Eski Binance rejimi ixtiyoriy (`ENABLE_BINANCE=true`), asosiy rejim — **Libertex MT5**

---

## 🌐 Qamrab olingan bozorlar (30+ instrument) — Libertex MT5

| Kategoriya | Instrumentlar | Tier | Manba |
|-----------|--------------|------|-------|
| 💱 Forex  | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD | Micro+ | Libertex MT5 |
| 🏅 Metallar | XAUUSD, XAGUSD | Micro+ | Libertex MT5 |
| 🛢️ Energiya | USOIL, UKOIL | Mini+ | Libertex MT5 |
| ₿ Crypto | BTCUSD, ETHUSD, BNBUSD, SOL, XRP, ADA, DOT, AVAX | Micro+ | Libertex MT5 CFD |
| 📊 Indekslar | US500, USTEC, US30, GER40 | Standard+ | Libertex MT5 |
| 📈 Aksiyalar | AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, META | Advanced+ | Libertex MT5 |

> **Barchasi bitta MT5 hisobda!** Binance kerak emas. Libertex MT5 da crypto ham CFD sifatida mavjud.

---

## 🏦 Libertex ga ulanish

```bash
# 1. Libertex hisobingizni oling
#    https://libertex.org → Ro'yxatdan o'tish → Tasdiqlash

# 2. MT5 ma'lumotlarini oling
#    Libertex kabineti → "Mening hisoblarim" → MT5 → Login / Parol / Server
#    Server masalan: ForexClub-MT5 Real Server (yoki ForexClub-MT5 Demo Server)

# 3. .env ni sozlang
cp .env.example .env
# .env da quyidagilarni to'ldiring:
# MT5_LOGIN=12345678
# MT5_PASSWORD=sizning_parol
# MT5_SERVER=ForexClub-MT5 Real Server  ← AYNAN shunday, 100% to'g'ri!

# 4. MT5 terminal o'rnating (Windows)
#    https://www.fxclub.org → MT5 yuklab olish → O'rnatish

# 5. Test qilish
python run.py --test
# [OK] Libertex MT5: ForexClub-MT5 Real Server | Balans $... bo'lsa tayyor!

# 6. Botni ishga tushirish
python run.py --bot
```

### ForexClub MT5 serverlari
| Hisob turi | Server nomi | Manzil |
|---|---|---|
| **Real** | `ForexClub-MT5 Real Server` | `mt5-real-prim.fxclub.org` |
| **Demo** | `ForexClub-MT5 Demo Server` | `mt5-demo-prim.fxclub.org` |
| **Real 2** | `ForexClub-MT5 Real Server 2` | alternativ |

> ⚠️ Server nomini Libertex kabinetidagi kabi **100% aynan** ko'chiring! Bitta harf xatosi ham loginni buzadi.

---

## 🤖 DeepSeek AI — yagona AI provayder

Barcha AI tahlillar (bozor sharhi, signal tekshiruvi, `/ask` chat) **faqat
DeepSeek** orqali ishlaydi — rasmiy docs: https://api-docs.deepseek.com

```env
DEEPSEEK_API_KEY=sk-...                 # platform.deepseek.com/api_keys
DEEPSEEK_MODEL=deepseek-flash           # arzon/tez (tavsiya)
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_REASONING_EFFORT=none          # none=tez | low | high | max
```

> ⚠️ **MUHIM:** eski `deepseek-chat` / `deepseek-reasoner` nomlari 2026-07-24 da
> o'chirilgan — ular endi ishlamaydi. Hozirgi modellar: `deepseek-flash` va
> `deepseek-v4-pro`. Tizim eski nomni avtomatik `deepseek-flash` ga almashtiradi.

```bash
python test_deepseek.py   # DeepSeek API ni alohida tekshirish
python run.py --test      # to'liq tizim testi (DeepSeek bo'limi bilan)
```

---

## 🎯 Fokus bozorlar va har daqiqa tahlil

Bot default holatda **faqat XAUUSD va ETHUSD** ni tahlil qiladi va
**har 60 soniyada** (har daqiqa) yangi sikl o'tkazadi:

```env
FOCUS_MARKETS=XAUUSD,ETHUSD   # asosiy savdo bozorlari
CYCLE_SECONDS=60              # tahlil davri (soniya)
SCAN_ALL_MARKETS=false        # true = barcha 30+ bozor
```

> Tahlil **har daqiqa** yuradi, lekin savdo faqat kuchli signal topilganda
> ochiladi (risk boshqaruvi shuni talab qiladi). Ko'proq savdo xohlasangiz:
> ```env
> MIN_CONFIDENCE=40   # default 45
> MIN_ADX=18          # default 20
> SIGNAL_STRENGTH=12  # default 14
> ```
> ⚠️ Ostonglarni pasaytirish ko'proq savdo beradi, lekin sifati/xavf ham o'zgaradi.
> Avval demo hisobda sinang!

---

## 🔁 Smart Dogon (DCA-recovery)

Zararda turgan pozitsiyaga **yangi tasdiqlovchi signal** kelsa, bot bitta
qo'shimcha pozitsiya ochadi — o'rtacha kirish narxi yaxshilanadi.
Bu **nazoratsiz martingale EMAS** — qat'iy himoya bilan:

- har pozitsiyaga **max 1 dogon** (`DOGON_MAX`)
- lot oshirilmaydi (`DOGON_LOT_MULT=1.0`)
- dogon signali **kuchliroq** bo'lishi shart (`DOGON_MIN_CONF=50`)
- zarar **2% dan oshsa** dogon qilinmaydi (`DOGON_MAX_LOSS_PCT`)
- bir symbolga **30 daqiqa** cooldown (`DOGON_COOLDOWN`)

```env
DOGON_ENABLED=true
DOGON_MAX=1
DOGON_LOT_MULT=1.0
DOGON_MIN_CONF=50
DOGON_MAX_LOSS_PCT=2.0
```

Logda: `🔁 DOGON XAUUSD BUY #1: zarar 1.5% | yangi signal 62.0%`
Telegramda signal xabarida `🔁 DOGON #1` belgisi ko'rinadi.

---

## 💰 Foydani himoya qilish tizimi (+EV uchun)

| Funksiya | Nima qiladi |
|----------|-------------|
| **Partial TP** | Narx 1R ga yetganda pozitsiyaning 50% i yopiladi — foyda qulflanadi, SL breakeven ga |
| **Break-even + Trailing** | 0.5 ATR foydada SL kirish narxiga, keyin narx ortidan yuradi |
| **Spread himoyasi** | Yangilik paytida spread kengaysa (`max_spread_pct=0.05%`) savdo ochilmaydi |
| **Symbol statistikasi** | Har symbol bo'yicha win-rate/P/L yig'iladi, kunlik hisobotda ko'rinadi |
| **Kunlik AI hisobot** | Har kun almashganda DeepSeek statistika bo'yicha xulosa yozib Telegram ga yuboradi |
| **Backtest** | `python backtest.py --days 60` — real pul tikmasdan strategiya testi |

### Backtest (Windows/MT5 da barcha bozorlar, Linux da crypto + oltin proksi)

```cmd
python backtest.py                          # XAUUSD+ETHUSD, 30 kun
python backtest.py --symbols XAUUSD --days 90
python backtest.py --symbols BTCUSD,ETHUSD --days 120 --risk 0.5
```

Natija: savdolar soni, win-rate, profit-factor, max drawdown va xulosa
(🟢/🟡/). Real hisobda savdo qilishdan OLDIN backtest o'tkazishni tavsiya qilamiz.

---

## 💰 Kapital o'sishi tizimi (Libertex uchun moslashtirilgan)

```
$10–100    → 🔵 MIKRO   (0.3% risk | 1 pozitsiya | 5 bozor)  — EURUSD, XAUUSD, BTCUSD, ETHUSD, GBPUSD
$100–500   → 🟢 MINI    (0.5% risk | 2 pozitsiya | 7 bozor)
$500–2000  → 🟡 STANDART(0.7% risk | 3 pozitsiya | 10 bozor)
$2000–5000 → 🟠 ADVANCED(1.0% risk | 4 pozitsiya | 18 bozor)
$5000+     → 🔴 PRO     (1.2% risk | 5 pozitsiya | 30+ bozor)
```

---

## 🐋 Whale & Volume Monitoring (Libertex)

```
Libertex rejimida:
├ MT5 tick_volume + V3 Cluster (POC/VAH/VAL) — ASOSIY
├ CVD (Cumulative Volume Delta) — sham strukturasidan
├ Volume Profile & Point of Control
├ VWAP deviation
├ SMC (BOS/CHOCH/OB/FVG)
└ Binance WS/OrderBook — faqat ENABLE_BINANCE=true bo'lsa
```

Whale signal turlari:
- **ACCUMULATION** → Kitlar yig'moqda → BUY
- **DISTRIBUTION** → Kitlar tarqatmoqda → SELL
- **STOP_HUNT** → Stop ovlash → Reversal kutish

---

## 🧠 Signal Generatsiya — Libertex Edition

```
Texnik tahlil    (18%) — EMA, RSI, MACD, Stoch, BB, Price Action
Liquidity Engine (12%) — POC, Support/Resistance, Sweep
SMC Engine       (20%) — BOS, CHOCH, OB, FVG, Premium/Discount
Whale Monitor    (12%) — Volume spike, CVD
Momentum         (8%)  — ROC/ATR
Volume Divergence(5%)  — Narx vs hajm
H1 Trend         (5%)  — EMA21/EMA50 + RSI (MT5 H1 dan)
V3 Cluster       (15%) — POC/VAH/VAL/CVD (MT5 OHLC dan)
OrderBook        (5%)  — faqat Binance yoqilganda, aks holda 0

JAMI → ≥45% ishonch + ADX ≥20 → TRADE!
```

---

## 🛡️ Risk boshqaruvi

| Parametr | Qiymat |
|----------|--------|
| Risk per trade | 0.3%–1.2% (tier bo'yicha) |
| Kunlik limit | 2%–5% |
| Haftalik limit | 10% |
| Max Drawdown | 20% |
| Min R:R | 1:1.5 |
| Smart SL | Swing + yumaloq sondan qochish + ATR multiple dan qochish |
| Emergency close | 18% drawdown da barcha yopiladi |

---

## 🚀 Ishga tushirish — Libertex

```bash
# 1. O'rnatish
pip install -r requirements.txt

# 2. Sozlash
cp .env.example .env
# MT5_LOGIN, MT5_PASSWORD, MT5_SERVER (Libertex) ni kiriting

# 3. Test
python run.py --test
# Barcha [OK] bo'lsa davom eting

# 4. Bot
python run.py --bot

# 5. API server (ixtiyoriy)
python run.py --api
# yoki
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 6. Telegram buyruqlari
# /status — Libertex balans
# /trades — ochiq pozitsiyalar
# /scan EURUSD — tahlil
# /buy EURUSD — qo'lda BUY
```

---

## 📡 API Endpointlar

| Method | URL | Tavsif |
|--------|-----|--------|
| GET | / | Broker va versiya |
| GET | /api/v2/dashboard | To'liq dashboard (Libertex balans) |
| GET | /api/v2/markets | Barcha bozorlar |
| GET | /api/v2/scan | Real-time skanerlash |
| GET | /api/v2/whale/{symbol} | Whale tahlili |
| GET | /api/v2/performance | Performance statistika |
| POST | /api/v2/trade/close-all | Barcha yopish |
| POST | /api/v2/system/start | Botni boshlash |

---

## ⚙️ .env — Libertex sozlanmasi

```env
# DeepSeek AI — YAGONA AI provayder (MUHIM)
# Key: https://platform.deepseek.com → API Keys → Create
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-flash          # deepseek-flash | deepseek-v4-pro
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_REASONING_EFFORT=none         # none | low | high | max

# Asosiy — Libertex MT5
MT5_LOGIN=12345678
MT5_PASSWORD=******
MT5_SERVER=ForexClub-MT5 Real Server
BROKER=ForexClub
MT5_PATH=  # Windows da kerak bo'lsa: C:\Program Files\ForexClub MT5\terminal64.exe

# Binance — ixtiyoriy (o'chiq holda Libertex 100% ishlaydi)
ENABLE_BINANCE=false

# Telegram, DB...
```

---

## ❓ Libertex vs Binance — farqi nima?

| | Libertex (ForexClub MT5) | Binance |
|---|---|---|
| **Bozorlar** | Forex + Crypto + Stocks + Gold (hammasi bir hisobda) | Faqat Crypto |
| **Regulyatsiya** | CySEC (EU litsenziya) | Yo'q |
| **Hisob** | Bir hisob — barcha instrumentlar | Faqat USDT Futures |
| **MT5** | Ha, professional terminal | Yo'q |
| **Komissiya** | Spread (0.0 dan) | 0.02-0.04% |
| **TORTINMANG.UZ uchun** | ✅ ASOSIY REJIM | Ixtiyoriy fallback |

---

## ⚠️ Muhim

> - Libertex da ham **$10 dan boshlash mumkin**, demo da sinab ko'ring
> - MT5_SERVER nomini **100% aniq** ko'chiring — eng ko'p xato shu yerda
> - Avval **Demo** hisobda sinab ko'ring: `ForexClub-MT5 Demo Server`
> - Bot avtomatik risk boshqaradi — qo'lda aralashmang
> - Yakshanba Forex yopiq — bot ham kutadi
