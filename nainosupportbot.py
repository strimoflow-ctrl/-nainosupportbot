import telebot
import sqlite3
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '8411214861:AAEBlPqlX5Vrc2xcEIncp8rWtHeKiJteL2w'  # BotFather se lo
ADMIN_ID = 7755459773              # Apni ID daalo (@userinfobot se milegi)

bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT)''')
    # Messages mapping (to reply easily)
    cursor.execute('''CREATE TABLE IF NOT EXISTS msg_map 
                      (admin_msg_id INTEGER PRIMARY KEY, user_id INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- HELPER FUNCTIONS ---
def save_user(user_id, first_name, username):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)", (user_id, first_name, username))
    conn.commit()
    conn.close()

def map_msg(admin_msg_id, user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO msg_map VALUES (?, ?)", (admin_msg_id, user_id))
    conn.commit()
    conn.close()

def get_user_from_msg(admin_msg_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM msg_map WHERE admin_msg_id = ?", (admin_msg_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# --- HANDLERS ---

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_ID:
        save_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
        bot.send_message(message.chat.id, "👋 Hii! Aapka message admin ko bhej diya gaya hai. Wait karein...")
    else:
        bot.send_message(ADMIN_ID, "🚀 Admin Panel Active! Users ke messages yahan aayenge.")

# Jab koi user message bhejta hai
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def handle_user_msg(message):
    user = message.from_user
    save_user(user.id, user.first_name, user.username)
    
    # Profile Card for Admin
    profile_text = (f"👤 **Naya Message!**\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"📝 Name: {user.first_name}\n"
                    f"🔗 Username: @{user.username if user.username else 'N/A'}\n"
                    f"🆔 ID: `{user.id}`\n"
                    f"💬 Msg: {message.text}\n"
                    f"━━━━━━━━━━━━━━\n"
                    f"ℹ️ *Reply karne ke liye isi message par 'Reply' karein.*")
    
    sent_msg = bot.send_message(ADMIN_ID, profile_text, parse_mode="Markdown")
    
    # Message mapping save karna taaki admin reply kar sake
    map_msg(sent_msg.message_id, user.id)

# Admin jab reply karega
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None)
def handle_admin_reply(message):
    original_msg_id = message.reply_to_message.message_id
    target_user_id = get_user_from_msg(original_msg_id)
    
    if target_user_id:
        try:
            bot.send_message(target_user_id, f"✉️ **Admin:** {message.text}")
            bot.reply_to(message, "✅ Jawab bhej diya gaya!")
        except Exception:
            bot.reply_to(message, "❌ Error: Shayad user ne bot block kar diya hai.")
    else:
        bot.reply_to(message, "❌ Ye message kis user ka hai, database me nahi mila.")

print("Bot is running...")
bot.infinity_polling()
