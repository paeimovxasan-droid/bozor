<?php
/**
 * TORTINMANG.UZ — ADMIN PANEL
 * ==========================
 * • Libertex MT5 hisobni panel orqali ulash (MetaApi provisioning)
 * • Avto savdoni yoqish/o'chirish
 * • Jonli holat, pozitsiyalarni yopish, jurnal, risk sozlamalari
 *
 * Kirish paroli: install.php da kiritilgan ADMIN_PASS
 */
session_start();
$dir = __DIR__;
$cfgFile = $dir . '/config.php';
if (!is_file($cfgFile)) die("Avval install.php ni ishlating.");
$baseCfg = require $cfgFile;
require_once $dir . '/lib.php';
require_once $dir . '/metaapi.php';

define('PROV_API', 'https://mt-provisioning-api-v1.agiliumtrade.ai');

$state = state_load($dir . '/state.json', $baseCfg);
$cfg = array_merge($baseCfg, $state['settings'] ?? []);
if (!empty($state['meta_token'])) $cfg['META_API_TOKEN'] = $state['meta_token'];
if (!empty($state['meta_account_id'])) $cfg['META_ACCOUNT_ID'] = $state['meta_account_id'];

$adminPass = $cfg['ADMIN_PASS'] ?? 'admin123';
$notice = '';

// ── Auth ───────────────────────────────────────────────────────
if (isset($_GET['logout'])) { unset($_SESSION['tm_admin']); }
if (!empty($_SESSION['tm_admin'])) {
    // kirgan
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['act'] ?? '') === 'login') {
    if (hash_equals($adminPass, $_POST['pass'] ?? '')) {
        $_SESSION['tm_admin'] = 1;
    } else {
        $notice = 'Parol noto\'g\'ri!';
    }
}
if (empty($_SESSION['tm_admin'])) {
    ?>
    <!doctype html><html lang="uz"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>TORTINMANG.UZ — Admin</title>
    <style>body{font-family:system-ui;background:#0d1117;color:#e6edf3;display:flex;
    align-items:center;justify-content:center;min-height:100vh;margin:0}
    .box{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:28px;width:300px}
    input{width:100%;padding:10px;margin:8px 0;border-radius:8px;border:1px solid #30363d;
    background:#0d1117;color:#e6edf3}
    button{width:100%;background:#238636;color:#fff;padding:11px;border:0;border-radius:8px;
    font-size:15px;cursor:pointer}h1{font-size:18px;color:#58a6ff}</style></head><body>
    <form class="box" method="post">
    <h1>🔐 TORTINMANG.UZ Admin</h1>
    <?php if ($notice): ?><p style="color:#f85149"><?= htmlspecialchars($notice) ?></p><?php endif; ?>
    <input type="password" name="pass" placeholder="Admin parol" autofocus>
    <input type="hidden" name="act" value="login">
    <button>Kirish</button></form></body></html>
    <?php exit;
}

// ── Amallar ────────────────────────────────────────────────────
$act = $_POST['act'] ?? '';

if ($act === 'connect') {
    // Libertex hisobni MetaApi orqali ulash
    $token = trim($_POST['mtoken'] ?? '') ?: $cfg['META_API_TOKEN'];
    $login = trim($_POST['mlogin'] ?? '');
    $mpass = trim($_POST['mpass'] ?? '');
    $server = trim($_POST['mserver'] ?? '') ?: 'ForexClub-MT5 Real Server';
    if ($token === '' || $login === '' || $mpass === '') {
        $notice = 'MetaApi token, MT5 login va parol majburiy!';
    } else {
        $r = http_json('POST', PROV_API . '/users/current/accounts', $token, [
            'login' => $login, 'password' => $mpass,
            'name' => 'TORTINMANG Libertex', 'server' => $server,
            'platform' => 'mt5',
        ], 30);
        $accId = $r['data']['id'] ?? null;
        if ($accId) {
            $state['meta_token'] = $token;
            $state['meta_account_id'] = $accId;
            $state['auto'] = $state['auto'] ?? true;
            $notice = "✅ Hisob ulandi! Account ID: $accId (bir daqiqada aktiv bo'ladi)";
        } else {
            $err = json_decode((string)($r['raw'] ?? ''), true);
            $notice = '❌ Ulanmadi: ' . mb_substr($err['message'] ?? ($r['error'] ?? 'noma\'lum xato'), 0, 200);
        }
    }
}

if ($act === 'manual_account') {
    // Tayyor MetaApi account ID ni qo'lda kiritish
    $state['meta_token'] = trim($_POST['mtoken'] ?? '') ?: $state['meta_token'] ?? '';
    $state['meta_account_id'] = trim($_POST['accid'] ?? '');
    $notice = '✅ Account ID saqlandi.';
}

if ($act === 'auto') {
    $state['auto'] = !empty($_POST['auto_on']);
    $notice = $state['auto'] ? '🟢 Avto savdo YOQILDI' : '⏸️ Avto savdo O\'CHIRILDI';
}

if ($act === 'close') {
    ma_close($cfg, $_POST['pid'] ?? '');
    $notice = '✅ Pozitsiya yopildi.';
}

if ($act === 'closeall') {
    foreach (ma_positions($cfg) as $p) ma_close($cfg, $p['id']);
    $notice = '✅ Barcha pozitsiyalar yopildi.';
}

if ($act === 'settings') {
    $s = $state['settings'] ?? [];
    $s['RISK_PCT'] = ['ETHUSD' => floatval($_POST['risk_eth'] ?? 1.0),
                      'XAUUSD' => floatval($_POST['risk_xau'] ?? 1.8)];
    $s['LOT_MAX'] = floatval($_POST['lot_max'] ?? 0.03);
    $s['DAILY_TARGET_USD'] = floatval($_POST['target'] ?? 5);
    $s['DAILY_LOSS_PCT'] = floatval($_POST['dloss'] ?? 3);
    $s['MAX_POSITIONS'] = intval($_POST['maxpos'] ?? 2);
    $s['MAX_TRADES_DAY'] = intval($_POST['maxtrades'] ?? 6);
    $state['settings'] = $s;
    $notice = '✅ Sozlamalar saqlandi (keyingi sikldan kuchga kiradi).';
}

if ($act !== '' && $act !== 'login') {
    state_save($dir . '/state.json', $state, $baseCfg);
}

// ── Jonli ma'lumotlar ──────────────────────────────────────────
$acc = ma_account($cfg);
$positions = ma_positions($cfg);
$stats = journal_stats($dir, null, $cfg);
$journal = array_slice(array_reverse(journal_load($dir, $cfg)), 0, 10);
$auto = $state['auto'] ?? true;
$acctId = $cfg['META_ACCOUNT_ID'] ?? '';
?>
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>TORTINMANG.UZ — Admin</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:16px;max-width:760px;margin:auto}
h1{color:#58a6ff;font-size:20px}h2{font-size:15px;color:#8b949e;margin:22px 0 8px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px;margin:10px 0}
label{display:block;color:#8b949e;font-size:12px;margin:8px 0 3px}
input{width:100%;padding:9px;border-radius:8px;border:1px solid #30363d;background:#0d1117;
color:#e6edf3;box-sizing:border-box}
button{background:#238636;color:#fff;padding:10px 16px;border:0;border-radius:8px;
cursor:pointer;margin-top:8px}
button.red{background:#da3633}button.gray{background:#30363d}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:6px 4px;border-bottom:1px solid #21262d;text-align:left}
.green{color:#3fb950}.red{color:#f85149}.gray{color:#8b949e}
.note{background:#0f2e1a;border:1px solid #238636;padding:10px;border-radius:8px;margin:10px 0}
.row{display:flex;gap:8px}.row>div{flex:1}
a{color:#58a6ff}
</style></head><body>
<h1>🤖 TORTINMANG.UZ — Admin Panel
<small class="gray">| <a href="status.php">status</a> | <a href="?logout=1">chiqish</a></small></h1>

<?php if ($notice): ?><div class="note"><?= htmlspecialchars($notice) ?></div><?php endif; ?>

<div class="card">
<h2>🏦 Libertex MT5 hisob</h2>
<?php if ($acc): ?>
  Balans: <b>$<?= round(floatval($acc['balance'] ?? 0), 2) ?></b> |
  Equity: <b>$<?= round(floatval($acc['equity'] ?? 0), 2) ?></b> |
  Server: <?= htmlspecialchars($acc['server'] ?? $acc['name'] ?? '—') ?>
  <span class="green">● ULANGAN</span>
<?php else: ?>
  <span class="red">● Hisob ulanmagan</span> — quyidagi forma orqali uling:
<?php endif; ?>
<form method="post">
  <input type="hidden" name="act" value="connect">
  <label>MetaApi API TOKEN (app.metaapi.cloud/token)</label>
  <input name="mtoken" placeholder="<?= $cfg['META_API_TOKEN'] ? '(config da bor)' : 'token...' ?>">
  <div class="row">
    <div><label>MT5 LOGIN</label><input name="mlogin" placeholder="12345678"></div>
    <div><label>MT5 PAROL</label><input name="mpass" type="password" placeholder="••••••"></div>
  </div>
  <label>MT5 SERVER</label>
  <input name="mserver" value="ForexClub-MT5 Real Server">
  <button>🔗 Libertex hisobni ulash</button>
</form>
<details style="margin-top:10px"><summary class="gray">yoki tayyor Account ID kiritish</summary>
<form method="post">
  <input type="hidden" name="act" value="manual_account">
  <label>MetaApi TOKEN</label><input name="mtoken">
  <label>ACCOUNT ID (uuid)</label><input name="accid" placeholder="865d3a4d-...">
  <button class="gray">Saqlash</button>
</form></details>
</div>

<div class="card">
<h2>🤖 Avto savdo</h2>
<form method="post" style="display:flex;gap:10px;align-items:center">
  <input type="hidden" name="act" value="auto">
  <label style="display:flex;gap:8px;align-items:center;color:#e6edf3">
  <input type="checkbox" name="auto_on" style="width:auto" <?= $auto ? 'checked' : '' ?>>
  Avto savdo (bot o'zi ochadi va foyda bilan yopadi)</label>
  <button><?= $auto ? 'Saqlash' : '🟢 Yoqish' ?></button>
</form>
<p class="gray">Hozir: <?= $auto ? '<span class="green">🟢 YOQIQ</span>' : '<span class="red">⏸️ O\'CHIQ</span>' ?>
| Pog'ona: <b><?= htmlspecialchars($state['tier'] ?? '—') ?></b>
| Bugun: <?= (int)($state['trades'] ?? 0) ?> savdo | P&L: <?= ($state['pnl'] ?? 0) >= 0 ? '+' : '' ?><?= $state['pnl'] ?? 0 ?>$</p>
</div>

<div class="card">
<h2>📂 Ochiq pozitsiyalar (<?= count($positions) ?>)</h2>
<?php if (!$positions): ?><p class="gray">Bo'sh</p><?php else: ?>
<table><tr><th>ID</th><th>Symbol</th><th>Yo'n.</th><th>Lot</th><th>P&L</th><th></th></tr>
<?php foreach ($positions as $p): $pl = floatval($p['profit'] ?? $p['unrealizedProfit'] ?? 0); ?>
<tr><td>#<?= htmlspecialchars($p['id']) ?></td><td><?= htmlspecialchars($p['symbol']) ?></td>
<td><?= stripos($p['type'] ?? '', 'BUY') !== false ? 'BUY' : 'SELL' ?></td>
<td><?= $p['volume'] ?></td>
<td class="<?= $pl >= 0 ? 'green' : 'red' ?>"><?= round($pl, 2) ?>$</td>
<td><form method="post"><input type="hidden" name="act" value="close">
<input type="hidden" name="pid" value="<?= htmlspecialchars($p['id']) ?>">
<button class="red" style="margin:0;padding:4px 10px">Yopish</button></form></td></tr>
<?php endforeach; ?></table>
<form method="post"><input type="hidden" name="act" value="closeall">
<button class="red">❌ Hammasini yopish</button></form>
<?php endif; ?>
</div>

<div class="card">
<h2>🛡️ Risk sozlamalari</h2>
<form method="post"><input type="hidden" name="act" value="settings">
<div class="row">
  <div><label>ETH risk %</label><input name="risk_eth" value="<?= htmlspecialchars($cfg['RISK_PCT']['ETHUSD'] ?? 1.0) ?>"></div>
  <div><label>XAU risk %</label><input name="risk_xau" value="<?= htmlspecialchars($cfg['RISK_PCT']['XAUUSD'] ?? 1.8) ?>"></div>
  <div><label>Lot max</label><input name="lot_max" value="<?= htmlspecialchars($cfg['LOT_MAX'] ?? 0.03) ?>"></div>
</div>
<div class="row">
  <div><label>Kunlik maqsad $</label><input name="target" value="<?= htmlspecialchars($cfg['DAILY_TARGET_USD'] ?? 5) ?>"></div>
  <div><label>Kunlik zarar %</label><input name="dloss" value="<?= htmlspecialchars($cfg['DAILY_LOSS_PCT'] ?? 3) ?>"></div>
  <div><label>Max pozitsiya</label><input name="maxpos" value="<?= htmlspecialchars($cfg['MAX_POSITIONS'] ?? 2) ?>"></div>
  <div><label>Max savdo/kun</label><input name="maxtrades" value="<?= htmlspecialchars($cfg['MAX_TRADES_DAY'] ?? 6) ?>"></div>
</div>
<button>💾 Saqlash</button></form>
</div>

<div class="card">
<h2>📈 Statistika: <?= $stats['total'] ?> savdo | WR <?= $stats['wr'] ?>% | PF <?= $stats['pf'] ?> | <?= $stats['net'] ?>$</h2>
<?php if ($journal): ?>
<table><tr><th>Sana</th><th>Symbol</th><th>Yo'n.</th><th>P&L</th></tr>
<?php foreach ($journal as $t): ?>
<tr><td class="gray"><?= date('d.m H:i', $t['ts'] ?? time()) ?></td>
<td><?= htmlspecialchars($t['symbol']) ?></td><td><?= htmlspecialchars($t['side'] ?? '') ?></td>
<td class="<?= $t['profit'] >= 0 ? 'green' : 'red' ?>"><?= ($t['profit'] >= 0 ? '+' : '') . $t['profit'] ?>$</td></tr>
<?php endforeach; ?></table>
<?php else: ?><p class="gray">Jurnal bo'sh</p><?php endif; ?>
</div>
</body></html>
