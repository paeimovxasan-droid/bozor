"""
TORTINMANG.UZ — Asosiy ishga tushirish skripti
Libertex (ForexClub) Edition

Foydalanish:
    python run.py           # Bot + API server birga
    python run.py --bot     # Faqat trading bot (Libertex MT5)
    python run.py --api     # Faqat FastAPI server
    python run.py --test    # Tizim tekshiruvi (Libertex)
"""

import sys
import os
import asyncio
import argparse

# Encoding fix for Windows — reconfigure() xavfsiz (yangi obyekt yaratmaydi,
# eski TextIOWrapper yopilish xatosini keltirib chiqarmaydi)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def check_env():
    """
    Muhit o'zgaruvchilarini tekshirish — Libertex.
    Endi qat'iy to'xtatmaydi: MT5/Telegram yo'q bo'lsa bot demo/paper
    rejimda davom etadi, DeepSeek AI esa kalit bor bo'lsa ishlaydi.
    """
    from dotenv import load_dotenv
    load_dotenv()

    base = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(base, ".env")
    env_exists = os.path.exists(env_file)

    if env_exists:
        # UTF-16 tekshiruvi (PowerShell muammosi)
        try:
            with open(env_file, "rb") as f:
                head = f.read(2)
            if head in (b"\xff\xfe", b"\xfe\xff"):
                print("  [!!] .env fayl UTF-16 kodlanishda (PowerShell yozgan).")
                print("       Bot avtomatik o'qiydi, lekin Notepad da UTF-8 qilib")
                print("       qayta saqlagan ma'qul (Save As → Encoding: UTF-8).")
            else:
                print(f"  [OK] .env topildi: {env_file}")
        except Exception:
            print(f"  [OK] .env topildi: {env_file}")
    else:
        print("  [!!] .env fayli topilmadi!")
        for cand in (".env.txt", "env.txt", "env", ".env.example"):
            if os.path.exists(os.path.join(base, cand)):
                hint = ""
                if cand != ".env.example":
                    hint = f" ← nomini '.env' ga o'zgartiring:  ren {cand} .env"
                print(f"       Diqqat: '{cand}' fayli bor!{hint}")
        print("       Yaratish:  copy .env.example .env   so'ng  notepad .env")

    mt5_keys = {
        "MT5_LOGIN": os.getenv("MT5_LOGIN"),
        "MT5_PASSWORD": os.getenv("MT5_PASSWORD"),
        "MT5_SERVER": os.getenv("MT5_SERVER"),
    }
    tg_keys = {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    }
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")

    print("=" * 55)
    print("  TORTINMANG.UZ — Libertex Edition — Muhit tekshiruvi")
    print("=" * 55)
    print(f"  Broker: {os.getenv('BROKER', 'ForexClub')} | Server: {os.getenv('MT5_SERVER', '?')}")
    print("=" * 55)



    # MT5
    mt5_ok = all(mt5_keys.values())
    print(f"\n  ── Libertex MT5 {'[OK]' if mt5_ok else '[!!]'}")
    for key, val in mt5_keys.items():
        print(f"     {'[OK]' if val else '[--]'} {key}: {'OK' if val else 'kiritilmagan'}")
    if not mt5_ok:
        print("     → MT5 ulanmasa bot DEMO/PAPER rejimda ishlaydi (savdosiz tahlil)")

    # DeepSeek AI
    if deepseek_key:
        masked = deepseek_key[:6] + "..." + deepseek_key[-4:] if len(deepseek_key) > 12 else "***"
        print(f"\n  ── DeepSeek AI [OK]")
        print(f"     [OK] DEEPSEEK_API_KEY: {masked}")
        print(f"     Model: {os.getenv('DEEPSEEK_MODEL', 'deepseek-flash')} | "
              f"Base: {os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')}")
        if not deepseek_key.strip().startswith("sk-"):
            print("     [!!] DIQQAT: kalit 'sk-' bilan boshlanmaydi — formatni tekshiring!")
    else:
        print(f"\n  ── DeepSeek AI [!!]")
        print("     [--] DEEPSEEK_API_KEY: kiritilmagan")
        print("     → AI tahlil ishlamaydi! Kalit oling: platform.deepseek.com/api_keys")

    # Telegram
    tg_ok = all(tg_keys.values())
    print(f"\n  ── Telegram {'[OK]' if tg_ok else '[--]'}")
    for key, val in tg_keys.items():
        print(f"     {'[OK]' if val else '[--]'} {key}: {'OK' if val else 'kiritilmagan (ixtiyoriy)'}")

    # Binance
    bn = os.getenv("ENABLE_BINANCE", "false").lower() == "true"
    bn_status = "YOQILGAN" if bn else "O'CHIQ (Libertex rejimi)"
    print(f"\n  ── Binance: {bn_status}")

    print("\n  💡 Libertex kabinetida MT5 ma'lumotlarini tekshiring:")
    print("     Libertex → Mening hisoblarim → MT5 → Login/Parol/Server")
    return True  # endi hech qachon bloklanmaydi — demo/paper fallback bor


async def run_system_test():
    """Tizim komponentlarini test qilish — Libertex"""
    from dotenv import load_dotenv
    load_dotenv()

    print("=" * 55)
    print("  TORTINMANG.UZ — Libertex Tizim Testi")
    print("=" * 55)

    errors = []        # kritik muammolar (botni to'xtatadi)
    warnings_list = [] # ogohlantirishlar (demo/paper bilan davom etiladi)

    # 1. Import test
    print("\n[1] Modullar:")
    modules = [
        ("core.config", "AppConfig"),
        ("core.logger", "logger"),
        ("engines.liquidity_engine", "LiquidityEngine"),
        ("engines.smc_engine", "SMCEngine"),
        ("agents.deepseek_agent", "DeepSeekAgent"),
        ("bot.telegram_bot", "TelegramBot"),
        ("engines.market_data", "MultiMarketDataEngine"),
        ("engines.risk_engine", "DynamicRiskEngine"),
        ("engines.execution_engine", "ExecutionEngine"),
        ("engines.whale_monitor", "WhaleMonitor"),
        ("engines.market_scanner", "MultiMarketScanner"),
    ]
    for mod, cls in modules:
        try:
            m = __import__(mod, fromlist=[cls])
            getattr(m, cls)
            print(f"    [OK] {mod}.{cls}")
        except Exception as e:
            print(f"    [!!] {mod}.{cls}: {e}")
            errors.append(f"{mod}: {e}")

    # 2. Telegram test
    print("\n[2] Telegram:")
    try:
        from bot.telegram_bot import TelegramBot
        from core.config import config as _cfg
        bot = TelegramBot()
        if not (_cfg.telegram.token and _cfg.telegram.chat_id):
            print("    [ -] Telegram: token/chat_id kiritilmagan (ixtiyoriy, o'tkazildi)")
            warnings_list.append("Telegram: sozlanmagan (ixtiyoriy)")
        else:
            ok = await bot.send(
                "<b>[TEST]</b> TORTINMANG.UZ Libertex testi... \n"
                "Agar bu xabarni ko'rsangiz, Telegram ishlaydi!"
            )
            print(f"    [{'OK' if ok else '!!'}] Telegram: {'xabar yuborildi' if ok else 'yuborilmadi'}")
            if not ok:
                errors.append("Telegram: xabar yuborilmadi (token/chat_id ni tekshiring)")
    except Exception as e:
        print(f"    [!!] Telegram: {e}")
        errors.append(f"Telegram: {e}")

    # 3. DeepSeek API test — yagona AI provayder
    print("\n[3] DeepSeek AI (yagona AI provayder):")
    try:
        from agents.deepseek_agent import DeepSeekAgent
        ai = DeepSeekAgent()
        if ai.api_key:
            res = await ai.test_connection()
            if res["ok"]:
                print(f"    [OK] DeepSeek ulandi!")
                print(f"         Model: {res['model']} | Javob tezligi: {res['latency_ms']} ms")
                u = res.get("usage", {})
                if u:
                    print(f"         Tokenlar: in={u.get('prompt_tokens')} out={u.get('completion_tokens')}")
                print(f"         {res['message']}")
            else:
                print(f"    [!!] DeepSeek xato: {res['message']}")
                errors.append(f"DeepSeek: {res['message']}")
        else:
            print("    [!!] DEEPSEEK_API_KEY yo'q — .env ga kiriting (platform.deepseek.com/api_keys)")
            errors.append("DeepSeek: API key kiritilmagan")
    except Exception as e:
        print(f"    [!!] DeepSeek: {e}")
        errors.append(f"DeepSeek: {e}")

    # 4. MT5 test — Libertex ASOSIY (lekin muvaffaqiyatsiz bo'lsa ham bot
    #    demo/paper rejimda ishlashda davom etadi — shuning uchun "warnings")
    print("\n[4] Libertex MT5:")
    mt5_ok = False
    try:
        import MetaTrader5 as mt5
        from core.config import config
        # MT5_PATH berilgan bo'lsa
        if config.mt5.path:
            mt5.initialize(path=config.mt5.path)
        else:
            mt5.initialize()
        # Login sinash
        login_ok = mt5.login(login=config.mt5.login, password=config.mt5.password, server=config.mt5.server)
        if login_ok:
            info = mt5.account_info()
            print(f"    [OK] Libertex MT5: {config.mt5.server}")
            print(f"         Login={info.login} | Balans=${info.balance:.2f} {info.currency} | Leverage 1:{info.leverage}")
            # Symbol tekshiruvi
            symbols = [s.name for s in (mt5.symbols_get() or [])[:5]]
            print(f"         Simvollar: {', '.join(symbols)}...")
            mt5.shutdown()
            mt5_ok = True
        else:
            err = mt5.last_error()
            print(f"    [!!] MT5 login xato: {err}")
            print(f"         Server: {config.mt5.server} | Login: {config.mt5.login}")
            print("         Libertex kabinetidagi server nomini 100% aniq ko'chiring!")
            # Fallback serverlar
            print(f"         Fallback: {config.mt5.fallback_servers[:3]}")
            mt5.shutdown()
            warnings_list.append(f"MT5 login: {err} (demo/paper rejimda davom etadi)")
    except ImportError as e:
        print(f"    [!!] MetaTrader5 kutubxonasi topilmadi: {e}")
        print("         Windows: pip install MetaTrader5 (Linux da MT5 ishlamaydi)")
        warnings_list.append(f"MT5 lib: {e} (demo/paper rejimda davom etadi)")
    except Exception as e:
        print(f"    [!!] MT5: {e}")
        warnings_list.append(f"MT5: {e} (demo/paper rejimda davom etadi)")

    # 5. Binance (faqat yoqilgan bo'lsa)
    print("\n[5] Binance (ixtiyoriy):")
    from core.config import config as cfg2
    if cfg2.enable_binance:
        try:
            from engines.binance_executor import BinanceExecutor
            be = BinanceExecutor()
            acct = await be.get_account_info()
            bal = acct.get("balance", 0)
            src = acct.get("source", "?")
            print(f"    [OK] Binance {src} | Balans: ${bal:.2f} USDT")
        except Exception as e:
            print(f"    [!!] Binance: {e}")
            errors.append(f"Binance: {e}")
    else:
        print("    [ -] O'CHIQ (Libertex rejimi — kerak emas)")

    print("\n" + "=" * 55)
    if mt5_ok:
        mode = f"LIBERTEX MT5 ({config.mt5.broker})"
    elif cfg2.enable_binance:
        mode = "BINANCE MODE (fallback)"
    else:
        mode = "DEMO (MT5 ulanmadi)"
    print(f"[>>] Aktiv rejim: {mode}")
    if errors:
        print(f"[!!] {len(errors)} kritik muammo topildi:")
        for e in errors:
            print(f"     - {e}")
    if warnings_list:
        print(f"[~] {len(warnings_list)} ogohlantirish (demo/paper bilan davom etadi):")
        for w in warnings_list:
            print(f"     - {w}")
        if not mt5_ok:
            print("\n💡 Libertex MT5 ni sozlash:")
            print("   1. Libertex kabinetiga kiring → MT5 hisob → Login/Parol/Server ni ko'chiring")
            print("   2. .env da MT5_SERVER ni aynan kabinetdagidek yozing")
            print("   3. MT5 terminal o'rnatilganligini tekshiring (Windows)")
    if not errors:
        if mt5_ok:
            print("[OK] Barcha testlar o'tdi! Libertex MT5 ishga tayyor. 🚀")
        else:
            print("[OK] Kritik testlar o'tdi! Bot demo/paper rejimda ishlaydi. 🚀")
    print("=" * 55)
    return len(errors) == 0


async def run_bot_only():
    """Faqat trading bot — Libertex"""
    import signal
    from dotenv import load_dotenv
    load_dotenv()
    from core.orchestrator import UltraOrchestrator
    bot = UltraOrchestrator()

    loop = asyncio.get_event_loop()

    def _shutdown_handler():
        print("\n[!!] Signal qabul qilindi — bot to'xtatilmoqda...")
        loop.create_task(bot.stop_async())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown_handler)
        except Exception:
            pass

    await bot.start()


async def run_api_and_bot():
    """Bot + FastAPI server parallel — bitta umumiy orchestrator"""
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv()

    import api.main as api_main
    from core.orchestrator import UltraOrchestrator

    bot = UltraOrchestrator()
    # Yagona orchestrator ni API ga injekt qilamiz — ikkinchi nusxa yaratilmaydi,
    # qo'shaloq MT5-login / ikki barobar skanerlash oldini oladi.
    api_main.orchestrator = bot

    uconfig = uvicorn.Config(
        api_main.app, host="0.0.0.0", port=int(os.getenv("API_PORT", 8000)),
        log_level="warning"
    )
    server = uvicorn.Server(uconfig)

    await asyncio.gather(
        bot.start(),
        server.serve()
    )


def main():
    parser = argparse.ArgumentParser(description="TORTINMANG.UZ — Libertex Edition")
    parser.add_argument("--bot", action="store_true", help="Faqat trading bot (Libertex MT5)")
    parser.add_argument("--api", action="store_true", help="Faqat API server")
    parser.add_argument("--test", action="store_true", help="Tizim testi (Libertex)")
    parser.add_argument("--backtest", action="store_true",
                        help="Tarixiy ma'lumotda strategiya testi (qo'shimcha: --days N --symbols X)")
    if "--backtest" in sys.argv:
        args, _ = parser.parse_known_args()   # qolgan arglar backtest ga o'tadi
    else:
        args = parser.parse_args()

    if args.backtest:
        # `python run.py --backtest --days 60` → backtest.py ga o'tkazish
        sys.argv = [a for a in sys.argv if a != "--backtest"]
        import backtest
        backtest.main()
        return

    if not check_env():
        print("\n[!!] Muhim o'zgaruvchilar topilmadi! .env faylini tekshiring.")
        if not args.test:
            sys.exit(1)

    if args.test:
        ok = asyncio.run(run_system_test())
        sys.exit(0 if ok else 1)

    elif args.bot:
        print("\n[>>] Libertex MT5 Trading Bot ishga tushmoqda...")
        asyncio.run(run_bot_only())

    elif args.api:
        print("\n[>>] Faqat FastAPI server ishga tushmoqda...")
        import uvicorn
        from dotenv import load_dotenv
        load_dotenv()
        uvicorn.run("api.main:app", host="0.0.0.0",
                    port=int(os.getenv("API_PORT", 8000)), reload=False)

    else:
        print("\n[>>] Bot (Libertex) + API server birga ishga tushmoqda...")
        asyncio.run(run_api_and_bot())


if __name__ == "__main__":
    main()
