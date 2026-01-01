import telebot
import sqlite3
import threading
import time
import os
import sys
import google.generativeai as genai
from flask import Flask
from master_prompt import SYSTEM_PROMPT # Prompt import kiya gaya

# --- CONFIGURATION (Environment Variables se Load karna) ---
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

try:
    # GROUP_ID ko integer mein badalna zaroori hai
    GROUP_ID = int(os.environ.get('TELEGRAM_GROUP_ID'))
except (TypeError, ValueError):
    print("ERROR: TELEGRAM_GROUP_ID not set or invalid in environment variables.")
    sys.exit(1)

if not all([API_TOKEN, GEMINI_KEY]):
    print("ERROR: Missing TELEGRAM_API_TOKEN or GEMINI_API_KEY environment variable.")
    sys.exit(1)

# AI and Bot Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# --- DATABASE SETUP ---
def init_db():
    # check_same_thread=False zaroori hai threading ke liye
    conn = sqlite3.connect('chat_bot.db', check_same_thread=False) 
    cursor = conn.cursor()
    # Table 1: Topic mapping aur last reply time
    cursor.execute('CREATE TABLE IF NOT EXISTS topics (user_id INTEGER PRIMARY KEY, topic_id INTEGER, last_reply_time REAL)')
    # Table 2: Chat History (Memory)
    cursor.execute('CREATE TABLE IF NOT EXISTS history (user_id INTEGER, role TEXT, content TEXT)')
    conn.commit()
    return conn

db = init_db()

# --- DATABASE HELPERS ---
def save_msg(user_id, role, content):
    # Message ko history mein save karna
    cursor = db.cursor()
    cursor.execute('INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)', (user_id, role, content))
    db.commit()

def get_history(user_id):
    # Pichle 15 messages nikalna (AI context ke liye)
    cursor = db.cursor()
    cursor.execute('SELECT role, content FROM history WHERE user_id = ? ORDER BY rowid DESC LIMIT 15', (user_id,))
    rows = cursor.fetchall()
    
    history = []
    # Gemini ko 'user' aur 'model' role chahiye
    for role, content in reversed(rows):
        role_type = 'user' if role == 'user' else 'model'
        history.append({"role": role_type, "parts": [content]})
    return history

def get_topic_data(user_id):
    # Last reply time check karna
    cursor = db.cursor()
    cursor.execute('SELECT topic_id, last_reply_time FROM topics WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def update_time(user_id):
    # Admin ke reply par time update karna (AI ko rokne ke liye)
    cursor = db.cursor()
    cursor.execute('UPDATE topics SET last_reply_time = ? WHERE user_id = ?', (time.time(), user_id))
    db.commit()

# --- AI LOGIC (30 SEC WAIT + MEMORY) ---
def ai_assistant_thread(user_id, topic_id):
    time.sleep(30) # 30 seconds ka intezaar

    data = get_topic_data(user_id)
    last_reply = data[1] if data else 0

    # Check: Kya 30 sec se Admin ne reply nahi kiya? (28 sec ka buffer)
    if (time.time() - last_reply) > 28:
        chat_history = get_history(user_id)
        
        try:
            # Chat history ke saath AI conversation start karna
            chat = model.start_chat(history=chat_history)
            
            # Master Prompt ko bhej kar AI se naya jawab mangna
            response = chat.send_message(SYSTEM_PROMPT) 
            ai_reply = response.text
            
            # Reply user ko bhej dena
            bot.send_message(user_id, f"🤖 {ai_reply}")
            # Aur group ke topic mein bhi record rakhna
            bot.send_message(GROUP_ID, f"🤖 **AI Assistant:** {ai_reply}", message_thread_id=topic_id)
            
            # AI ke jawab ko bhi history mein save karna
            save_msg(user_id, 'model', ai_reply) 
        except Exception as e:
            print(f"AI Error for user {user_id}: {e}")

# --- BOT HANDLERS ---

@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_user_msg(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    text = message.text

    data = get_topic_data(user_id)

    if not data:
        # Naya user: Topic create karna
        topic = bot.create_forum_topic(GROUP_ID, f"{name} ({user_id})")
        topic_id = topic.message_thread_id
        cursor = db.cursor()
        cursor.execute('INSERT INTO topics VALUES (?, ?, ?)', (user_id, topic_id, time.time())) # Time.time() initial set
        db.commit()
    else:
        topic_id = data[0]
        update_time(user_id) # User ke message par bhi time update karo (taki AI uske hi message par khud reply na kare)

    # User ke message ko history aur group mein save karna
    save_msg(user_id, 'user', text)
    bot.send_message(GROUP_ID, f"👤 **{name}**: {text}", message_thread_id=topic_id)
    
    # AI timer thread chalu karna
    threading.Thread(target=ai_assistant_thread, args=(user_id, topic_id)).start()

@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.is_topic_message)
def handle_admin_reply(message):
    topic_id = message.message_thread_id
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM topics WHERE topic_id = ?', (topic_id,))
    res = cursor.fetchone()

    if res:
        user_id = res[0]
        update_time(user_id) # MOST IMPORTANT: Admin ke reply par time update
        save_msg(user_id, 'model', message.text) # Admin ki baat AI ki memory mein daalo

        try:
            bot.send_message(user_id, f"👨‍💻 **Admin:** {message.text}")
        except:
            bot.reply_to(message, "❌ User tak message nahi gaya. Shayad usne bot block kar diya hai.")

# --- WEB SERVER (Render ke liye) ---
@app.route('/')
def home(): 
    return "<h1>Naino Academy Hybrid Bot is Online!</h1><p>Bot is running with AI and Admin support.</p>"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    # Flask ko run karna
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Web server aur Bot polling ko alag threads mein run karna
    threading.Thread(target=run_web_server).start()
    print("Hybrid Bot is now LIVE. Polling started...")
    bot.infinity_polling()
