import telebot
import sqlite3
import threading
import os
import sys
from flask import Flask

# --- CONFIGURATION (Environment Variables se Load karna) ---
# Environment Variables set karein: TELEGRAM_API_TOKEN aur ADMIN_ID
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')

try:
    # ADMIN_ID ko integer mein badalna zaroori hai
    ADMIN_ID = int(os.environ.get('ADMIN_TELEGRAM_ID'))
except (TypeError, ValueError):
    # Agar variable set nahi hai ya galat hai toh error dega
    print("ERROR: ADMIN_TELEGRAM_ID not set or invalid in environment variables.")
    sys.exit(1)

if not API_TOKEN:
    print("ERROR: TELEGRAM_API_TOKEN not set in environment variables.")
    sys.exit(1)


bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- WEB SERVER FOR UPTIME ROBOT ---
@app.route('/')
def index():
    return "<h1>Simple Forwarding Bot is Running!</h1><p>UptimeRobot is monitoring this page.</p>"

def run_flask():
    # Render ke liye port set karna
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- DATABASE LOGIC ---
# Note: Isme thread safety ke liye check_same_thread=False zaroori hai
def init_db():
    conn = sqlite3.connect('forward_data.db', check_same_thread=False)
    cursor = conn.cursor()
    # admin_msg_id ko user_id se map karna
    cursor.execute('CREATE TABLE IF NOT EXISTS msg_map (admin_msg_id INTEGER PRIMARY KEY, user_id INTEGER)')
    conn.commit()
    return conn

db_conn = init_db()

def save_mapping(admin_msg_id, user_id):
    cursor = db_conn.cursor()
    cursor.execute('INSERT INTO msg_map VALUES (?, ?)', (admin_msg_id, user_id))
    db_conn.commit()

def get_user_id(admin_msg_id):
    cursor = db_conn.cursor()
    cursor.execute('SELECT user_id FROM msg_map WHERE admin_msg_id = ?', (admin_msg_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "✅ Welcome Boss! Main taiyar hoon messages receive karne ke liye.")
    else:
        # User ko jawab
        bot.reply_to(message, "Hii! 😊Aapka message Admin tak pahuncha diya jaayega  📩Wo aapko jald hi reply karenge ⏳   👉 Apna message yahan likh dijiye ✍️Thank You! 🙏")

# Jab koi User message kare (Admin ko forward hoga)
# Ye function user ke private chat messages ko ADMIN_ID ko forward karega
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID and message.chat.type == 'private')
def forward_to_admin(message):
    user = message.from_user
    # Profile Card banana
    profile = (f"👤 **Naya Message!**\n"
               f"━━━━━━━━━━━━━━\n"
               f"📝 Name: {user.first_name}\n"
               f"🔗 Username: @{user.username if user.username else 'None'}\n"
               f"🆔 User ID: `{user.id}`\n"
               f"💬 Msg: {message.text}\n"
               f"━━━━━━━━━━━━━━\n"
               f"ℹ️ *Reply karne ke liye isi message par 'Reply' karein.*")
    
    try:
        # Message ko Admin ko bhejo
        sent_msg = bot.send_message(ADMIN_ID, profile, parse_mode="Markdown")
        # Database me mapping save karein
        save_mapping(sent_msg.message_id, user.id)
    except Exception as e:
        print(f"Error forwarding: {e}")
        # Agar Admin ID galat ho ya bot ne Admin se baat na ki ho toh yahan error aayega
        bot.send_message(user.id, "❌ Sorry, Admin tak message nahi pahucha. Shayad koi technical problem hai.")

# Admin jab kisi message par Reply kare (Sirf Admin se aane wale reply par trigger hoga)
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None)
def handle_admin_reply(message):
    original_msg_id = message.reply_to_message.message_id
    target_user_id = get_user_id(original_msg_id)
    
    if target_user_id:
        try:
            bot.send_message(target_user_id, f"✉️ **Admin ka Jawab:**\n\n{message.text}")
            bot.reply_to(message, "✅ Jawab bhej diya gaya!")
        except Exception:
            bot.reply_to(message, "❌ Error: Shayad user ne bot block kar diya.")
    else:
        bot.reply_to(message, "❌ Ye message kis user ka hai, database me nahi mila.")

# --- START BOT ---
if __name__ == "__main__":
    # Flask ko thread me chalana taaki bot aur web sath chalein
    threading.Thread(target=run_flask).start()
    print("Bot is starting...")
    bot.infinity_polling()
