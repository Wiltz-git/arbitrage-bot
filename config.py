# Configuration file for Crypto Arbitrage Bot

import os
from dotenv import load_dotenv

load_dotenv()

# Exchange API Configuration - UK Friendly Exchanges (FCA Compliant)
EXCHANGE_CONFIG = {
    'kraken': {
        'api_key': os.getenv('KRAKEN_API_KEY'),
        'secret': os.getenv('KRAKEN_SECRET'),
        'enableRateLimit': True,
    },
    'coinbase': {
        'api_key': os.getenv('COINBASE_API_KEY'),
        'secret': os.getenv('COINBASE_SECRET'),
        'sandbox': False,
        'enableRateLimit': True,
    },
    'bitstamp': {
        'api_key': os.getenv('BITSTAMP_API_KEY'),
        'secret': os.getenv('BITSTAMP_SECRET'),
        'uid': os.getenv('BITSTAMP_CUSTOMER_ID'),
        'enableRateLimit': True,
    },
    'cryptocom': {
        'api_key': os.getenv('CRYPTOCOM_API_KEY'),
        'secret': os.getenv('CRYPTOCOM_SECRET'),
        'sandbox': False,
        'enableRateLimit': True,
    }
}

# Trading Configuration - TRIAL MODE
TRADING_CONFIG = {
    'cryptocurrencies': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT'],
    'min_profit_threshold': 0.003,  # 0.3% minimum profit
    'max_trade_amount': 10,  # $10 max per trade (TRIAL MODE) - base amount when scaling disabled
    'daily_limit': 50,  # $50 daily limit (TRIAL MODE)
    'stop_loss': 0.005,  # 0.5% stop loss
    'reserve_percentage': 0.2,  # Keep 20% as reserve
    'max_trades_per_hour': 20,  # Reduced for trial
    'fee_buffer': 0.002,  # 0.2% buffer for exchange fees
}

# Compounding/Scaling Configuration
SCALING_CONFIG = {
    'enabled': os.getenv('SCALING_ENABLED', 'false').lower() == 'true',
    'mode': 'percentage',  # 'percentage' or 'fixed_increment'
    
    # Percentage mode: trade amount = balance * trade_percentage
    'trade_percentage': 0.02,  # Risk 2% of balance per trade
    
    # Limits to manage risk even when scaling
    'min_trade_amount': 10,    # Never trade less than $10
    'max_trade_amount': 500,   # Never trade more than $500 (hard cap)
    
    # Growth thresholds - increase trade size at these balance milestones
    'scaling_tiers': [
        {'balance_threshold': 1000, 'max_trade': 10},    # $1000 balance = max $10 trades
        {'balance_threshold': 1500, 'max_trade': 20},    # $1500 balance = max $20 trades
        {'balance_threshold': 2000, 'max_trade': 35},    # $2000 balance = max $35 trades
        {'balance_threshold': 3000, 'max_trade': 50},    # $3000 balance = max $50 trades
        {'balance_threshold': 5000, 'max_trade': 100},   # $5000 balance = max $100 trades
        {'balance_threshold': 10000, 'max_trade': 200},  # $10000 balance = max $200 trades
        {'balance_threshold': 20000, 'max_trade': 500},  # $20000+ balance = max $500 trades
    ],
    
    # Daily limit scaling (proportional to balance growth)
    'scale_daily_limit': True,
    'daily_limit_percentage': 0.10,  # Daily limit = 10% of balance
    'min_daily_limit': 50,           # Minimum $50 daily
    'max_daily_limit': 2000,         # Maximum $2000 daily
}

# Paper Trading Configuration
PAPER_TRADING_CONFIG = {
    'enabled': os.getenv('PAPER_TRADING_MODE', 'false').lower() == 'true',
    'initial_balance': 1000,  # Starting with $1000 virtual balance
    'log_directory': 'paper_trading_logs',
    'detailed_logging': True,
    'daily_summary_enabled': True,
    'summary_time': '23:59',  # Time to generate daily summary (HH:MM format)
}

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email': os.getenv('EMAIL_ADDRESS'),
    'password': os.getenv('EMAIL_PASSWORD'),
    'recipient': os.getenv('RECIPIENT_EMAIL'),
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/arbitrage_bot.log',
}

# Database Configuration (for trade history)
DATABASE_CONFIG = {
    'file': 'data/trades.db',
}