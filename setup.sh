#!/bin/bash
# ============================================================
# CRYPTO ARBITRAGE BOT - AUTOMATED SETUP SCRIPT
# ============================================================
# Run this script after cloning the repository to your VPS
# Usage: chmod +x setup.sh && ./setup.sh
# ============================================================

set -e  # Exit on any error

echo "========================================"
echo "  Crypto Arbitrage Bot - Setup Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root. Run as regular user with sudo access.${NC}"
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}[2/7] Installing Python 3 and pip...${NC}"
sudo apt install -y python3 python3-pip python3-venv

echo -e "${YELLOW}[3/7] Creating Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}[4/7] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}[5/7] Setting up directories...${NC}"
mkdir -p logs
mkdir -p paper_trading_logs
mkdir -p reports

echo -e "${YELLOW}[6/7] Checking .env configuration...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.template ]; then
        cp .env.template .env
        echo -e "${YELLOW}Created .env from template. Please edit it with your API keys!${NC}"
        echo -e "${RED}IMPORTANT: Run 'nano .env' to add your exchange API credentials${NC}"
    else
        echo -e "${RED}Warning: No .env.template found. Please create .env manually.${NC}"
    fi
else
    echo -e "${GREEN}.env file already exists.${NC}"
fi

echo -e "${YELLOW}[7/7] Installing systemd service...${NC}"
if [ -f crypto-arbitrage-bot.service ]; then
    # Update paths in service file
    sed -i "s|/home/ubuntu/crypto_arbitrage_bot|$SCRIPT_DIR|g" crypto-arbitrage-bot.service
    sed -i "s|User=ubuntu|User=$USER|g" crypto-arbitrage-bot.service
    
    sudo cp crypto-arbitrage-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo -e "${GREEN}Systemd service installed.${NC}"
else
    echo -e "${YELLOW}Service file not found, skipping systemd setup.${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}  Setup Complete!${NC}"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit your .env file with API credentials:"
echo "   nano .env"
echo ""
echo "2. Test the bot manually first:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Once confirmed working, enable auto-start:"
echo "   sudo systemctl enable crypto-arbitrage-bot"
echo "   sudo systemctl start crypto-arbitrage-bot"
echo ""
echo "4. Check status and logs:"
echo "   sudo systemctl status crypto-arbitrage-bot"
echo "   tail -f logs/bot.log"
echo ""
echo -e "${YELLOW}IMPORTANT: Ensure PAPER_TRADING_MODE=true until you're ready for live trading!${NC}"
