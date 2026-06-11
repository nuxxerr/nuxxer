# ⚡ NUX Agent

> **Toxic. Based. Always right.**

NUX is an onchain AI agent built natively for the **Base** ecosystem. Brutally honest token analysis, DeFi alpha hunting, and wallet profiling — with zero filter and maximum toxicity.

**Chain:** Base (8453) | **Token:** $NUX | **Launchpad:** [SGF Launchpad](https://supergemma.ai/launch)

---

## 🔥 What NUX Does

| Skill | Description | Data Source |
|-------|-------------|-------------|
| **Token Analysis** | Security scan — honeypot, rug signals, tax, liquidity locks | GoPlus API + Basescan |
| **DeFi Alpha** | Trending tokens, new pools, volume spikes on Base | GeckoTerminal + Dexscreener |
| **Wallet Intel** | Wallet profiling — balance, activity, degen score | Basescan API |
| **LLM Chat** | Context-aware toxic alpha with onchain knowledge | Groq / OpenRouter |

---

## 🏗️ Architecture

```
nux-agent/
├── main.py                  # Entry point (CLI + Telegram)
├── agent.py                 # NuxAgent class — skill routing + LLM
├── config/
│   ├── settings.py          # Centralized configuration
│   └── persona.txt          # NUX personality system prompt
├── skills/
│   ├── token_analysis.py    # GoPlus + Basescan integration
│   ├── defi_alpha.py        # GeckoTerminal + Dexscreener
│   └── wallet_intel.py      # Basescan wallet profiling
├── utils/
│   └── formatter.py         # Terminal UI formatting
├── requirements.txt
├── .env.example
└── .gitignore
```

**Flow:**
```
User Input → Skill Router → [Token/DeFi/Wallet API] → Data Injection → LLM → Toxic Response
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- API Key: [Groq](https://console.groq.com) (free) or [OpenRouter](https://openrouter.ai)
- Optional: [Basescan API Key](https://basescan.org/apis) (free, 5 req/s)

### Install & Run

```bash
git clone https://github.com/nuxxerr/nux-agent
cd nux-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python main.py
```

### Telegram Bot

```bash
# Add TELEGRAM_BOT_TOKEN to .env (from @BotFather)
python main.py telegram
```

---

## ⚙️ Configuration

```env
LLM_PROVIDER=groq                          # groq | openrouter
API_BASE_URL=https://api.groq.com/openai/v1
API_KEY=your_key_here
MODEL=llama-3.3-70b-versatile
BASESCAN_API_KEY=your_basescan_key          # optional, free tier
TELEGRAM_BOT_TOKEN=your_bot_token           # optional
INTERFACE=cli                               # cli | telegram
```

---

## 🛠️ Skills

### Token Analysis (`/check <address>`)
Paste any contract address and NUX will:
- Fetch security data from GoPlus Security API
- Check contract verification on Basescan
- Detect honeypots, hidden owners, high taxes, rug signals
- Score red flags and give a toxic verdict

### DeFi Alpha (`/alpha`)
- Trending pools on Base (GeckoTerminal)
- New pools with liquidity data
- Volume spike detection
- Token search via Dexscreener

### Wallet Intel (`/wallet <address>`)
- ETH balance on Base
- Recent token transfer analysis
- Buy/sell ratio tracking
- Degen score based on contract interactions

---

## 🔑 API Keys

| Service | Free Tier | Link |
|---------|-----------|------|
| Groq | ✅ Generous free tier | [console.groq.com](https://console.groq.com) |
| GoPlus | ✅ No key needed | [gopluslabs.io](https://gopluslabs.io) |
| GeckoTerminal | ✅ Public API | [geckoterminal.com](https://www.geckoterminal.com) |
| Dexscreener | ✅ Public API | [dexscreener.com](https://dexscreener.com) |
| Basescan | ✅ 5 req/s free | [basescan.org/apis](https://basescan.org/apis) |

---

## 🔗 Links

- **Network:** [Base](https://base.org) (Chain ID: 8453)
- **Token:** $NUX
- **Launchpad:** [SGF Launchpad](https://supergemma.ai/launch)
- **BaseScan:** [View on BaseScan](https://basescan.org)

---

## 📜 License

MIT — free to fork, build, deploy.

---

*Built by [@nuxxerr](https://github.com/nuxxerr) — toxic, based, always right.*
