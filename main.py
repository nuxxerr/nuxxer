"""
NUX Agent — Entry Point
Toxic onchain AI agent for Base ecosystem.

Usage:
    python main.py          # CLI mode
    python main.py telegram # Telegram bot mode
"""

import os
import sys
import time
import logging
from agent import NuxAgent
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("nux")

# ── Terminal Colors ──────────────────────────────────────
G  = "\033[92m"
DG = "\033[32m"
CY = "\033[96m"
GR = "\033[90m"
RS = "\033[0m"


def print_splash():
    """Display the NUX ASCII splash screen."""
    os.system("clear" if os.name != "nt" else "cls")

    logo = [
        f"{G}    ███╗  ██╗██╗   ██╗██╗  ██╗{RS}",
        f"{G}    ████╗ ██║██║   ██║╚██╗██╔╝{RS}",
        f"{G}    ██╔██╗██║██║   ██║ ╚███╔╝ {RS}",
        f"{G}    ██║╚████║██║   ██║ ██╔██╗ {RS}",
        f"{G}    ██║ ╚███║╚██████╔╝██╔╝╚██╗{RS}",
        f"{G}    ╚═╝  ╚══╝ ╚═════╝ ╚═╝  ╚═╝{RS}",
    ]

    border = [
        f"{DG}    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RS}",
        f"{DG}    ░░  ╱◥██◤╲  TOXIC ONCHAIN AGENT  ╱◥██◤╲  ░░{RS}",
        f"{DG}    ░░ ◥████████◤  ⚡ BASE NATIVE ⚡ ◥████████◤ ░░{RS}",
        f"{DG}    ░░  ╲██████╱   SGF LAUNCHPAD    ╲██████╱  ░░{RS}",
        f"{DG}    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░{RS}",
    ]

    print()
    for line in border:
        print(line)
        time.sleep(0.04)
    print()
    for line in logo:
        print(line)
        time.sleep(0.04)
    print()
    print(f"{DG}    ─────────────────────────────────────────────{RS}")
    print(f"{G}    ⚡ Toxic. Based. Always right.{RS}   {GR}v{settings.AGENT_VERSION}{RS}")
    print(f"{DG}    ─────────────────────────────────────────────{RS}")
    print()
    time.sleep(0.2)
    print(f"{GR}    commands: 'exit' quit | 'alpha' trending | 'reset' clear{RS}")
    print()


def run_cli():
    """Run NUX in CLI mode."""
    from utils.formatter import print_user, print_nux, print_thinking

    print_splash()
    agent = NuxAgent()

    while True:
        try:
            user_input = input(f"\n{CY}  ❯ {RS}").strip()
        except (KeyboardInterrupt, EOFError):
            print_nux("ngmi. bye tolol.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print_nux("finally. gw udah bosen dari tadi.")
            break

        if user_input.lower() == "reset":
            agent.reset_history()
            print_nux("history cleared. mulai dari awal, semoga lo lebih pinter.")
            continue

        print_user(user_input)
        print_thinking()
        response = agent.process(user_input)
        print_nux(response)


def run_telegram():
    """Run NUX as a Telegram bot."""
    try:
        from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
    except ImportError:
        log.error("Install python-telegram-bot: pip install python-telegram-bot")
        sys.exit(1)

    if not settings.TELEGRAM_BOT_TOKEN:
        log.error("Set TELEGRAM_BOT_TOKEN in .env")
        sys.exit(1)

    agent = NuxAgent()
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", agent.cmd_start))
    app.add_handler(CommandHandler("check", agent.cmd_check))
    app.add_handler(CommandHandler("analyze", agent.cmd_check))
    app.add_handler(CommandHandler("wallet", agent.cmd_wallet))
    app.add_handler(CommandHandler("alpha", agent.cmd_alpha))
    app.add_handler(CommandHandler("help", agent.cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, agent.cmd_chat))

    log.info("⚡ NUX Telegram bot live on Base 🔥")
    app.run_polling()


def main():
    log.info(f"⚡ NUX Agent v{settings.AGENT_VERSION} starting...")
    log.info(f"LLM: {settings.LLM_PROVIDER} / {settings.LLM_MODEL}")

    mode = sys.argv[1] if len(sys.argv) > 1 else settings.INTERFACE

    if mode == "telegram":
        run_telegram()
    else:
        run_cli()


if __name__ == "__main__":
    main()
