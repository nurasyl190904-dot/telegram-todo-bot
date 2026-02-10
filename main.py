import telebot
from telebot import types
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# ----------------------------------------------------
# 1. СЕРВЕРГЕ АРНАЛҒАН ҚОСЫМША (FLASK)
# ----------------------------------------------------
# Бұл бөлік Render сервері ботты "сайт" деп ойлап,
# өшірмеуі үшін керек.
server = Flask(__name__)

@server.route('/')
def home():
    return "Бот жұмыс істеп тұр! (Bot is running)"

def run():
    # Сервер 8080 портында іске қосылады
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

# Бастапқы модель
current_model_name = "gemini-1.5-flash"
try:
    model = genai.GenerativeModel(current_model_name)
except:
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
        "Сәлем! 👋 Мен серверде қосылдым!\n"
        "24/7 жұмыс істеуге дайынмын.\n\n"
        "✅ /ai [сұрақ] - Жасанды интеллект\n"
        "✅ /mode - Модельді ауыстыру\n"
        "✅ /show - Шаруалар тізімі"
    )

@bot.message_handler(commands=['mode'])
def change_mode(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("🚀 Flash (Жылдам)", callback_data="set_flash")
    btn2 = types.InlineKeyboardButton("🧠 Pro (Ақылды)", callback_data="set_pro")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, f"Қазіргі модель: {current_model_name}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global current_model_name, model
    if call.data == "set_flash":
        current_model_name = "gemini-1.5-flash"
    elif call.data == "set_pro":
        current_model_name = "gemini-1.5-pro"
    
    try:
        model = genai.GenerativeModel(current_model_name)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                              text=f"✅ Модель ауысты: {current_model_name}")
    except:
        bot.send_message(call.message.chat.id, "Бұл модель қолжетімсіз, ескісі қалды.")

@bot.message_handler(commands=['ai'])
def ask_ai(message):
    chat_id = message.chat.id
    question = message.text[4:].strip()
    if len(question) < 2:
        bot.send_message(chat_id, "Сұрақты дұрыс қойшы.")
        return

    wait_msg = bot.send_message(chat_id, "Ойланып жатырмын...")
    try:
        response = model.generate_content(question)
        bot.send_message(chat_id, response.text)
        bot.delete_message(chat_id, wait_msg.message_id)
    except Exception as e:
        bot.send_message(chat_id, f"Қате: {e}")

# Шаруа қосу (Todo)
@bot.message_handler(content_types=['text'])
def add_task(message):
    chat_id = message.chat.id
    text = message.text
    if text.startswith('/'): return
    
    if chat_id not in user_data: user_data[chat_id] = []
    user_data[chat_id].append(text)
    bot.send_message(chat_id, f"✅ Қосылды: {text}")

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

# ----------------------------------------------------
# 4. ІСКЕ ҚОСУ
# ----------------------------------------------------
# Алдымен "жалған сайтты" қосамыз, сосын ботты.
keep_alive() 
bot.infinity_polling()
