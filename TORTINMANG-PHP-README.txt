==========================================================
  TORTINMANG.UZ PHP Lite — TEZKOR BOSHQICH (5 daqiqa)
==========================================================

1) ZIP ni oching, php/ ichidagini hosting public_html/tortinmang/ ga yuklang.

2) MetaApi: https://app.metaapi.cloud
   - Ro'yxatdan o'ting
   - Accounts -> Add account: ForexClub/Libertex MT5 login/parol/server
   - Token va Account ID ni oling

3) Brauzerda: https://saytingiz.uz/tortinmang/install.php
   - Formani to'ldiring -> Saqlash
   - check.php oching: hammasi YASHIL bo'lsin
   - install.php faylni O'CHIRING (xavfsizlik!)

4) cPanel -> Cron Jobs:
   * * * * * /usr/bin/php /home/USER/public_html/tortinmang/cycle.php >> /dev/null 2>&1

5) status.php — jonli panel; Telegram: /status /positions /closeall /pause /resume

Birinchi hafta DEMO Libertex hisobda sinang!
To'liq qo'llanma: php/README_PHP.md
