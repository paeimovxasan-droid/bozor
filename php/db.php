<?php
/**
 * TORTINMANG.UZ PHP Lite — MySQL qatlami (ISPmanager/shared hosting)
 * ================================================================
 * config da DB_* to'ldirilgan bo'lsa state va jurnal MySQL da
 * saqlanadi (ishonchli), aks holda json fayllarda (fallback).
 * PHP 8.4 + PDO mysql.
 */

function db_conn($cfg) {
    static $pdo = null;
    static $tried = false;
    if ($tried) return $pdo;
    $tried = true;
    if (empty($cfg['DB_HOST']) || empty($cfg['DB_NAME'])) return null;
    try {
        $pdo = new PDO(
            'mysql:host=' . $cfg['DB_HOST'] . ';dbname=' . $cfg['DB_NAME'] . ';charset=utf8mb4',
            $cfg['DB_USER'] ?? '', $cfg['DB_PASS'] ?? '',
            [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
             PDO::ATTR_TIMEOUT => 5]
        );
    } catch (Exception $e) {
        $pdo = null;
    }
    return $pdo;
}

function db_schema($pdo) {
    $pdo->exec("CREATE TABLE IF NOT EXISTS tm_state (
        k VARCHAR(64) NOT NULL PRIMARY KEY,
        v MEDIUMTEXT NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    $pdo->exec("CREATE TABLE IF NOT EXISTS tm_journal (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        ts INT UNSIGNED NOT NULL,
        pid VARCHAR(64) NOT NULL DEFAULT '',
        symbol VARCHAR(32) NOT NULL DEFAULT '',
        side VARCHAR(8) NOT NULL DEFAULT '',
        profit DECIMAL(12,2) NOT NULL DEFAULT 0,
        tier VARCHAR(16) NOT NULL DEFAULT '',
        INDEX idx_symbol (symbol)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
}

// ── state (kalit-qiymat) ───────────────────────────────────────
function db_state_load($cfg) {
    $pdo = db_conn($cfg);
    if (!$pdo) return null;
    try {
        $st = $pdo->query("SELECT k, v FROM tm_state")->fetchAll(PDO::FETCH_KEY_PAIR);
        $out = [];
        foreach ($st as $k => $v) {
            $out[$k] = json_decode($v, true);
        }
        return $out;
    } catch (Exception $e) {
        return null;
    }
}

function db_state_save($cfg, $data) {
    $pdo = db_conn($cfg);
    if (!$pdo) return false;
    try {
        $sql = "INSERT INTO tm_state (k, v) VALUES (?, ?)
                ON DUPLICATE KEY UPDATE v = VALUES(v)";
        $sth = $pdo->prepare($sql);
        foreach ($data as $k => $v) {
            $sth->execute([(string)$k, json_encode($v, JSON_UNESCAPED_UNICODE)]);
        }
        return true;
    } catch (Exception $e) {
        return false;
    }
}

// ── jurnal ─────────────────────────────────────────────────────
function db_journal_add($cfg, $rec) {
    $pdo = db_conn($cfg);
    if (!$pdo) return false;
    try {
        $pdo->prepare(
            "INSERT INTO tm_journal (ts, pid, symbol, side, profit, tier)
             VALUES (?, ?, ?, ?, ?, ?)")
            ->execute([
                time(), (string)($rec['id'] ?? ''), (string)($rec['symbol'] ?? ''),
                (string)($rec['side'] ?? ''), floatval($rec['profit'] ?? 0),
                (string)($rec['tier'] ?? ''),
            ]);
        return true;
    } catch (Exception $e) {
        return false;
    }
}

function db_journal_load($cfg, $limit = 300) {
    $pdo = db_conn($cfg);
    if (!$pdo) return null;
    try {
        $rows = $pdo->query(
            "SELECT ts, pid AS id, symbol, side, profit, tier
             FROM tm_journal ORDER BY id DESC LIMIT " . (int)$limit)
            ->fetchAll(PDO::FETCH_ASSOC);
        return array_reverse(array_map(function ($r) {
            $r['profit'] = floatval($r['profit']);
            $r['ts'] = intval($r['ts']);
            return $r;
        }, $rows));
    } catch (Exception $e) {
        return null;
    }
}
