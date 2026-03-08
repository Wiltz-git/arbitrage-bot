#!/bin/bash
# ============================================================
# CRYPTO ARBITRAGE BOT - CONTROL SCRIPT
# ============================================================
# Usage: ./botctl.sh [start|stop|restart|status|logs|test]
# ============================================================

SERVICE_NAME="crypto-arbitrage-bot"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

case "$1" in
    start)
        echo "Starting $SERVICE_NAME..."
        sudo systemctl start $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    stop)
        echo "Stopping $SERVICE_NAME..."
        sudo systemctl stop $SERVICE_NAME
        echo "Bot stopped."
        ;;
    restart)
        echo "Restarting $SERVICE_NAME..."
        sudo systemctl restart $SERVICE_NAME
        sleep 2
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    status)
        sudo systemctl status $SERVICE_NAME --no-pager
        echo ""
        echo "Recent activity:"
        tail -5 "$SCRIPT_DIR/logs/bot.log" 2>/dev/null || echo "No logs yet."
        ;;
    logs)
        echo "Showing live logs (Ctrl+C to exit)..."
        tail -f "$SCRIPT_DIR/logs/bot.log"
        ;;
    errors)
        echo "Showing error logs..."
        tail -50 "$SCRIPT_DIR/logs/bot_error.log" 2>/dev/null || echo "No error logs."
        ;;
    test)
        echo "Running bot in test mode (foreground)..."
        cd "$SCRIPT_DIR"
        source venv/bin/activate
        python main.py
        ;;
    enable)
        echo "Enabling auto-start on boot..."
        sudo systemctl enable $SERVICE_NAME
        echo "Bot will now start automatically on system boot."
        ;;
    disable)
        echo "Disabling auto-start on boot..."
        sudo systemctl disable $SERVICE_NAME
        ;;
    *)
        echo "Crypto Arbitrage Bot Control"
        echo "Usage: $0 {start|stop|restart|status|logs|errors|test|enable|disable}"
        echo ""
        echo "  start   - Start the bot service"
        echo "  stop    - Stop the bot service"
        echo "  restart - Restart the bot service"
        echo "  status  - Show current status and recent logs"
        echo "  logs    - Follow live log output"
        echo "  errors  - Show recent error logs"
        echo "  test    - Run bot in foreground (for testing)"
        echo "  enable  - Enable auto-start on boot"
        echo "  disable - Disable auto-start on boot"
        exit 1
        ;;
esac
