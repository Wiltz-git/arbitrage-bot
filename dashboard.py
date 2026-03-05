from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import asyncio
import threading
from datetime import datetime, timedelta
from arbitrage_bot import ArbitrageBot
from config import DASHBOARD_CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'crypto_arbitrage_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global bot instance
bot = None
bot_thread = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current bot status"""
    if bot:
        return jsonify(bot.get_status())
    else:
        return jsonify({
            'is_running': False,
            'daily_volume': 0,
            'daily_limit': 5000,
            'hourly_trades': 0,
            'hourly_limit': 10,
            'last_scan': None,
            'opportunities_found': 0,
            'exchange_status': {}
        })

@app.route('/api/opportunities')
def get_opportunities():
    """Get recent arbitrage opportunities"""
    if bot:
        opportunities = bot.get_recent_opportunities(20)
        return jsonify(opportunities)
    else:
        return jsonify([])

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    if bot:
        trades = bot.get_trade_history(50)
        return jsonify(trades)
    else:
        return jsonify([])

@app.route('/api/current_opportunities')
def get_current_opportunities():
    """Get current live opportunities"""
    if bot and hasattr(bot, 'last_opportunities'):
        return jsonify(bot.last_opportunities)
    else:
        return jsonify([])

@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the arbitrage bot"""
    global bot, bot_thread
    
    if bot and bot.is_running:
        return jsonify({'success': False, 'message': 'Bot is already running'})
    
    try:
        bot = ArbitrageBot()
        
        # Start bot in separate thread
        def run_bot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.start())
        
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Send startup notification
        asyncio.create_task(bot.email_notifier.send_startup_notification())
        
        return jsonify({'success': True, 'message': 'Bot started successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to start bot: {str(e)}'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the arbitrage bot"""
    global bot
    
    if not bot or not bot.is_running:
        return jsonify({'success': False, 'message': 'Bot is not running'})
    
    try:
        bot.stop()
        
        # Send shutdown notification
        asyncio.create_task(bot.email_notifier.send_shutdown_notification())
        
        return jsonify({'success': True, 'message': 'Bot stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to stop bot: {str(e)}'})

@app.route('/api/stats')
def get_stats():
    """Get trading statistics"""
    if not bot:
        return jsonify({})
    
    trades = bot.get_trade_history(100)
    
    # Calculate statistics
    total_trades = len(trades)
    successful_trades = len([t for t in trades if t['status'] == 'SUCCESS'])
    total_profit = sum(t['profit'] for t in trades if t['profit'])
    total_volume = sum(t['amount'] for t in trades if t['amount'])
    
    # Daily stats
    today = datetime.now().date()
    today_trades = [t for t in trades if datetime.fromisoformat(t['timestamp']).date() == today]
    today_profit = sum(t['profit'] for t in today_trades if t['profit'])
    today_volume = sum(t['amount'] for t in today_trades if t['amount'])
    
    # Weekly stats
    week_ago = datetime.now() - timedelta(days=7)
    week_trades = [t for t in trades if datetime.fromisoformat(t['timestamp']) > week_ago]
    week_profit = sum(t['profit'] for t in week_trades if t['profit'])
    
    return jsonify({
        'total_trades': total_trades,
        'successful_trades': successful_trades,
        'success_rate': (successful_trades / total_trades * 100) if total_trades > 0 else 0,
        'total_profit': total_profit,
        'total_volume': total_volume,
        'today_trades': len(today_trades),
        'today_profit': today_profit,
        'today_volume': today_volume,
        'week_trades': len(week_trades),
        'week_profit': week_profit,
        'avg_profit_per_trade': (total_profit / successful_trades) if successful_trades > 0 else 0
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', 'Connected to Crypto Arbitrage Bot Dashboard')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

def broadcast_updates():
    """Broadcast real-time updates to connected clients"""
    while True:
        if bot:
            try:
                # Emit current status
                socketio.emit('status_update', bot.get_status())
                
                # Emit current opportunities
                if hasattr(bot, 'last_opportunities'):
                    socketio.emit('opportunities_update', bot.last_opportunities)
                
            except Exception as e:
                print(f"Error broadcasting updates: {e}")
        
        socketio.sleep(5)  # Update every 5 seconds

# Start background thread for real-time updates
socketio.start_background_task(broadcast_updates)

if __name__ == '__main__':
    socketio.run(
        app, 
        host=DASHBOARD_CONFIG['host'], 
        port=DASHBOARD_CONFIG['port'], 
        debug=DASHBOARD_CONFIG['debug']
    )