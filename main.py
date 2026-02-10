import telebot
from telebot import types
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# ----------------------------------------------------
# 1. СЕРВЕРГЕ АРНАЛҒАН ҚОСЫМША (FLASK)
# ----------------------------------------------------
server = Flask(__name__)

@server.route('/')
def home():
    return "Bot is running in AI MODE!"

def run():
    server.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----------------------------------------------------
# 2. БАПТАУЛАР
# ----------------------------------------------------
TELEGRAM_TOKEN = "8444548738:AAETJGiufSA5dCg4j2lOBo_dEIOB_KU-GHU"
GEMINI_API_KEY = "AIzaSyBMlHtTPTrgIJcslZN7KU8zvPsFeP5Gkl0"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Ең күшті модельді қосамыз
model = genai.GenerativeModel("gemini-2.0-flash")

# Пайдаланушы күйі (Сурет сұрап жатыр ма, жоқ па?)
user_state = {} 
user_tasks = {} # Шаруалар тізімі

# ----------------------------------------------------
# 3. МӘЗІР (MENU)
# ----------------------------------------------------
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🎨 Сурет салғызу")
    btn2 = types.KeyboardButton("🎥 Видео жібер")
    btn3 = types.KeyboardButton("📝 Тізімді көрсет")
    btn4 = types.KeyboardButton("🗑 Тазалау")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ----------------------------------------------------
# 4. БОТ ФУНКЦИЯЛАРЫ
# ----------------------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 
        "Сәлем! 👋 Мен дайынмын!\n\n"
        "💬 **Маған кез келген нәрсе жаз — бірден жауап беремін!**\n"
        "📝 Егер тізімге қосқың келсе: 'Сақта: [шаруа]' деп жаз.\n", 
        reply_markup=main_menu()
    )

# --- БАТЫРМАЛАРДЫ БАСҚАРУ ---
@bot.message_handler(func=lambda message: message.text in ["🎨 Сурет салғызу", "🎥 Видео жібер", "📝 Тізімді көрсет", "🗑 Тазалау"])
def menu_handler(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🎨 Сурет салғызу":
        user_state[chat_id] = "waiting_image"
        bot.send_message(chat_id, "Қандай сурет салайын? Сипаттамасын жаз (Мысалы: Ғарыштағы мысық):")

    elif text == "🎥 Видео жібер":
        bot.send_message(chat_id, "Видео жүктеліп жатыр...")
        try:
            # Мысал видео (Demo)
            video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
            bot.send_video(chat_id, video_url, caption="Міне, видео!")
        except:
            bot.send_message(chat_id, "Қате шықты.")

    elif text == "📝 Тізімді көрсет":
        if chat_id in user_tasks and user_tasks[chat_id]:
            tasks = "\n".join([f"{i+1}. {t}" for i, t in enumerate(user_tasks[chat_id])])
            bot.send_message(chat_id, f"📋 Тізім:\n{tasks}")
        else:
            bot.send_message(chat_id, "Тізім бос.")

    elif text == "🗑 Тазалау":
        if chat_id in user_tasks:
            user_tasks[chat_id].clear()
        bot.send_message(chat_id, "Чат тарихы мен тізім тазартылды! (Жаңа өмір 🌿)")

# --- НЕГІЗГІ ЧАТ (AI) ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    # 1. Егер сурет күтіп тұрсақ
    if user_state.get(chat_id) == "waiting_image":
        bot.send_message(chat_id, f"🖼 '{text}' бойынша сурет салу сұранысы қабылданды! (Серверде Image API болса, сурет шығар еді).")
        user_state[chat_id] = None # Режимнен шығамыз
        return

    # 2. Егер "Сақта:" деп бастаса -> Тізімге қосамыз
    if text.lower().startswith("сақта:") or text.lower().startswith("save:"):
        task = text.split(":", 1)[1].strip()
        if chat_id not in user_tasks: user_tasks[chat_id] = []
        user_tasks[chat_id].append(task)
        bot.send_message(chat_id, f"✅ Тізімге қосылды: {task}")
        return

    # 3. ҚАЛҒАНЫНЫҢ БӘРІ -> AI ЖАУАП БЕРЕДІ (ТІКЕЛЕЙ)
    try:
        # "Ойланып жатырмын" дегенді алып тастадым, тез жауап беру үшін
        response = model.generate_content(text)
        bot.send_message(chat_id, response.text)
    except Exception as e:
        bot.send_message(chat_id, "Кешір, сұрағыңды түсінбедім немесе қате шықты.")

# ----------------------------------------------------
# 5. ІСКЕ ҚОСУ
# ----------------------------------------------------
keep_alive()
bot.infinity_polling()
