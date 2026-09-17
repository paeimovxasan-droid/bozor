"""
TORTINMANG.UZ v2.0 — ENG OSON ishga tushirish
============================================
    python run_v2.py              # botni darhol ishga tushiradi (hech qanday flag kerak emas!)
    python run_v2.py --test       # tizim self-test (10 sekund)
    python run_v2.py --check      # muhit tekshiruvi (.env, MT5, AI, Telegram)
    python run_v2.py --backtest   # tarixiy test (--days N --symbols X)
"""
import sys
import os

# Encoding fix for Windows — reconfigure() xavfsiz (yangi obyekt yaratmaydi)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def main():
    argv = sys.argv[1:]

    # ── --backtest: argumentlarni backtest.py ga uzatish ─────────
    if "--backtest" in argv:
        sys.argv = [a for a in sys.argv if a != "--backtest"]
        import backtest
        backtest.main()
        return

    # ── --check: muhit tekshiruvi ────────────────────────────────
    if "--check" in argv:
        from run import check_env
        check_env()
        return

    # ── --test: self-test ────────────────────────────────────────
    if "--test" in argv:
        import asyncio
        from v2.selftest import run_selftest
        ok = asyncio.run(run_selftest())
        sys.exit(0 if ok else 1)

    # ── Default: BOTNI ISHGA TUSHIRISH ───────────────────────────
    from run import check_env
    check_env()

    import asyncio
    from v2.bot import UltraBotV2

    banner = (
        "\n"
        "╔════════════════════════════════════════════════╗\n"
        "║         🤖  TORTINMANG.UZ v2.0  🤖              ║\n"
        "║     Pog'ona tizimi • AI Kengash • Risk Desk     ║\n"
        "║        Mustaqil savdo — har daqiqa tahlil       ║\n"
        "╚════════════════════════════════════════════════╝\n"
    )
    print(banner)

    bot = UltraBotV2()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n✅ Bot to'xtatildi. Xayr!")


if __name__ == "__main__":
    main()
