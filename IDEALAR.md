# 🏗️ TORTINMANG.UZ v2.0 — QAYTA TAYYORLASH MASTER-REJASI (136 g'oya)

> Maqsad: **$10–$100 balans, 0.01–0.03 lot, tahlil asosida BUY/SELL, +$1…+$5 foyda bilan yopish,
> har savdoda risk ≤1.02%, to'liq mustaqil ishlash.**
>
> ⚠️ Halol ogohlantirish: hech bir robot 100% foyda kafolatlamaydi. Bizning vazifa —
> ehtimollikni biz tomonga og'dirish va zararni matematik jihatdan cheklash.

---

## 📐 0. HALOL MATEMATIKA (kelishib olish uchun)

| Fakt | Hisob | Xulosa |
|------|-------|--------|
| $10 balansda 1.02% risk | = **$0.10** savdo riski | Juda kichik |
| XAUUSD 0.01 lot | $0.10 risk = narxda $0.10 harakat | Spreadning o'zi ko'pincha $0.20–0.50 → **oltinda 1% risk mumkin emas** |
| ETHUSD 0.01 lot | $0.10 risk = ETH narxida $10 harakat | ✅ Real (odatda SL $5–15) |
| +$1 foyda XAUUSD 0.01 | narxda $1 harakat | Real (gold kuniga $20–40 yuradi) |
| +$5 kunlik maqsad $10 balansda | = 50%/kun | Agar har kuni takrorlansa — murakkab, lekin zinapoya bilan erishiladi |

## 🏦 0A. KAPITAL POG'ONALARI MATRITSA (barcha balanslar uchun)

> Professional qoida: **balans qancha katta bo'lsa, risk foizi shuncha KICHIK** —
> kichik hisob o'sish uchun, katta hisob HIMOYA uchun ishlaydi.

### Pog'ona 1: BRONZE — $10–$100 (o'sish rejimi)
| Parametr | Qiymat |
|----------|--------|
| Lot | 0.01–0.03 (hard-cap 0.03) |
| Risk/savdo | ETHUSD 1%, XAUUSD 1.5–2% |
| Kunlik zarar limiti | 3% |
| Ochiq pozitsiya | max 2 (symbolga 1 + dogon) |
| Uslub | Scalp + intraday, faqat London/NY sessiya |
| Simbollar | ETHUSD asosiy, XAUUSD faqat A+ setup |
| Kunlik maqsad | +$1…+$5 (yig'ilsa — kun yopiladi) |
| Dogon | Ruxsat (max 1, x2 emas, 1x lot) |
| Maqsad | $100 ga yetish → SILVER ga o'tish |

### Pog'ona 2: SILVER — $100–$500 (barqaror o'sish)
| Parametr | Qiymat |
|----------|--------|
| Lot | 0.03–0.10 |
| Risk/savdo | 1–1.5% |
| Kunlik zarar limiti | 2.5% |
| Ochiq pozitsiya | max 3 |
| Uslub | Intraday + qisqa swing (4–8 soat) |
| Simbollar | XAUUSD + ETHUSD teng vazn |
| Partial TP | Majburiy (1R da 50% + BE) |
| Yangilik filtri | Qattiq (qizil yangilik ±30 daqiqa) |
| Maqsad | Oyiga +30–60%, $500 ga yetish |

### Pog'ona 3: GOLD — $500–$2000 (professional rejim)
| Parametr | Qiymat |
|----------|--------|
| Lot | 0.05–0.30 |
| Risk/savdo | 0.75–1% |
| Kunlik zarar limiti | 2% |
| Haftalik zarar limiti | 5% |
| Ochiq pozitsiya | max 4 (korrelyatsiya nazorati bilan) |
| Uslub | Swing asosiy (H1–H4), scalp qo'shimcha |
| Yangi | Majburiy VPS/uzluksiz server, slippage nazorati |
| Diversifikatsiya | Trend strategiya 60% + Range 25% + Dogon byudjeti 15% |
| Maqsad | Oyiga +15–25%, barqarorlik birinchi o'rinda |

### Pog'ona 4: PLATINUM — $2000–$5000 (kapitalni asrash + o'sish)
| Parametr | Qiymat |
|----------|--------|
| Lot | 0.10–0.50 |
| Risk/savdo | 0.5–0.75% |
| Kunlik zarar limiti | 1.5% |
| Haftalik zarar limiti | 4% |
| Umumiy drawdown stop | 12% |
| Ochiq pozitsiya | max 5, symbolga max 2 |
| Uslub | 70% swing (H4–D1), 30% intraday |
| Yangi | Equity hedge logikasi (qarama-qarshi pozitsiyalar bilan himoya) |
| Maqsad | Oyiga +10–15%, kapital himoyasi ustuvor |

### Pog'ona 5: DIAMOND — $5000+ (institut darajasi)
| Parametr | Qiymat |
|----------|--------|
| Lot | 0.20–1.0+ (balans formulasi bilan) |
| Risk/savdo | 0.3–0.5% |
| Kunlik zarar limiti | 1% |
| Haftalik zarar limiti | 3% |
| Ochiq pozitsiya | max 6–8, risk-parity taqsimoti |
| Uslub | Portfel yondashuvi: bir nechta timeframe va setup parallel |
| Yangi | "Risk desk" — AI risk-ofitser VETO huquqi har savdoda |
| Broker | ECN/RAW spread hisob, alohida server |
| Maqsad | Oyiga +5–12%, barqaror compound, hech qachon "hamma pulni tikish" yo'q |

### 🔄 Pog'onalar arasi avtomatika
- **Auto-promotion**: balans 5 kun ketma-ket yangi pog'ona chegarasidan yuqori → yangi qoidalar yoqiladi
- **Auto-demotion**: balans orqaga tushsa → darhol eski qoidalar (hech qanday "qaytarib olaman" ruhsati yo'q)
- **Profit lock**: har pog'onada boshlang'ich kapital himoyalangan zona (masalan $1500 da: drawdown $1250 dan pastga tushsa bot to'xtaydi)
- **Pog'ona pasporti**: Telegram da doim ko'rinadi: "🥈 SILVER | $247 | keyingi: GOLD ($500) — 21 kun tempo"

---

## A. SAVDO YURAGI — signal generatsiyasi (1–15)

1. **Multi-timeframe kelishuv o'lchagi**: M5 kirish, M15 trend, H1 yo'nalish — 3/3 kelishuvidagina savdo.
2. **Trend filtri qat'iy**: EMA50/200 + ADX 25+ bo'lmasa umuman savdo yo'q.
3. **Market Structure Break (BOS/CHoCH) detektori** — SMC asosida, aniq buzilish nuqtasida kirish.
4. **Fair Value Gap (FVG) scanner** — bo'shliqqa qaytishni kutib kirish (sniper entry).
5. **Order Block zonalar** — institucional kirish hududlarini belgilash.
6. **Liquidity Sweep + Rejection** — stop-ovdan keyin qaytish (eng kuchli setup).
7. **RSI divergence scanner** — narx yangi cho'qqi, RSI yo'q = reversal belgisi.
8. **CVD (kumulyativ hajm delta) divergence** — buy hajm bor narx tushmoqda = tuzoq.
9. **Session filtri**: London (15:00–19:00 TST) va NY (17:00–22:00 TST) — gold/ETH eng likvid vaqtlar.
10. **Osiyo sessiyasi taqiqlash** — gold tunda spreadsiz yuradi, faqat range-break.
11. **Volatillik darvoza**: ATR juda past yoki juda yuqori bo'lsa savdo yo'q (chop/xaos himoyasi).
12. **Signal konflyuence ball** — 5+ indikator tasdig'i bitta ball tizimiga yig'iladi, 80+ bo'lsagina savdo.
13. **Anti-korrelation guard** — XAUUSD BUY va ETHUSD SELL bir vaqtda bo'lmasligi (ikkalasi ham USD qarshi).
14. **Yangilik blackout**: ForexFactory kalendar API → qizil yangilikdan ±15 daqiqa oldin/ keyin savdo taqiqlanadi.
15. **Whale activity gate** — katta hajm anomaly bo'lmasa kirish kechiktiriladi.

## B. SNIPER KIRISH (16–25)

16. **Retest kutish** — daraja buzilganda darhol emas, qayta testini kutish (false-break filtri).
17. **Signal umri (TTL)** — signal chiqqandan 3 daqiqa ichida kirilmasa bekor.
18. **Sham tasdig'i** — signal shamining yopilishini kutish, ichida kirish yo'q.
19. **Limit order rejimi** — market emas, FVG/order-block chekkasida pending order.
20. **Pending order expiry** — 15 daqiqada ishga tushmasa avtomatik o'chirish.
21. **Spread sniffer** — sekundiga 1 marta spread o'lchami, o'rtachadan 1.5x keng bo'lsa kutish.
22. **Slippage himoya** — buyrug' bajarilish narxi kutilgandan 30%+ yomon bo'lsa pozitsiyani darhol yopish.
23. **Entry drift guard** — signal chiqqan narxdan 0.3%+ uzoqlashsa savdo bekor.
24. **Eng yaxshi soat xaritasi** — o'z tarixidan o'rganib, qaysi soatlarda WR yuqori bo'lsa shunda savdo.
25. **One-shot per setup** — bitta setupdan faqat 1 savdo, qayta urinish yangi setupni kutadi.

## C. RISK BOSHQARUVI (26–40)

26. **Fixed-fractional sizing**: lot = balans × risk% ÷ (SL masofasi × pip qiymati) — 1.02% aniq kafolat.
27. **Risk zinapoya**: balans o'sgani sari risk% ham o'sadi (yuqoridagi ladder).
28. **Maksimal lot hard-cap** — 0.03 dan oshmaydi (env bilan sozlanadi).
29. **Kunlik zarar limiti 3%** → kun to'xtaydi, Telegram ogohlantirish.
30. **Haftalik zarar limiti 7%** → bot 24 soat paper rejimga tushadi.
31. **Umumiy drawdown 15%** → bot to'liq to'xtaydi, faqat /start bilan qayta.
32. **Anti-tilt**: 2 ketma-ket zarar → lot 50% kamayadi; 3 zarar → 2 soat pauza.
33. **Kunlik savdo limiti** (masalan 6 ta) — overtrading yo'q.
34. **Ochiq pozitsiya limiti** — max 2 bir vaqtda, bitta symbolga max 1 (+dogon).
35. **Equity Guardian** — equity peak dan 5% tushsa barcha yangi savdolar to'xtaydi.
36. **SL must-exist check** — har 30 sekundda barcha pozitsiyada SL borligi tekshiriladi, yo'q bo'lsa darhol qo'yiladi.
37. **Broker margin tekshiruvi** — free margin yetarli bo'lmasa savdo yo'q.
38. **Juma himoyasi** — juma 20:00 dan keyin yangi savdo yo'q, ochiqlari ixtiyoriy yopish.
39. **Swap filtri** — tun bo'yi ushlash swap-manfiy bo'lsa, kunning oxirida yopishga moyillik.
40. **Risk audit log** — har savdoning risk hisobi jurnalga yoziladi (keyin audit mumkin).

## D. SAVDONI BOSHQARISH — chiqish (41–52)

41. **ATR-based TP/SL** — fixed emas, bozor volatilligiga moslashuvchan.
42. **Partial TP ladder**: 1R da 50% yopish + BE; qolgani 2R yoki trail bilan.
43. **Break-even avto**: +1R → SL kirishga.
44. **Trailing stop (ATR masofa)** — trend davomida foydani sudrab borish.
45. **Time-stop** — 90 daqiqada foyda/zarar bo'lmasa pozitsiya yopiladi (o'lik pul yo'q).
46. **Opposing signal exit** — kuchli teskari signal kelsa savdo darhol yopiladi.
47. **Kunlik maqsad qulfi**: +$5 (sozlanadi) yig'ilsa — bugun savdo tamom.
48. **News-exit** — savdo ochiq payt qizil yangilik chiqsa, pozitsiya BE ga o'tkaziladi.
49. **Weekend auto-close** — juma oqshom barcha pozitsiyalar yopiladi (gap himoyasi).
50. **Partial profit protect** — olingan foyda qaytmasligi uchun trailing faqat foyda tomon.
51. **Exit sifati metrikasi** — har yopilgan savdo "erta/kech/aniq" deb baholanadi, AI o'rganadi.
52. **Emergency flat** — Telegram /stop bitta buyruq bilan hammasini yopadi.

## E. KAPITAL ZINAPOYASI — $10→$100 (53–60)

53. **Bosqichlar tizimi**: BRONZE ($10–25) → SILVER ($25–50) → GOLD ($50–100), har bosqichda lot/risk qoidalari.
54. **Auto-promotion** — balans bosqich chegarasini 3 kun ushlab tursa yangi bosqich qoidalari yoqiladi.
55. **Auto-demotion** — balans orqaga tushsa darhol past bosqich qaytadi.
56. **Compound lot** — balans oshgani sari lot avtomatik o'sadi (lekin hard-cap 0.03).
57. **Foyda himoya zonasi**: $100 ga yetganda boshlang'ich $10 "himoyalangan" — drawdown $85 dan pastga tushsa stop.
58. **Daily goal tracker** — Telegram da progress: "Bugungi maqsad +$5: $3.2 ✅ 64%".
59. **Streak bonus** — 5 g'alabali savdo ketin risk 0.2% bonus (ehtiyot).
60. **Haftalik compound hisobot** — "bu hafta $12 → $17 (+41%), tempo: SILVER ga 4 kun".

## F. AI / DeepSeek INTEGRATSIYASI (61–72)

61. **AI Kengash (Council)**: 3 persona — Trendchi, Skalpchi, Risk-ofitser — ovoz berishadi; 2/3 bo'lsagina savdo.
62. **Risk-ofitser veto** — DeepSeek har savdoga "NO" deyish huquqiga ega.
63. **AI signal sharhi har savdoda** — Telegram ga nega aynan shu savdo (1 qator).
64. **Kunlik AI hisobot** — statistikani DeepSeek tahlil qiladi (bor, kuchaytiriladi).
65. **Yo'qotilgan savdo tahlili** — har zarar savdoni AI tahlil qilib "sabab darsini" yozadi.
66. **AI darslar bazasi** — yig'ilgan darslar keyingi signallarga filtr bo'ladi ("oldingi xato takrorlanmasin").
67. **Haftalik AI strategiya ko'rib chiqishi** — sozlamalarni o'zgartirish takliflari (faqat taklif, siz tasdiqlaysiz).
68. **Prompt cache/tejamkorlik** — takroriy kontekst bitta chaqiruvda, token xarajati minimal.
69. **DeepSeek JSON mode** — barcha javoblar strukturali JSON, ishonchli parse.
70. **Model fallback** — deepseek-flash asosiy, xatoda retry → fallback javob.
71. **Token byudjet** — kunlik token limiti, oshsa AI "uxlaydi".
72. **AI ishonch kalibrlash** — AI aytgan ishonch vs real natija jadvali, oyiga bir hisobot.

## G. MA'LUMOT VA ANALITIKA (73–82)

73. **Tick-level ma'lumot yig'ish** — har signal vaqtidagi bid/ask/spread arxivda saqlanadi.
74. **Orderbook imbalance** (Binance ETH) — ETHUSD uchun real oqim signali.
75. **Funding rate filtri** (Binance futures) — ekstremal funding = kontrarian belgi.
76. **DXY korrelyatsiya kuzatuvchi** — dollar indeksi kuchaysa gold savdolar ehtiyotkor.
77. **Gold/ETH nisbati (ratio) monitor** — ikki aktiv o'rtasidagi munosabat trendi.
78. **Volatility regime classifier** — "trend/chop/xaos" rejimlari avtomatik aniqlanadi, chop da savdo yo'q.
79. **Session xususiyat profili** — har sessiya uchun WR, o'rtacha harakat, spread statistikasi.
80. **Symbol salomatlik paneli** — har symbol uchun oxirgi 7 kun WR/PF, yomon symbol avtomatik fokusdan chiqadi.
81. **Ma'lumot sifat nazorati** — keline olmasa/nuqta bo'lsa savdo sikli o'tkaziladi, logga yoziladi.
82. **Broker server vaqti sinxronlash** — sessiya chegaralari broker vaqtiga aniq moslanadi.

## H. O'Z-O'ZINI O'RGATISH (83–92)

83. **Signal DNA** — har signal indikatorlar vektori sifatida saqlanadi.
84. **Pattern Memory (kNN)** — o'tgan G'ALABA savdolarga o'xshash hozirgi holat topilsa ishonch oshadi.
85. **Cluster winners** — g'olib signallar klasterlari aniqlanadi, shu klasterlarda threshold pasayadi.
86. **Auto-backtest har yakshanba** — bot o'zi backtest qilib natijani Telegram ga yuboradi.
87. **Self-tuning thresholds** — backtest natijasiga qarab MIN_CONFIDENCE avtomatik ±5 sozlanadi.
88. **Drift detection** — WR 10 savdada 10%+ tushsa bot avtomatik paper rejimga.
89. **Paper→Real darvoza** — paper da 20 savdo PF≥1.3 bo'lsagina real savdo davom etadi.
90. **A/B strategiya arenasi** — 2 xil config paper da poygalashadi, g'olibi realga o'tadi.
91. **Exit review AI** — yopilish sifatini har hafta baholab TP/SL koeffitsiyentlari taklif qiladi.
92. **Soat xaritasi o'rganish** — o'z savdolaridan eng foydali soatlarni o'zi topadi (24 bilan o'zgaradi).

## I. TELEGRAM VA BOSHQARUV (93–104)

93. **Buyruqlar to'plami**: /status /positions /pause /resume /risk /lot /focus /dogon /report /backtest /stop /help
94. **Jonli status** — /status: balans, equity, ochiq savdolar, bugungi P&L, AI kayfiyati.
95. **Har savdo kartasi** — entry/SL/TP/R:R/isbot/emoji bilan chiroyli karta.
96. **Yopilish kartasi** — foyda/zarar, sabab, davomiyligi, streak holati.
97. **Kunlik hisobot 23:59** — avtomatik (AI matni bilan).
98. **Equity curve rasm** — matplotlib bilan PNG grafik, Telegram ga rasm.
99. **Ogohlantirish darajalari** — 🔴 kritik / 🟡 diqqat / 🟢 info, spam filtri.
100. **Admin himoya** — faqat sizning chat_id buyruq beradi.
101. **Inline tugmalar** — "Yopish ❌ / BE ga o'tkaz 🔒 / Davom ✅" tugmalari savdo kartasida.
102. **Screenshot-jurnal** — har savdo grafigi PNG saqlanadi, /journal bilan ko'rish.
103. **Heartbeat** — har soat qisqa "men tirik" xabar (o'chiriladigan).
104. **Ovozli ogohlantirish (variant)** — kritik hodisada qisqa ovozli xabar.

## J. ISHONCHLILIK VA INFRASTRUKTURA (105–114)

105. **Watchdog 2.0** — process o'lsa auto-restart + Telegram xabar (ps1/systemd).
106. **MT5 auto-reconnect** — terminal uzilsa 30 sekundda qayta urinish, 5 marta.
107. **State crash-safety** — har o'zgarishda atomar yozish (fayl buzilmasligi).
108. **Config hot-reload** — .env ni o'zgartirsangiz /reload bilan qayta ishga tushmasdan qo'llanadi.
109. **Sessiya logi** — har ishga tushish alohida log fayl, /logs buyrug'i bilan oxirgisi.
110. **Health endpoint** — API da /health: MT5/AI/Telegram holati bir qarashda.
111. **Disk tozalash** — loglar 30 kundan keyin avtomatik arxiv/tozalanadi.
112. **Backup** — tortinmang_state.json har kuni GitHub gist yoki zip backup (siz tasdiqlasangiz).
113. **Windows rejalashtiruvchi** — kompyuter yoqilganda bot avtomatik ishga tushadi.
114. **Sinov rejimi** — --selftest: barcha modullarni 10 sekundda tekshirib natija beradi.

## K. TAKRORLANMAS — "HECH KIMDA YO'Q" G'OYALAR (115–126)

115. **"Bozor Nafasi" indeksi** — volatillik+oqim+yangilik bitta 0–100 indikator, har daqiqa Telegram statusda.
116. **Whale Trap Detection** — stop-hunt shamini aniqlab, tuzoqdan keyin teskariga kirish.
117. **Liquidity Magnet xaritasi** — orderbook asosida narx qayerga "tortilishi" ehtimoli.
118. **AI O'qituvchi kechki dars** — har oqshom DeepSeek kunning barcha savdolarini "o'qituvchi" sifatida baholaydi, ertalabki filtrga aylanadi.
119. **Signal DNA klaster tizimi** (83–85 ning to'liq avtomatlashtirilgan versiyasi) — o'z-o'zidan qaysi turdagi signallar pul topishini topadi.
120. **Rejim moslashuvchan savdo** — trend/chop/xaos aniqlanib, har rejimga alohida mini-strategiya yoqiladi.
121. **Zinapoya psixologiya muhofizi** — foyda seriyasida bot O'ZI ehtiyotkorlashadi (odam aksincha qiladi).
122. **Soat mexanizmi (Clockwork)** — faqat o'zi o'rgangan "oltin soatlar"da savdo, qolganida kuzatuvchi.
123. **Ikki qurol tizimi** — XAUUSD trendda, ETHUSD range-da ishlaydi; qaysi bozor qaysi rejimda bo'lsa shu qurol.
124. **Equity yurak urishi** — Telegram profil rasmi kabi equity chizig'i jonli ASCII.
125. **Halollik paneli** — bot har hafta "bu hafta omad omilligi: X%, mahorat: Y%" deb o'z omadini baholaydi.
126. **O'lim tugmasi + meros** — /wipe barcha ma'lumotni o'chiradi; /export barcha jurnalni zip qiladi.

## L. POG'ONA TIZIMI MEXANIKASI (127–136)

127. **Adaptive Profile Engine** — bot balansni o'qib, pog'ona qoidalarini AVTO almashtiradi (kodda 5 profil: BRONZE→DIAMOND).
128. **Pog'ona qoidalari config-da** — har pog'onaning lot/risk/limit jadvali bitta `tiers.yaml` faylda, o'zingiz o'zgartira olasiz.
129. **Promotion/Demotion test rejimi** — pog'ona almashishdan oldin 24 soat yangi qoidalar PAPER da sinanadi.
130. **Pog'ona pasporti Telegram da** — /status da joriy pog'ona, progress, keyinchi chegara ko'rinadi.
131. **Pog'onaga mos strategiya tanlash** — kichik balansda scalp, kattada swing ustunligi avtomatik.
132. **Risk-desk veto (katta hisoblar)** — $2000+ da har savdo oldidan AI risk-ofitser alohida tasdiq beradi.
133. **Profit lock zonalari** — har pog'ona uchun "himoyalangan kapital" chegarasi, pastga tushsa emergency stop.
134. **Pog'ona statistikasi** — har pog'onada qancha vaqt, qanday natija — alohida jurnal.
135. **Compound kalkulyator** — "hozirgi tempo bilan $X ga Y kunda yetasiz" prognozi (real ma'lumotdan).
136. **Katta hisob slippage shield** — $2000+ da lotni bozorga bir emas, 2–3 qismda yuborish (ICEBERG uslub).

---

## ⭐ TAVSIYA QILINADIGAN "SKELET" PAKET (agar hammasini tanlash qiyin bo'lsa)

**Bosqich 1 — Asos (eng muhim 25 ta):**
1, 2, 3, 6, 9, 12, 14, 17, 18, 21, 26, 28, 29, 32, 34, 36, 41, 42, 43, 47, 53, 54, 56, 88, 93

**Bosqich 2 — Aql (AI + o'rganish, 15 ta):**
61, 62, 64, 65, 66, 83, 84, 85, 86, 87, 90, 118, 119, 120, 122

**Bosqich 3 — Sayqal (10 ta):**
45, 58, 78, 80, 94, 95, 98, 106, 107, 115

**Bosqich 4 — Pog'ona tizimi (barcha balanslar uchun, 10 ta):**
127, 128, 129, 130, 131, 132, 133, 134, 135, 136

---

## ❓ KELISHIB OLISH SAVOLLARI

1. **Qaysi g'oyalar quriladi?** Javob variantlari:
   - "SKELET paket" → Bosqich 1+2+3+4 (60 ta eng muhim) — TAVSIYA
   - "HAMMASI" → 136 g'oya (eng mukammal, uzoqroq)
   - yoki raqamlarni o'zingiz yozing: "1–15, 26–40, 53–60…"
2. **Risk taqsimoti:** ETHUSD 1%, XAUUSD 2% — ma'qulmi? (matritsa bo'yicha)
3. **Kunlik maqsad:** BRONZE da +$5 lock, SILVER da +$10, GOLD da +$20 — qabulmi?
4. **Arxitektura:** shu repoda modulma-modul yangilaymizmi yoki `tortinmang-v2` toza qurilishmi?
