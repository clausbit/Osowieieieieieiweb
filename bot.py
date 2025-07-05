import asyncio
import logging
import sys
import json
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

# --- Configuration ---
try:
    from config import BOT_TOKEN, WEB_APP_URL
except ImportError:
    print("Error: Could not find config.py file.")
    print("Please make sure you ran the installation script start.sh")
    sys.exit(1)

# Initialize Firebase
try:
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

# User data management
async def get_user_data(user_id: int):
    """Get user data from Firebase"""
    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logging.error(f"Error getting user data: {e}")
        return None

async def save_user_data(user_id: int, data: dict):
    """Save user data to Firebase"""
    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc_ref.set(data, merge=True)
        return True
    except Exception as e:
        logging.error(f"Error saving user data: {e}")
        return False

async def create_new_user(user: types.User):
    """Create new user in Firebase"""
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'balance': 20.0,  # Welcome bonus
        'total_bets_placed': 0,
        'total_winnings': 0,
        'games_played': 0,
        'referrals': {'l1': 0, 'l2': 0, 'l3': 0},
        'tasks': [],
        'completed_tasks': [],
        'created_at': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat(),
        'is_new_user': False
    }
    
    await save_user_data(user.id, user_data)
    return user_data

# Handler for /start command
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler is called when user sends /start command.
    It sends a welcome message and button to launch the Web App.
    """
    user = message.from_user
    user_name = user.first_name or user.username or "Player"
    
    # Check if user exists in database
    user_data = await get_user_data(user.id)
    
    if not user_data:
        # New user - create account with welcome bonus
        user_data = await create_new_user(user)
        welcome_text = f"🎉 Welcome to Neon Roll, <b>{user_name}</b>!\n\n" \
                      f"🎁 You've received <b>20 EC</b> as a welcome bonus!\n\n"
    else:
        # Existing user - update last login
        await save_user_data(user.id, {'last_login': datetime.now().isoformat()})
        welcome_text = f"🎰 Welcome back, <b>{user_name}</b>!\n\n" \
                      f"💰 Your balance: <b>{user_data.get('balance', 0):.2f} EC</b>\n\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Launch Game", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    
    await message.answer(
        welcome_text +
        "🎯 Place bets on colors (Red, Blue, Green, Yellow)\n"
        "💎 Win up to 45x multiplier on Yellow!\n"
        "🤖 AI-powered predictions\n"
        "👥 Referral program with rewards\n"
        "📋 Daily tasks and challenges\n"
        "💳 Crypto deposits and withdrawals\n\n"
        "Click the button below to start playing!",
        reply_markup=builder.as_markup()
    )

# Handler for referral links
@dp.message(CommandStart(deep_link=True))
async def referral_handler(message: Message) -> None:
    """Handle referral links"""
    user = message.from_user
    user_name = user.first_name or user.username or "Player"
    
    # Extract referrer ID from deep link
    args = message.text.split()
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            
            # Check if user is new
            user_data = await get_user_data(user.id)
            
            if not user_data and referrer_id != user.id:
                # New user referred by someone
                user_data = await create_new_user(user)
                
                # Update referrer's stats
                referrer_data = await get_user_data(referrer_id)
                if referrer_data:
                    referrer_data['referrals']['l1'] += 1
                    await save_user_data(referrer_id, referrer_data)
                    
                    # Notify referrer
                    try:
                        await bot.send_message(
                            referrer_id,
                            f"🎉 Great news! <b>{user_name}</b> joined using your referral link!\n"
                            f"💰 You'll earn 5% from all their bets!"
                        )
                    except:
                        pass  # Referrer might have blocked the bot
                
                welcome_text = f"🎉 Welcome to Neon Roll, <b>{user_name}</b>!\n\n" \
                              f"🎁 You've received <b>20 EC</b> as a welcome bonus!\n" \
                              f"👥 You were referred by a friend!\n\n"
            else:
                welcome_text = f"🎰 Welcome back, <b>{user_name}</b>!\n\n"
        except ValueError:
            # Invalid referrer ID, treat as normal start
            await command_start_handler(message)
            return
    else:
        await command_start_handler(message)
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Launch Game", 
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    
    await message.answer(
        welcome_text +
        "🎯 Place bets on colors (Red, Blue, Green, Yellow)\n"
        "💎 Win up to 45x multiplier on Yellow!\n"
        "🤖 AI-powered predictions\n"
        "👥 Referral program with rewards\n"
        "📋 Daily tasks and challenges\n"
        "💳 Crypto deposits and withdrawals\n\n"
        "Click the button below to start playing!",
        reply_markup=builder.as_markup()
    )

# Game statistics handler
@dp.message(lambda message: message.text and message.text.lower() in ['/stats', '/statistics'])
async def stats_handler(message: Message) -> None:
    """Show user statistics"""
    user_data = await get_user_data(message.from_user.id)
    
    if not user_data:
        await message.answer("❌ You haven't started playing yet! Use /start to begin.")
        return
    
    stats_text = f"📊 <b>Your Statistics</b>\n\n" \
                f"💰 Balance: <b>{user_data.get('balance', 0):.2f} EC</b>\n" \
                f"🎮 Games Played: <b>{user_data.get('games_played', 0)}</b>\n" \
                f"💸 Total Bets: <b>{user_data.get('total_bets_placed', 0):.2f} EC</b>\n" \
                f"🏆 Total Winnings: <b>{user_data.get('total_winnings', 0):.2f} EC</b>\n" \
                f"👥 Referrals: <b>{user_data.get('referrals', {}).get('l1', 0)}</b>\n" \
                f"📅 Member Since: <b>{user_data.get('created_at', 'Unknown')[:10]}</b>"
    
    await message.answer(stats_text)

# Help handler
@dp.message(lambda message: message.text and message.text.lower() in ['/help', '/info'])
async def help_handler(message: Message) -> None:
    """Show help information"""
    help_text = """
🎰 <b>Neon Roll - How to Play</b>

🎯 <b>Game Rules:</b>
• Place bets on colors: Red, Blue, Green, or Yellow
• Red & Blue: 2x multiplier (44% chance each)
• Green: 5x multiplier (10% chance)
• Yellow: 45x multiplier (2% chance)

💰 <b>Features:</b>
• 🎁 20 EC welcome bonus for new players
• 🤖 AI analyst predictions
• 👥 3-level referral program (5%, 1%, 1%)
• 📋 Daily tasks and challenges
• 💳 Crypto deposits/withdrawals

🎮 <b>Commands:</b>
/start - Launch the game
/stats - View your statistics
/help - Show this help message

💡 <b>Tips:</b>
• Start with small bets to learn the game
• Use the AI analyst for predictions
• Complete daily tasks for extra EC
• Invite friends to earn referral bonuses

Good luck and have fun! 🍀
    """
    
    await message.answer(help_text)

# Error handler
@dp.error()
async def error_handler(event, exception):
    """Handle errors"""
    logging.error(f"Error occurred: {exception}")
    return True

async def main() -> None:
    """
    Main function to run the bot.
    """
    # Set bot commands
    commands = [
        types.BotCommand(command="start", description="🚀 Launch Neon Roll game"),
        types.BotCommand(command="stats", description="📊 View your statistics"),
        types.BotCommand(command="help", description="❓ Get help and game rules"),
    ]
    
    await bot.set_my_commands(commands)
    
    # Start polling
    await dp.start_polling(bot)

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
