import telebot
import sqlite3
import threading
import os
import sys
from flask import Flask

# --- CONFIGURATION (Environment Variables se Load karna) ---
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')

try:
    # Admin ki Personal Chat ID (is bot ke liye Group ID ki zaroorat nahi)
    ADMIN_ID = int(os.environ.get('ADMIN_TELEGRAM_ID')) 
except (TypeError, ValueError):
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
    return "<h1>Simple Forwarding Bot is Running! (No AI/Topics)</h1>"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- DATABASE LOGIC ---
# Note: Ye database Admin ko reply karne ke liye zaroori hai
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
        bot.reply_to(message, "✅ Welcome Boss! Users ke messages yahan aayenge. Reply karne ke liye seedhe message par Reply karein.")
    else:
        bot.reply_to(message, "👋 Hii! Aapka message Admin tak pahuch gaya hai. Wo aapko jald reply karenge.")

# Jab koi User message kare (Admin ki Personal Chat mein forward hoga)
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID and message.chat.type == 'private')
def forward_to_admin(message):
    user = message.from_user
    # Profile Card for Admin
    profile = (f"👤 **Naya Message!**\n"
               f"━━━━━━━━━━━━━━\n"
               f"📝 Name: {user.first_name}\n"
               f"🔗 Username: @{user.username if user.username else 'None'}\n"
               f"🆔 User ID: `{user.id}`\n"
               f"💬 Msg: {message.text}\n"
               f"━━━━━━━━━━━━━━\n"
               f"ℹ️ *Reply karne ke liye isi message par 'Reply' karein.*")
    
    try:
        # Message ko Admin ki Personal Chat mein bhejo
        sent_msg = bot.send_message(ADMIN_ID, profile, parse_mode="Markdown")
        # Mapping save karein
        save_mapping(sent_msg.message_id, user.id)
    except Exception as e:
        print(f"Error forwarding: {e}")
        bot.send_message(user.id, "❌ Sorry, Admin tak message nahi pahucha. Koi technical problem hai.")

# Admin jab kisi user ke message par Reply kare (Sirf Admin ki chat mein kaam karega)
@bot.message_handler(func=lambda message: message.chat.id == ADMIN_ID and message.reply_to_message is not None)
def handle_admin_reply(message):
    original_msg_id = message.reply_to_message.message_id
    target_user_id = get_user_id(original_msg_id)
    
    if target_user_id:
        try:
            # Jawab user ko bhejo
            bot.send_message(target_user_id, f"✉️ **Admin ka Jawab:**\n\n{message.text}")
            bot.reply_to(message, "✅ Jawab bhej diya gaya!")
        except Exception:
            bot.reply_to(message, "❌ Error: Shayad user ne bot block kar diya.")
    else:
        bot.reply_to(message, "❌ Ye message kis user ka hai, database me nahi mila.")

# --- START BOT ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Forwarding Bot is now LIVE. Polling started...")
    bot.infinity_polling()
