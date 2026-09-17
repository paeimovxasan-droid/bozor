<?php
/**
 * TORTINMANG.UZ PHP Lite — asosiy sikl (v2)
 * ==========================================
 * Cron da HAR DAQIQA:
 *   * * * * * /usr/bin/php /path/php/cycle.php >> /dev/null 2>&1
 *
 * Sikl: Telegram buyruqlari → hisob → risk qalqonlari → pozitsiya
 * boshqaruvi (partial TP/BE/time-stop) → signal → AI veto → savdo.
 */
$dir = __DIR__;
$cfgFile = $dir . '/config.php';
if (!is_file($cfgFile)) { exit(0); }   // o'rnatilmagan — jim chiqish
$cfg = require $cfgFile;
require_once $dir . '/lib.php';
require_once $dir . '/metaapi.php';

date_default_timezone_set($cfg['TIMEZONE'] ?? 'Asia/Tashkent');

// ── Lock: parallel cron nusxalarini to'xtatish ─────────────────
$lockF = fopen($dir . '/cycle.lock', 'c');
if (!$lockF || !flock($lockF, LOCK_EX | LOCK_NB)) exit(0);

$state = state_load($dir . '/state.json');
$today = date('Y-m-d');
if (($state['day'] ?? '') !== $today) {
    // ── KUNLIK AI HISOBOT: kechagi kun yakuni (yangi kun boshida) ──
    $st = journal_stats($dir);
    if ($st['total'] > 0) {
        $rep = "📊 <b>KUNLIK HISOBOT</b>\nSavdolar: {$st['total']} | G'alaba: {$st['wins']} " .
            "({$st['wr']}%) | PF: {$st['pf']}\nTo'plangan: {$st['net']}\$";
        $txt = deepseek_report($cfg,
            "Sen savdo ustashsisan. Kecha: {$st['total']} savdo, {$st['wins']} g'alaba " .
            "({$st['wr']}%), PF {$st['pf']}, natija {$st['net']} dollar. " .
            "3 qatorda qisqa o'zbekcha xulosa va bugun uchun maslahat yoz.");
        if ($txt) $rep .= "\n🤖 " . $txt;
        tg_send($cfg, $rep);
    }
    $state['day'] = $today;
    $state['trades'] = 0;
    $state['daily_start'] = null;
    $state['pnl'] = 0.0;
    $state['target_done'] = false;
}
$week = date('o-W');
if (($state['week'] ?? '') !== $week) {
    $state['week'] = $week;
    $state['week_start'] = null;
}

if (empty($cfg['META_API_TOKEN']) || empty($cfg['META_ACCOUNT_ID'])) {
    log_line($dir, "config: META_API_TOKEN/META_ACCOUNT_ID bo'sh");
    flock($lockF, LOCK_UN); exit(1);
}

$acc = ma_account($cfg);
if (!$acc) {
    log_line($dir, "MetaApi hisob o'qilmadi");
    if (($state['err_notified'] ?? 0) < time() - 3600) {
        tg_send($cfg, "⚠️ PHP Lite: MetaApi ga ulanib bo'lmadi (token/hisob/aloqa)");
        $state['err_notified'] = time();
    }
    state_save($dir . '/state.json', $state);
    flock($lockF, LOCK_UN); exit(1);
}
$balance = floatval($acc['balance'] ?? 0);
$equity  = floatval($acc['equity'] ?? $balance);
if (!($state['daily_start'] > 0)) $state['daily_start'] = $balance;
if (!($state['week_start'] > 0))  $state['week_start'] = $balance;
$daily_pnl = $equity - $state['daily_start'];
$week_pnl  = $equity - $state['week_start'];
$tier = tier_for($balance);

$positions = ma_positions($cfg);

// ── Telegram buyruqlari (har siklda poll) ──────────────────────
$updates = tg_get_updates($cfg, $state['tg_offset'] ?? 0);
foreach ($updates as $u) {
    $state['tg_offset'] = max($state['tg_offset'] ?? 0, ($u['update_id'] ?? 0) + 1);
    $msg = $u['message'] ?? null;
    if (!$msg) continue;
    if ((string)($msg['chat']['id'] ?? '') !== (string)$cfg['TELEGRAM_CHAT_ID']) continue;
    $text = trim($msg['text'] ?? '');
    if (strpos($text, '/') !== 0) continue;
    handle_cmd($cfg, $state, $positions, $acc, $tier, $text);
}

// ── Risk qalqonlari ────────────────────────────────────────────
$can_trade = true; $why = '';
if (!empty($state['paused'])) { $can_trade = false; $why = 'pauza (/resume)'; }
if (!empty($state['paused_until'])) {
    if (time() < $state['paused_until']) { $can_trade = false; $why = 'anti-tilt pauza'; }
    else $state['paused_until'] = 0;
}
list($nb, $nb_reason) = news_blackout();
if ($nb) { $can_trade = false; $why = "blackout: $nb_reason"; }
if ($state['daily_start'] > 0 &&
    (-$daily_pnl) / $state['daily_start'] * 100 >= $cfg['DAILY_LOSS_PCT']) {
    $can_trade = false; $why = 'kunlik zarar limiti';
}
if ($state['week_start'] > 0 &&
    (-$week_pnl) / $state['week_start'] * 100 >= ($cfg['WEEKLY_LOSS_PCT'] ?? 7.0)) {
    $can_trade = false; $why = 'haftalik zarar limiti';
}
if ($daily_pnl >= $cfg['DAILY_TARGET_USD']) {
    $can_trade = false; $why = "kunlik maqsad yig'ildi";
    if (empty($state['target_done'])) {
        $state['target_done'] = true;
        tg_send($cfg, "🎯 <b>KUNLIK MAQSAD YIG'ILDI!</b> +" . round($daily_pnl, 2) .
            '$ — bugun savdo yopiladi 🛡️');
    }
}
if (count($positions) >= $cfg['MAX_POSITIONS']) { $can_trade = false; $why = 'pozitsiya limiti'; }
if (($state['trades'] ?? 0) >= $cfg['MAX_TRADES_DAY']) { $can_trade = false; $why = 'kunlik savdo limiti'; }
if (!session_ok($cfg)) { $can_trade = false; $why = 'sessiya tashqarisi'; }

// ── Juma himoyasi: 20:00 dan keyin barcha pozitsiyalar yopiladi ──
if ((int)date('N') === 5 && (int)date('G') >= 20 && $positions) {
    foreach ($positions as $p) {
        ma_close($cfg, $p['id']);
        unset($state['pos'][(string)$p['id']]);
    }
    tg_send($cfg, "🛡️ <b>Juma himoyasi</b>: weekend gap riskidan barcha pozitsiyalar yopildi");
    log_line($dir, 'weekend close');
}

// ── Ochiq pozitsiyalarni boshqarish ────────────────────────────
foreach ($positions as $p) {
    $id = (string)($p['id'] ?? '');
    if ($id === '') continue;
    $sym = $p['symbol'] ?? '';
    $rec = $state['pos'][$id] ?? null;

    // yangi ochilgan pozitsiyani pending dan bog'lash
    if (!$rec && isset($state['pending'][$sym])) {
        $rec = $state['pending'][$sym];
        $state['pos'][$id] = $rec;
        unset($state['pending'][$sym]);
    }

    $entry = floatval($p['openPrice'] ?? 0);
    $cur   = floatval($p['currentPrice'] ?? $entry);
    $side  = (stripos((string)($p['type'] ?? ''), 'BUY') !== false) ? 'BUY' : 'SELL';

    // SL XAVFSIZLIGI: broker tomonda SL yo'qolgan bo'lsa darhol tiklash
    $sl_now = floatval($p['stopLoss'] ?? 0);
    $rec_sl = floatval($rec['sl'] ?? 0);
    if ($rec_sl > 0 && $sl_now <= 0) {
        ma_modify($cfg, $id, $rec_sl);
        tg_send($cfg, "🛡️ #{$id} {$sym}: SL yo'qolgan edi — darhol tiklandi");
        log_line($dir, "SL restore #$id");
    }

    // Partial TP: +1R da 50% + SL breakeven
    $sl0 = floatval($rec['sl'] ?? 0);
    if ($rec && $sl0 > 0 && empty($rec['partial'])) {
        $r_dist = abs($entry - $sl0);
        $gain = ($side === 'BUY') ? ($cur - $entry) : ($entry - $cur);
        if ($r_dist > 0 && $gain >= $r_dist) {
            $vol = round(floatval($p['volume'] ?? 0) / 2, 2);
            if ($vol >= 0.01) {
                ma_partial($cfg, $id, $vol);
                ma_modify($cfg, $id, $entry);
                $state['pos'][$id]['partial'] = true;
                tg_send($cfg, "💰 <b>Partial TP</b> #{$id} {$sym}: 50% 1R da yopildi, SL breakeven 🔒");
                log_line($dir, "partial+BE #$id $sym");
            }
        }
    }

    // Time-stop: 90 daqiqada natijasiz bo'lsa yopish
    $ts = intval($rec['ts'] ?? 0);
    if ($ts > 0 && (time() - $ts) > 90 * 60) {
        $profit = floatval($p['profit'] ?? $p['unrealizedProfit'] ?? 0);
        if (abs($profit) < 0.3) {
            ma_close($cfg, $id);
            unset($state['pos'][$id]);
            tg_send($cfg, "⏱️ <b>Time-stop</b>: #{$id} {$sym} 90 daqiqada natijasiz yopildi");
            log_line($dir, "time-stop #$id $sym");
        }
    }
}

// ── Yangi signallar ────────────────────────────────────────────
if ($can_trade) {
    foreach ($cfg['SYMBOLS'] as $sym) {
        $has = false;
        foreach ($positions as $p) if (($p['symbol'] ?? '') === $sym) $has = true;
        if ($has || isset($state['pending'][$sym])) continue;

        $c = ma_candles($cfg, $sym, '15m', 200);
        if (!$c || count($c) < 60) continue;
        $cl = []; $hi = []; $lo = []; $sp = [];
        foreach ($c as $k) {
            $cl[] = floatval($k['close']);
            $hi[] = floatval($k['high']);
            $lo[] = floatval($k['low']);
            $sp[] = floatval($k['spread'] ?? 0);
        }
        // Spread sniffer: oxirgi spread o'rtachadan 1.5x keng bo'lsa kutamiz
        if (count($sp) > 20) {
            $last_sp = end($sp);
            $avg_sp = array_sum(array_slice($sp, -60)) / min(60, count($sp));
            if ($avg_sp > 0 && $last_sp > $avg_sp * 1.5) {
                log_line($dir, "$sym spread keng — kutish");
                continue;
            }
        }

        $e20 = ema_last($cl, 20);
        $e50 = ema_last($cl, 50);
        $rsi = rsi_last($cl);
        $atr = atr_last($hi, $lo, $cl);
        $price = end($cl);
        if ($price <= 0 || $atr <= 0) continue;
        $atr_pct = $atr / $price * 100;
        if ($atr_pct < 0.02 || $atr_pct > 2.5) continue;   // volatillik darvozasi

        $signal = null;
        if ($e20 > $e50 && $rsi > 45 && $rsi < 70) $signal = 'BUY';
        elseif ($e20 < $e50 && $rsi > 30 && $rsi < 55) $signal = 'SELL';
        if (!$signal) continue;

        // H1 MULTI-TIMEFRAME TASDIQ: katta trend qarshi bo'lsa savdo yo'q
        $c1h = ma_candles($cfg, $sym, '1h', 100);
        if ($c1h && count($c1h) > 50) {
            $hcl = [];
            foreach ($c1h as $k) $hcl[] = floatval($k['close']);
            $he20 = ema_last($hcl, 20);
            $he50 = ema_last($hcl, 50);
            if (($signal === 'BUY' && $he20 < $he50) ||
                ($signal === 'SELL' && $he20 > $he50)) {
                log_line($dir, "$sym H1 trend qarshi — o'tkazildi");
                continue;
            }
        }

        // Konflyuens ball
        $conf = 50 + min(20, abs($e20 - $e50) / $price * 2000) +
                ($signal === 'BUY' ? (70 - $rsi) / 3 : ($rsi - 30) / 3) +
                ($atr_pct > 0.1 ? 5 : 0);
        if ($conf < ($cfg['MIN_CONFIDENCE'] ?? 55)) continue;

        $sl = ($signal === 'BUY') ? $price - 1.5 * $atr : $price + 1.5 * $atr;
        $tp = ($signal === 'BUY') ? $price + 3.0 * $atr : $price - 3.0 * $atr;

        // DeepSeek AI tasdig'i
        $ai = deepseek_review($cfg,
            "Savdo signali: $signal $sym, ishonch " . round($conf) . "%, RSI " . round($rsi) .
            ", trend " . ($e20 > $e50 ? 'yuqori' : 'past') . ". Tasdiqlaysanmi?");
        if (!$ai['ok']) {
            tg_send($cfg, "🛑 <b>AI VETO</b> $sym $signal — " . $ai['reason']);
            log_line($dir, "AI veto $sym");
            continue;
        }
        if (!empty($ai['wait'])) { log_line($dir, "AI wait $sym"); continue; }

        // Sizing: fixed-fractional + pog'ona lot cap + hard risk cap
        $risk_pct = min(floatval($cfg['RISK_PCT'][$sym] ?? 1.0), $tier['risk_cap']);
        $sl_dist = abs($price - $sl);
        if ($sl_dist <= 0 || $balance <= 0) continue;
        $cs  = floatval($cfg['CONTRACT'][$sym] ?? 10);
        // Anti-tilt: 2 ketma-ket zarar bo'lsa lot 50% kamayadi
        $tilt = (($state['consec_losses'] ?? 0) >= 2) ? 0.5 : 1.0;
        $lot = round(max($cfg['LOT_MIN'], min($balance * $risk_pct / 100 / ($sl_dist * $cs) * $tilt,
                 min($cfg['LOT_MAX'], $tier['lot_max']))), 2);
        $actual = $lot * $sl_dist * $cs / $balance * 100;
        if ($actual > $cfg['MAX_ACTUAL_RISK_PCT']) {
            log_line($dir, "$sym o'tkazildi: min lot risk " . round($actual, 1) . '%');
            continue;
        }

        $r = ma_open($cfg, $sym, $signal, $lot, round($sl, 5), round($tp, 5));
        if (($r['code'] ?? 0) === 200) {
            $state['pending'][$sym] = ['symbol' => $sym, 'side' => $signal,
                                       'entry' => $price, 'sl' => $sl, 'ts' => time()];
            $state['trades'] = ($state['trades'] ?? 0) + 1;
            tg_send($cfg,
                "🚀 <b>SAVDO OCHILDI</b> {$tier['name']} | $signal $sym\n" .
                "Lot: $lot | Risk: " . round($actual, 2) . "%\n" .
                "Entry: " . round($price, 4) . " | SL: " . round($sl, 4) . " | TP: " . round($tp, 4) . "\n" .
                "Ishonch: " . round($conf) . "% | R:R 2.0" .
                ($ai['reason'] ? "\n🤖 " . $ai['reason'] : ''));
            log_line($dir, "OPEN $signal $sym lot=$lot risk=" . round($actual, 2) . '%');
        } else {
            log_line($dir, "OPEN xato $sym: " . substr((string)($r['raw'] ?? ''), 0, 200));
        }
    }
}

// ── Yopilgan pozitsiyalar → xabar ──────────────────────────────
$open_ids = [];
foreach ($positions as $p) $open_ids[] = (string)($p['id'] ?? '');
foreach (array_keys($state['pos'] ?? []) as $pid) {
    if (!in_array($pid, $open_ids, true)) {
        $info = $state['pos'][$pid];
        unset($state['pos'][$pid]);
        // P&L: equity o'zgarishidan (bir daqiqada bitta yopilish taxmini)
        $profit = round($equity - floatval($state['last_equity'] ?? $equity), 2);
        journal_add($dir, ['ts' => time(), 'id' => $pid,
            'symbol' => $info['symbol'], 'side' => $info['side'] ?? '',
            'profit' => $profit, 'tier' => $tier['name']]);
        if ($profit < 0) {
            $state['consec_losses'] = ($state['consec_losses'] ?? 0) + 1;
            if ($state['consec_losses'] >= 3) {
                $state['paused_until'] = time() + 2 * 3600;
                $state['consec_losses'] = 0;
                tg_send($cfg, "😤 <b>ANTI-TILT</b>: 3 zarar ketma-ket — bot 2 soat dam oladi");
            }
        } else {
            $state['consec_losses'] = 0;
        }
        tg_send($cfg, ($profit >= 0 ? "✅" : "❌") . " #{$pid} {$info['symbol']} yopildi: " .
            ($profit >= 0 ? '+' : '') . $profit . '$ | Bugun: ' . round($daily_pnl, 2) .
            '$ | Balans: ' . round($balance, 2) . '$');
        log_line($dir, "closed #$pid {$info['symbol']} pnl=$profit");
    }
}
$state['last_equity'] = $equity;

$state['pnl'] = round($daily_pnl, 2);
$state['balance'] = $balance;
$state['equity'] = round($equity, 2);
$state['tier'] = $tier['name'];
$state['last_cycle'] = time();
state_save($dir . '/state.json', $state);
log_line($dir, "sikl ok: bal=$balance pos=" . count($positions) .
    ($can_trade ? '' : " [$why]"));
flock($lockF, LOCK_UN);
exit(0);

// ═══════════════ Telegram buyruqlari ═══════════════
function handle_cmd($cfg, &$state, $positions, $acc, $tier, $text) {
    $cmd = strtolower(strtok($text, ' '));
    $arg = trim(substr($text, strlen($cmd)));

    switch ($cmd) {
        case '/start':
        case '/help':
            tg_send($cfg,
                "🤖 <b>TORTINMANG.UZ PHP Lite buyruqlari</b>\n\n" .
                "/status — hisob holati\n" .
                "/positions — ochiq savdolar\n" .
                "/closeall — hammasini yopish\n" .
                "/close ID — bitta savdoni yopish\n" .
                "/pause — savdoni to'xtatish\n" .
                "/resume — davom ettirish\n" .
                "/stats — statistika (WR/PF)\n" .
                "/history — oxirgi savdolar\n" .
                "/risk — risk qoidalari");
            break;

        case '/status':
            $pnl = floatval($acc['equity'] ?? 0) - floatval($state['daily_start'] ?? $acc['balance'] ?? 0);
            tg_send($cfg,
                "📊 <b>HOLAT</b> | {$tier['name']}\n" .
                "💰 Balans: $" . round(floatval($acc['balance'] ?? 0), 2) .
                " | Equity: $" . round(floatval($acc['equity'] ?? 0), 2) . "\n" .
                "📈 Bugungi P&L: " . round($pnl, 2) . '$' . "\n" .
                "📂 Ochiq: " . count($positions) . " | Savdolar: " . ($state['trades'] ?? 0) . "\n" .
                ($state['paused'] ? "⏸️ PAUZA da" : "🟢 Aktiv"));
            break;

        case '/positions':
            if (!$positions) { tg_send($cfg, "📭 Ochiq pozitsiya yo'q"); break; }
            $lines = [];
            foreach ($positions as $p) {
                $lines[] = '#' . $p['id'] . ' ' . $p['symbol'] . ' ' .
                    ((stripos($p['type'] ?? '', 'BUY') !== false) ? 'BUY' : 'SELL') . ' ' .
                    $p['volume'] . ' @' . round(floatval($p['openPrice'] ?? 0), 3) .
                    ' P&L:' . round(floatval($p['profit'] ?? $p['unrealizedProfit'] ?? 0), 2);
            }
            tg_send($cfg, "📂 <b>Ochiq pozitsiyalar</b>\n" . implode("\n", $lines));
            break;

        case '/closeall':
            $n = 0;
            foreach ($positions as $p) {
                ma_close($cfg, $p['id']);
                unset($state['pos'][(string)$p['id']]);
                $n++;
            }
            tg_send($cfg, "✅ $n ta pozitsiya yopildi");
            break;

        case '/close':
            $found = false;
            foreach ($positions as $p) {
                if ((string)$p['id'] === $arg) { ma_close($cfg, $p['id']); $found = true; break; }
            }
            tg_send($cfg, $found ? "✅ #$arg yopildi" : "❌ #$arg topilmadi");
            break;

        case '/pause':
            $state['paused'] = true;
            tg_send($cfg, "⏸️ Savdolar to'xtatildi. /resume bilan davom.");
            break;

        case '/resume':
            $state['paused'] = false;
            tg_send($cfg, "🟢 Savdolar qayta yoqildi.");
            break;

        case '/stats':
            $s = journal_stats(__DIR__);
            tg_send($cfg,
                "📈 <b>STATISTIKA</b> (journal)\n" .
                "Jami: {$s['total']} | ✅ {$s['wins']} | ❌ {$s['losses']}\n" .
                "Winrate: {$s['wr']}% | PF: {$s['pf']}\n" .
                "To'plangan: {$s['net']}\$");
            break;

        case '/history':
            $j = journal_load(__DIR__);
            $last = array_slice($j, -5);
            if (!$last) { tg_send($cfg, "📭 Jurnal bo'sh"); break; }
            $lines = [];
            foreach (array_reverse($last) as $t) {
                $lines[] = ($t['profit'] >= 0 ? '✅' : '❌') . ' ' . $t['symbol'] . ' ' .
                    ($t['side'] ?? '') . ' ' . ($t['profit'] >= 0 ? '+' : '') . $t['profit'] .
                    '$ | ' . date('d.m H:i', $t['ts'] ?? time());
            }
            tg_send($cfg, "📒 <b>Oxirgi savdolar</b>\n" . implode("\n", $lines));
            break;

        case '/risk':
            tg_send($cfg,
                "🛡️ <b>Risk qoidalari</b>\n" .
                "• Savdo riski: ETH {$cfg['RISK_PCT']['ETHUSD']}% / XAU {$cfg['RISK_PCT']['XAUUSD']}%\n" .
                "• Min lot risk cap: {$cfg['MAX_ACTUAL_RISK_PCT']}%\n" .
                "• Kunlik zarar: −{$cfg['DAILY_LOSS_PCT']}% | Haftalik: −" . ($cfg['WEEKLY_LOSS_PCT'] ?? 7) . "%\n" .
                "• Kunlik maqsad: +{$cfg['DAILY_TARGET_USD']}$\n" .
                "• Max " . $cfg['MAX_POSITIONS'] . " pozitsiya, " . $cfg['MAX_TRADES_DAY'] . " savdo/kun");
            break;
    }
}
