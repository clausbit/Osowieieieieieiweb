# Bot Configuration
BOT_TOKEN = "7967948563:AAEcl-6mW5kd4jaqjsRIqnv34egBWmh1LiI"
WEB_APP_URL = "https://agrobmin.com.ua"

# Firebase Configuration
FIREBASE_PROJECT_ID = "neonroll-26174"

# Game Configuration
WELCOME_BONUS = 20.0
MIN_BET = 1.0
MAX_BET = 1000.0


MASTER_SEED_PHRASE = "nothing ridge argue engine loan boat dry radar wink universe remind fence"
# Crypto Configuration
CRYPTO_WALLETS = {
    'ton': 'UQBvI0aFLnw2QbZgjMPCLRdtRHxhUyinQudg6sdiohIwg5jL',
    'usdt': 'TXYZabcd1234567890ABCDEF1234567890abcdef',
    'btc': 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
}

# Supported Cryptocurrencies
SUPPORTED_CRYPTOS = {
    'ton': {
        'name': 'TON',
        'network': 'ton',
        'decimals': 9,
        'min_deposit': 1,
        'min_withdraw': 27,
        'rate_to_ec': 2.45
    },
    'usdt': {
        'name': 'USDT TRC20',
        'network': 'tron',
        'decimals': 6,
        'min_deposit': 5,
        'min_withdraw': 45,
        'rate_to_ec': 1.00
    },
    'tron': {
        'name': 'TRON',
        'network': 'tron',
        'decimals': 6,
        'min_deposit': 50,
        'min_withdraw': 15,
        'rate_to_ec': 0.15
    },
    'bnb': {
        'name': 'BNB BEP20',
        'network': 'bsc',
        'decimals': 18,
        'min_deposit': 0.01,
        'min_withdraw': 29,
        'rate_to_ec': 650.00
    },
    'btc': {
        'name': 'Bitcoin',
        'network': 'bitcoin',
        'decimals': 8,
        'min_deposit': 0.001,
        'min_withdraw': 100,
        'rate_to_ec': 45000
    },
    'doge': {
        'name': 'Dogecoin',
        'network': 'dogecoin',
        'decimals': 8,
        'min_deposit': 10,
        'min_withdraw': 41,
        'rate_to_ec': 0.35
    },
    'ltc': {
        'name': 'LiteCoin',
        'network': 'litecoin',
        'decimals': 8,
        'min_deposit': 0.1,
        'min_withdraw': 15,
        'rate_to_ec': 85.00
    },
    'usdc': {
        'name': 'USDC ERC20',
        'network': 'ethereum',
        'decimals': 6,
        'min_deposit': 5,
        'min_withdraw': 45,
        'rate_to_ec': 1.00
    }
}

# Wallet Generation Settings
DERIVATION_PATHS = {
    'bitcoin': "m/44'/0'/0'/0/0",
    'ethereum': "m/44'/60'/0'/0/0",
    'tron': "m/44'/195'/0'/0/0",
    'ton': "m/44'/607'/0'/0/0",
    'bsc': "m/44'/60'/0'/0/0",
    'dogecoin': "m/44'/3'/0'/0/0",
    'litecoin': "m/44'/2'/0'/0/0"
}

# Security Settings
ENCRYPTION_KEY = "your-encryption-key-here"  # For encrypting sensitive data
MAX_DAILY_WITHDRAWAL = 10000  # Maximum daily withdrawal in EC
MAX_TRANSACTION_AMOUNT = 50000  # Maximum single transaction in EC

# Performance Settings
MAX_CONCURRENT_USERS = 1000
CACHE_TIMEOUT = 300  # 5 minutes
DATABASE_POOL_SIZE = 20

# API Keys (optional)
GEMINI_API_KEY = ""  # Add your Gemini API key for AI features (removed from app)
