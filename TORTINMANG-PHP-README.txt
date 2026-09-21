==========================================================
  TORTINMANG.UZ PHP Lite — TEZKOR BOSHQICH
  (ISPmanager shared hosting, PHP 8.4 + MySQL uchun)
==========================================================

1) ZIP ni oching -> papka ichini hosting www/tortinmang/ ga yuklang.

2) MetaApi: https://app.metaapi.cloud
   - Libertex MT5 hisobni qo'shing -> Token + Account ID oling

3) ISPmanager:
   - PHP versiya: 8.4
   - Ma'lumot bazalari: yangi DB yarating (name/user/pass)

4) Brauzerda: /tortinmang/install.php
   - Formani to'ldiring (MetaApi + DB ma'lumotlari ham)
   - Saqlash -> "MySQL jadvallari yaratildi"
   - check.php: hammasi YASHIL
   - install.php ni O'CHIRING!

5) ISPmanager -> Cron:
   * * * * * /usr/bin/php /home/USER/www/domen/tortinmang/cycle.php >> /dev/null 2>&1

6) status.php — jonli panel; Telegram: /status /stats /history /closeall

DB bo'lmasa ham ishlaydi (json fayl rejimi).
Birinchi hafta DEMO Libertex hisobda sinang!
To'liq qo'llanma: php/README_PHP.md
