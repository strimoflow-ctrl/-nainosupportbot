import telebot
import sqlite3
import threading
import os
from flask import Flask

# --- CONFIGURATION ---
# Yahan apna Token aur ID daalein
API_TOKEN = '8411214861:AAEBlPqlX5Vrc2xcEIncp8rWtHeKiJteL2w' 
ADMIN_ID = 7755459773 # Apni numerical ID daalo

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- WEB SERVER FOR UPTIME ROBOT ---
@app.route('/')
def index():
    return "<h1>Bot is Running!</h1><p>UptimeRobot is monitoring this page.</p>"

def run_flask():
    # Render ke liye port set karna
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('data.db', check_same_thread=False)
    cursor = conn.cursor()
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
        bot.reply_to(message, "👋 Hii! Aapka message Admin tak pahuch jayega. Wo aapko jald reply karenge.")

# Jab koi User message kare (Admin ko forward hoga)
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
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
        sent_msg = bot.send_message(ADMIN_ID, profile, parse_mode="Markdown")
        # Database me mapping save karein
        save_mapping(sent_msg.message_id, user.id)
    except Exception as e:
        print(f"Error forwarding: {e}")

# Admin jab kisi message par Reply kare
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
