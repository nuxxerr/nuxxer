"""
Skill: Wallet Intel
Source: Basescan API
Chain: Base (8453)

Profiles wallet behavior — balance, token holdings, recent transactions.
"""

import re
import requests
from typing import Optional
from config.settings import settings

BASESCAN_URL = "https://api.basescan.org/api"


def detect_address(text: str) -> Optional[str]:
    """Extract 0x... wallet address from text."""
    match = re.search(r"0x[a-fA-F0-9]{40}", text)
    return match.group(0) if match else None


def _get_eth_balance(address: str) -> Optional[str]:
    """Get ETH balance on Base."""
    try:
        resp = requests.get(
            BASESCAN_URL,
            params={
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": settings.BASESCAN_API_KEY or "YourApiKeyToken",
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("status") == "1":
            wei = int(data["result"])
            eth = wei / 1e18
            return f"{eth:.6f} ETH"
    except Exception:
        pass
    return None


def _get_token_transfers(address: str, limit: int = 10) -> list:
    """Get recent ERC-20 token transfers."""
    try:
        resp = requests.get(
            BASESCAN_URL,
            params={
                "module": "account",
                "action": "tokentx",
                "address": address,
                "page": "1",
                "offset": str(limit),
                "sort": "desc",
                "apikey": settings.BASESCAN_API_KEY or "YourApiKeyToken",
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("status") == "1":
            return data.get("result", [])
    except Exception:
        pass
    return []


def _get_normal_txs(address: str, limit: int = 10) -> list:
    """Get recent normal transactions."""
    try:
        resp = requests.get(
            BASESCAN_URL,
            params={
                "module": "account",
                "action": "txlist",
                "address": address,
                "page": "1",
                "offset": str(limit),
                "sort": "desc",
                "apikey": settings.BASESCAN_API_KEY or "YourApiKeyToken",
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("status") == "1":
            return data.get("result", [])
    except Exception:
        pass
    return []


def _format_wallet_report(address: str, balance: str, token_txs: list, normal_txs: list) -> str:
    """Format wallet data into a report for LLM context."""
    lines = [f"[WALLET INTEL — Base]"]
    lines.append(f"  Address: {address}")
    lines.append(f"  ETH Balance: {balance or 'unknown'}")

    # Analyze token activity
    if token_txs:
        unique_tokens = {}
        buys = 0
        sells = 0
        for tx in token_txs:
            token_name = tx.get("tokenName", "Unknown")
            token_symbol = tx.get("tokenSymbol", "???")
            key = tx.get("contractAddress", "").lower()

            if key not in unique_tokens:
                unique_tokens[key] = {"name": token_name, "symbol": token_symbol}

            if tx.get("to", "").lower() == address.lower():
                buys += 1
            else:
                sells += 1

        lines.append(f"\n  TOKEN ACTIVITY (last {len(token_txs)} transfers):")
        lines.append(f"  Buys: {buys} | Sells: {sells}")
        lines.append(f"  Unique Tokens Touched: {len(unique_tokens)}")

        lines.append(f"\n  RECENT TOKENS:")
        for i, (ca, info) in enumerate(list(unique_tokens.items())[:5], 1):
            lines.append(f"    #{i} {info['name']} (${info['symbol']})")
    else:
        lines.append("\n  No recent token transfers found.")

    # Normal tx activity
    if normal_txs:
        total_gas_used = 0
        contract_interactions = 0
        for tx in normal_txs:
            gas = int(tx.get("gasUsed", 0)) * int(tx.get("gasPrice", 0))
            total_gas_used += gas
            if tx.get("input", "0x") != "0x":
                contract_interactions += 1

        lines.append(f"\n  TX ACTIVITY (last {len(normal_txs)} txs):")
        lines.append(f"  Contract Interactions: {contract_interactions}/{len(normal_txs)}")
        lines.append(f"  Total Gas Spent: {total_gas_used / 1e18:.6f} ETH")

        # Classify wallet behavior
        if contract_interactions > 7:
            lines.append("  Behavior: DEGEN (high contract interaction)")
        elif contract_interactions > 3:
            lines.append("  Behavior: ACTIVE TRADER")
        else:
            lines.append("  Behavior: CASUAL / HOLDER")
    else:
        lines.append("\n  No recent transactions found.")

    lines.append(f"\n  🔗 https://basescan.org/address/{address}")
    lines.append("\nIMPORTANT: Base your analysis ONLY on this real data.")

    return "\n".join(lines)


def get_wallet_intel(user_message: str) -> Optional[str]:
    """
    Main entry: detect wallet address, fetch data, return report.
    """
    address = detect_address(user_message)
    if not address:
        return None

    balance = _get_eth_balance(address)
    token_txs = _get_token_transfers(address)
    normal_txs = _get_normal_txs(address)

    return _format_wallet_report(address, balance, token_txs, normal_txs)
