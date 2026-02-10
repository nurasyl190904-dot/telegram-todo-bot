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
    return "Bot is running with MENU!"

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

# Модельдер
text_model = genai.GenerativeModel("gemini-2.0-flash")
# Егер сурет моделі қолжетімді болса (кейде gemini-pro-vision немесе imagen қолданылады)
# Қазірше текстік модельді қолданамыз, сурет генерациясы бөлек API сұрауы мүмкін.

# ПАЙДАЛАНУШЫНЫҢ КҮЙІН САҚТАУ (Кім не істеп жатыр?)
user_state = {} 
# "chat" -> жай сөйлесу
# "image" -> сурет сипаттамасын күту
# "todo" -> тізімге қосу

user_data = {} # Шаруалар тізімі

# ----------------------------------------------------
# 3. МӘЗІР (MENU) ЖАСАУ
# ----------------------------------------------------
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🤖 AI Чат")
    btn2 = types.KeyboardButton("🎨 Сурет жасау")
    btn3 = types.KeyboardButton("📝 Шаруалар")
    btn4 = types.KeyboardButton("🎥 Видео жасау")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# ----------------------------------------------------
# 4. БОТ ФУНКЦИЯЛАРЫ
# ----------------------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    user_state[chat_id] = "chat" # Бастапқыда жай сөйлесу режимі
    
    bot.send_message(chat_id, 
        "Сәлем! Мен супер-ботпын. Не істейміз?", 
        reply_markup=main_menu()
    )

# БАТЫРМАЛАРДЫ ҰСТАУ
@bot.message_handler(func=lambda message: message.text in ["🤖 AI Чат", "🎨 Сурет жасау", "📝 Шаруалар", "🎥 Видео жасау"])
def menu_handler(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🤖 AI Чат":
        user_state[chat_id] = "chat"
        bot.send_message(chat_id, "Ок, сұрағыңды қоя бер! (Мәтін режимі)", reply_markup=main_menu())

    elif text == "🎨 Сурет жасау":
        user_state[chat_id] = "image"
        bot.send_message(chat_id, "Қандай сурет салайын? Сипаттамасын жаз (Мысалы: Ғарыштағы мысық):", reply_markup=types.ReplyKeyboardRemove())

    elif text == "📝 Шаруалар":
        # Тізімді көрсету
        if chat_id in user_data and user_data[chat_id]:
            tasks = "\n".join([f"{i+1}. {t}" for i, t in enumerate(user_data[chat_id])])
            bot.send_message(chat_id, f"📋 Сенің тізімің:\n{tasks}\n\nҚосу үшін жай жаза бер.", reply_markup=main_menu())
        else:
            bot.send_message(chat_id, "Тізім бос. Жаңа шаруа жазсаң, қосып қоямын.", reply_markup=main_menu())
        user_state[chat_id] = "todo"

    elif text == "🎥 Видео жасау":
        bot.send_message(chat_id, "Видео генерациясы өте ауыр процесс. \nМен саған қазір демо видео жіберемін...", reply_markup=main_menu())
        # Бұл жерде дайын видео жіберуге болады
        # Егер AI видео жасау керек болса, арнайы (Sora/Runway) API керек.
        # Мысал ретінде, бот "жүктеп жатырмын" деп файл жібереді:
        try:
             # Мысал видео (MP4 сілтемесі)
             demo_video = "https://www.w3schools.com/html/mov_bbb.mp4" 
             bot.send_video(chat_id, demo_video, caption="Міне, мысал видео!")
        except:
             bot.send_message(chat_id, "Видео жіберуде қате шықты.")

# МӘТІНДІ ӨҢДЕУ (РЕЖИМГЕ БАЙЛАНЫСТЫ)
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    
    # Егер күй белгісіз болса, чат деп есептейміз
    if chat_id not in user_state:
        user_state[chat_id] = "chat"

    # 1. СУРЕТ ЖАСАУ РЕЖИМІ
    if user_state[chat_id] == "image":
        bot.send_message(chat_id, f"🖌 '{text}' бойынша сурет салып жатырмын... (Күте тұр)")
        try:
            # Gemini арқылы сурет жасау әрекеті (Егер доступ болса)
            # Қазіргі Python SDK-да сурет генерациясы былай шақырылуы мүмкін:
            # model_image = genai.GenerativeModel('imagen-3.0-generate-001')
            # result = model_image.generate_content(text)
            
            # ӘЗІРГЕ СИМУЛЯЦИЯ (Себебі Image API кілті бөлек болуы мүмкін)
            # Шын сурет жасау үшін сенің API кілтіңде "Image Generation" рұқсаты болуы керек.
            bot.send_message(chat_id, "⚠️ Менің серверімде әзірге 'Imagen' моделі қосылмаған. \nБірақ мен сенің сұранысыңды қабылдадым!")
            
            # Мәзірді қайтару
            user_state[chat_id] = "chat"
            bot.send_message(chat_id, "Басқа не істейміз?", reply_markup=main_menu())
            
        except Exception as e:
            bot.send_message(chat_id, f"Қате: {e}")
            user_state[chat_id] = "chat"
            bot.send_message(chat_id, "Мәзірге қайттық.", reply_markup=main_menu())

    # 2. ТІЗІМ РЕЖИМІ
    elif user_state[chat_id] == "todo":
        if chat_id not in user_data: user_data[chat_id] = []
        user_data[chat_id].append(text)
        bot.send_message(chat_id, f"✅ Тізімге қосылды: {text}", reply_markup=main_menu())
        # Бір қосқан соң, мәзірге қайтаруға болады немесе қалдыруға болады.
    
    # 3. ЧАТ РЕЖИМІ (AI)
    else: # "chat"
        try:
            response = text_model.generate_content(text)
            bot.send_message(chat_id, response.text, reply_markup=main_menu())
        except Exception as e:
            bot.send_message(chat_id, "AI жауап бере алмады. Қайталап көр.", reply_markup=main_menu())

# ----------------------------------------------------
# 5. ІСКЕ ҚОСУ
# ----------------------------------------------------
keep_alive()
bot.infinity_polling()
