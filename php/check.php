<?php
/**
 * TORTINMANG.UZ PHP Lite — ULANISH TEKSHIRUVI
 * Ochish: https://saytingiz.uz/tortinmang/check.php
 * Hamma narsa yashil bo'lguncha cron qo'shmang.
 */
$dir = __DIR__;
if (!is_file($dir . '/config.php')) {
    die("config.php yo'q — avval install.php ni oching.");
}
$cfg = require $dir . '/config.php';
require_once $dir . '/lib.php';
require_once $dir . '/metaapi.php';

function row($ok, $label, $extra = '') {
    echo '<div style="padding:10px;margin:6px 0;border-radius:8px;background:' .
        ($ok ? '#0f2e1a' : '#2e0f0f') . ';">' . ($ok ? '✅' : '❌') . ' ' .
        htmlspecialchars($label) . ($extra ? ' — <small>' . htmlspecialchars($extra) . '</small>' : '') . '</div>';
}
?>
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORTINMANG.UZ — Tekshiruv</title>
<style>body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px;max-width:560px;margin:auto}h1{color:#58a6ff}</style>
</head><body>
<h1>🧪 TORTINMANG.UZ — Tekshiruv</h1>
<?php
// 1. MetaApi hisob
$acc = ma_account($cfg);
row(is_array($acc), 'MetaApi hisob', $acc ? ('balans: $' . round(floatval($acc['balance'] ?? 0), 2)) : 'token/account xato');

// 2. Shamlar
$c = ma_candles($cfg, $cfg['SYMBOLS'][0] ?? 'XAUUSD', '15m', 50);
row(is_array($c) && count($c) > 10, 'Shamlar (MetaApi market-data)', $c ? count($c) . ' ta sham' : 'aloqa yo\'q');

// 3. Pozitsiyalar
$p = ma_positions($cfg);
row(is_array($p), 'Pozitsiyalar ro\'yxati', count($p) . ' ta ochiq');

// 4. DeepSeek
if (empty($cfg['DEEPSEEK_API_KEY'])) {
    row(true, 'DeepSeek (o\'chiq — ixtiyoriy)');
} else {
    $r = deepseek_review($cfg, 'Test: 1+1=2. Tasdiqlaysanmi?');
    row($r['ok'] || !$r['wait'], 'DeepSeek AI', $r['reason'] ?: 'javob keldi');
}

// 5. Telegram
if (empty($cfg['TELEGRAM_BOT_TOKEN'])) {
    row(true, 'Telegram (o\'chiq — ixtiyoriy)');
} else {
    $ok = tg_send($cfg, '🧪 TORTINMANG.UZ PHP Lite: tekshiruv xabari ✅');
    row($ok, 'Telegram xabar yuborish');
}

// 6. Yozish huquqi (state/log)
$w = @file_put_contents($dir . '/.write_test', 'ok');
row($w !== false, 'Papka yozish huquqi');
@unlink($dir . '/.write_test');

echo '<p><a href="status.php" style="color:#58a6ff">→ Jonli status paneli</a></p>';
?>
</body></html>
