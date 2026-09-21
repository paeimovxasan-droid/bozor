<?php
/**
 * TORTINMANG.UZ PHP Lite — yordamchi funksiyalar (v3: MySQL qatlami)
 */
require_once __DIR__ . '/db.php';

// ── State: MySQL bor bo'lsa unda, yo'q bo'lsa json faylda ──────
function state_load($path, $cfg = null) {
    if ($cfg) {
        $db = db_state_load($cfg);
        if ($db !== null) return $db;
    }
    if (!is_file($path)) return [];
    $d = json_decode(@file_get_contents($path), true);
    return is_array($d) ? $d : [];
}

function state_save($path, $data, $cfg = null) {
    if ($cfg && db_state_save($cfg, $data)) {
        @file_put_contents($path, json_encode($data, JSON_UNESCAPED_UNICODE)); // zaxira
        return;
    }
    $tmp = $path . '.tmp';
    @file_put_contents($tmp, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    @rename($tmp, $path);   // atomar yozish
}

// ── HTTP (curl) ────────────────────────────────────────────────
function http_json($method, $url, $token = null, $body = null, $timeout = 20) {
    $ch = curl_init($url);
    $headers = ['Accept: application/json'];
    if ($token) $headers[] = 'auth-token: ' . $token;
    if ($body !== null) {
        $headers[] = 'Content-Type: application/json';
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
    } elseif ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
    }
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, $timeout);
    $raw = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    $err = curl_error($ch);
    curl_close($ch);
    if ($raw === false) return ['error' => $err, 'code' => 0];
    return ['data' => json_decode($raw, true), 'code' => $code, 'raw' => $raw];
}

// ── Indikatorlar ───────────────────────────────────────────────
function ema_series($vals, $period) {
    $k = 2 / ($period + 1);
    $prev = null;
    $out = [];
    foreach ($vals as $v) {
        $prev = ($prev === null) ? $v : $v * $k + $prev * (1 - $k);
        $out[] = $prev;
    }
    return $out;
}

function ema_last($vals, $period) {
    $s = ema_series($vals, $period);
    return end($s);
}

function rsi_last($closes, $period = 14) {
    $n = count($closes);
    if ($n < $period + 1) return 50.0;
    $gain = 0; $loss = 0;
    for ($i = 1; $i <= $period; $i++) {
        $d = $closes[$i] - $closes[$i - 1];
        if ($d > 0) $gain += $d; else $loss -= $d;
    }
    $avgG = $gain / $period; $avgL = $loss / $period;
    for ($i = $period + 1; $i < $n; $i++) {
        $d = $closes[$i] - $closes[$i - 1];
        $avgG = ($avgG * ($period - 1) + max($d, 0)) / $period;
        $avgL = ($avgL * ($period - 1) + max(-$d, 0)) / $period;
    }
    if ($avgL == 0) return 100.0;
    return 100 - (100 / (1 + $avgG / $avgL));
}

function atr_last($h, $l, $c, $period = 14) {
    $n = count($c);
    if ($n < $period + 1) return 0.0;
    $trs = [];
    for ($i = 1; $i < $n; $i++) {
        $trs[] = max($h[$i] - $l[$i], abs($h[$i] - $c[$i - 1]), abs($l[$i] - $c[$i - 1]));
    }
    $atr = array_sum(array_slice($trs, 0, $period)) / $period;
    for ($i = $period; $i < count($trs); $i++) {
        $atr = ($atr * ($period - 1) + $trs[$i]) / $period;
    }
    return $atr;
}

// ── Pog'ona (balansga qarab lot/risk qalqoni) ──────────────────
function tier_for($balance) {
    if ($balance >= 5000) return ['name' => 'DIAMOND', 'lot_max' => 1.0,  'risk_cap' => 0.5];
    if ($balance >= 2000) return ['name' => 'PLATINUM','lot_max' => 0.5,  'risk_cap' => 0.75];
    if ($balance >= 500)  return ['name' => 'GOLD',    'lot_max' => 0.3,  'risk_cap' => 1.0];
    if ($balance >= 100)  return ['name' => 'SILVER',  'lot_max' => 0.10, 'risk_cap' => 1.5];
    return ['name' => 'BRONZE', 'lot_max' => 0.03, 'risk_cap' => 2.0];
}

// ── Telegram ───────────────────────────────────────────────────
function tg_send($cfg, $text) {
    if (empty($cfg['TELEGRAM_BOT_TOKEN']) || empty($cfg['TELEGRAM_CHAT_ID'])) return false;
    $url = 'https://api.telegram.org/bot' . $cfg['TELEGRAM_BOT_TOKEN'] . '/sendMessage';
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => http_build_query([
            'chat_id' => $cfg['TELEGRAM_CHAT_ID'],
            'text' => $text,
            'parse_mode' => 'HTML',
            'disable_web_page_preview' => true,
        ]),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
    ]);
    $raw = curl_exec($ch);
    curl_close($ch);
    return $raw !== false;
}

function tg_get_updates($cfg, $offset) {
    if (empty($cfg['TELEGRAM_BOT_TOKEN'])) return [];
    $url = 'https://api.telegram.org/bot' . $cfg['TELEGRAM_BOT_TOKEN'] .
        '/getUpdates?timeout=0&offset=' . (int)$offset;
    $ch = curl_init($url);
    curl_setopt_array($ch, [CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 8]);
    $raw = curl_exec($ch);
    curl_close($ch);
    $d = json_decode($raw, true);
    return is_array($d['result'] ?? null) ? $d['result'] : [];
}

// ── DeepSeek AI veto/sharh ─────────────────────────────────────
function deepseek_review($cfg, $prompt) {
    if (empty($cfg['DEEPSEEK_API_KEY'])) return ['ok' => true, 'wait' => false, 'reason' => ''];
    $ch = curl_init('https://api.deepseek.com/chat/completions');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'Authorization: Bearer ' . $cfg['DEEPSEEK_API_KEY'],
        ],
        CURLOPT_POSTFIELDS => json_encode([
            'model' => 'deepseek-flash',
            'messages' => [['role' => 'user', 'content' =>
                $prompt . ' Javob: faqat JSON {"vote":"YES|NO|WAIT","reason":"qisqa sabab"}']],
            'max_tokens' => 100,
            'response_format' => ['type' => 'json_object'],
        ]),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 15,
    ]);
    $raw = curl_exec($ch);
    curl_close($ch);
    $d = json_decode($raw, true);
    $txt = $d['choices'][0]['message']['content'] ?? '';
    $j = json_decode($txt, true);
    if (!$j) return ['ok' => true, 'wait' => false, 'reason' => ''];
    $vote = strtoupper($j['vote'] ?? 'YES');
    return ['ok' => $vote !== 'NO', 'wait' => $vote === 'WAIT',
            'reason' => mb_substr($j['reason'] ?? '', 0, 120)];
}

// ── Log ────────────────────────────────────────────────────────
function log_line($dir, $msg) {
    $line = date('Y-m-d H:i:s') . ' ' . $msg . PHP_EOL;
    @file_put_contents($dir . '/lite.log', $line, FILE_APPEND);
    if (is_file($dir . '/lite.log') && filesize($dir . '/lite.log') > 500000) {
        @rename($dir . '/lite.log', $dir . '/lite.old.log');
    }
}

// ── Sessiya filtri ─────────────────────────────────────────────
function session_ok($cfg) {
    $h = (int)date('G');   // server vaqti — config da sozlanadi
    $from = (int)$cfg['SESSION_FROM'];
    $to   = (int)$cfg['SESSION_TO'];
    if ($from < $to) return $h >= $from && $h < $to;
    return $h >= $from || $h < $to;
}

// ── Yangilik blackout (NFP / CPI atrofi) ───────────────────────
function news_blackout() {
    $now = time();
    $h = (int)date('G'); $m = (int)date('i');
    $day = (int)date('j'); $dow = (int)date('N');   // N: 5 = juma
    $ev = null;
    if ($dow === 5 && $day <= 7) $ev = 'NFP (birinchi juma)';
    if ($day >= 10 && $day <= 15) $ev = 'CPI (oy o\'rtasi)';
    if ($ev === null) return [false, ''];
    $ev_min = 17 * 60 + 30;
    $now_min = $h * 60 + $m;
    if (abs($now_min - $ev_min) <= 60) return [true, $ev];
    return [false, ''];
}

// ── Savdo jurnali (MySQL bor bo'lsa unda, yo'q bo'lsa json) ────
function journal_add($dir, $rec, $cfg = null) {
    if ($cfg && db_journal_add($cfg, $rec)) return;
    $j = journal_load($dir, $cfg);
    $j[] = $rec;
    if (count($j) > 300) $j = array_slice($j, -300);
    @file_put_contents($dir . '/journal.json',
        json_encode($j, JSON_UNESCAPED_UNICODE));
}

function journal_load($dir, $cfg = null) {
    if ($cfg) {
        $db = db_journal_load($cfg);
        if ($db !== null) return $db;
    }
    $d = json_decode(@file_get_contents($dir . '/journal.json'), true);
    return is_array($d) ? $d : [];
}

function journal_stats($dir, $symbol = null, $cfg = null) {
    $j = journal_load($dir, $cfg);
    $wins = 0; $losses = 0; $gw = 0.0; $gl = 0.0;
    foreach ($j as $t) {
        if ($symbol && ($t['symbol'] ?? '') !== $symbol) continue;
        $p = floatval($t['profit'] ?? 0);
        if ($p > 0) { $wins++; $gw += $p; } else { $losses++; $gl += -$p; }
    }
    $total = $wins + $losses;
    return [
        'total' => $total, 'wins' => $wins, 'losses' => $losses,
        'wr' => $total ? round($wins / $total * 100, 1) : 0,
        'pf' => $gl > 0 ? round($gw / $gl, 2) : ($gw > 0 ? 99 : 0),
        'net' => round($gw - $gl, 2),
    ];
}

// ── DeepSeek erkin matn (hisobot/sharh uchun) ──────────────────
function deepseek_report($cfg, $prompt) {
    if (empty($cfg['DEEPSEEK_API_KEY'])) return '';
    $ch = curl_init('https://api.deepseek.com/chat/completions');
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'Authorization: Bearer ' . $cfg['DEEPSEEK_API_KEY'],
        ],
        CURLOPT_POSTFIELDS => json_encode([
            'model' => 'deepseek-flash',
            'messages' => [['role' => 'user', 'content' => $prompt]],
            'max_tokens' => 200,
        ]),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 15,
    ]);
    $raw = curl_exec($ch);
    curl_close($ch);
    $d = json_decode($raw, true);
    return mb_substr(trim($d['choices'][0]['message']['content'] ?? ''), 0, 400);
}

