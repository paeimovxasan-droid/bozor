-- TORTINMANG.UZ PHP Lite — MySQL sxemasi (ISPmanager/phpMyAdmin da qo'lda import uchun)
-- Odatda install.php buni AVTOMATIK bajaradi; qo'lda kerak bo'lsa:

CREATE TABLE IF NOT EXISTS tm_state (
    k VARCHAR(64) NOT NULL PRIMARY KEY,
    v MEDIUMTEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS tm_journal (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    ts INT UNSIGNED NOT NULL,
    pid VARCHAR(64) NOT NULL DEFAULT '',
    symbol VARCHAR(32) NOT NULL DEFAULT '',
    side VARCHAR(8) NOT NULL DEFAULT '',
    profit DECIMAL(12,2) NOT NULL DEFAULT 0,
    tier VARCHAR(16) NOT NULL DEFAULT '',
    INDEX idx_symbol (symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
