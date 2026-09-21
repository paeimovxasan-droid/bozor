==========================================================
  TORTINMANG.UZ PHP Lite — TEZKOR BOSHQICH
  (ISPmanager shared hosting, PHP 8.4 + MySQL uchun)

  ✅ 100% HOSTING REJIMI — KOMPYUTER UMUMAN KERAK EMAS!
  Bot hostingda 24/7 ishlaydi; siz faqat telefonda
  admin.php va Telegram orqali boshqarasiz.
==========================================================

1) ZIP ni oching -> papka ichini hosting www/tortinmang/ ga yuklang.

2) MetaApi: https://app.metaapi.cloud
   - Ro'yxatdan o'ting -> API TOKEN oling (hisob admin panelda avtomatik ulanadi)

3) ISPmanager:
   - PHP versiya: 8.4
   - Ma'lumot bazalari: yangi DB yarating (name/user/pass)

4) Brauzerda: /tortinmang/install.php
   - Formani to'ldiring (MetaApi + DB + admin parol)
   - Saqlash -> "MySQL jadvallari yaratildi" + CRON URL (nusxalang!)
   - check.php: ulanishlar YASHIL
   - test.php: dvigatel logikasi YASHIL
   - install.php ni O'CHIRING!

5) /tortinmang/admin.php — ADMIN PANEL:
   - Libertex MT5 login/parol/server kiritang -> hisob AVTO ulanadi
   - "Avto savdo" tugmasini yoqing -> bot o'zi savdo ochib yopadi
   - Pozitsiyalar, risk sozlamalari, statistika — hammasi shu yerda

6) Cron (3 usuldan biri — crontab.txt da batafsil):
   A) CLI (eng ishonchli):
      * * * * * /usr/bin/php /home/USER/www/domen/tortinmang/cycle.php >> /dev/null 2>&1
   B) HTTP (CLI yo'q bo'lsa): install.php ko'rsatgan CRON URL:
      * * * * * wget -q -O /dev/null "https://domen/tortinmang/cycle.php?key=KEY"
   C) Tashqi servis: cron-job.org da shu URL ni 60 sekka qo'ying

7) status.php — jonli panel; Telegram: /status /stats /history /closeall

DB bo'lmasa ham ishlaydi (json fayl rejimi).
Birinchi hafta DEMO Libertex hisobda sinang!
To'liq qo'llanma: php/README_PHP.md
