# =============================================================================
# NEON CASINO - ENTERPRISE TELEGRAM BOT
# =============================================================================

import asyncio
import logging
import sys
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, WebAppInfo, InlineKeyboardMarkup, 
    InlineKeyboardButton, CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Crypto utilities
from crypto_utils import (
    get_user_wallet_address, get_all_user_wallets, 
    validate_crypto_address, get_supported_cryptos,
    calculate_deposit_ec, calculate_withdrawal_crypto
)

# Configuration imports
try:
    from config import (
        BOT_TOKEN, WEB_APP_URL, BOT_USERNAME, WELCOME_BONUS,
        CASINO_GAMES, REFERRAL_SYSTEM, TASK_SYSTEM, VIP_SYSTEM,
        ACHIEVEMENTS, ERROR_MESSAGES, SUCCESS_MESSAGES, BOT_COMMANDS,
        SECURITY, PERFORMANCE, SUPPORTED_CRYPTOS, FIREBASE_PROJECT_ID
    )
except ImportError:
    logging.error("Configuration import failed. Check config.py")
    sys.exit(1)

# Initialize Firebase
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("neonrollfirebase-service-account.json")
        firebase_admin.initialize_app(cred, {
            'projectId': FIREBASE_PROJECT_ID
        })
    db = firestore.client()
    logging.info("✅ Firebase initialized successfully")
except Exception as e:
    logging.error(f"❌ Firebase initialization failed: {e}")
    sys.exit(1)

# Initialize bot
bot = Bot(
    token=BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Global variables
active_games = {}
rate_limits = {}

class NeonCasinoBot:
    """Main casino bot class with enterprise features"""
    
    def __init__(self):
        self.games = CasinoGames()
        self.user_manager = UserManager()
        self.crypto_manager = CryptoManager()
        self.task_manager = TaskManager()
        self.security = SecurityManager()
        
    async def start(self):
        """Start the bot with proper initialization"""
        try:
            await self.setup_bot_commands()
            await self.setup_webhooks()
            logging.info("🎰 Neon Casino Bot started successfully!")
            await dp.start_polling(bot, skip_updates=True)
        except Exception as e:
            logging.error(f"Failed to start bot: {e}")
            raise

    async def setup_bot_commands(self):
        """Setup bot commands and description"""
        try:
            commands = [
                types.BotCommand(command=cmd["command"], description=cmd["description"])
                for cmd in BOT_COMMANDS
            ]
            await bot.set_my_commands(commands)
            await bot.set_my_description("🎰 Welcome to Neon Casino - The Ultimate Crypto Gaming Experience! 🎰")
            await bot.set_my_short_description("🎮 Play & Win Big in Neon Casino!")
            logging.info("Bot commands configured")
        except Exception as e:
            logging.error(f"Error setting bot commands: {e}")

    async def setup_webhooks(self):
        """Setup webhook if needed"""
        pass  # Polling mode for now


class UserManager:
    """Manages user data and operations"""
    
    async def get_user_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from Firebase"""
        try:
            doc_ref = db.collection('users').document(str(user_id))
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                logging.info(f"User {user_id} data loaded")
                return data
            return None
        except Exception as e:
            logging.error(f"Error loading user {user_id}: {e}")
            return None

    async def save_user_data(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Save user data to Firebase"""
        try:
            doc_ref = db.collection('users').document(str(user_id))
            data['last_updated'] = datetime.now().isoformat()
            doc_ref.set(data, merge=True)
            return True
        except Exception as e:
            logging.error(f"Error saving user {user_id}: {e}")
            return False

    async def create_user(self, user: types.User, referrer_id: Optional[int] = None) -> Dict[str, Any]:
        """Create new user with welcome bonus"""
        try:
            # Generate crypto wallets
            user_wallets = get_all_user_wallets(user.id)
            
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'balance': float(WELCOME_BONUS),
                'total_wagered': 0.0,
                'total_won': 0.0,
                'games_played': 0,
                'referrer_id': referrer_id,
                'referral_earnings': 0.0,
                'vip_level': 'bronze',
                'achievements': [],
                'daily_streak': 1,
                'last_daily_bonus': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat(),
                'crypto_wallets': user_wallets,
                'game_stats': {
                    'neon_roll': {'played': 0, 'won': 0, 'total_bet': 0.0},
                    'neon_dice': {'played': 0, 'won': 0, 'total_bet': 0.0},
                    'neon_slots': {'played': 0, 'won': 0, 'total_bet': 0.0},
                    'neon_crash': {'played': 0, 'won': 0, 'total_bet': 0.0}
                },
                'preferences': {
                    'language': 'en',
                    'notifications': True,
                    'auto_play': False
                }
            }
            
            success = await self.save_user_data(user.id, user_data)
            if success and referrer_id:
                await self.process_referral(referrer_id, user.id)
            
            return user_data
        except Exception as e:
            logging.error(f"Error creating user {user.id}: {e}")
            return {}

    async def process_referral(self, referrer_id: int, new_user_id: int):
        """Process referral system"""
        try:
            referrer_data = await self.get_user_data(referrer_id)
            if not referrer_data:
                return
            
            # Track referral
            referrals = referrer_data.get('referrals', [])
            referrals.append({
                'user_id': new_user_id,
                'joined_at': datetime.now().isoformat(),
                'total_earned': 0.0
            })
            referrer_data['referrals'] = referrals
            
            await self.save_user_data(referrer_id, referrer_data)
            
            # Notify referrer
            try:
                await bot.send_message(
                    referrer_id,
                    f"🎉 New referral! Someone joined using your link!\n"
                    f"💰 You'll earn from their bets!"
                )
            except:
                pass
                
        except Exception as e:
            logging.error(f"Error processing referral: {e}")


class CasinoGames:
    """Manages all casino games"""
    
    def __init__(self):
        self.games = CASINO_GAMES
        
    def calculate_outcome(self, game: str, bet_data: Dict) -> Dict:
        """Calculate game outcome with proper house edge"""
        try:
            if game == 'neon_roll':
                return self._calculate_neon_roll(bet_data)
            elif game == 'neon_dice':
                return self._calculate_neon_dice(bet_data)
            elif game == 'neon_slots':
                return self._calculate_neon_slots(bet_data)
            elif game == 'neon_crash':
                return self._calculate_neon_crash(bet_data)
            else:
                raise ValueError(f"Unknown game: {game}")
        except Exception as e:
            logging.error(f"Error calculating outcome for {game}: {e}")
            return {'won': False, 'amount': 0, 'multiplier': 0}

    def _calculate_neon_roll(self, bet_data: Dict) -> Dict:
        """Calculate Neon Roll outcome"""
        colors = self.games['neon_roll']['colors']
        
        # Generate random number
        rand = random.random()
        cumulative = 0
        
        for color, data in colors.items():
            cumulative += data['probability']
            if rand <= cumulative:
                winning_color = color
                break
        else:
            winning_color = 'red'  # Fallback
        
        # Check if user won
        bet_color = bet_data.get('color')
        bet_amount = bet_data.get('amount', 0)
        
        if bet_color == winning_color:
            multiplier = colors[winning_color]['multiplier']
            win_amount = bet_amount * multiplier
            return {
                'won': True,
                'winning_color': winning_color,
                'multiplier': multiplier,
                'amount': win_amount,
                'bet_amount': bet_amount
            }
        
        return {
            'won': False,
            'winning_color': winning_color,
            'multiplier': 0,
            'amount': 0,
            'bet_amount': bet_amount
        }

    def _calculate_neon_dice(self, bet_data: Dict) -> Dict:
        """Calculate Neon Dice outcome"""
        roll = random.randint(1, 100)
        bet_type = bet_data.get('type')
        bet_amount = bet_data.get('amount', 0)
        
        outcomes = self.games['neon_dice']['outcomes']
        
        if bet_type == 'under_50' and roll < 50:
            multiplier = outcomes['under_50']['multiplier']
        elif bet_type == 'over_50' and roll > 50:
            multiplier = outcomes['over_50']['multiplier']
        elif bet_type == 'exact_50' and roll == 50:
            multiplier = outcomes['exact_50']['multiplier']
        else:
            multiplier = 0
            
        won = multiplier > 0
        win_amount = bet_amount * multiplier if won else 0
        
        return {
            'won': won,
            'roll': roll,
            'multiplier': multiplier,
            'amount': win_amount,
            'bet_amount': bet_amount
        }

    def _calculate_neon_slots(self, bet_data: Dict) -> Dict:
        """Calculate Neon Slots outcome"""
        symbols = list(self.games['neon_slots']['symbols'].keys())
        
        # Generate 3 reels
        reels = []
        for _ in range(3):
            rand = random.random()
            cumulative = 0
            for symbol, data in self.games['neon_slots']['symbols'].items():
                cumulative += data['probability']
                if rand <= cumulative:
                    reels.append(symbol)
                    break
            else:
                reels.append('🍒')  # Fallback
        
        bet_amount = bet_data.get('amount', 0)
        
        # Check for winning combinations
        if len(set(reels)) == 1:  # All same
            symbol = reels[0]
            multiplier = self.games['neon_slots']['symbols'][symbol]['multiplier']
            win_amount = bet_amount * multiplier
            won = True
        else:
            multiplier = 0
            win_amount = 0
            won = False
            
        return {
            'won': won,
            'reels': reels,
            'multiplier': multiplier,
            'amount': win_amount,
            'bet_amount': bet_amount
        }

    def _calculate_neon_crash(self, bet_data: Dict) -> Dict:
        """Calculate Neon Crash outcome"""
        # Simplified crash game
        crash_point = random.uniform(1.0, 10.0)
        cash_out = bet_data.get('cash_out', 0)
        bet_amount = bet_data.get('amount', 0)
        
        if cash_out > 0 and cash_out <= crash_point:
            multiplier = cash_out
            win_amount = bet_amount * multiplier
            won = True
        else:
            multiplier = 0
            win_amount = 0
            won = False
            
        return {
            'won': won,
            'crash_point': round(crash_point, 2),
            'cash_out': cash_out,
            'multiplier': multiplier,
            'amount': win_amount,
            'bet_amount': bet_amount
        }


class CryptoManager:
    """Manages cryptocurrency operations"""
    
    async def get_deposit_address(self, user_id: int, crypto_id: str) -> Optional[str]:
        """Get deposit address for user"""
        try:
            address = get_user_wallet_address(crypto_id, user_id)
            return address
        except Exception as e:
            logging.error(f"Error getting deposit address: {e}")
            return None

    async def process_deposit(self, user_id: int, crypto_id: str, amount: float) -> bool:
        """Process cryptocurrency deposit"""
        try:
            # Calculate EC amount
            ec_amount = calculate_deposit_ec(amount, crypto_id)
            
            if ec_amount <= 0:
                return False
            
            # Update user balance
            user_manager = UserManager()
            user_data = await user_manager.get_user_data(user_id)
            if not user_data:
                return False
                
            user_data['balance'] = user_data.get('balance', 0) + ec_amount
            
            # Log transaction
            transaction = {
                'user_id': user_id,
                'type': 'deposit',
                'crypto_id': crypto_id,
                'crypto_amount': amount,
                'ec_amount': ec_amount,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            }
            
            # Save to database
            db.collection('transactions').add(transaction)
            await user_manager.save_user_data(user_id, user_data)
            
            return True
        except Exception as e:
            logging.error(f"Error processing deposit: {e}")
            return False


class TaskManager:
    """Manages daily tasks and achievements"""
    
    async def generate_daily_tasks(self, user_id: int) -> List[Dict]:
        """Generate daily tasks for user"""
        try:
            tasks = [
                {
                    'id': 'daily_win',
                    'title': 'Win any game',
                    'description': 'Win at least one game today',
                    'reward': 25,
                    'target': 1,
                    'progress': 0,
                    'type': 'win'
                },
                {
                    'id': 'daily_bet',
                    'title': 'Place 10 bets',
                    'description': 'Place 10 bets of any amount',
                    'reward': 20,
                    'target': 10,
                    'progress': 0,
                    'type': 'bet_count'
                },
                {
                    'id': 'daily_wager',
                    'title': 'Wager 100 EC',
                    'description': 'Wager a total of 100 EC',
                    'reward': 30,
                    'target': 100,
                    'progress': 0,
                    'type': 'wager'
                }
            ]
            
            return tasks
        except Exception as e:
            logging.error(f"Error generating tasks: {e}")
            return []


class SecurityManager:
    """Manages security and anti-fraud"""
    
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is rate limited"""
        now = time.time()
        user_requests = rate_limits.get(user_id, [])
        
        # Remove old requests (older than 1 minute)
        user_requests = [req for req in user_requests if now - req < 60]
        
        # Check limit
        if len(user_requests) >= SECURITY['rate_limit_requests_per_minute']:
            return False
            
        # Add current request
        user_requests.append(now)
        rate_limits[user_id] = user_requests
        
        return True

    def validate_bet_amount(self, amount: float, game: str) -> Tuple[bool, str]:
        """Validate bet amount"""
        game_config = CASINO_GAMES.get(game, {})
        min_bet = game_config.get('min_bet', 1.0)
        max_bet = game_config.get('max_bet', 1000.0)
        
        if amount < min_bet:
            return False, f"Minimum bet is {min_bet} EC"
        if amount > max_bet:
            return False, f"Maximum bet is {max_bet} EC"
            
        return True, ""


# Initialize the casino bot
casino_bot = NeonCasinoBot()
user_manager = UserManager()

# Message handlers
@dp.message(CommandStart())
async def start_handler(message: Message):
    """Enhanced start command with referral support"""
    try:
        user = message.from_user
        user_name = user.first_name or user.username or "Player"
        
        # Extract referrer ID
        referrer_id = None
        if message.text and len(message.text.split()) > 1:
            try:
                potential_referrer = message.text.split()[1]
                referrer_id = int(potential_referrer) if potential_referrer.isdigit() else None
                if referrer_id == user.id:
                    referrer_id = None
            except (ValueError, IndexError):
                referrer_id = None
        
        # Get or create user
        user_data = await user_manager.get_user_data(user.id)
        
        if not user_data:
            user_data = await user_manager.create_user(user, referrer_id)
            welcome_text = (
                f"🎰 <b>Welcome to Neon Casino, {user_name}!</b>\n\n"
                f"🎁 You've received <b>{WELCOME_BONUS} EC</b> as welcome bonus!\n\n"
            )
            if referrer_id:
                welcome_text += "👥 You were referred by a friend!\n\n"
        else:
            user_data['last_login'] = datetime.now().isoformat()
            await user_manager.save_user_data(user.id, user_data)
            
            balance = user_data.get('balance', 0)
            welcome_text = (
                f"🎰 <b>Welcome back, {user_name}!</b>\n\n"
                f"💰 Balance: <b>{balance:.2f} EC</b>\n\n"
            )
        
        # Create main menu
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Play Games", web_app=WebAppInfo(url=WEB_APP_URL))],
            [
                InlineKeyboardButton(text="🎰 Neon Roll", callback_data="game_neon_roll"),
                InlineKeyboardButton(text="🎲 Neon Dice", callback_data="game_neon_dice")
            ],
            [
                InlineKeyboardButton(text="🎰 Slots", callback_data="game_neon_slots"),
                InlineKeyboardButton(text="📈 Crash", callback_data="game_neon_crash")
            ],
            [
                InlineKeyboardButton(text="💰 Deposit", callback_data="deposit"),
                InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton(text="👥 Referrals", callback_data="referrals"),
                InlineKeyboardButton(text="📊 Stats", callback_data="stats")
            ]
        ])
        
        await message.answer(
            welcome_text +
            "🎯 <b>Available Games:</b>\n"
            "🎰 Neon Roll - Classic color betting\n"
            "🎲 Neon Dice - Predict the roll\n"
            "🎰 Neon Slots - Match the symbols\n"
            "📈 Neon Crash - Cash out before crash\n\n"
            "💎 <b>Features:</b>\n"
            "• Instant crypto deposits/withdrawals\n"
            "• Multi-level referral system\n"
            "• Daily tasks and achievements\n"
            "• VIP program with exclusive benefits\n\n"
            "Choose an option below to get started!",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logging.error(f"Error in start handler: {e}")
        await message.answer("⚠️ Something went wrong. Please try again.")

@dp.callback_query(F.data.startswith("game_"))
async def game_handler(callback: CallbackQuery):
    """Handle game selection"""
    try:
        await callback.answer()
        
        game_name = callback.data.split("_", 1)[1]
        user_id = callback.from_user.id
        
        if not casino_bot.security.check_rate_limit(user_id):
            await callback.message.answer("⏰ Please slow down! Too many requests.")
            return
        
        # Get user data
        user_data = await user_manager.get_user_data(user_id)
        if not user_data:
            await callback.message.answer("❌ Please use /start first")
            return
        
        balance = user_data.get('balance', 0)
        
        # Game-specific interfaces
        if game_name == "neon_roll":
            await show_neon_roll_game(callback.message, balance)
        elif game_name == "neon_dice":
            await show_neon_dice_game(callback.message, balance)
        elif game_name == "neon_slots":
            await show_neon_slots_game(callback.message, balance)
        elif game_name == "neon_crash":
            await show_neon_crash_game(callback.message, balance)
        
    except Exception as e:
        logging.error(f"Error in game handler: {e}")
        await callback.message.answer("⚠️ Game error. Please try again.")

async def show_neon_roll_game(message: Message, balance: float):
    """Show Neon Roll game interface"""
    try:
        colors = CASINO_GAMES['neon_roll']['colors']
        
        text = (
            "🎰 <b>NEON ROLL</b>\n\n"
            f"💰 Your Balance: <b>{balance:.2f} EC</b>\n\n"
            "🎯 Choose your color and bet amount:\n\n"
        )
        
        for color, data in colors.items():
            emoji = {'red': '🔴', 'blue': '🔵', 'green': '🟢', 'yellow': '🟡'}
            text += f"{emoji.get(color, '⚪')} {color.title()}: {data['multiplier']}x ({data['probability']*100:.0f}%)\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 Red 2x", callback_data="bet_neon_roll_red_5"),
                InlineKeyboardButton(text="🔵 Blue 2x", callback_data="bet_neon_roll_blue_5")
            ],
            [
                InlineKeyboardButton(text="🟢 Green 5x", callback_data="bet_neon_roll_green_5"),
                InlineKeyboardButton(text="🟡 Yellow 45x", callback_data="bet_neon_roll_yellow_5")
            ],
            [
                InlineKeyboardButton(text="💰 Custom Bet", callback_data="custom_bet_neon_roll")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        await message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error showing neon roll: {e}")

async def show_neon_dice_game(message: Message, balance: float):
    """Show Neon Dice game interface"""
    try:
        text = (
            "🎲 <b>NEON DICE</b>\n\n"
            f"💰 Your Balance: <b>{balance:.2f} EC</b>\n\n"
            "🎯 Predict the dice roll (1-100):\n\n"
            "📉 Under 50: 1.98x (49.5% chance)\n"
            "📈 Over 50: 1.98x (49.5% chance)\n"
            "🎯 Exactly 50: 99x (1% chance)\n"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📉 Under 50", callback_data="bet_neon_dice_under_50_5"),
                InlineKeyboardButton(text="📈 Over 50", callback_data="bet_neon_dice_over_50_5")
            ],
            [
                InlineKeyboardButton(text="🎯 Exactly 50", callback_data="bet_neon_dice_exact_50_5")
            ],
            [
                InlineKeyboardButton(text="💰 Custom Bet", callback_data="custom_bet_neon_dice")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        await message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error showing neon dice: {e}")

async def show_neon_slots_game(message: Message, balance: float):
    """Show Neon Slots game interface"""
    try:
        text = (
            "🎰 <b>NEON SLOTS</b>\n\n"
            f"💰 Your Balance: <b>{balance:.2f} EC</b>\n\n"
            "🎯 Match 3 symbols to win:\n\n"
            "🍒 Cherry: 2x\n"
            "🍋 Lemon: 3x\n"
            "🍊 Orange: 5x\n"
            "⭐ Star: 10x\n"
            "💎 Diamond: 25x\n"
            "🎰 Jackpot: 100x\n"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🎰 Spin (5 EC)", callback_data="bet_neon_slots_spin_5"),
                InlineKeyboardButton(text="🎰 Spin (10 EC)", callback_data="bet_neon_slots_spin_10")
            ],
            [
                InlineKeyboardButton(text="🎰 Spin (25 EC)", callback_data="bet_neon_slots_spin_25"),
                InlineKeyboardButton(text="🎰 Spin (50 EC)", callback_data="bet_neon_slots_spin_50")
            ],
            [
                InlineKeyboardButton(text="💰 Custom Bet", callback_data="custom_bet_neon_slots")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        await message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error showing neon slots: {e}")

async def show_neon_crash_game(message: Message, balance: float):
    """Show Neon Crash game interface"""
    try:
        text = (
            "📈 <b>NEON CRASH</b>\n\n"
            f"💰 Your Balance: <b>{balance:.2f} EC</b>\n\n"
            "🚀 Watch the multiplier rise and cash out before it crashes!\n\n"
            "🎯 The higher you wait, the more you can win\n"
            "⚠️ But if it crashes before you cash out, you lose everything\n\n"
            "💡 Tip: Cash out early for safer wins!"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Start Game", callback_data="start_crash_5")
            ],
            [
                InlineKeyboardButton(text="💰 Custom Bet", callback_data="custom_bet_neon_crash")
            ],
            [
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        await message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error showing neon crash: {e}")

@dp.callback_query(F.data.startswith("bet_"))
async def bet_handler(callback: CallbackQuery):
    """Handle game bets"""
    try:
        await callback.answer()
        
        # Parse bet data: bet_game_type_amount or bet_game_color_amount
        parts = callback.data.split("_")
        if len(parts) < 4:
            await callback.message.answer("❌ Invalid bet format")
            return
            
        game = parts[1]
        bet_type = parts[2]
        amount = float(parts[3])
        
        user_id = callback.from_user.id
        
        # Security checks
        if not casino_bot.security.check_rate_limit(user_id):
            await callback.message.answer("⏰ Please slow down!")
            return
            
        valid, error_msg = casino_bot.security.validate_bet_amount(amount, game)
        if not valid:
            await callback.message.answer(f"❌ {error_msg}")
            return
        
        # Get user data
        user_data = await user_manager.get_user_data(user_id)
        if not user_data:
            await callback.message.answer("❌ Please use /start first")
            return
            
        balance = user_data.get('balance', 0)
        if balance < amount:
            await callback.message.answer(f"💸 Insufficient balance! You need {amount} EC but have {balance:.2f} EC")
            return
        
        # Process the bet
        if game == "neon":
            if len(parts) >= 5:  # neon_roll_color_amount
                game = f"{parts[1]}_{parts[2]}"  # neon_roll
                color = parts[3]
                amount = float(parts[4])
                bet_data = {'color': color, 'amount': amount}
            else:
                bet_data = {'type': bet_type, 'amount': amount}
        else:
            bet_data = {'type': bet_type, 'amount': amount}
        
        # Calculate outcome
        outcome = casino_bot.games.calculate_outcome(game, bet_data)
        
        # Update user balance
        if outcome['won']:
            new_balance = balance - amount + outcome['amount']
            user_data['total_won'] = user_data.get('total_won', 0) + outcome['amount']
        else:
            new_balance = balance - amount
            
        user_data['balance'] = new_balance
        user_data['total_wagered'] = user_data.get('total_wagered', 0) + amount
        user_data['games_played'] = user_data.get('games_played', 0) + 1
        
        # Update game stats
        game_stats = user_data.get('game_stats', {}).get(game, {'played': 0, 'won': 0, 'total_bet': 0.0})
        game_stats['played'] += 1
        game_stats['total_bet'] += amount
        if outcome['won']:
            game_stats['won'] += 1
        
        if 'game_stats' not in user_data:
            user_data['game_stats'] = {}
        user_data['game_stats'][game] = game_stats
        
        await user_manager.save_user_data(user_id, user_data)
        
        # Send result
        await send_game_result(callback.message, game, outcome, new_balance)
        
    except Exception as e:
        logging.error(f"Error in bet handler: {e}")
        await callback.message.answer("⚠️ Bet processing error. Please try again.")

async def send_game_result(message: Message, game: str, outcome: Dict, new_balance: float):
    """Send game result to user"""
    try:
        if game == "neon_roll":
            color_emoji = {'red': '🔴', 'blue': '🔵', 'green': '🟢', 'yellow': '🟡'}
            winning_color = outcome.get('winning_color', 'red')
            
            if outcome['won']:
                result_text = (
                    f"🎉 <b>YOU WON!</b>\n\n"
                    f"🎰 Winning Color: {color_emoji.get(winning_color, '⚪')} {winning_color.title()}\n"
                    f"💰 Won: <b>{outcome['amount']:.2f} EC</b> ({outcome['multiplier']}x)\n"
                    f"💳 New Balance: <b>{new_balance:.2f} EC</b>"
                )
            else:
                result_text = (
                    f"😔 <b>YOU LOST</b>\n\n"
                    f"🎰 Winning Color: {color_emoji.get(winning_color, '⚪')} {winning_color.title()}\n"
                    f"💸 Lost: <b>{outcome['bet_amount']:.2f} EC</b>\n"
                    f"💳 New Balance: <b>{new_balance:.2f} EC</b>"
                )
                
        elif game == "neon_dice":
            roll = outcome.get('roll', 0)
            
            if outcome['won']:
                result_text = (
                    f"🎉 <b>YOU WON!</b>\n\n"
                    f"🎲 Roll: <b>{roll}</b>\n"
                    f"💰 Won: <b>{outcome['amount']:.2f} EC</b> ({outcome['multiplier']}x)\n"
                    f"💳 New Balance: <b>{new_balance:.2f} EC</b>"
                )
            else:
                result_text = (
                    f"😔 <b>YOU LOST</b>\n\n"
                    f"🎲 Roll: <b>{roll}</b>\n"
                    f"💸 Lost: <b>{outcome['bet_amount']:.2f} EC</b>\n"
                    f"💳 New Balance: <b>{new_balance:.2f} EC</b>"
                )
                
        elif game == "neon_slots":
            reels = outcome.get('reels', ['🍒', '🍒', '🍒'])
            
            if outcome['won']:
                result_text = (
                    f"🎰 <b>JACKPOT!</b>\n\n"
                    f"🎰 Reels: {' '.join(reels)}\n"
                    f"💰 Won: <b>{outcome['amount']:.2f} EC</b> ({outcome['multiplier']}x)\n"
                    f"💳 New Balance: <b>{new_balance:.2f} EC</b>"
                )
            else:
                result_text = (
                    f"🎰 <b>TRY AGAIN</b>\n\n"
                    f"🎰 Reels: {' '.join(reels)}\n"
                    f"💸 Lost: <b>{outcome['bet_amount']:.2f} EC</b>\n"
                    f"💳 New Balance: <b>{new_balance:.2f} EC</b>"
                )
        
        # Add play again buttons
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Play Again", callback_data=f"game_{game}"),
                InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
            ]
        ])
        
        await message.edit_text(result_text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error sending game result: {e}")

@dp.callback_query(F.data == "deposit")
async def deposit_handler(callback: CallbackQuery):
    """Handle deposit requests"""
    try:
        await callback.answer()
        
        user_id = callback.from_user.id
        user_data = await user_manager.get_user_data(user_id)
        
        if not user_data:
            await callback.message.answer("❌ Please use /start first")
            return
        
        text = (
            "💰 <b>DEPOSIT CRYPTOCURRENCY</b>\n\n"
            "Choose your preferred cryptocurrency:\n\n"
        )
        
        keyboard_rows = []
        for crypto_id, crypto_info in SUPPORTED_CRYPTOS.items():
            icon = crypto_info.get('icon', '💎')
            name = crypto_info.get('name', crypto_id.upper())
            rate = crypto_info.get('rate_to_ec', 1)
            
            text += f"{icon} {name}: 1 = {rate} EC\n"
            
            keyboard_rows.append([
                InlineKeyboardButton(
                    text=f"{icon} {name}", 
                    callback_data=f"deposit_{crypto_id}"
                )
            ])
        
        keyboard_rows.append([
            InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in deposit handler: {e}")

@dp.callback_query(F.data.startswith("deposit_"))
async def deposit_crypto_handler(callback: CallbackQuery):
    """Handle specific crypto deposit"""
    try:
        await callback.answer()
        
        crypto_id = callback.data.split("_")[1]
        user_id = callback.from_user.id
        
        if crypto_id not in SUPPORTED_CRYPTOS:
            await callback.message.answer("❌ Invalid cryptocurrency")
            return
        
        # Get deposit address
        address = await casino_bot.crypto_manager.get_deposit_address(user_id, crypto_id)
        if not address:
            await callback.message.answer("⚠️ Error generating deposit address")
            return
        
        crypto_info = SUPPORTED_CRYPTOS[crypto_id]
        
        text = (
            f"💰 <b>DEPOSIT {crypto_info['name']}</b>\n\n"
            f"🔗 Network: {crypto_info['network_name']}\n"
            f"📍 Deposit Address:\n"
            f"<code>{address}</code>\n\n"
            f"💱 Exchange Rate: 1 {crypto_info['symbol']} = {crypto_info['rate_to_ec']} EC\n"
            f"💰 Minimum Deposit: {crypto_info['min_deposit']} {crypto_info['symbol']}\n"
            f"⏰ Confirmations: {crypto_info['confirmation_blocks']}\n\n"
            f"⚠️ <b>Important:</b>\n"
            f"• Only send {crypto_info['name']} to this address\n"
            f"• Deposits are credited automatically\n"
            f"• Do not send from exchanges directly\n"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Address", callback_data=f"copy_{crypto_id}")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data=f"deposit_{crypto_id}")],
            [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in deposit crypto handler: {e}")

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    """Return to main menu"""
    try:
        await callback.answer()
        
        # Simulate the start command
        user = callback.from_user
        user_name = user.first_name or user.username or "Player"
        
        user_data = await user_manager.get_user_data(user.id)
        if not user_data:
            await callback.message.answer("❌ Please use /start first")
            return
        
        balance = user_data.get('balance', 0)
        
        welcome_text = (
            f"🎰 <b>Welcome back, {user_name}!</b>\n\n"
            f"💰 Balance: <b>{balance:.2f} EC</b>\n\n"
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎮 Play Games", web_app=WebAppInfo(url=WEB_APP_URL))],
            [
                InlineKeyboardButton(text="🎰 Neon Roll", callback_data="game_neon_roll"),
                InlineKeyboardButton(text="🎲 Neon Dice", callback_data="game_neon_dice")
            ],
            [
                InlineKeyboardButton(text="🎰 Slots", callback_data="game_neon_slots"),
                InlineKeyboardButton(text="📈 Crash", callback_data="game_neon_crash")
            ],
            [
                InlineKeyboardButton(text="💰 Deposit", callback_data="deposit"),
                InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton(text="👥 Referrals", callback_data="referrals"),
                InlineKeyboardButton(text="📊 Stats", callback_data="stats")
            ]
        ])
        
        await callback.message.edit_text(
            welcome_text +
            "🎯 <b>Available Games:</b>\n"
            "🎰 Neon Roll - Classic color betting\n"
            "🎲 Neon Dice - Predict the roll\n"
            "🎰 Neon Slots - Match the symbols\n"
            "📈 Neon Crash - Cash out before crash\n\n"
            "Choose an option below:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logging.error(f"Error in main menu handler: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('neon_casino.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    try:
        asyncio.run(casino_bot.start())
    except KeyboardInterrupt:
        logging.info("🛑 Bot stopped by user")
    except Exception as e:
        logging.error(f"💥 Fatal error: {e}")
        sys.exit(1)