<?php
/**
 * TORTINMANG.UZ PHP Lite — BOSH SAHIFA
 */
$hasCfg = is_file(__DIR__ . '/config.php');
?>
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORTINMANG.UZ</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:24px;max-width:560px;margin:auto}
h1{color:#58a6ff}
a.card{display:block;background:#161b22;border:1px solid #30363d;border-radius:12px;
padding:16px;margin:12px 0;color:#e6edf3;text-decoration:none}
a.card:hover{border-color:#58a6ff}
small{color:#8b949e}
</style></head><body>
<h1>🤖 TORTINMANG.UZ <small>PHP Lite</small></h1>
<?php if (!$hasCfg): ?>
<a class="card" href="install.php">🛠️ <b>O'rnatish</b><br>
<small>config.php hali yo'q — birinchi shu yerdan boshlang</small></a>
<?php endif; ?>
<a class="card" href="check.php">🧪 <b>Ulanish tekshiruvi</b><br>
<small>MetaApi / DeepSeek / Telegram holati</small></a>
<a class="card" href="status.php">📊 <b>Jonli status paneli</b><br>
<small>balans, P&L, pog'ona, statistika</small></a>
<a class="card" href="admin.php">🛠️ <b>Admin panel</b><br>
<small>Libertex hisob ulash, avto savdo, pozitsiyalar, sozlamalar</small></a>
<p><small>Qo'llanma: README_PHP.md | Cron: crontab.txt</small></p>
</body></html>
