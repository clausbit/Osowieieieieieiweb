import asyncio
import logging
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# Crypto utilities
from crypto_utils import get_user_wallet_address, get_all_user_wallets, validate_crypto_address, get_supported_cryptos

# --- Configuration ---
try:
    from config import (
        BOT_TOKEN, WEB_APP_URL, WELCOME_BONUS, REFERRAL_LEVELS, 
        SUPPORTED_CRYPTOS, BOT_COMMANDS, BOT_DESCRIPTION, 
        BOT_SHORT_DESCRIPTION, MASTER_SEED_PHRASE
    )
except ImportError:
    print("Error: Could not find config.py file.")
    print("Please make sure you ran the installation script start.sh")
    sys.exit(1)

# Initialize Firebase with better error handling
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("neonrollfirebase-service-account.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    sys.exit(1)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Enhanced User data management
class UserDataManager:
    @staticmethod
    async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data from Firebase with error handling"""
        try:
            doc_ref = db.collection('users').document(str(user_id))
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                logging.info(f"User {user_id} data retrieved from Firebase")
                return data
            return None
        except Exception as e:
            logging.error(f"Error getting user data for {user_id}: {e}")
            return None

    @staticmethod
    async def save_user_data(user_id: int, data: Dict[str, Any]) -> bool:
        """Save user data to Firebase with enhanced error handling"""
        try:
            doc_ref = db.collection('users').document(str(user_id))
            # Add timestamp for last update
            data['last_updated'] = datetime.now().isoformat()
            doc_ref.set(data, merge=True)
            logging.info(f"User {user_id} data saved to Firebase")
            return True
        except Exception as e:
            logging.error(f"Error saving user data for {user_id}: {e}")
            return False

    @staticmethod
    async def create_new_user(user: types.User, referrer_id: Optional[int] = None) -> Dict[str, Any]:
        """Create new user in Firebase with enhanced data structure"""
        try:
            # Generate crypto wallets for the user
            user_wallets = get_all_user_wallets(user.id)
            
            user_data = {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'balance': float(WELCOME_BONUS),
                'total_bets_placed': 0.0,
                'total_winnings': 0.0,
                'games_played': 0,
                'referrals': {'l1': 0, 'l2': 0, 'l3': 0},
                'referrer_id': referrer_id,
                'referral_earnings': 0.0,
                'tasks': [],
                'completed_tasks': [],
                'created_at': datetime.now().isoformat(),
                'last_login': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'is_new_user': True,
                'daily_login_streak': 1,
                'last_daily_bonus': datetime.now().isoformat(),
                'game_stats': {
                    'favorite_color': None,
                    'biggest_win': 0.0,
                    'total_deposits': 0.0,
                    'total_withdrawals': 0.0,
                    'win_rate': 0.0
                },
                'crypto_wallets': user_wallets,
                'deposit_history': [],
                'withdrawal_history': [],
                'bet_history': [],
                'preferences': {
                    'language': 'en',
                    'notifications': True,
                    'sound_enabled': True
                }
            }
            
            # Save user data
            success = await UserDataManager.save_user_data(user.id, user_data)
            if success:
                logging.info(f"New user {user.id} created successfully")
                # Handle referral if exists
                if referrer_id:
                    await UserDataManager.process_referral(referrer_id, user.id)
                return user_data
            else:
                logging.error(f"Failed to create new user {user.id}")
                return {}
                
        except Exception as e:
            logging.error(f"Error creating new user {user.id}: {e}")
            return {}

    @staticmethod
    async def process_referral(referrer_id: int, new_user_id: int) -> bool:
        """Process referral system with proper level tracking"""
        try:
            # Get referrer data
            referrer_data = await UserDataManager.get_user_data(referrer_id)
            if not referrer_data:
                return False
            
            # Update referrer's level 1 referrals
            referrer_data['referrals']['l1'] += 1
            
            # Process level 2 referrals
            if referrer_data.get('referrer_id'):
                level2_referrer_data = await UserDataManager.get_user_data(referrer_data['referrer_id'])
                if level2_referrer_data:
                    level2_referrer_data['referrals']['l2'] += 1
                    await UserDataManager.save_user_data(referrer_data['referrer_id'], level2_referrer_data)
                    
                    # Process level 3 referrals
                    if level2_referrer_data.get('referrer_id'):
                        level3_referrer_data = await UserDataManager.get_user_data(level2_referrer_data['referrer_id'])
                        if level3_referrer_data:
                            level3_referrer_data['referrals']['l3'] += 1
                            await UserDataManager.save_user_data(level2_referrer_data['referrer_id'], level3_referrer_data)
            
            # Save referrer data
            await UserDataManager.save_user_data(referrer_id, referrer_data)
            
            # Log referral activity
            await UserDataManager.log_referral_activity(referrer_id, new_user_id)
            
            return True
        except Exception as e:
            logging.error(f"Error processing referral {referrer_id} -> {new_user_id}: {e}")
            return False

    @staticmethod
    async def log_referral_activity(referrer_id: int, new_user_id: int):
        """Log referral activity for analytics"""
        try:
            activity_data = {
                'referrer_id': referrer_id,
                'new_user_id': new_user_id,
                'timestamp': datetime.now().isoformat(),
                'bonus_given': WELCOME_BONUS
            }
            
            db.collection('referral_activities').add(activity_data)
            logging.info(f"Referral activity logged: {referrer_id} -> {new_user_id}")
        except Exception as e:
            logging.error(f"Error logging referral activity: {e}")

    @staticmethod
    async def update_user_balance(user_id: int, amount: float, operation: str = 'add') -> bool:
        """Update user balance with transaction logging"""
        try:
            user_data = await UserDataManager.get_user_data(user_id)
            if not user_data:
                return False
            
            current_balance = float(user_data.get('balance', 0))
            
            if operation == 'add':
                new_balance = current_balance + amount
            elif operation == 'subtract':
                if current_balance < amount:
                    return False  # Insufficient funds
                new_balance = current_balance - amount
            else:
                return False
            
            user_data['balance'] = new_balance
            
            # Log transaction
            await UserDataManager.log_transaction(user_id, operation, amount, current_balance, new_balance)
            
            return await UserDataManager.save_user_data(user_id, user_data)
        except Exception as e:
            logging.error(f"Error updating balance for user {user_id}: {e}")
            return False

    @staticmethod
    async def log_transaction(user_id: int, operation: str, amount: float, old_balance: float, new_balance: float):
        """Log transaction for audit trail"""
        try:
            transaction_data = {
                'user_id': user_id,
                'operation': operation,
                'amount': amount,
                'old_balance': old_balance,
                'new_balance': new_balance,
                'timestamp': datetime.now().isoformat()
            }
            
            db.collection('transactions').add(transaction_data)
            logging.info(f"Transaction logged for user {user_id}: {operation} {amount}")
        except Exception as e:
            logging.error(f"Error logging transaction: {e}")

# Enhanced command handlers
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """Enhanced start command handler with better referral system"""
    try:
        user = message.from_user
        user_name = user.first_name or user.username or "Player"
        
        # Check if user exists in database
        user_data = await UserDataManager.get_user_data(user.id)
        
        # Extract referrer ID from deep link
        referrer_id = None
        if message.text and len(message.text.split()) > 1:
            try:
                potential_referrer = message.text.split()[1]
                referrer_id = int(potential_referrer) if potential_referrer.isdigit() else None
                if referrer_id == user.id:
                    referrer_id = None  # Can't refer yourself
            except (ValueError, IndexError):
                referrer_id = None
        
        if not user_data:
            # New user - create account with welcome bonus
            user_data = await UserDataManager.create_new_user(user, referrer_id)
            if user_data:
                welcome_text = f"🎉 Welcome to Neon Roll, <b>{user_name}</b>!\n\n" \
                              f"🎁 You've received <b>{WELCOME_BONUS} EC</b> as a welcome bonus!\n\n"
                
                if referrer_id:
                    welcome_text += f"👥 You were referred by a friend!\n\n"
                    
                    # Notify referrer
                    try:
                        await bot.send_message(
                            referrer_id,
                            f"🎉 Great news! <b>{user_name}</b> joined using your referral link!\n"
                            f"💰 You'll earn from their bets through our referral program!"
                        )
                    except Exception:
                        pass  # Referrer might have blocked the bot
            else:
                welcome_text = f"🎰 Welcome to Neon Roll, <b>{user_name}</b>!\n\n" \
                              f"⚠️ There was an issue setting up your account. Please try again.\n\n"
        else:
            # Existing user - update last login
            user_data['last_login'] = datetime.now().isoformat()
            await UserDataManager.save_user_data(user.id, user_data)
            
            # Check for daily login bonus
            daily_bonus = await check_daily_bonus(user.id, user_data)
            
            welcome_text = f"🎰 Welcome back, <b>{user_name}</b>!\n\n" \
                          f"💰 Your balance: <b>{user_data.get('balance', 0):.2f} EC</b>\n\n"
            
            if daily_bonus > 0:
                welcome_text += f"🎁 Daily login bonus: <b>+{daily_bonus} EC</b>\n\n"
        
        # Create inline keyboard with web app
        builder = InlineKeyboardBuilder()
        builder.button(
            text="🚀 Launch Game", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
        builder.button(
            text="💰 Deposit", 
            callback_data="deposit"
        )
        builder.button(
            text="💸 Withdraw", 
            callback_data="withdraw"
        )
        builder.button(
            text="👥 Referrals", 
            callback_data="referrals"
        )
        builder.adjust(1, 2, 1)
        
        await message.answer(
            welcome_text +
            "🎯 Place bets on colors (Red, Blue, Green, Yellow)\n"
            "💎 Win up to 45x multiplier on Yellow!\n"
            "🤖 AI-powered predictions\n"
            "👥 Multi-level referral program\n"
            "📋 Daily tasks and challenges\n"
            "💳 Crypto deposits and withdrawals\n"
            "🎁 Daily login bonuses\n\n"
            "Click the button below to start playing!",
            reply_markup=builder.as_markup()
        )
        
    except Exception as e:
        logging.error(f"Error in start command: {e}")
        await message.answer(
            "⚠️ Something went wrong. Please try again later.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔄 Try Again", callback_data="start")
            ]])
        )

@dp.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    """Enhanced statistics handler"""
    try:
        user_data = await UserDataManager.get_user_data(message.from_user.id)
        
        if not user_data:
            await message.answer("❌ You haven't started playing yet! Use /start to begin.")
            return
        
        # Calculate additional stats
        win_rate = 0
        if user_data.get('games_played', 0) > 0:
            wins = user_data.get('total_winnings', 0)
            games = user_data.get('games_played', 0)
            win_rate = (wins / (user_data.get('total_bets_placed', 1))) * 100
        
        referral_earnings = user_data.get('referral_earnings', 0)
        biggest_win = user_data.get('game_stats', {}).get('biggest_win', 0)
        
        stats_text = f"📊 <b>Your Statistics</b>\n\n" \
                    f"💰 Balance: <b>{user_data.get('balance', 0):.2f} EC</b>\n" \
                    f"🎮 Games Played: <b>{user_data.get('games_played', 0)}</b>\n" \
                    f"💸 Total Bets: <b>{user_data.get('total_bets_placed', 0):.2f} EC</b>\n" \
                    f"🏆 Total Winnings: <b>{user_data.get('total_winnings', 0):.2f} EC</b>\n" \
                    f"🎯 Win Rate: <b>{win_rate:.1f}%</b>\n" \
                    f"💎 Biggest Win: <b>{biggest_win:.2f} EC</b>\n" \
                    f"👥 Referrals: L1: <b>{user_data.get('referrals', {}).get('l1', 0)}</b>, " \
                    f"L2: <b>{user_data.get('referrals', {}).get('l2', 0)}</b>, " \
                    f"L3: <b>{user_data.get('referrals', {}).get('l3', 0)}</b>\n" \
                    f"💼 Referral Earnings: <b>{referral_earnings:.2f} EC</b>\n" \
                    f"🔥 Login Streak: <b>{user_data.get('daily_login_streak', 0)} days</b>\n" \
                    f"📅 Member Since: <b>{user_data.get('created_at', 'Unknown')[:10]}</b>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Play Now", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="👥 Share Referral", callback_data="referrals")]
        ])
        
        await message.answer(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in stats command: {e}")
        await message.answer("⚠️ Error retrieving statistics. Please try again.")

@dp.message(Command("deposit"))
async def deposit_handler(message: Message) -> None:
    """Enhanced deposit command handler"""
    try:
        user_data = await UserDataManager.get_user_data(message.from_user.id)
        if not user_data:
            await message.answer("❌ Please start the bot first with /start")
            return
        
        # Get user's crypto wallets
        user_wallets = user_data.get('crypto_wallets', {})
        
        text = "💰 <b>Deposit Cryptocurrency</b>\n\n"
        text += "Choose your preferred cryptocurrency:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for crypto_id, crypto_info in SUPPORTED_CRYPTOS.items():
            wallet_info = user_wallets.get(crypto_id, {})
            rate = crypto_info.get('rate_to_ec', 1)
            min_deposit = crypto_info.get('min_deposit', 1)
            
            text += f"• <b>{crypto_info['name']}</b> ({crypto_info['network_name']})\n"
            text += f"  Rate: 1 {crypto_info['name'].split()[0]} = {rate} EC\n"
            text += f"  Min: {min_deposit} {crypto_info['name'].split()[0]}\n\n"
            
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"💳 {crypto_info['name']}", 
                    callback_data=f"deposit_{crypto_id}"
                )
            ])
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="🚀 Play Game", web_app=WebAppInfo(url=WEB_APP_URL))
        ])
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in deposit command: {e}")
        await message.answer("⚠️ Error loading deposit options. Please try again.")

@dp.message(Command("withdraw"))
async def withdraw_handler(message: Message) -> None:
    """Enhanced withdraw command handler"""
    try:
        user_data = await UserDataManager.get_user_data(message.from_user.id)
        if not user_data:
            await message.answer("❌ Please start the bot first with /start")
            return
        
        balance = user_data.get('balance', 0)
        
        text = f"💸 <b>Withdraw Funds</b>\n\n"
        text += f"Your balance: <b>{balance:.2f} EC</b>\n\n"
        text += "Available withdrawal methods:\n\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        for crypto_id, crypto_info in SUPPORTED_CRYPTOS.items():
            min_withdraw = crypto_info.get('min_withdraw', 50)
            rate = crypto_info.get('rate_to_ec', 1)
            
            text += f"• <b>{crypto_info['name']}</b>\n"
            text += f"  Min: {min_withdraw} EC\n"
            text += f"  Rate: {rate} EC = 1 {crypto_info['name'].split()[0]}\n\n"
            
            keyboard.inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"💸 {crypto_info['name']}", 
                    callback_data=f"withdraw_{crypto_id}"
                )
            ])
        
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="🚀 Play Game", web_app=WebAppInfo(url=WEB_APP_URL))
        ])
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in withdraw command: {e}")
        await message.answer("⚠️ Error loading withdrawal options. Please try again.")

@dp.message(Command("referral"))
async def referral_handler(message: Message) -> None:
    """Enhanced referral command handler"""
    try:
        user_data = await UserDataManager.get_user_data(message.from_user.id)
        if not user_data:
            await message.answer("❌ Please start the bot first with /start")
            return
        
        referral_link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"
        
        referrals = user_data.get('referrals', {})
        total_referrals = referrals.get('l1', 0) + referrals.get('l2', 0) + referrals.get('l3', 0)
        referral_earnings = user_data.get('referral_earnings', 0)
        
        text = f"👥 <b>Referral Program</b>\n\n"
        text += f"🔗 Your referral link:\n<code>{referral_link}</code>\n\n"
        text += f"📊 <b>Your Referrals:</b>\n"
        text += f"• Level 1: {referrals.get('l1', 0)} friends ({REFERRAL_LEVELS['level_1']['percentage']*100:.0f}%)\n"
        text += f"• Level 2: {referrals.get('l2', 0)} friends ({REFERRAL_LEVELS['level_2']['percentage']*100:.0f}%)\n"
        text += f"• Level 3: {referrals.get('l3', 0)} friends ({REFERRAL_LEVELS['level_3']['percentage']*100:.0f}%)\n"
        text += f"• Total: {total_referrals} friends\n\n"
        text += f"💰 Total Earned: <b>{referral_earnings:.2f} EC</b>\n\n"
        text += f"🎯 <b>How it works:</b>\n"
        text += f"• Get {REFERRAL_LEVELS['level_1']['percentage']*100:.0f}% from direct referrals' bets\n"
        text += f"• Get {REFERRAL_LEVELS['level_2']['percentage']*100:.0f}% from their referrals' bets\n"
        text += f"• Get {REFERRAL_LEVELS['level_3']['percentage']*100:.0f}% from 3rd level referrals' bets\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Link", callback_data="copy_referral")],
            [InlineKeyboardButton(text="📱 Share Link", callback_data="share_referral")],
            [InlineKeyboardButton(text="🚀 Play Game", web_app=WebAppInfo(url=WEB_APP_URL))]
        ])
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in referral command: {e}")
        await message.answer("⚠️ Error loading referral information. Please try again.")

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Enhanced help command handler"""
    help_text = f"""
🎰 <b>Neon Roll - Help & Rules</b>

🎮 <b>Game Rules:</b>
• Place bets on colors: Red, Blue, Green, or Yellow
• Red & Blue: 2x multiplier (44% chance each)
• Green: 5x multiplier (10% chance)
• Yellow: 45x multiplier (2% chance)

💰 <b>Features:</b>
• 🎁 {WELCOME_BONUS} EC welcome bonus for new players
• 🤖 AI analyst predictions
• 👥 Multi-level referral program
• 📋 Daily tasks and challenges
• 💳 Crypto deposits/withdrawals
• 🎁 Daily login bonuses
• 🔥 Login streak rewards

🎮 <b>Commands:</b>
/start - Launch the game
/stats - View your statistics
/deposit - Deposit cryptocurrency
/withdraw - Withdraw your winnings
/referral - Get your referral link
/help - Show this help message

💡 <b>Tips:</b>
• Start with small bets to learn the game
• Use the AI analyst for predictions
• Complete daily tasks for extra EC
• Invite friends to earn referral bonuses
• Login daily to maintain your streak

🔐 <b>Security:</b>
• Your funds are secured with blockchain technology
• All transactions are encrypted and logged
• Wallets are generated from secure seed phrases

Good luck and have fun! 🍀
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Play Now", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="💰 Deposit", callback_data="deposit"),
         InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton(text="👥 Referrals", callback_data="referrals")]
    ])
    
    await message.answer(help_text, reply_markup=keyboard)

# Callback handlers
@dp.callback_query(lambda c: c.data == "deposit")
async def deposit_callback(callback_query: types.CallbackQuery):
    """Handle deposit callback"""
    await callback_query.answer()
    await deposit_handler(callback_query.message)

@dp.callback_query(lambda c: c.data == "withdraw")
async def withdraw_callback(callback_query: types.CallbackQuery):
    """Handle withdraw callback"""
    await callback_query.answer()
    await withdraw_handler(callback_query.message)

@dp.callback_query(lambda c: c.data == "referrals")
async def referrals_callback(callback_query: types.CallbackQuery):
    """Handle referrals callback"""
    await callback_query.answer()
    await referral_handler(callback_query.message)

@dp.callback_query(lambda c: c.data.startswith("deposit_"))
async def deposit_crypto_callback(callback_query: types.CallbackQuery):
    """Handle specific crypto deposit"""
    await callback_query.answer()
    crypto_id = callback_query.data.split("_")[1]
    
    try:
        user_data = await UserDataManager.get_user_data(callback_query.from_user.id)
        if not user_data:
            await callback_query.message.answer("❌ Please start the bot first with /start")
            return
        
        # Get user's wallet address for this crypto
        user_wallets = user_data.get('crypto_wallets', {})
        wallet_info = user_wallets.get(crypto_id, {})
        
        if not wallet_info:
            await callback_query.message.answer("❌ Error getting wallet address. Please try again.")
            return
        
        crypto_info = SUPPORTED_CRYPTOS.get(crypto_id, {})
        address = wallet_info.get('address', '')
        
        text = f"💳 <b>Deposit {crypto_info['name']}</b>\n\n"
        text += f"🔗 <b>Network:</b> {crypto_info['network_name']}\n"
        text += f"📍 <b>Address:</b>\n<code>{address}</code>\n\n"
        text += f"💱 <b>Exchange Rate:</b>\n1 {crypto_info['name'].split()[0]} = {crypto_info['rate_to_ec']} EC\n\n"
        text += f"💰 <b>Minimum Deposit:</b> {crypto_info['min_deposit']} {crypto_info['name'].split()[0]}\n\n"
        text += f"⚠️ <b>Important:</b>\n"
        text += f"• Only send {crypto_info['name']} to this address\n"
        text += f"• Deposits are credited automatically\n"
        text += f"• Min {crypto_info['confirmation_blocks']} confirmations required\n"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Copy Address", callback_data=f"copy_address_{crypto_id}")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data=f"deposit_{crypto_id}")],
            [InlineKeyboardButton(text="🚀 Play Game", web_app=WebAppInfo(url=WEB_APP_URL))]
        ])
        
        await callback_query.message.edit_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logging.error(f"Error in deposit crypto callback: {e}")
        await callback_query.message.answer("⚠️ Error processing deposit. Please try again.")

# Utility functions
async def check_daily_bonus(user_id: int, user_data: Dict[str, Any]) -> float:
    """Check and give daily login bonus"""
    try:
        last_bonus = user_data.get('last_daily_bonus')
        if not last_bonus:
            return 0
        
        last_bonus_date = datetime.fromisoformat(last_bonus).date()
        today = datetime.now().date()
        
        if last_bonus_date < today:
            # Calculate bonus based on streak
            streak = user_data.get('daily_login_streak', 0)
            bonus = min(10 + (streak * 2), 100)  # Max 100 EC bonus
            
            # Update user data
            user_data['balance'] = user_data.get('balance', 0) + bonus
            user_data['last_daily_bonus'] = datetime.now().isoformat()
            
            # Check if consecutive day
            if last_bonus_date == today - timedelta(days=1):
                user_data['daily_login_streak'] = streak + 1
            else:
                user_data['daily_login_streak'] = 1
            
            await UserDataManager.save_user_data(user_id, user_data)
            return bonus
        
        return 0
    except Exception as e:
        logging.error(f"Error checking daily bonus: {e}")
        return 0

# Error handler
@dp.error()
async def error_handler(event, exception):
    """Enhanced error handler with logging"""
    logging.error(f"Error occurred: {exception}")
    logging.error(f"Event: {event}")
    return True

async def setup_bot_commands():
    """Setup bot commands and description"""
    try:
        commands = [
            types.BotCommand(command=cmd["command"], description=cmd["description"]) 
            for cmd in BOT_COMMANDS
        ]
        await bot.set_my_commands(commands)
        
        # Set bot description
        await bot.set_my_description(BOT_DESCRIPTION)
        await bot.set_my_short_description(BOT_SHORT_DESCRIPTION)
        
        logging.info("Bot commands and description set successfully")
    except Exception as e:
        logging.error(f"Error setting bot commands: {e}")

async def main() -> None:
    """Main function to run the bot"""
    try:
        # Setup bot commands
        await setup_bot_commands()
        
        # Test Firebase connection
        try:
            test_doc = db.collection('system').document('test')
            test_doc.set({'status': 'online', 'timestamp': datetime.now().isoformat()})
            logging.info("Firebase connection test successful")
        except Exception as e:
            logging.error(f"Firebase connection test failed: {e}")
        
        # Start polling
        logging.info("Starting bot polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logging.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, 
        stream=sys.stdout,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
