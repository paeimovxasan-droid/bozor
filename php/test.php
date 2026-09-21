<?php
/**
 * TORTINMANG.UZ PHP Lite — DVIGATEL SELF-TEST (tarmoqsiz)
 * Ochish: https://saytingiz.uz/tortinmang/test.php
 * Ichki logika (indikatorlar, risk, pog'ona, jurnal) hostingning
 * o'zida tekshiriladi. Ulanish testlari uchun check.php ishlating.
 */
$dir = __DIR__;
require_once $dir . '/lib.php';
require_once $dir . '/db.php';

$cfg = is_file($dir . '/config.php') ? require $dir . '/config.php' : [];

function row($ok, $label, $extra = '') {
    echo '<div style="padding:9px;margin:5px 0;border-radius:8px;background:' .
        ($ok ? '#0f2e1a' : '#2e0f0f') . ';font-size:14px">' . ($ok ? '✅' : '❌') . ' ' .
        htmlspecialchars($label) . ($extra !== '' ? ' — <small>' . htmlspecialchars($extra) . '</small>' : '') . '</div>';
}
$pass = 0; $fail = 0;
function t($ok, $label, $extra = '') {
    global $pass, $fail;
    $ok ? $pass++ : $fail++;
    row($ok, $label, $extra);
}
?>
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TORTINMANG.UZ — Self-test</title>
<style>body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:20px;max-width:620px;margin:auto}
h1{color:#58a6ff;font-size:20px}h2{color:#8b949e;font-size:14px;margin:18px 0 6px}small{color:#8b949e}</style>
</head><body>
<h1>🧪 TORTINMANG.UZ — Dvigatel self-test</h1>
<?php
// ── 1. Muhit ───────────────────────────────────────────────────
t(PHP_VERSION_ID >= 80100, 'PHP versiya >= 8.1', PHP_VERSION);
$need = ['cycle.php','lib.php','metaapi.php','db.php','status.php','admin.php','.htaccess','schema.sql'];
$miss = [];
foreach ($need as $f) if (!is_file($dir . '/' . $f)) $miss[] = $f;
t(!$miss, 'Kerakli fayllar mavjud', $miss ? 'yo\'q: ' . implode(', ', $miss) : count($need) . ' fayl');
t(is_file($dir . '/config.php'), 'config.php',
    is_file($dir . '/config.php') ? 'o\'rnatilgan' : 'avval install.php ni ishlating');
t(is_writable($dir), 'Papka yozish huquqi');

// ── 2. Pog'ona (tier) ──────────────────────────────────────────
$tiers = [
    [10,   'BRONZE',   0.03],
    [250,  'SILVER',   0.10],
    [700,  'GOLD',     0.3],
    [2500, 'PLATINUM', 0.5],
    [6000, 'DIAMOND',  1.0],
];
foreach ($tiers as $x) {
    $t = tier_for($x[0]);
    t($t['name'] === $x[1] && abs($t['lot_max'] - $x[2]) < 1e-9,
        '$' . $x[0] . ' -> ' . $x[1], "lot_max {$t['lot_max']}, risk_cap {$t['risk_cap']}%");
}

// ── 3. Indikatorlar (sintetik ma'lumot) ────────────────────────
$flat = array_fill(0, 60, 100.0);
t(abs(ema_last($flat, 20) - 100) < 0.01, 'EMA — tekis qator', 'natija ' . round(ema_last($flat, 20), 2));
$up = range(1, 60);   $up = array_map('floatval', $up);
$dn = array_reverse($up);
t(rsi_last($up) > 95, 'RSI o\'suvchi qator ≈ 100', round(rsi_last($up), 1));
t(rsi_last($dn) < 5,  'RSI tushuvchi qator ≈ 0',  round(rsi_last($dn), 1));
$h = array_fill(0, 40, 101.0); $l = array_fill(0, 40, 100.0); $c = array_fill(0, 40, 100.5);
$atr = atr_last($h, $l, $c, 14);
t(abs($atr - 1.0) < 0.05, 'ATR — TR=1 shamlar', round($atr, 3));

// ── 4. Lot hisobi (real dvigatel formulasi) ────────────────────
$defCfg = array_merge([
    'LOT_MIN' => 0.01, 'LOT_MAX' => 0.03, 'MAX_ACTUAL_RISK_PCT' => 3.0,
    'RISK_PCT' => ['XAUUSD' => 1.8, 'ETHUSD' => 1.0],
    'CONTRACT' => ['XAUUSD' => 100, 'ETHUSD' => 1],
], $cfg);
$cases = [
    ['XAUUSD', 10, 3.0],   // $10 balans, 3 dollar SL masofasi
    ['ETHUSD', 10, 10.0],
    ['XAUUSD', 250, 3.0],
];
foreach ($cases as $cs_) {
    [$sym, $bal, $sl_dist] = $cs_;
    $tier = tier_for($bal);
    $risk_pct = $defCfg['RISK_PCT'][$sym];
    $cs = $defCfg['CONTRACT'][$sym];
    $lot = round(max($defCfg['LOT_MIN'], min($bal * $risk_pct / 100 / ($sl_dist * $cs),
        min($defCfg['LOT_MAX'], $tier['lot_max']))), 2);
    $actual = $lot * $sl_dist * $cs / $bal * 100;
    $skip = $actual > $defCfg['MAX_ACTUAL_RISK_PCT'];
    $ok = $lot >= $defCfg['LOT_MIN'] && $lot <= $defCfg['LOT_MAX'] && (!$skip || $bal < 20);
    t($ok, 'Lot: ' . $sym . ' $' . $bal, "lot=$lot risk=" . round($actual, 2) . '%' .
        ($skip ? ' (min-lot cap: o\'tkaziladi)' : ''));
}

// ── 5. Sessiya va blackout ─────────────────────────────────────
$sc = ['SESSION_FROM' => 0, 'SESSION_TO' => 24];
t(session_ok($sc) === true, 'Sessiya 0-24 doim ochiq');
$sc2 = ['SESSION_FROM' => 12, 'SESSION_TO' => 13];
$hh = (int)date('G');
t(session_ok($sc2) === ($hh >= 12 && $hh < 13), 'Sessiya mantiqiy tekshiruv', "hozir soat $hh");
$nb = news_blackout();
t(is_array($nb) && is_bool($nb[0]), 'Yangilik blackout funksiyasi',
    $nb[0] ? 'FAOL: ' . $nb[1] : 'hozir yo\'q');

// ── 6. Jurnal va state (vaqtinchalik papkada) ──────────────────
$tmp = $dir . '/.selftest_tmp';
@mkdir($tmp);
journal_add($tmp, ['ts' => time() - 60, 'symbol' => 'XAUUSD', 'side' => 'BUY', 'profit' => 2.5]);
journal_add($tmp, ['ts' => time(), 'symbol' => 'ETHUSD', 'side' => 'SELL', 'profit' => -1.0]);
$j = journal_load($tmp);
t(count($j) === 2, 'Jurnal yozish/o\'qish', count($j) . ' yozuv');
$st = journal_stats($tmp);
t($st['total'] === 2 && abs($st['net'] - 1.5) < 1e-9 && abs($st['pf'] - 2.5) < 1e-9,
    'Jurnal statistika (WR/PF/net)', "WR={$st['wr']}% PF={$st['pf']} net={$st['net']}\$");
state_save($tmp . '/state.json', ['test' => 123]);
$s = state_load($tmp . '/state.json');
t(($s['test'] ?? 0) === 123, 'State yozish/o\'qish');
@unlink($tmp . '/journal.json'); @unlink($tmp . '/state.json'); @rmdir($tmp);

// ── 7. MySQL (sozlangan bo'lsa) ────────────────────────────────
if (!empty($cfg['DB_NAME'])) {
    $pdo = db_conn($cfg);
    if ($pdo) {
        try {
            db_schema($pdo);
            $one = $pdo->query('SELECT 1')->fetchColumn();
            t($one == 1, 'MySQL ulanish + jadvallar', $cfg['DB_NAME']);
        } catch (Exception $e) { t(false, 'MySQL jadvallar', $e->getMessage()); }
    } else {
        t(false, 'MySQL ulanish', 'host/user/parolni tekshiring');
    }
} else {
    row(true, 'MySQL (sozlanmagan — json rejim, xato emas)');
}

echo '<h2>NATIJA: <span style="color:' . ($fail ? '#f85149' : '#3fb950') . '">' .
    "$pass ta o'tdi" . ($fail ? ", $fail ta xato" : '') . '</span></h2>';
echo $fail === 0
    ? '<p>✅ Dvigatel logikasi soz. Endi <a href="check.php" style="color:#58a6ff">check.php</a> bilan tarmoq ulanishlarini tekshiring.</p>'
    : '<p style="color:#f85149">❌ Xatolarni rasmini yuboring — tuzatiladi.</p>';
?>
<p><a href="status.php" style="color:#58a6ff">→ Status panel</a> |
<a href="admin.php" style="color:#58a6ff">Admin panel</a></p>
</body></html>
