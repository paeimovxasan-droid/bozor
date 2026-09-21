"""
TORTINMANG.UZ — DeepSeek API alohida testi
=========================================
DeepSeek API kalitingiz va sozlamalaringizni tekshiradi.
Bu skript loyihadan mustaqil, faqat DeepSeek bilan ishlaydi.

Foydalanish:
    python test_deepseek.py                 # oddiy test
    python test_deepseek.py --model deepseek-v4-pro   # boshqa model
    python test_deepseek.py --reasoning high          # thinking rejim

Rasmiy docs: https://api-docs.deepseek.com
"""
import sys
import os
import asyncio
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


async def main():
    parser = argparse.ArgumentParser(description="DeepSeek API testi")
    parser.add_argument("--model", help="Model nomi (deepseek-flash / deepseek-v4-pro)")
    parser.add_argument("--reasoning", choices=["none", "low", "high", "max"],
                        help="Thinking rejimi (none=tez/arzon)")
    parser.add_argument("--ask", help="O'zingizning savolingiz bilan sinash")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    # CLI argumentlar .env dan ustun
    if args.model:
        os.environ["DEEPSEEK_MODEL"] = args.model
    if args.reasoning:
        os.environ["DEEPSEEK_REASONING_EFFORT"] = args.reasoning

    # Config ni qayta yuklash (env o'zgarishlari bilan)
    import importlib
    import core.config as cfg_mod
    importlib.reload(cfg_mod)
    from core.config import config
    import agents.deepseek_agent as ds_mod
    importlib.reload(ds_mod)
    DeepSeekAgent = ds_mod.DeepSeekAgent

    print("=" * 60)
    print("  TORTINMANG.UZ — DeepSeek API Testi")
    print("=" * 60)
    print(f"  Base URL : {config.deepseek.base_url}")
    print(f"  Model    : {config.deepseek.model}")
    print(f"  Reasoning: {config.deepseek.reasoning_effort}")
    print(f"  Timeout  : {config.deepseek.timeout}s")
    key = config.deepseek.api_key
    if key:
        print(f"  API key  : {key[:8]}...{key[-4:]} (len={len(key)})")
    else:
        print("  API key  : [YO'Q]")
    print("=" * 60)

    if not key:
        print("\n[!!] DEEPSEEK_API_KEY topilmadi!")
        print("     1. https://platform.deepseek.com ga kiring")
        print("     2. API Keys → Create new API key")
        print("     3. .env fayliga DEEPSEEK_API_KEY=sk-... qo'shing")
        sys.exit(1)

    ai = DeepSeekAgent()

    # 1) Ulanish testi
    print("\n[1] Ulanish testi (ping)...")
    res = await ai.test_connection()
    if res["ok"]:
        print(f"    [OK] Ulandi! Model={res['model']} | {res['latency_ms']} ms")
        u = res.get("usage", {})
        print(f"         Tokenlar: in={u.get('prompt_tokens')} out={u.get('completion_tokens')}")
    else:
        print(f"    [!!] Xato: {res['message']}")
        sys.exit(1)

    # 2) Trading savol testi
    print("\n[2] Trading chat testi...")
    question = args.ask or "Bugun XAUUSD (oltin) uchun qanday strategiya tavsiya qilasan? Qisqa javob ber."
    print(f"    Savol: {question}")
    answer = await ai.trading_chat(question, context={"balance": 100.0, "positions": []})
    print(f"\n    {answer}")

    # 3) Signal tahlil testi (JSON mode)
    print("\n[3] Signal tahlil testi (JSON mode)...")
    verdict = await ai.analyze_signal({
        "signal": "BUY", "symbol": "BTCUSD", "confidence": 68,
        "entry": 65000, "stop_loss": 64000, "take_profit": 67000,
        "rr_ratio": 2.0, "reason": "SMC BOS + whale accumulation",
    })
    print(f"    Natija: approved={verdict.get('approved')} | {verdict.get('reason')}")

    print("\n" + "=" * 60)
    print(f"  [OK] DeepSeek to'liq ishlayapti! Jami token: "
          f"in={ai.total_prompt_tokens} out={ai.total_completion_tokens}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
