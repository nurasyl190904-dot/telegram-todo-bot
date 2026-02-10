import telebot
from telebot import types
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
import time

# ----------------------------------------------------
# 1. СЕРВЕРГЕ АРНАЛҒАН ҚОСЫМША (FLASK)
# ----------------------------------------------------
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running OK!"

def run():
    server.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------------------------------------------
# 2. БОТТЫҢ НЕГІЗГІ БАПТАУЛАРЫ
# ----------------------------------------------------
TELEGRAM_TOKEN = "8444548738:AAETJGiufSA5dCg4j2lOBo_dEIOB_KU-GHU"
GEMINI_API_KEY = "AIzaSyBMlHtTPTrgIJcslZN7KU8zvPsFeP5Gkl0"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# --- ТҮЗЕТІЛГЕН ЖЕРІ: Gemini 2.0 Flash ---
current_model_name = "gemini-2.0-flash" 

# Модельді жүктейміз
try:
    model = genai.GenerativeModel(current_model_name)
except:
    # Егер 2.0 істемесе, ең қарапайым Pro-ға ауысады
    current_model_name = "gemini-pro"
    model = genai.GenerativeModel("gemini-pro")

user_data = {}

# ----------------------------------------------------
# 3. БОТ ФУНКЦИЯЛАРЫ
# ----------------------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data: user_data[chat_id] = []
    
    bot.send_message(chat_id, 
        f"Сәлем! 👋 Мен сервердемін!\n"
        f"Қазіргі миым: {current_model_name}\n\n"
        "✅ /ai [сұрақ] - Сұрақ қою\n"
        "✅ /mode - Модельді ауыстыру\n"
        "✅ /show - Шаруалар"
    )

@bot.message_handler(commands=['mode'])
def change_mode(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Сенің тізіміңдегі нақты бар модельдер:
    btn1 = types.InlineKeyboardButton("🚀 Flash 2.0 (Жылдам)", callback_data="set_flash")
    btn2 = types.InlineKeyboardButton("🧠 Pro (Классика)", callback_data="set_pro")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f"Модельді таңда (Қазір: {current_model_name}):", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global current_model_name, model
    chat_id = call.message.chat.id
    
    if call.data == "set_flash":
        new_model = "gemini-2.0-flash"
    elif call.data == "set_pro":
        new_model = "gemini-pro"
    
    try:
        model = genai.GenerativeModel(new_model)
        current_model_name = new_model
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, 
                              text=f"✅ Ауыстырылды: {current_model_name}")
    except Exception as e:
        bot.send_message(chat_id, f"Қате: {e}")

@bot.message_handler(commands=['ai'])
def ask_ai(message):
    chat_id = message.chat.id
    question = message.text[4:].strip()
    if len(question) < 2:
        bot.send_message(chat_id, "Сұрақты жазшы.")
        return

    wait_msg = bot.send_message(chat_id, "Ойланып жатырмын...")
    try:
        response = model.generate_content(question)
        bot.send_message(chat_id, response.text)
        bot.delete_message(chat_id, wait_msg.message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Қате: {e}")

# Шаруа қосу
@bot.message_handler(content_types=['text'])
def add_task(message):
    if message.text.startswith('/'): return
    chat_id = message.chat.id
    if chat_id not in user_data: user_data[chat_id] = []
    user_data[chat_id].append(message.text)
    bot.send_message(chat_id, f"✅ Қосылды: {message.text}")

@bot.message_handler(commands=['show'])
def show_tasks(message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id]:
        msg = "📝 Тізім:\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(user_data[chat_id])])
        bot.send_message(chat_id, msg)
    else:
        bot.send_message(chat_id, "Тізім бос.")

@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    if message.chat.id in user_data:
        user_data[message.chat.id].clear()
        bot.send_message(message.chat.id, "Тазартылды!")

# 4. ІСКЕ ҚОСУ
keep_alive()
bot.infinity_polling()
