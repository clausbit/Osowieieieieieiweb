# Bot Configuration
BOT_TOKEN = "7967948563:AAEcl-6mW5kd4jaqjsRIqnv34egBWmh1LiI"
WEB_APP_URL = "https://agrobmin.com.ua"

# Firebase Configuration
FIREBASE_PROJECT_ID = "neonroll-26174"

# Game Configuration
WELCOME_BONUS = 20.0
MIN_BET = 1.0
MAX_BET = 1000.0

# Master seed phrase for wallet generation
MASTER_SEED_PHRASE = "nothing ridge argue engine loan boat dry radar wink universe remind fence"

# Crypto Configuration with proper wallet generation
CRYPTO_WALLETS = {
    'ton': 'UQBvI0aFLnw2QbZgjMPCLRdtRHxhUyinQudg6sdiohIwg5jL',
    'usdt': 'TXYZabcd1234567890ABCDEF1234567890abcdef',
    'btc': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
}

# Supported Cryptocurrencies with enhanced configuration
SUPPORTED_CRYPTOS = {
    'ton': {
        'name': 'TON',
        'full_name': 'Toncoin',
        'network': 'ton',
        'network_name': 'TON Network',
        'decimals': 9,
        'min_deposit': 1,
        'min_withdraw': 27,
        'rate_to_ec': 2.45,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/11419.png',
        'address_prefix': 'UQ',
        'confirmation_blocks': 1
    },
    'usdt': {
        'name': 'USDT TRC20',
        'full_name': 'Tether USD (TRC20)',
        'network': 'tron',
        'network_name': 'TRON Network',
        'decimals': 6,
        'min_deposit': 5,
        'min_withdraw': 45,
        'rate_to_ec': 1.00,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/825.png',
        'address_prefix': 'T',
        'confirmation_blocks': 1
    },
    'tron': {
        'name': 'TRON',
        'full_name': 'TRON',
        'network': 'tron',
        'network_name': 'TRON Network',
        'decimals': 6,
        'min_deposit': 50,
        'min_withdraw': 15,
        'rate_to_ec': 0.15,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/1958.png',
        'address_prefix': 'T',
        'confirmation_blocks': 1
    },
    'bnb': {
        'name': 'BNB BEP20',
        'full_name': 'Binance Coin (BEP20)',
        'network': 'bsc',
        'network_name': 'BSC Network',
        'decimals': 18,
        'min_deposit': 0.01,
        'min_withdraw': 29,
        'rate_to_ec': 650.00,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/1839.png',
        'address_prefix': '0x',
        'confirmation_blocks': 12
    },
    'btc': {
        'name': 'Bitcoin',
        'full_name': 'Bitcoin',
        'network': 'bitcoin',
        'network_name': 'Bitcoin Network',
        'decimals': 8,
        'min_deposit': 0.001,
        'min_withdraw': 100,
        'rate_to_ec': 45000,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/1.png',
        'address_prefix': 'bc1',
        'confirmation_blocks': 6
    },
    'eth': {
        'name': 'Ethereum',
        'full_name': 'Ethereum',
        'network': 'ethereum',
        'network_name': 'Ethereum Network',
        'decimals': 18,
        'min_deposit': 0.01,
        'min_withdraw': 85,
        'rate_to_ec': 2500.00,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png',
        'address_prefix': '0x',
        'confirmation_blocks': 12
    },
    'doge': {
        'name': 'Dogecoin',
        'full_name': 'Dogecoin',
        'network': 'dogecoin',
        'network_name': 'Dogecoin Network',
        'decimals': 8,
        'min_deposit': 10,
        'min_withdraw': 41,
        'rate_to_ec': 0.35,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/74.png',
        'address_prefix': 'D',
        'confirmation_blocks': 6
    },
    'ltc': {
        'name': 'Litecoin',
        'full_name': 'Litecoin',
        'network': 'litecoin',
        'network_name': 'Litecoin Network',
        'decimals': 8,
        'min_deposit': 0.1,
        'min_withdraw': 15,
        'rate_to_ec': 85.00,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/2.png',
        'address_prefix': 'ltc1',
        'confirmation_blocks': 6
    },
    'usdc': {
        'name': 'USDC ERC20',
        'full_name': 'USD Coin (ERC20)',
        'network': 'ethereum',
        'network_name': 'Ethereum Network',
        'decimals': 6,
        'min_deposit': 5,
        'min_withdraw': 45,
        'rate_to_ec': 1.00,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/3408.png',
        'address_prefix': '0x',
        'confirmation_blocks': 12
    },
    'ada': {
        'name': 'Cardano',
        'full_name': 'Cardano',
        'network': 'cardano',
        'network_name': 'Cardano Network',
        'decimals': 6,
        'min_deposit': 5,
        'min_withdraw': 35,
        'rate_to_ec': 0.45,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/2010.png',
        'address_prefix': 'addr',
        'confirmation_blocks': 5
    },
    'sol': {
        'name': 'Solana',
        'full_name': 'Solana',
        'network': 'solana',
        'network_name': 'Solana Network',
        'decimals': 9,
        'min_deposit': 0.1,
        'min_withdraw': 25,
        'rate_to_ec': 95.00,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/5426.png',
        'address_prefix': '',
        'confirmation_blocks': 1
    },
    'xrp': {
        'name': 'XRP',
        'full_name': 'XRP',
        'network': 'ripple',
        'network_name': 'XRP Ledger',
        'decimals': 6,
        'min_deposit': 20,
        'min_withdraw': 30,
        'rate_to_ec': 0.55,
        'icon': 'https://s2.coinmarketcap.com/static/img/coins/64x64/52.png',
        'address_prefix': 'r',
        'confirmation_blocks': 1
    }
}

# Wallet Generation Settings with enhanced derivation paths
DERIVATION_PATHS = {
    'bitcoin': "m/44'/0'/0'/0/0",
    'ethereum': "m/44'/60'/0'/0/0",
    'tron': "m/44'/195'/0'/0/0",
    'ton': "m/44'/607'/0'/0/0",
    'bsc': "m/44'/60'/0'/0/0",  # BSC uses same as Ethereum
    'dogecoin': "m/44'/3'/0'/0/0",
    'litecoin': "m/44'/2'/0'/0/0",
    'cardano': "m/44'/1815'/0'/0/0",
    'solana': "m/44'/501'/0'/0/0",
    'ripple': "m/44'/144'/0'/0/0"
}

# Enhanced Security Settings
ENCRYPTION_KEY = "neonroll-secure-key-2024"
MAX_DAILY_WITHDRAWAL = 10000
MAX_TRANSACTION_AMOUNT = 50000
TRANSACTION_FEE_PERCENTAGE = 0.02  # 2% transaction fee

# Enhanced Performance Settings
MAX_CONCURRENT_USERS = 2000
CACHE_TIMEOUT = 300
DATABASE_POOL_SIZE = 50
MAX_RETRY_ATTEMPTS = 3
CONNECTION_TIMEOUT = 30

# Game Settings
GAME_ROUNDS_PER_MINUTE = 6
BETTING_PHASE_DURATION = 10  # seconds
ROLLING_PHASE_DURATION = 4   # seconds
RESULT_PHASE_DURATION = 3    # seconds

# Referral System Settings
REFERRAL_LEVELS = {
    'level_1': {
        'percentage': 0.05,  # 5%
        'name': 'Direct Referral'
    },
    'level_2': {
        'percentage': 0.01,  # 1%
        'name': 'Second Level'
    },
    'level_3': {
        'percentage': 0.01,  # 1%
        'name': 'Third Level'
    }
}

# Task System Settings
DAILY_TASKS_LIMIT = 10
TASK_REWARD_MULTIPLIER = 1.5
SPECIAL_TASK_BONUS = 50

# Database Settings
DATABASE_BACKUP_INTERVAL = 3600  # 1 hour
USER_DATA_RETENTION_DAYS = 365
TRANSACTION_LOG_RETENTION_DAYS = 90

# API Settings
API_RATE_LIMIT = 1000  # requests per minute
API_KEY_ROTATION_INTERVAL = 86400  # 24 hours

# UI/UX Settings
ANIMATION_DURATION = 300  # milliseconds
PARTICLE_SYSTEM_MAX_PARTICLES = 50
SOUND_ENABLED_BY_DEFAULT = True
HAPTIC_FEEDBACK_ENABLED = True

# Monitoring and Analytics
ENABLE_ANALYTICS = True
ERROR_REPORTING_ENABLED = True
PERFORMANCE_MONITORING_ENABLED = True

# Development Settings
DEBUG_MODE = False
TESTING_MODE = False
MOCK_TRANSACTIONS = False

# Bot Settings
BOT_DESCRIPTION = "🎰 Neon Roll - The Ultimate Crypto Casino Experience! 🎰"
BOT_SHORT_DESCRIPTION = "Win big in our neon-powered casino!"
BOT_COMMANDS = [
    {"command": "start", "description": "🚀 Start playing Neon Roll"},
    {"command": "stats", "description": "📊 View your game statistics"},
    {"command": "help", "description": "❓ Get help and game rules"},
    {"command": "deposit", "description": "💰 Deposit cryptocurrency"},
    {"command": "withdraw", "description": "💸 Withdraw your winnings"},
    {"command": "referral", "description": "👥 Get your referral link"}
]
