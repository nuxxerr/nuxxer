"""
Skill: DeFi Alpha
Sources: GeckoTerminal API + Dexscreener API (no API key needed)
Chain: Base (network = base)

Fetches trending tokens, new pools, and volume data on Base.
"""

import requests
from typing import Optional

GECKO_BASE = "https://api.geckoterminal.com/api/v2"
DEXSCREENER_BASE = "https://api.dexscreener.com/latest"

HEADERS = {"Accept": "application/json"}


def get_trending_base() -> str:
    """Fetch trending tokens on Base from GeckoTerminal."""
    try:
        resp = requests.get(
            f"{GECKO_BASE}/networks/base/trending_pools",
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        pools = data.get("data", [])[:8]

        if not pools:
            return "[BASE TRENDING] No trending pools found right now."

        lines = ["[BASE TRENDING POOLS — GeckoTerminal]"]
        for i, pool in enumerate(pools, 1):
            attrs = pool.get("attributes", {})
            name = attrs.get("name", "???")
            price_change = attrs.get("price_change_percentage", {})
            h24 = price_change.get("h24", "?")
            volume_usd = attrs.get("volume_usd", {}).get("h24", "?")
            reserve = attrs.get("reserve_in_usd", "?")

            # Token info
            base_token = attrs.get("base_token_price_usd", "?")
            dex = attrs.get("dex_id", "?")

            lines.append(
                f"  #{i} {name} | "
                f"24h: {h24}% | "
                f"Vol: ${_fmt_num(volume_usd)} | "
                f"Liq: ${_fmt_num(reserve)} | "
                f"DEX: {dex}"
            )

        return "\n".join(lines)
    except Exception as e:
        return f"[BASE TRENDING] Error fetching data: {str(e)}"


def get_new_pools_base() -> str:
    """Fetch recently created pools on Base from GeckoTerminal."""
    try:
        resp = requests.get(
            f"{GECKO_BASE}/networks/base/new_pools",
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        pools = data.get("data", [])[:6]

        if not pools:
            return "[NEW POOLS] No new pools found."

        lines = ["[NEW POOLS ON BASE — GeckoTerminal]"]
        for i, pool in enumerate(pools, 1):
            attrs = pool.get("attributes", {})
            name = attrs.get("name", "???")
            created = attrs.get("pool_created_at", "?")
            reserve = attrs.get("reserve_in_usd", "?")
            volume_usd = attrs.get("volume_usd", {}).get("h24", "?")

            lines.append(
                f"  #{i} {name} | "
                f"Created: {created[:10] if created != '?' else '?'} | "
                f"Liq: ${_fmt_num(reserve)} | "
                f"Vol: ${_fmt_num(volume_usd)}"
            )

        return "\n".join(lines)
    except Exception as e:
        return f"[NEW POOLS] Error: {str(e)}"


def search_token_dexscreener(query: str) -> str:
    """Search for a token on Dexscreener."""
    try:
        resp = requests.get(
            f"{DEXSCREENER_BASE}/dex/search",
            params={"q": query},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        pairs = [p for p in data.get("pairs", []) if p.get("chainId") == "base"][:5]

        if not pairs:
            return f"[DEXSCREENER] No Base pairs found for '{query}'."

        lines = [f"[DEXSCREENER SEARCH: {query}]"]
        for i, pair in enumerate(pairs, 1):
            base_token = pair.get("baseToken", {})
            name = base_token.get("name", "???")
            symbol = base_token.get("symbol", "???")
            price = pair.get("priceUsd", "?")
            h24_change = pair.get("priceChange", {}).get("h24", "?")
            volume = pair.get("volume", {}).get("h24", "?")
            liquidity = pair.get("liquidity", {}).get("usd", "?")
            dex = pair.get("dexId", "?")
            ca = base_token.get("address", "?")

            lines.append(
                f"  #{i} {name} (${symbol}) | "
                f"${price} | "
                f"24h: {h24_change}% | "
                f"Vol: ${_fmt_num(volume)} | "
                f"Liq: ${_fmt_num(liquidity)} | "
                f"DEX: {dex}"
            )
            lines.append(f"      CA: {ca}")

        return "\n".join(lines)
    except Exception as e:
        return f"[DEXSCREENER] Error: {str(e)}"


def get_defi_alpha(user_message: str = "") -> Optional[str]:
    """
    Main entry for DeFi alpha skill.
    Returns trending + new pool data, or token search results.
    """
    lower = user_message.lower()

    # If user is searching for a specific token
    if any(kw in lower for kw in ["search", "find", "where", "price of"]):
        # Extract potential token name (last word or quoted string)
        words = user_message.split()
        query = words[-1] if words else ""
        if query and len(query) > 1:
            return search_token_dexscreener(query)

    # If asking about new pools
    if any(kw in lower for kw in ["new pool", "new pair", "just listed", "baru"]):
        return get_new_pools_base()

    # Default: trending
    trending = get_trending_base()
    return trending


def _fmt_num(val) -> str:
    """Format large numbers for readability."""
    try:
        num = float(val)
        if num >= 1_000_000:
            return f"{num/1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        else:
            return f"{num:.2f}"
    except (ValueError, TypeError):
        return str(val)
