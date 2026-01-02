import telebot
import sqlite3
import threading
import time
import os
import sys
import google.generativeai as genai
from flask import Flask
from master_prompt import SYSTEM_PROMPT 

# --- CONFIGURATION (Environment Variables) ---
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

try:
    GROUP_ID = int(os.environ.get('TELEGRAM_GROUP_ID'))
    ADMIN_ID = int(os.environ.get('ADMIN_TELEGRAM_ID', '0'))
except (TypeError, ValueError):
    print("ERROR: Environment variables missing or invalid.")
    sys.exit(1)

# AI Setup (Keep it for memory setup)
# (Same logic as before, AI is disabled by default)
try:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception:
    pass
    
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- DATABASE SETUP (Same as before) ---
def init_db():
    conn = sqlite3.connect('chat_bot.db', check_same_thread=False) 
    cursor = conn.cursor()
    # topics table mein topic_id save hota hai
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
    # Returns (topic_id, last_reply_time)
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
    # User ke liye welcome message
    if message.chat.type == 'private':
        welcome_text = (
            "👋 **Welcome to Naino Academy Support!**\n\n"
            "Aapka swagat hai. Aap apna message yahan likh dijiye.\n"
            "Admin se aapko jald hi jawab milega!"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")
    # Admin ke liye confirmation
    elif message.chat.id == GROUP_ID:
        bot.send_message(GROUP_ID, "✅ Bot Active! New user messages will create topics here.", message_thread_id=1)


@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    text = message.text

    data = get_topic_data(user_id) # (topic_id, last_reply_time)

    if not data:
        # 1. Naya user: Topic create karna
        try:
            topic = bot.create_forum_topic(GROUP_ID, f"{name} ({user_id})")
            topic_id = topic.message_thread_id
            cursor = db.cursor()
            # Topic ID ko database mein save karna
            cursor.execute('INSERT INTO topics VALUES (?, ?, ?)', (user_id, topic_id, time.time())) 
            db.commit()
            print(f"New Topic Created for user {user_id}")
        except Exception as e:
            # Topic creation fail hone par (Permission/ID error)
            print(f"!!! TOPIC CREATION FAILED: {e}")
            bot.send_message(user_id, "❌ Sorry, system error hai. Admin jald hi aayenge.")
            return # Code ko aage mat chalao
    else:
        # 2. Purana user: Existing topic ID use karna
        topic_id = data[0]
        update_time(user_id) # Last reply time update

    # User ke message ko history aur GROUP ke ussi topic mein save karna
    save_msg(user_id, 'user', text)
    bot.send_message(GROUP_ID, f"👤 **{name}**: {text}", message_thread_id=topic_id)
    
    # AI timer thread chalu karna - FILHAL BAND HAI
    # threading.Thread(target=ai_assistant_thread, args=(user_id, topic_id)).start()

@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.is_topic_message)
def handle_admin_reply(message):
    # Admin reply logic
    # ... (Same as before) ...
    topic_id = message.message_thread_id
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
            bot.send_message(user_id, f"👨‍💻 **Admin:** {message.text}")
            bot.reply_to(message, "✅ User tak jawab pahunch gaya.")
        except:
            bot.reply_to(message, "❌ User tak message nahi gaya.")

# --- WEB SERVER (Render ke liye) ---
@app.route('/')
def home(): 
    return "<h1>Naino Academy Hybrid Bot is Online!</h1><p>AI is disabled for testing. Topic forwarding is active.</p>"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    print("Hybrid Bot is now LIVE. Polling started...")
    bot.infinity_polling()
