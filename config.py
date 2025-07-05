# =============================================================================
# NEON ROLL CASINO - PRODUCTION CONFIGURATION
# =============================================================================

# Bot Configuration
BOT_TOKEN = "7967948563:AAEcl-6mW5kd4jaqjsRIqnv34egBWmh1LiI"
WEB_APP_URL = "https://agrobmin.com.ua"
BOT_USERNAME = "neonroll_casino_bot"

# Firebase Configuration
FIREBASE_PROJECT_ID = "neonroll-26174"
FIREBASE_COLLECTION_USERS = "users"
FIREBASE_COLLECTION_GAMES = "games"
FIREBASE_COLLECTION_TRANSACTIONS = "transactions"
FIREBASE_COLLECTION_REFERRALS = "referrals"

# Crypto Wallet Generation (SEED PHRASE ONLY - NO HARDCODED ADDRESSES)
MASTER_SEED_PHRASE = "nothing ridge argue engine loan boat dry radar wink universe remind fence"
WALLET_ENCRYPTION_KEY = "neon-casino-2024-secure-key"

# Game Configuration
WELCOME_BONUS = 50.0
MIN_BET = 1.0
MAX_BET = 10000.0
HOUSE_EDGE = 0.02  # 2% house edge for profitability

# Casino Games Configuration
CASINO_GAMES = {
    'neon_roll': {
        'name': 'Neon Roll',
        'min_bet': 1.0,
        'max_bet': 1000.0,
        'colors': {
            'red': {'multiplier': 2.0, 'probability': 0.44, 'color': '#FF1B55'},
            'blue': {'multiplier': 2.0, 'probability': 0.44, 'color': '#00BFFF'}, 
            'green': {'multiplier': 5.0, 'probability': 0.10, 'color': '#00FF7F'},
            'yellow': {'multiplier': 45.0, 'probability': 0.02, 'color': '#FFD700'}
        }
    },
    'neon_dice': {
        'name': 'Neon Dice',
        'min_bet': 1.0,
        'max_bet': 2000.0,
        'outcomes': {
            'under_50': {'multiplier': 1.98, 'probability': 0.495},
            'over_50': {'multiplier': 1.98, 'probability': 0.495},
            'exact_50': {'multiplier': 99.0, 'probability': 0.01}
        }
    },
    'neon_slots': {
        'name': 'Neon Slots',
        'min_bet': 1.0,
        'max_bet': 500.0,
        'symbols': {
            '🍒': {'probability': 0.30, 'multiplier': 2.0},
            '🍋': {'probability': 0.25, 'multiplier': 3.0},
            '🍊': {'probability': 0.20, 'multiplier': 5.0},
            '⭐': {'probability': 0.15, 'multiplier': 10.0},
            '💎': {'probability': 0.08, 'multiplier': 25.0},
            '🎰': {'probability': 0.02, 'multiplier': 100.0}
        }
    },
    'neon_crash': {
        'name': 'Neon Crash',
        'min_bet': 1.0,
        'max_bet': 1500.0,
        'max_multiplier': 10.0,
        'crash_probability': 0.01  # 1% chance per 0.1x increment
    }
}

# Cryptocurrency Configuration (ADDRESSES GENERATED FROM SEED ONLY)
SUPPORTED_CRYPTOS = {
    'ton': {
        'name': 'TON',
        'full_name': 'Toncoin',
        'network': 'ton',
        'network_name': 'TON Network',
        'symbol': 'TON',
        'decimals': 9,
        'min_deposit': 1,
        'min_withdraw': 25,
        'rate_to_ec': 2.45,
        'icon': '💎',
        'color': '#0088CC',
        'confirmation_blocks': 1
    },
    'usdt': {
        'name': 'USDT TRC20',
        'full_name': 'Tether USD (TRC20)',
        'network': 'tron',
        'network_name': 'TRON Network',
        'symbol': 'USDT',
        'decimals': 6,
        'min_deposit': 5,
        'min_withdraw': 45,
        'rate_to_ec': 1.00,
        'icon': '💵',
        'color': '#26A17B',
        'confirmation_blocks': 1
    },
    'btc': {
        'name': 'Bitcoin',
        'full_name': 'Bitcoin',
        'network': 'bitcoin',
        'network_name': 'Bitcoin Network',
        'symbol': 'BTC',
        'decimals': 8,
        'min_deposit': 0.0001,
        'min_withdraw': 100,
        'rate_to_ec': 45000,
        'icon': '₿',
        'color': '#F7931A',
        'confirmation_blocks': 3
    },
    'eth': {
        'name': 'Ethereum',
        'full_name': 'Ethereum',
        'network': 'ethereum',
        'network_name': 'Ethereum Network',
        'symbol': 'ETH',
        'decimals': 18,
        'min_deposit': 0.001,
        'min_withdraw': 80,
        'rate_to_ec': 2500.00,
        'icon': '⟠',
        'color': '#627EEA',
        'confirmation_blocks': 12
    },
    'bnb': {
        'name': 'BNB',
        'full_name': 'Binance Coin',
        'network': 'bsc',
        'network_name': 'BSC Network',
        'symbol': 'BNB',
        'decimals': 18,
        'min_deposit': 0.01,
        'min_withdraw': 30,
        'rate_to_ec': 650.00,
        'icon': '🔶',
        'color': '#F3BA2F',
        'confirmation_blocks': 15
    },
    'ltc': {
        'name': 'Litecoin',
        'full_name': 'Litecoin',
        'network': 'litecoin',
        'network_name': 'Litecoin Network',
        'symbol': 'LTC',
        'decimals': 8,
        'min_deposit': 0.01,
        'min_withdraw': 15,
        'rate_to_ec': 85.00,
        'icon': 'Ł',
        'color': '#BFBBBB',
        'confirmation_blocks': 6
    }
}

# Derivation Paths for Wallet Generation
DERIVATION_PATHS = {
    'bitcoin': "m/44'/0'/0'/0",
    'ethereum': "m/44'/60'/0'/0",
    'tron': "m/44'/195'/0'/0",
    'ton': "m/44'/607'/0'/0",
    'bsc': "m/44'/60'/0'/0",
    'litecoin': "m/44'/2'/0'/0"
}

# Referral System Configuration
REFERRAL_SYSTEM = {
    'enabled': True,
    'levels': {
        1: {'percentage': 0.05, 'name': 'Direct Referral'},  # 5%
        2: {'percentage': 0.02, 'name': 'Second Level'},     # 2%
        3: {'percentage': 0.01, 'name': 'Third Level'}       # 1%
    },
    'min_bet_for_referral': 5.0,
    'max_referral_bonus': 1000.0
}

# Task System Configuration
TASK_SYSTEM = {
    'enabled': True,
    'max_active_tasks': 8,
    'daily_refresh': True,
    'difficulty_levels': {
        'beginner': {'max_games': 20, 'max_bets': 100},
        'intermediate': {'max_games': 100, 'max_bets': 1000},
        'advanced': {'max_games': 500, 'max_bets': 10000},
        'expert': {'max_games': float('inf'), 'max_bets': float('inf')}
    },
    'task_categories': {
        'daily': {'reward_multiplier': 1.0, 'refresh_hours': 24},
        'weekly': {'reward_multiplier': 2.0, 'refresh_hours': 168},
        'achievement': {'reward_multiplier': 5.0, 'refresh_hours': None}
    }
}

# Security Configuration
SECURITY = {
    'max_daily_withdrawal': 50000,
    'max_single_bet': 10000,
    'rate_limit_requests_per_minute': 60,
    'anti_fraud_enabled': True,
    'min_account_age_for_withdrawal': 24,  # hours
    'require_2fa_for_large_withdrawals': True,
    'large_withdrawal_threshold': 1000
}

# Performance Configuration
PERFORMANCE = {
    'cache_user_data_seconds': 300,
    'max_concurrent_games': 1000,
    'database_connection_pool': 50,
    'auto_save_interval_seconds': 30,
    'cleanup_old_data_days': 90
}

# UI/UX Configuration
UI_CONFIG = {
    'theme': 'neon',
    'animations_enabled': True,
    'sound_enabled': True,
    'haptic_feedback': True,
    'auto_play_enabled': False,
    'max_bet_buttons': 8,
    'default_language': 'en'
}

# Bot Commands Configuration
BOT_COMMANDS = [
    {"command": "start", "description": "🎰 Start playing Neon Casino"},
    {"command": "games", "description": "🎮 View all casino games"},
    {"command": "stats", "description": "📊 View your statistics"},
    {"command": "deposit", "description": "💰 Deposit cryptocurrency"},
    {"command": "withdraw", "description": "💸 Withdraw your winnings"},
    {"command": "referral", "description": "👥 Get your referral link"},
    {"command": "tasks", "description": "📋 View daily tasks"},
    {"command": "vip", "description": "👑 VIP program information"},
    {"command": "help", "description": "❓ Help and game rules"}
]

# VIP System Configuration
VIP_SYSTEM = {
    'enabled': True,
    'levels': {
        'bronze': {'min_wagered': 0, 'bonus_percentage': 0, 'color': '#CD7F32'},
        'silver': {'min_wagered': 1000, 'bonus_percentage': 5, 'color': '#C0C0C0'},
        'gold': {'min_wagered': 10000, 'bonus_percentage': 10, 'color': '#FFD700'},
        'platinum': {'min_wagered': 50000, 'bonus_percentage': 15, 'color': '#E5E4E2'},
        'diamond': {'min_wagered': 200000, 'bonus_percentage': 25, 'color': '#B9F2FF'}
    }
}

# Achievement System
ACHIEVEMENTS = {
    'first_win': {'reward': 25, 'icon': '🎉', 'name': 'First Victory'},
    'high_roller': {'reward': 100, 'icon': '💎', 'name': 'High Roller'},
    'lucky_seven': {'reward': 77, 'icon': '🍀', 'name': 'Lucky Seven'},
    'streak_master': {'reward': 200, 'icon': '🔥', 'name': 'Streak Master'},
    'jackpot_winner': {'reward': 500, 'icon': '💰', 'name': 'Jackpot Winner'},
    'referral_king': {'reward': 300, 'icon': '👑', 'name': 'Referral King'},
    'daily_player': {'reward': 50, 'icon': '📅', 'name': 'Daily Player'},
    'vip_member': {'reward': 1000, 'icon': '💎', 'name': 'VIP Member'}
}

# Error Messages
ERROR_MESSAGES = {
    'insufficient_balance': '💸 Insufficient balance! Please deposit more funds.',
    'bet_too_low': '📉 Bet amount is too low! Minimum bet is {min_bet} EC.',
    'bet_too_high': '📈 Bet amount is too high! Maximum bet is {max_bet} EC.',
    'game_in_progress': '🎮 Game already in progress! Please wait.',
    'invalid_crypto': '❌ Invalid cryptocurrency selected.',
    'withdrawal_limit': '🚫 Daily withdrawal limit exceeded.',
    'address_invalid': '📍 Invalid wallet address format.',
    'maintenance': '🔧 Casino is under maintenance. Please try again later.',
    'rate_limit': '⏰ Too many requests. Please slow down.',
    'account_suspended': '🚫 Your account has been suspended. Contact support.'
}

# Success Messages  
SUCCESS_MESSAGES = {
    'deposit_confirmed': '✅ Deposit confirmed! {amount} EC added to your balance.',
    'withdrawal_processed': '💸 Withdrawal processed! Funds sent to your wallet.',
    'level_up': '🎉 Congratulations! You reached {level} level!',
    'achievement_unlocked': '🏆 Achievement unlocked: {achievement}!',
    'referral_bonus': '👥 Referral bonus received: {amount} EC!',
    'task_completed': '✅ Task completed! Reward: {reward} EC.',
    'jackpot_won': '🎰 JACKPOT! You won {amount} EC!',
    'vip_promotion': '👑 Welcome to VIP {level}! Enjoy your benefits.'
}

# Development Settings
DEBUG_MODE = False
LOG_LEVEL = 'INFO'
ENABLE_ANALYTICS = True
TEST_MODE = False

# External APIs (Optional)
EXTERNAL_APIS = {
    'crypto_prices': 'https://api.coingecko.com/api/v3/simple/price',
    'exchange_rates': 'https://api.exchangerate-api.com/v4/latest/USD',
    'blockchain_explorer': {
        'bitcoin': 'https://blockstream.info/api',
        'ethereum': 'https://api.etherscan.io/api',
        'tron': 'https://api.trongrid.io'
    }
}
