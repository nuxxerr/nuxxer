"""
Skill: Token Analysis
Sources: GoPlus Security API + Basescan API
Default Chain: Base (chain_id = 8453)

Fetches real on-chain security data for token contract analysis.
"""

import re
import requests
from typing import Optional
from config.settings import settings

GOPLUS_BASE = "https://api.gopluslabs.io/api/v1"
BASESCAN_URL = "https://api.basescan.org/api"

CHAIN_MAP = {
    "eth": "1", "ethereum": "1",
    "bsc": "56", "bnb": "56", "binance": "56",
    "base": "8453",
    "arb": "42161", "arbitrum": "42161",
}

CHAIN_NAMES = {"1": "ETH", "56": "BSC", "8453": "Base", "42161": "Arbitrum"}


def detect_contract(text: str) -> Optional[str]:
    """Extract 0x... contract address from user message."""
    match = re.search(r"0x[a-fA-F0-9]{40}", text)
    return match.group(0) if match else None


def detect_chain(text: str) -> str:
    """Detect chain from user message. Default = Base."""
    text_lower = text.lower()
    for keyword, chain_id in CHAIN_MAP.items():
        if keyword in text_lower:
            return chain_id
    return "8453"  # Default Base — NUX lives on Base


def _goplus_scan(address: str, chain_id: str) -> Optional[dict]:
    """Fetch token security data from GoPlus API."""
    try:
        headers = {}
        if settings.GOPLUS_API_KEY:
            headers["Authorization"] = settings.GOPLUS_API_KEY
        resp = requests.get(
            f"{GOPLUS_BASE}/token_security/{chain_id}",
            params={"contract_addresses": address},
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 1 and data.get("result"):
            return data["result"].get(address.lower())
    except Exception:
        pass
    return None


def _basescan_info(address: str) -> Optional[dict]:
    """Fetch contract source info from Basescan."""
    try:
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": settings.BASESCAN_API_KEY or "YourApiKeyToken",
        }
        resp = requests.get(BASESCAN_URL, params=params, timeout=10)
        data = resp.json()
        if data.get("status") == "1" and data.get("result"):
            return data["result"][0]
    except Exception:
        pass
    return None


def _format_report(address: str, chain_id: str, gp: dict, bs: dict) -> str:
    """Format GoPlus + Basescan data into a structured report for LLM context."""
    chain_name = CHAIN_NAMES.get(chain_id, chain_id)

    if not gp and not bs:
        return f"[CONTRACT DATA UNAVAILABLE for {address} on {chain_name}]\nCannot fetch data. Tell user to check manually at gopluslabs.io or basescan.org"

    lines = [f"[REAL CONTRACT DATA from GoPlus Security API + Basescan]"]
    lines.append(f"  Chain: {chain_name}")
    lines.append(f"  Contract: {address}")

    if gp:
        token_name = gp.get("token_name", "Unknown")
        token_symbol = gp.get("token_symbol", "???")
        lines.append(f"  Token: {token_name} ({token_symbol})")

        # Security flags
        is_honeypot = gp.get("is_honeypot", "unknown")
        buy_tax = gp.get("buy_tax", "unknown")
        sell_tax = gp.get("sell_tax", "unknown")
        is_open_source = gp.get("is_open_source", "unknown")
        is_proxy = gp.get("is_proxy", "unknown")
        is_mintable = gp.get("is_mintable", "unknown")
        can_take_back_ownership = gp.get("can_take_back_ownership", "unknown")
        owner_change_balance = gp.get("owner_change_balance", "unknown")
        hidden_owner = gp.get("hidden_owner", "unknown")
        selfdestruct = gp.get("selfdestruct", "unknown")
        cannot_sell_all = gp.get("cannot_sell_all", "unknown")
        slippage_modifiable = gp.get("slippage_modifiable", "unknown")
        transfer_pausable = gp.get("transfer_pausable", "unknown")
        is_blacklisted = gp.get("is_blacklisted", "unknown")
        is_anti_whale = gp.get("is_anti_whale", "unknown")
        honeypot_with_same_creator = gp.get("honeypot_with_same_creator", "0")

        def flag(val, yes_label, no_label="✅"):
            if val == "1":
                return yes_label
            elif val == "0":
                return no_label
            return "unknown"

        buy_pct = f"{float(buy_tax)*100:.1f}%" if buy_tax != "unknown" else "unknown"
        sell_pct = f"{float(sell_tax)*100:.1f}%" if sell_tax != "unknown" else "unknown"

        lines.append("")
        lines.append("  SECURITY:")
        lines.append(f"  Honeypot: {flag(is_honeypot, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Buy Tax: {buy_pct}")
        lines.append(f"  Sell Tax: {sell_pct}")
        lines.append(f"  Open Source: {flag(is_open_source, 'YES ✅', 'NO 🟡')}")
        lines.append(f"  Proxy: {flag(is_proxy, 'YES 🟡', 'NO ✅')}")
        lines.append(f"  Mintable: {flag(is_mintable, 'YES 🟡', 'NO ✅')}")
        lines.append(f"  Can Take Back Ownership: {flag(can_take_back_ownership, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Owner Can Change Balance: {flag(owner_change_balance, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Hidden Owner: {flag(hidden_owner, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Self-destruct: {flag(selfdestruct, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Cannot Sell All: {flag(cannot_sell_all, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Slippage Modifiable: {flag(slippage_modifiable, 'YES 🔴', 'NO ✅')}")
        lines.append(f"  Transfer Pausable: {flag(transfer_pausable, 'YES 🟡', 'NO ✅')}")
        lines.append(f"  Blacklist: {flag(is_blacklisted, 'YES 🟡', 'NO ✅')}")
        lines.append(f"  Anti-whale: {flag(is_anti_whale, 'YES', 'NO')}")

        # Info
        lines.append("")
        lines.append("  INFO:")
        lines.append(f"  Creator: {gp.get('creator_address', 'unknown')}")
        lines.append(f"  Owner: {gp.get('owner_address', 'unknown')}")
        lines.append(f"  Total Supply: {gp.get('total_supply', 'unknown')}")
        lines.append(f"  Holders: {gp.get('holder_count', 'unknown')}")
        lines.append(f"  LP Holders: {gp.get('lp_holder_count', 'unknown')}")
        lines.append(f"  On DEX: {flag(gp.get('is_in_dex', 'unknown'), 'YES', 'NO')}")

        # Top holders
        holders = gp.get("holders", [])
        if holders:
            lines.append("")
            lines.append("  TOP HOLDERS:")
            for i, h in enumerate(holders[:5], 1):
                pct = float(h.get("percent", 0)) * 100
                is_contract = " (CONTRACT)" if h.get("is_contract") == 1 else ""
                is_locked = " (LOCKED)" if h.get("is_locked") == 1 else ""
                lines.append(f"    #{i}: {pct:.2f}%{is_contract}{is_locked}")

        # LP holders
        lp_holders = gp.get("lp_holders", [])
        if lp_holders:
            lines.append("")
            lines.append("  LP HOLDERS:")
            for lp in lp_holders[:3]:
                pct = float(lp.get("percent", 0)) * 100
                locked = " LOCKED" if lp.get("is_locked") == 1 else " UNLOCKED"
                lines.append(f"    {pct:.2f}%{locked}")

        # DEX info
        dex = gp.get("dex", [])
        if dex:
            lines.append("")
            lines.append("  DEX LIQUIDITY:")
            for d in dex[:3]:
                name = d.get("name", "Unknown")
                liquidity = d.get("liquidity", "?")
                lines.append(f"    {name}: ${liquidity}")

        # Red flags
        red_flags = []
        if is_honeypot == "1":
            red_flags.append("🔴 HONEYPOT DETECTED")
        if buy_tax != "unknown" and float(buy_tax) > 0.1:
            red_flags.append(f"🔴 HIGH BUY TAX: {float(buy_tax)*100:.1f}%")
        if sell_tax != "unknown" and float(sell_tax) > 0.1:
            red_flags.append(f"🔴 HIGH SELL TAX: {float(sell_tax)*100:.1f}%")
        if cannot_sell_all == "1":
            red_flags.append("🔴 CANNOT SELL ALL TOKENS")
        if is_mintable == "1":
            red_flags.append("🟡 MINTABLE")
        if hidden_owner == "1":
            red_flags.append("🔴 HIDDEN OWNER")
        if can_take_back_ownership == "1":
            red_flags.append("🔴 CAN TAKE BACK OWNERSHIP")
        if owner_change_balance == "1":
            red_flags.append("🔴 OWNER CAN CHANGE BALANCES")
        if selfdestruct == "1":
            red_flags.append("🔴 SELF-DESTRUCT FUNCTION")
        if transfer_pausable == "1":
            red_flags.append("🟡 TRANSFERS PAUSABLE")
        if is_blacklisted == "1":
            red_flags.append("🟡 HAS BLACKLIST")
        if slippage_modifiable == "1":
            red_flags.append("🔴 SLIPPAGE MODIFIABLE")
        if is_open_source == "0":
            red_flags.append("🟡 NOT OPEN SOURCE")
        if honeypot_with_same_creator not in ("0", "unknown"):
            red_flags.append(f"🔴 CREATOR MADE {honeypot_with_same_creator} OTHER HONEYPOTS")

        lines.append("")
        lines.append("  RED FLAGS:")
        if red_flags:
            for rf in red_flags:
                lines.append(f"  {rf}")
        else:
            lines.append("  None detected")

    # Basescan contract info
    if bs and "error" not in bs:
        lines.append("")
        lines.append("  BASESCAN CONTRACT:")
        verified = bs.get("ABI", "") != "Contract source code not verified"
        lines.append(f"  Verified: {'YES ✅' if verified else 'NO 🚨'}")
        lines.append(f"  Contract Name: {bs.get('ContractName', 'Unknown')}")
        lines.append(f"  Compiler: {bs.get('CompilerVersion', '?')}")

    lines.append("")
    lines.append("IMPORTANT: Base your analysis ONLY on this real data. Do NOT make up numbers.")
    lines.append("Give verdict based on what you see above.")

    return "\n".join(lines)


def analyze_token(user_message: str) -> Optional[str]:
    """
    Main entry: detect contract address in user message,
    fetch GoPlus + Basescan data, return formatted report or None.
    """
    address = detect_contract(user_message)
    if not address:
        return None

    chain_id = detect_chain(user_message)
    gp_data = _goplus_scan(address, chain_id)
    bs_data = _basescan_info(address) if chain_id == "8453" else None
    return _format_report(address, chain_id, gp_data or {}, bs_data or {})
