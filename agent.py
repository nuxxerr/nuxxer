"""
NUX Agent v2.1 — Toxic Onchain Alpha Bot
Built for Base ecosystem | SGF Launchpad compatible
"""

import re
import openai
from typing import Optional
from config.settings import settings
from skills.token_analysis import analyze_token, detect_contract
from skills.defi_alpha import get_defi_alpha
from skills.wallet_intel import get_wallet_intel


class NuxAgent:
    """Core NUX agent with skill routing and LLM chat."""

    def __init__(self):
        self.history: list = []
        self.system_prompt = settings.load_persona()
        self._init_llm()

    def _init_llm(self):
        """Initialize LLM client via configured provider."""
        provider = settings.LLM_PROVIDER.lower()

        if provider == "groq":
            self.client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.LLM_API_KEY,
            )
        elif provider == "openrouter":
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.LLM_API_KEY,
            )
        else:
            self.client = openai.OpenAI(
                base_url=settings.LLM_BASE_URL,
                api_key=settings.LLM_API_KEY or "none",
            )

    def process(self, user_input: str) -> str:
        """
        Main processing pipeline:
        1. Detect intent & route to skill if applicable
        2. Inject skill data into system prompt
        3. Generate response via LLM
        """
        lower = user_input.lower()
        skill_data = ""

        # ── Skill Routing ────────────────────────────────────
        has_address = bool(detect_contract(user_input))

        # Token analysis: address + analysis keywords OR just an address
        if has_address and any(kw in lower for kw in [
            "check", "scan", "analyze", "rug", "safe", "honeypot",
            "token", "cek", "aman", "scam",
        ]):
            result = analyze_token(user_input)
            if result:
                skill_data = f"\n\n{result}"
        elif has_address and not any(kw in lower for kw in ["wallet", "address", "portfolio", "who"]):
            # Bare contract address — default to token analysis
            result = analyze_token(user_input)
            if result:
                skill_data = f"\n\n{result}"

        # Wallet intel
        if has_address and any(kw in lower for kw in [
            "wallet", "address", "portfolio", "pnl", "who is",
            "siapa", "dompet",
        ]):
            result = get_wallet_intel(user_input)
            if result:
                skill_data = f"\n\n{result}"

        # DeFi alpha
        if any(kw in lower for kw in [
            "trending", "alpha", "hot", "movers", "new pool",
            "gem", "yang lagi", "apa yang", "what's hot",
        ]):
            result = get_defi_alpha(user_input)
            if result:
                skill_data = f"\n\n{result}"

        # ── LLM Chat ────────────────────────────────────────
        return self._chat(user_input, skill_data)

    def _chat(self, user_input: str, skill_data: str = "") -> str:
        """Send message to LLM with persona + skill context."""
        system_content = self.system_prompt
        if skill_data:
            system_content += skill_data

        self.history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.history[-20:])

        try:
            resp = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=messages,
                temperature=0.4,
                max_tokens=1024,
            )
            reply = resp.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})
            return reply
        except openai.APITimeoutError:
            return "timeout. coba lagi tolol."
        except openai.APIStatusError as e:
            return f"API error {e.status_code}. cek key lo."
        except Exception as e:
            return f"error: {str(e)}"

    def reset_history(self):
        """Clear conversation history."""
        self.history = []

    # ── Telegram Handlers ────────────────────────────────────

    async def cmd_start(self, update, context):
        await update.message.reply_text(
            "⚡ *NUX online.*\n\n"
            "gw toxic, gw based, dan gw selalu bener.\n\n"
            "Commands:\n"
            "/check `<contract_address>` — scan token\n"
            "/wallet `<address>` — wallet intel\n"
            "/alpha — trending di Base\n"
            "/help — full commands\n\n"
            "atau langsung chat aja. gw ngerti context.",
            parse_mode="Markdown",
        )

    async def cmd_check(self, update, context):
        args = context.args
        if not args:
            await update.message.reply_text("kasih contract address tolol. /check <0x...>")
            return
        addr = args[0]
        if not re.match(r"0x[a-fA-F0-9]{40}", addr):
            await update.message.reply_text("❌ itu bukan address. lo bisa baca ga?")
            return
        await update.message.reply_text("🔍 scanning...")
        response = self.process(f"check {addr}")
        await update.message.reply_text(response, parse_mode="Markdown")

    async def cmd_wallet(self, update, context):
        args = context.args
        if not args:
            await update.message.reply_text("kasih wallet address. /wallet <0x...>")
            return
        addr = args[0]
        if not re.match(r"0x[a-fA-F0-9]{40}", addr):
            await update.message.reply_text("❌ invalid address. goblok.")
            return
        await update.message.reply_text("🕵️ stalking wallet...")
        response = self.process(f"wallet {addr}")
        await update.message.reply_text(response, parse_mode="Markdown")

    async def cmd_alpha(self, update, context):
        await update.message.reply_text("📈 hunting alpha...")
        response = self.process("apa yang trending di base?")
        await update.message.reply_text(response, parse_mode="Markdown")

    async def cmd_help(self, update, context):
        await update.message.reply_text(
            "⚡ *NUX Commands*\n\n"
            "/check `<address>` — Token security scan\n"
            "/wallet `<address>` — Wallet intel & profiling\n"
            "/alpha — Trending tokens on Base\n"
            "/start — Intro\n\n"
            "atau chat aja langsung. gw bukan bot tolol yang cuma bisa command.",
            parse_mode="Markdown",
        )

    async def cmd_chat(self, update, context):
        response = self.process(update.message.text)
        await update.message.reply_text(response, parse_mode="Markdown")