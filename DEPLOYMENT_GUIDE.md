# Crypto Arbitrage Bot - VPS Deployment Guide

## Overview
This guide will help you deploy your crypto arbitrage trading bot to a Hostinger VPS (or any Ubuntu-based VPS).

---

## Prerequisites

### VPS Requirements
- **OS:** Ubuntu 22.04 LTS (recommended) or Ubuntu 20.04
- **RAM:** Minimum 1GB (2GB recommended)
- **CPU:** 1 vCPU minimum
- **Storage:** 10GB minimum
- **Network:** Stable internet connection

### Hostinger VPS Plans That Work
- KVM 1 (~$5-6/month) ✅
- KVM 2 (~$8-10/month) ✅
- Any Cloud VPS plan ✅

❌ **Shared Hosting will NOT work** (no SSH access, no Python support)

---

## Step 1: Initial VPS Setup

### 1.1 Access Your VPS
After purchasing your Hostinger VPS:

1. Go to Hostinger hPanel → VPS section
2. Note your **IP address** and **root password**
3. Connect via SSH:

```bash
ssh root@YOUR_VPS_IP
```

### 1.2 Create a Non-Root User
```bash
# Create user
adduser ubuntu

# Add to sudo group
usermod -aG sudo ubuntu

# Switch to new user
su - ubuntu
```

### 1.3 Update System
```bash
sudo apt update && sudo apt upgrade -y
```

---

## Step 2: Install Git & Clone Repository

```bash
# Install git
sudo apt install -y git

# Clone your repository (replace with your actual repo URL)
git clone https://github.com/YOUR_USERNAME/crypto_arbitrage_bot.git

# Navigate to the bot directory
cd crypto_arbitrage_bot
```

---

## Step 3: Run Setup Script

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

This will:
- Install Python 3 and pip
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Install the systemd service

---

## Step 4: Configure API Keys

### 4.1 Edit Environment File
```bash
nano .env
```

### 4.2 Fill In Your API Credentials

#### Kraken
1. Go to https://www.kraken.com/u/security/api
2. Create new API key with trading permissions
3. Copy API Key and Private Key to .env

#### Coinbase (Advanced Trade API)
1. Go to https://www.coinbase.com/settings/api
2. Create new API key (select "Advanced Trade" permissions)
3. **IMPORTANT:** Download the JSON file with your credentials
4. The API key format is: `organizations/{org_id}/apiKeys/{key_id}`
5. The secret is a PEM-formatted private key - keep the `\n` characters!

#### Bitstamp
1. Go to https://www.bitstamp.net/account/security/api/
2. Create API key with appropriate permissions
3. **IMPORTANT:** Note your Customer ID from account settings

#### Crypto.com
1. Go to https://crypto.com/exchange/user/settings/api-management
2. Create API key
3. **CRITICAL:** Add your VPS IP address to the whitelist!
   - Run `curl ifconfig.me` on your VPS to get the IP
   - Add this IP in Crypto.com API settings

### 4.3 Save and Exit
Press `Ctrl+X`, then `Y`, then `Enter`

---

## Step 5: Test the Bot

### 5.1 Run in Test Mode First
```bash
# Activate virtual environment
source venv/bin/activate

# Run bot manually
python main.py
```

Watch for:
- ✅ "Connected to Kraken"
- ✅ "Connected to Coinbase"
- ✅ "Connected to Bitstamp"
- ✅ "Connected to Crypto.com"
- ✅ "Starting arbitrage scan..."

Press `Ctrl+C` to stop after confirming it works.

### 5.2 Verify Paper Trading Mode
Ensure `.env` contains:
```
PAPER_TRADING_MODE=true
```

---

## Step 6: Enable Auto-Start Service

```bash
# Enable service to start on boot
sudo systemctl enable crypto-arbitrage-bot

# Start the service now
sudo systemctl start crypto-arbitrage-bot

# Check status
sudo systemctl status crypto-arbitrage-bot
```

---

## Step 7: Managing the Bot

Use the control script for easy management:

```bash
# Make control script executable (if not already)
chmod +x botctl.sh

# Start bot
./botctl.sh start

# Stop bot
./botctl.sh stop

# Restart bot
./botctl.sh restart

# Check status
./botctl.sh status

# View live logs
./botctl.sh logs

# View error logs
./botctl.sh errors

# Test in foreground
./botctl.sh test
```

---

## Monitoring & Maintenance

### View Logs
```bash
# Live bot activity
tail -f logs/bot.log

# Paper trading results
ls -la paper_trading_logs/
cat paper_trading_logs/paper_trading_log_$(date +%Y-%m-%d).txt
```

### Check Bot is Running
```bash
# Quick status check
systemctl is-active crypto-arbitrage-bot

# Detailed status
sudo systemctl status crypto-arbitrage-bot
```

### Restart After Config Changes
```bash
sudo systemctl restart crypto-arbitrage-bot
```

---

## Troubleshooting

### Bot Won't Start
```bash
# Check error logs
cat logs/bot_error.log

# Check systemd journal
sudo journalctl -u crypto-arbitrage-bot -n 50
```

### Exchange Connection Errors

#### Crypto.com "IP not whitelisted"
1. Get your VPS IP: `curl ifconfig.me`
2. Add to Crypto.com API whitelist

#### Coinbase Authentication Failed
1. Verify PEM key format in .env (needs `\n` line breaks)
2. Ensure API key has Advanced Trade permissions

#### Bitstamp Auth Error
1. Verify Customer ID is correct
2. Check API key permissions

### Memory Issues
If running low on memory:
```bash
# Check memory usage
free -h

# Create swap file (if needed)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Security Best Practices

1. **Never commit .env to Git** - it contains your API keys!
2. **Use IP whitelisting** on all exchanges that support it
3. **Set API key permissions** to minimum required (no withdrawal permissions)
4. **Enable 2FA** on all exchange accounts
5. **Regularly rotate API keys** (every 3-6 months)
6. **Keep system updated**: `sudo apt update && sudo apt upgrade`

---

## Dashboard Integration

Your bot automatically syncs trade data to your remote dashboard at:
**https://crypto-arbitrage-das-bs7yse.abacusai.app**

### How It Works

When the bot executes a trade (paper or live), it automatically:
1. Saves the trade locally to `paper_trading_logs/`
2. Sends the trade data to your dashboard via secure API
3. The dashboard stores it in the database for visualization

### Configuration

In your `.env` file:
```
DASHBOARD_SYNC_ENABLED=true
DASHBOARD_URL=https://crypto-arbitrage-das-bs7yse.abacusai.app
DASHBOARD_SYNC_API_KEY=88288ef6359dc87d659b087fdcc78a8a3e155639d5a2758ed4d502440f36e426
DASHBOARD_SYNC_TIMEOUT=10
```

### Verify Connection

Test the dashboard sync manually:
```bash
source venv/bin/activate
python -c "from dashboard_sync import DashboardSync; s = DashboardSync(); print(s.check_status())"
```

You should see:
```json
{"status": "online", "api_version": "1.0", "stats": {...}}
```

### Troubleshooting Sync Issues

If trades aren't appearing on the dashboard:
1. Check your VPS has internet access: `curl -I https://crypto-arbitrage-das-bs7yse.abacusai.app`
2. Verify API key in `.env` matches the dashboard
3. Check bot logs for sync errors: `grep "Dashboard" logs/bot.log`

---

## Switching to Live Trading

⚠️ **Only do this when you're confident the bot is working correctly!**

1. Edit .env:
   ```bash
   nano .env
   ```

2. Change:
   ```
   PAPER_TRADING_MODE=false
   ```

3. Restart:
   ```bash
   ./botctl.sh restart
   ```

---

## Support

If you encounter issues:
1. Check logs first: `./botctl.sh logs` and `./botctl.sh errors`
2. Verify all API keys are correctly configured
3. Ensure your VPS IP is whitelisted on Crypto.com
4. Check exchange status pages for any outages

---

## File Structure

```
crypto_arbitrage_bot/
├── main.py              # Main entry point
├── arbitrage_bot.py     # Core trading logic
├── config.py            # Configuration settings
├── exchange_manager.py  # Exchange connections
├── .env                 # Your API keys (DO NOT SHARE)
├── .env.template        # Template for .env
├── requirements.txt     # Python dependencies
├── setup.sh             # Installation script
├── botctl.sh            # Control script
├── crypto-arbitrage-bot.service  # Systemd service
├── logs/                # Bot logs
├── paper_trading_logs/  # Paper trading results
└── venv/                # Python virtual environment
```

---

Good luck with your trading! 🚀
