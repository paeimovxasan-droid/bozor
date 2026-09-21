<?php
/**
 * TORTINMANG.UZ PHP Lite — BOSH SAHIFA (o'rnatish bosqichlari bilan)
 */
$dir = __DIR__;
$hasCfg = is_file($dir . '/config.php');
$step = [
    1 => $hasCfg,                    // config o'rnatilgan
    2 => false,                      // Libertex hisob ulangan
    3 => false,                      // avto savdo yoqiq
    4 => false,                      // cron ishlayapti
];
if ($hasCfg) {
    require_once $dir . '/lib.php';
    $cfg = require $dir . '/config.php';
    $state = state_load($dir . '/state.json', $cfg);
    $accId = $state['meta_account_id'] ?? ($cfg['META_ACCOUNT_ID'] ?? '');
    $step[2] = $accId !== '';
    $step[3] = ($state['auto'] ?? true) && $step[2];
    $last = $state['last_cycle'] ?? 0;
    $step[4] = $last > 0 && (time() - $last) < 180;
}
$done = count(array_filter($step));
function chk($ok) { return $ok ? '✅' : '⬜'; }
?>
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="30">
<title>TORTINMANG.UZ</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:24px;max-width:560px;margin:auto}
h1{color:#58a6ff}h2{font-size:14px;color:#8b949e;margin:20px 0 8px}
a.card{display:block;background:#161b22;border:1px solid #30363d;border-radius:12px;
padding:14px;margin:10px 0;color:#e6edf3;text-decoration:none}
a.card:hover{border-color:#58a6ff}
small{color:#8b949e}
.steps{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px;margin:12px 0;font-size:14px;line-height:2}
.bar{height:8px;background:#21262d;border-radius:4px;margin:8px 0}
.fill{height:8px;background:#238636;border-radius:4px}
.live{background:#0f2e1a;border:1px solid #238636;border-radius:12px;padding:14px;margin:12px 0}
</style></head><body>
<h1>🤖 TORTINMANG.UZ <small>PHP Lite</small></h1>

<?php if ($done === 4): ?>
<div class="live">🟢 <b>BOT TO'LIQ ISHLAMOQDA!</b><br>
<small>Kompyuter kerak emas — hammasi hostingda yuryapti.
<a href="status.php">Status</a> | <a href="admin.php">Admin</a></small></div>
<?php else: ?>
<div class="steps">
<b>🚀 Ishga tushirish: <?= $done ?>/4 bosqich</b>
<div class="bar"><div class="fill" style="width:<?= $done * 25 ?>%"></div></div>
<?= chk($step[1]) ?> 1. <a href="install.php" style="color:#58a6ff">install.php</a> — formani to'ldiring<br>
<?= chk($step[2]) ?> 2. <a href="admin.php" style="color:#58a6ff">admin.php</a> — Libertex hisobni ulang<br>
<?= chk($step[3]) ?> 3. <a href="admin.php" style="color:#58a6ff">admin.php</a> — avto savdoni yoqing<br>
<?= chk($step[4]) ?> 4. Cron qo'shing (install.php ko'rsatadi) — 3 daqiqada yonadi
</div>
<?php endif; ?>

<h2>PANELLAR</h2>
<?php if (!$hasCfg): ?>
<a class="card" href="install.php">🛠️ <b>O'rnatish</b> — <small>birinchi shu yerdan boshlang</small></a>
<?php endif; ?>
<a class="card" href="admin.php">🛠️ <b>Admin panel</b><br>
<small>Libertex hisob ulash, avto savdo, pozitsiyalar, sozlamalar</small></a>
<a class="card" href="status.php">📊 <b>Jonli status paneli</b><br>
<small>balans, P&L, pog'ona, statistika</small></a>
<a class="card" href="check.php">🧪 <b>Ulanish tekshiruvi</b><br>
<small>MetaApi / DeepSeek / Telegram holati</small></a>
<a class="card" href="test.php">🔬 <b>Dvigatel self-test</b><br>
<small>indikatorlar, risk, pog'ona, jurnal — ichki mantiq tekshiruvi</small></a>
<p><small>Qo'llanma: README_PHP.md | Cron: crontab.txt</small></p>
</body></html>
