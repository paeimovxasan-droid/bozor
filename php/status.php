<?php
/**
 * TORTINMANG.UZ PHP Lite — JONLI STATUS PANELI (mobilga mos)
 * Ochish: https://saytingiz.uz/tortinmang/status.php
 */
$dir = __DIR__;
$state = state_load($dir . '/state.json');
$cfgFile = $dir . '/config.php';
$cfg = is_file($cfgFile) ? require $cfgFile : [];
$tier = $state['tier'] ?? '—';
$last = $state['last_cycle'] ?? 0;
$ago = $last ? (time() - $last) : null;
$alive = $ago !== null && $ago < 180;
$stats = journal_stats($dir);
$recent = array_slice(journal_load($dir), -5);
?>
<!doctype html><html lang="uz"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="60">
<title>TORTINMANG.UZ — Status</title>
<style>
body{font-family:system-ui;background:#0d1117;color:#e6edf3;padding:16px;max-width:560px;margin:auto}
h1{color:#58a6ff;font-size:20px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:14px;margin:10px 0}
.big{font-size:26px;font-weight:700}
.green{color:#3fb950}.red{color:#f85149}.gray{color:#8b949e}
small{color:#8b949e}
</style></head><body>
<h1>🤖 TORTINMANG.UZ <small>PHP Lite</small></h1>

<div class="card">
  <span class="<?= $alive ? 'green' : 'red' ?>"><?= $alive ? '🟢 BOT JONLI' : '🔴 BOT UXLAMAGAN (cron?)' ?></span>
  <?php if ($ago !== null): ?><small> — <?= $ago ?> soniya oldin sikl</small><?php endif; ?>
</div>

<div class="card">
  <div class="gray">Pog'ona</div>
  <div class="big"><?= htmlspecialchars($tier) ?></div>
</div>

<div class="card">
  <div class="gray">Balans / Equity</div>
  <div class="big">$<?= htmlspecialchars($state['balance'] ?? '—') ?>
    <small>/ $<?= htmlspecialchars($state['equity'] ?? '—') ?></small></div>
  <div class="gray">Bugungi P&L</div>
  <div class="big <?= ($state['pnl'] ?? 0) >= 0 ? 'green' : 'red' ?>">
    <?= ($state['pnl'] ?? 0) >= 0 ? '+' : '' ?><?= htmlspecialchars($state['pnl'] ?? '0') ?>$</div>
</div>

<div class="card">
  <div class="gray">Bugungi savdolar / Rejim</div>
  <div class="big"><?= (int)($state['trades'] ?? 0) ?>
    <small>| <?= !empty($state['paused']) ? '⏸️ pauza' : '🟢 aktiv' ?></small></div>
</div>

<div class="card">
  <div class="gray">Statistika (journal)</div>
  <div class="big"><?= $stats['total'] ?> <small>savdo</small></div>
  <div>WR: <span class="<?= $stats['wr'] >= 50 ? 'green' : 'red' ?>"><?= $stats['wr'] ?>%</span>
   | PF: <?= $stats['pf'] ?> | Natija:
   <span class="<?= $stats['net'] >= 0 ? 'green' : 'red' ?>"><?= $stats['net'] ?>$</span></div>
  <?php if ($recent): ?>
  <hr style="border-color:#30363d">
  <?php foreach (array_reverse($recent) as $t): ?>
    <div><small><?= ($t['profit'] >= 0 ? '✅' : '❌') ?>
    <?= htmlspecialchars($t['symbol']) ?> <?= htmlspecialchars($t['side'] ?? '') ?>
    <?= ($t['profit'] >= 0 ? '+' : '') . htmlspecialchars($t['profit']) ?>$
    — <?= date('d.m H:i', $t['ts'] ?? time()) ?></small></div>
  <?php endforeach; endif; ?>
</div>

<div class="card"><small>
Buyruqlar: /status /positions /closeall /pause /resume /stats /history /risk<br>
Kun: <?= htmlspecialchars($state['day'] ?? '—') ?>
</small></div>
</body></html>
