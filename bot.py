import telebot
import sqlite3
import threading
import time
import os
import sys
from flask import Flask
from telebot import types

# --- CONFIGURATION (Environment Variables) ---
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')

try:
    # GROUP_ID aur ADMIN_ID dono ki zaroorat hai
    GROUP_ID = int(os.environ.get('TELEGRAM_GROUP_ID'))
    ADMIN_ID = int(os.environ.get('ADMIN_TELEGRAM_ID')) 
except (TypeError, ValueError):
    print("ERROR: Environment variables TELEGRAM_GROUP_ID or ADMIN_TELEGRAM_ID are missing or invalid.")
    sys.exit(1)

if not API_TOKEN:
    print("ERROR: Missing TELEGRAM_API_TOKEN environment variable.")
    sys.exit(1)

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- INLINE BUTTON CONFIGURATION ---
IS_BUTTON_ENABLED = True 
GROUP_LINK = "https://t.me/nainoneet"
BUTTON_TEXT = "🚀 Join Naino NEET Group"

# --- DATABASE SETUP (SQLite) ---
def init_db():
    conn = sqlite3.connect('chat_bot.db', check_same_thread=False) 
    cursor = conn.cursor()
    # topics table ka use Topic ID aur User ID ko map karne ke liye
    cursor.execute('CREATE TABLE IF NOT EXISTS topics (user_id INTEGER PRIMARY KEY, topic_id INTEGER, last_reply_time REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS history (user_id INTEGER, role TEXT, content TEXT)')
    conn.commit()
    return conn
db = init_db()

# --- DATABASE HELPERS ---
def save_msg(user_id, role, content):
    cursor = db.cursor()
    cursor.execute('INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)', (user_id, role, content))
    db.commit()

def get_topic_data(user_id):
    cursor = db.cursor()
    cursor.execute('SELECT topic_id, last_reply_time FROM topics WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def update_time(user_id):
    cursor = db.cursor()
    cursor.execute('UPDATE topics SET last_reply_time = ? WHERE user_id = ?', (time.time(), user_id))
    db.commit()

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        
        welcome_text = (
            "👋 **Welcome to Naino Academy Support!**\n\n"
            "Drop your message here. Admin will reply soon."
        )
        
        markup = None
        if IS_BUTTON_ENABLED:
            markup = types.InlineKeyboardMarkup()
            url_button = types.InlineKeyboardButton(text=BUTTON_TEXT, url=GROUP_LINK)
            markup.add(url_button)

        bot.reply_to(message, welcome_text, parse_mode="Markdown", reply_markup=markup)
        
    elif message.chat.id == GROUP_ID:
        # Topic 1 (General) mein confirmation
        bot.send_message(GROUP_ID, "✅ Bot Active! New user messages will create topics here.", message_thread_id=1)


@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    text = message.text

    data = get_topic_data(user_id)

    if not data:
        # Naya user: Topic create karna (User ka ID aur Naam Topic Title mein)
        try:
            topic = bot.create_forum_topic(GROUP_ID, f"{name} ({user_id})")
            topic_id = topic.message_thread_id
            cursor = db.cursor()
            cursor.execute('INSERT INTO topics VALUES (?, ?, ?)', (user_id, topic_id, time.time())) 
            db.commit()
        except Exception as e:
            print(f"!!! TOPIC CREATION FAILED: {e}")
            bot.send_message(user_id, "❌ Sorry, system error hai. Admin jald hi aayenge.")
            return
    else:
        # Purana user: Existing topic ID use karna
        topic_id = data[0]
        update_time(user_id)

    # User ke message ko history aur GROUP ke ussi topic mein save karna (Clean format: only text)
    save_msg(user_id, 'user', text)
    bot.send_message(GROUP_ID, f"💬 {text}", message_thread_id=topic_id)
    

@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.is_topic_message)
def handle_admin_reply(message):
    topic_id = message.message_thread_id
    
    # Security Check: Only allow replies from the designated ADMIN_ID
    if message.from_user.id != ADMIN_ID:
         bot.reply_to(message, "❌ Sirf authorized admin hi user ko reply kar sakte hain.")
         return

    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM topics WHERE topic_id = ?', (topic_id,))
    res = cursor.fetchone()

    if res:
        user_id = res[0]
        update_time(user_id)
        save_msg(user_id, 'model', message.text) 

        try:
            # FIX 1: Admin Name Hidden
            # Jawab user ko bhejo (User ko sirf bot ka display name aur 👨‍💻 emoji dikhega)
            bot.send_message(user_id, f"👨‍💻 {message.text}")
            
            # FIX 2: No Green Tick/Done Message (Silent Success)
            # Success hone par group mein koi reply nahi jayega
            
        except:
            # Failure message (Block hone par hi ye dikhega)
            bot.reply_to(message, "❌ User Blocked Bot") 

# --- WEB SERVER (Render ke liye) ---
@app.route('/')
def home(): 
    return "<h1>Naino Academy Support Bot is Online!</h1>"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Web server aur Bot polling ko alag threads mein run karna
    threading.Thread(target=run_web_server).start()
    print("Support Bot is now LIVE. Polling started...")
    bot.infinity_polling()
