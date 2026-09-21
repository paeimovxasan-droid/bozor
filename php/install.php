<?php
/**
 * TORTINMANG.UZ PHP Lite — WEB O'RNATUVCHI (bir marta ishlatiladi!)
 * Ochish: https://saytingiz.uz/tortinmang/install.php
 * To'ldiring → Saqlash → config.php yoziladi → install.php ni O'CHIRING!
 */
$dir = __DIR__;
$msg = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $cfg = [
        'META_API_TOKEN'  => trim($_POST['token'] ?? ''),
        'META_ACCOUNT_ID' => trim($_POST['account'] ?? ''),
        'DEEPSEEK_API_KEY'=> trim($_POST['deepseek'] ?? ''),
        'TELEGRAM_BOT_TOKEN' => trim($_POST['tgtoken'] ?? ''),
        'TELEGRAM_CHAT_ID'   => trim($_POST['tgchat'] ?? ''),
        'DB_HOST' => trim($_POST['dbhost'] ?? ''),
        'DB_NAME' => trim($_POST['dbname'] ?? ''),
        'DB_USER' => trim($_POST['dbuser'] ?? ''),
        'DB_PASS' => trim($_POST['dbpass'] ?? ''),
        'ADMIN_PASS' => trim($_POST['adminpass'] ?? '') ?: 'admin123',
    ];
    if ($cfg['META_API_TOKEN'] === '' || $cfg['META_ACCOUNT_ID'] === '') {
        $msg = 'MetaApi token va account ID majburiy!';
    } else {
        $extra = <<<'PHP'

    // ── Savdo parametrlari ─────────────────────────────────────
    'SYMBOLS'   => ['XAUUSD', 'ETHUSD'],
    'RISK_PCT'  => ['XAUUSD' => 1.8, 'ETHUSD' => 1.0],
    'LOT_MIN'   => 0.01,
    'LOT_MAX'   => 0.03,
    'MAX_ACTUAL_RISK_PCT' => 3.0,
    'CONTRACT'  => ['XAUUSD' => 100, 'ETHUSD' => 1],
    'DAILY_LOSS_PCT'   => 3.0,
    'WEEKLY_LOSS_PCT'  => 7.0,
    'DAILY_TARGET_USD' => 5.0,
    'MAX_POSITIONS'    => 2,
    'MAX_TRADES_DAY'   => 6,
    'MIN_CONFIDENCE'   => 55,
    'SESSION_FROM' => 14,
    'SESSION_TO'   => 24,
    'TIMEZONE' => 'Asia/Tashkent',
PHP;
        $php = "<?php\nreturn [\n";
        foreach ($cfg as $k => $v) {
            $php .= "    '$k' => '" . addslashes($v) . "',\n";
        }
        $php .= $extra . "\n];\n";
        file_put_contents($dir . '/config.php', $php);
        // MySQL bor bo'lsa — jadvallarni avtomatik yaratish
        if ($cfg['DB_HOST'] !== '' && $cfg['DB_NAME'] !== '') {
            require_once $dir . '/db.php';
            $newcfg = require $dir . '/config.php';
            $pdo = db_conn($newcfg);
            if ($pdo) {
                try { db_schema($pdo); $msg = 'OK_DB'; }
                catch (Exception $e) { $msg = 'OK'; }
            } else {
                $msg = 'OK_DBERR';
            }
        } else {
            $msg = 'OK';
        }
    }
}
?>
<!doctype html>
<html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORTINMANG.UZ — O'rnatish</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px;max-width:560px;margin:auto}
h1{color:#58a6ff}input{width:100%;padding:10px;margin:6px 0 14px;border-radius:8px;border:1px solid #30363d;background:#161b22;color:#e6edf3}
button{background:#238636;color:#fff;padding:12px 24px;border:0;border-radius:8px;font-size:16px}
.ok{background:#0f2e1a;border:1px solid #238636;padding:14px;border-radius:8px}
.err{background:#2e0f0f;border:1px solid #da3633;padding:14px;border-radius:8px}
label{color:#8b949e;font-size:13px}
</style></head><body>
<h1>🤖 TORTINMANG.UZ — O'rnatish</h1>
<?php if ($msg === 'OK' || $msg === 'OK_DB'): ?>
<div class="ok">✅ <b>config.php saqlandi!</b>
<?= $msg === 'OK_DB' ? ' MySQL jadvallari yaratildi 🗄️' : '' ?><br>
Endi: 1) <a href="check.php">check.php</a> bilan ulanishni tekshiring,
2) cron qo'shing, 3) <b>install.php faylni o'chiring</b> (xavfsizlik)!</div>
<?php elseif ($msg === 'OK_DBERR'): ?>
<div class="err">⚠️ config saqlandi, lekin <b>MySQL ga ulanib bo'lmadi</b> —
ma'lumotlar faylda saqlanadi. DB ma'lumotlarini ISPmanager da tekshiring.</div>
<?php elseif ($msg): ?>
<div class="err">❌ <?= htmlspecialchars($msg) ?></div>
<?php endif; ?>
<form method="post">
<label>MetaApi TOKEN (app.metaapi.cloud/token)</label>
<input name="token" placeholder="eyJhbGciOi...">
<label>MetaApi ACCOUNT ID (uuid)</label>
<input name="account" placeholder="865d3a4d-...">
<label>DeepSeek API KEY (ixtiyoriy, sk-...)</label>
<input name="deepseek" placeholder="sk-...">
<label>Telegram BOT TOKEN (ixtiyoriy)</label>
<input name="tgtoken" placeholder="123456:AAH...">
<label>Telegram CHAT ID (ixtiyoriy)</label>
<input name="tgchat" placeholder="8870183299">
<label>🔐 ADMIN PANEL PAROLI (admin.php uchun)</label>
<input name="adminpass" type="password" placeholder="admin123 (o'zgartiring!)">
<h1 style="font-size:16px">🗄️ MySQL (ISPmanager — tavsiya etiladi)</h1>
<label>DB HOST (ISPmanager → Ma'lumot bazalari)</label>
<input name="dbhost" placeholder="localhost">
<label>DB NAME</label>
<input name="dbname" placeholder="username_tm">
<label>DB USER</label>
<input name="dbuser" placeholder="username_tmuser">
<label>DB PASSWORD</label>
<input name="dbpass" type="password" placeholder="parol">
<button type="submit">💾 Saqlash</button>
</form>
</body></html>
