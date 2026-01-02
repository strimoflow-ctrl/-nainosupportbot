import telebot
import sqlite3
import threading
import time
import os
import sys
import google.generativeai as genai
from flask import Flask
from master_prompt import SYSTEM_PROMPT 

# --- CONFIGURATION (Environment Variables se Load karna) ---
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

try:
    ADMIN_ID = int(os.environ.get('ADMIN_TELEGRAM_ID'))
    GROUP_ID = int(os.environ.get('TELEGRAM_GROUP_ID'))
except (TypeError, ValueError):
    print("ERROR: One or more ID environment variables are missing or invalid.")
    sys.exit(1)

if not all([API_TOKEN, GEMINI_KEY]):
    print("ERROR: Missing TELEGRAM_API_TOKEN or GEMINI_API_KEY environment variable.")
    sys.exit(1)

# AI and Bot Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- DATABASE SETUP (Same as before) ---
def init_db():
    conn = sqlite3.connect('chat_bot.db', check_same_thread=False) 
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS topics (user_id INTEGER PRIMARY KEY, topic_id INTEGER, last_reply_time REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS history (user_id INTEGER, role TEXT, content TEXT)')
    conn.commit()
    return conn

db = init_db()

# --- DATABASE HELPERS (Same as before) ---
def save_msg(user_id, role, content):
    cursor = db.cursor()
    cursor.execute('INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)', (user_id, role, content))
    db.commit()

def get_history(user_id):
    cursor = db.cursor()
    cursor.execute('SELECT role, content FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT 15', (user_id,))
    rows = cursor.fetchall()
    history = []
    for role, content in reversed(rows):
        role_type = 'user' if role == 'user' else 'model'
        history.append({"role": role_type, "parts": [content]})
    return history

def get_topic_data(user_id):
    cursor = db.cursor()
    cursor.execute('SELECT topic_id, last_reply_time FROM topics WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def update_time(user_id):
    cursor = db.cursor()
    cursor.execute('UPDATE topics SET last_reply_time = ? WHERE user_id = ?', (time.time(), user_id))
    db.commit()

# --- AI LOGIC (INSTANT REPLY FOR TESTING) ---
def ai_assistant_thread(user_id, topic_id):
    # **TIME.SLEEP HATA DIYA GAYA HAI (Zero delay)**
    # time.sleep(0)
    
    chat_history = get_history(user_id)
    
    try:
        # Chat history ke saath AI conversation start
        chat = model.start_chat(history=chat_history)
        
        # Master Prompt bhej kar jawab mangna
        response = chat.send_message(SYSTEM_PROMPT) 
        ai_reply = response.text
        
        # Reply user ko bhej dena
        bot.send_message(user_id, f"🤖 **Naino Academy AI:** {ai_reply}")
        # Aur group ke topic mein bhi record rakhna
        bot.send_message(GROUP_ID, f"🤖 **AI (Instant Test Mode):** {ai_reply}", message_thread_id=topic_id)
        
        # AI ke jawab ko bhi history mein save karna
        save_msg(user_id, 'model', ai_reply) 
        print(f"AI SUCCESS: Replied to user {user_id} in topic {topic_id}")
    except genai.errors.APIError as e:
        # GEMINI Error ko console me dikhana
        print(f"!!! GEMINI API ERROR for user {user_id}: {e}")
        bot.send_message(user_id, "🤖 Sorry! AI system mein error hai. Admin jald hi aayenge.")
    except Exception as e:
        # Koi aur error
        print(f"!!! GENERAL AI ERROR for user {user_id}: {e}")
        bot.send_message(user_id, "❌ Sorry! System error hai. Admin jald hi aayenge.")

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Naya message: Jab koi /start kare
    bot.reply_to(message, "👋 Hii! Main Naino Academy ka AI Support Agent hoon. Aapka message Admin tak pahunch gaya hai, aur main aapko turant reply de raha hoon. Aapko kis chiz ki jankari chahiye?")
    # Ye message aate hi next function mein turant chala jayega

@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    text = message.text

    data = get_topic_data(user_id)

    if not data:
        # Naya user: Topic create karna aur DB mein dalna
        topic = bot.create_forum_topic(GROUP_ID, f"{name} ({user_id})")
        topic_id = topic.message_thread_id
        cursor = db.cursor()
        cursor.execute('INSERT INTO topics VALUES (?, ?, ?)', (user_id, topic_id, time.time())) 
        db.commit()
    else:
        topic_id = data[0]
        update_time(user_id) # Last reply time update

    # User ke message ko history aur group mein save karna
    save_msg(user_id, 'user', text)
    bot.send_message(GROUP_ID, f"👤 **{name}**: {text}", message_thread_id=topic_id)
    
    # AI timer thread chalu karna (Ab delay zero hai)
    threading.Thread(target=ai_assistant_thread, args=(user_id, topic_id)).start()

@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.is_topic_message)
def handle_admin_reply(message):
    topic_id = message.message_thread_id
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM topics WHERE topic_id = ?', (topic_id,))
    res = cursor.fetchone()

    if res:
        user_id = res[0]
        update_time(user_id) # Admin ke reply par time update
        save_msg(user_id, 'model', message.text) # Admin ki baat AI ki memory mein daalo

        try:
            bot.send_message(user_id, f"👨‍💻 **Admin:** {message.text}")
            # Admin ko turant feedback
            bot.reply_to(message, "✅ User tak jawab pahunch gaya.")
        except Exception:
            bot.reply_to(message, "❌ User tak message nahi gaya. Shayad usne bot block kar diya hai.")

# --- WEB SERVER ---
@app.route('/')
def home(): return "<h1>Naino Academy Hybrid Bot is Online!</h1>"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_web_server).start()
    print("Hybrid Bot is now LIVE. Polling started...")
    bot.infinity_polling()
