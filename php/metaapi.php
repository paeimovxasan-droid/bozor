<?php
/**
 * TORTINMANG.UZ PHP Lite — MetaApi ko'prigi (Libertex MT5)
 * Docs: metaapi.cloud/docs/client/restApi
 *
 * MetaApi bulutida sizning Libertex MT5 hisobingiz ulangan bo'ladi;
 * PHP har qanday hostingdan REST orqali savdo yuboradi.
 */

define('METAAPI_CLIENT', 'https://mt-client-api-v1.new-york.agiliumtrade.ai');
define('METAAPI_MARKET', 'https://mt-market-data-client-api-v1.new-york.agiliumtrade.ai');

function ma_candles($cfg, $symbol, $tf = '15m', $limit = 200) {
    $url = METAAPI_MARKET . '/users/current/accounts/' . $cfg['META_ACCOUNT_ID'] .
        '/historical-market-data/symbols/' . $symbol .
        '/timeframes/' . $tf . '/candles?limit=' . $limit;
    $r = http_json('GET', $url, $cfg['META_API_TOKEN']);
    return is_array($r['data'] ?? null) ? $r['data'] : null;
}

function ma_account($cfg) {
    $url = METAAPI_CLIENT . '/users/current/accounts/' . $cfg['META_ACCOUNT_ID'] . '/account';
    $r = http_json('GET', $url, $cfg['META_API_TOKEN']);
    return $r['data'] ?? null;
}

function ma_positions($cfg) {
    $url = METAAPI_CLIENT . '/users/current/accounts/' . $cfg['META_ACCOUNT_ID'] . '/positions';
    $r = http_json('GET', $url, $cfg['META_API_TOKEN']);
    return is_array($r['data'] ?? null) ? $r['data'] : [];
}

function ma_trade($cfg, $body) {
    $url = METAAPI_CLIENT . '/users/current/accounts/' . $cfg['META_ACCOUNT_ID'] . '/trade';
    $r = http_json('POST', $url, $cfg['META_API_TOKEN'], $body);
    return $r;
}

function ma_open($cfg, $symbol, $side, $volume, $sl, $tp) {
    return ma_trade($cfg, [
        'actionType' => ($side === 'BUY') ? 'ORDER_TYPE_BUY' : 'ORDER_TYPE_SELL',
        'symbol' => $symbol,
        'volume' => $volume,
        'stopLoss' => $sl,
        'takeProfit' => $tp,
        'comment' => 'Tortinmang PHP',
    ]);
}

function ma_close($cfg, $positionId) {
    return ma_trade($cfg, [
        'actionType' => 'POSITION_CLOSE_ID',
        'positionId' => (string)$positionId,
    ]);
}

function ma_partial($cfg, $positionId, $volume) {
    return ma_trade($cfg, [
        'actionType' => 'POSITION_PARTIAL',
        'positionId' => (string)$positionId,
        'volume' => $volume,
    ]);
}

function ma_modify($cfg, $positionId, $sl = null, $tp = null) {
    $body = ['actionType' => 'POSITION_MODIFY', 'positionId' => (string)$positionId];
    if ($sl !== null) $body['stopLoss'] = $sl;
    if ($tp !== null) $body['takeProfit'] = $tp;
    return ma_trade($cfg, $body);
}
