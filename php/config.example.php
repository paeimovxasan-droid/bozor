<?php
/**
 * TORTINMANG.UZ PHP Lite — sozlamalar
 * ===================================
 * Bu faylni `config.php` nomi bilan nusxalang va to'ldiring:
 *     cp config.example.php config.php
 *
 * MetaApi: https://app.metaapi.cloud da ro'yxatdan o'ting,
 * Libertex MT5 hisobingizni qo'shing (login/parol/server),
 * so'ng Token va Account ID ni shu yerga yozing.
 */
return [
    // ── MetaApi (Libertex MT5 ko'prigi) ─────────────────────────
    'META_API_TOKEN'  => '',   // app.metaapi.cloud/token sahifasidan
    'META_ACCOUNT_ID' => '',   // admin.php o'zi yaratadi yoki qo'lda kiriting

    // ── Admin panel va HTTP cron ─────────────────────────────────
    'ADMIN_PASS' => 'admin123', // admin.php kirish paroli (o'zgartiring!)
    'CRON_KEY'   => '',          // cycle.php?key=... HTTP cron uchun kalit

    // ── DeepSeek AI (ixtiyoriy, lekin tavsiya) ──────────────────
    'DEEPSEEK_API_KEY' => '',  // sk-...

    // ── Telegram (xabarlar uchun) ───────────────────────────────
    'TELEGRAM_BOT_TOKEN' => '',
    'TELEGRAM_CHAT_ID'   => '',

    // ── Savdo parametrlari (BRONZE pog'ona mantiqi) ─────────────
    'SYMBOLS'   => ['XAUUSD', 'ETHUSD'],
    'RISK_PCT'  => ['XAUUSD' => 1.8, 'ETHUSD' => 1.0],   // savdo riski %
    'LOT_MIN'   => 0.01,
    'LOT_MAX'   => 0.03,
    'MAX_ACTUAL_RISK_PCT' => 3.0,   // min lot risk shundan oshsa savdo yo'q
    'CONTRACT'  => ['XAUUSD' => 100, 'ETHUSD' => 1],

    // ── Risk qalqonlari ─────────────────────────────────────────
    'DAILY_LOSS_PCT'   => 3.0,   // kunlik zarar limiti %
    'WEEKLY_LOSS_PCT'  => 7.0,   // haftalik zarar limiti %
    'DAILY_TARGET_USD' => 5.0,   // kunlik foyda maqsadi $ (yig'ilsa kun yopiladi)
    'MAX_POSITIONS'    => 2,
    'MAX_TRADES_DAY'   => 6,
    'MIN_CONFIDENCE'   => 55,    // signal ishonch chegarasi

    // ── Savdo oynasi (soat) va vaqt mintaqasi ───────────────────
    'SESSION_FROM' => 14,
    'SESSION_TO'   => 24,
    'TIMEZONE'     => 'Asia/Tashkent',
];
