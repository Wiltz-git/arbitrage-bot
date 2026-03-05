# Crypto Arbitrage Trading Bot

An automated cryptocurrency arbitrage trading bot for UK-friendly (FCA-compliant) exchanges.

## Supported Exchanges

- **Kraken** ✅
- **Coinbase** (Advanced Trade API) ✅
- **Bitstamp** ✅
- **Crypto.com** ✅

## Features

- Real-time price monitoring across multiple exchanges
- Automatic arbitrage opportunity detection
- Paper trading mode for risk-free testing
- Configurable profit thresholds (default: 0.3%)
- Trade amount scaling based on balance
- Comprehensive logging and reporting
- Systemd service for 24/7 operation

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/crypto_arbitrage_bot.git
cd crypto_arbitrage_bot

# 2. Run setup
chmod +x setup.sh
./setup.sh

# 3. Configure API keys
nano .env

# 4. Test the bot
source venv/bin/activate
python main.py

# 5. Enable 24/7 operation
sudo systemctl enable crypto-arbitrage-bot
sudo systemctl start crypto-arbitrage-bot
```

## Configuration

Copy `.env.template` to `.env` and fill in your exchange API credentials.

**Important Settings in `.env`:**
- `PAPER_TRADING_MODE=true` - Start with paper trading!
- `SCALING_ENABLED=false` - Disable trade scaling initially

## Trading Pairs

Monitoring: BTC, ETH, ADA, SOL, DOT (all paired with USDT)

## Management Commands

```bash
./botctl.sh start     # Start bot
./botctl.sh stop      # Stop bot
./botctl.sh status    # Check status
./botctl.sh logs      # View live logs
./botctl.sh restart   # Restart bot
```

## Documentation

See `DEPLOYMENT_GUIDE.md` for detailed VPS deployment instructions.

## ⚠️ Disclaimer

This bot is for educational purposes. Cryptocurrency trading involves significant risk. Always start with paper trading and never invest more than you can afford to lose.

## License

MIT License
