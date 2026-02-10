import telebot
from telebot import types # Кнопкалар үшін керек
import google.generativeai as genai

# ----------------------------------------------------
# 1. БАПТАУЛАР
# ----------------------------------------------------
TELEGRAM_TOKEN = "8444548738:AAETJGiufSA5dCg4j2lOBo_dEIOB_KU-GHU"
GEMINI_API_KEY = "AIzaSyBMlHtTPTrgIJcslZN7KU8zvPsFeP5Gkl0"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Бұл жерде қазіргі таңдаулы тұрған модель сақталады
# Бастапқыда ең жылдамы тұрсын
current_model_name = "gemini-2.5-flash"
model = genai.GenerativeModel(current_model_name)

user_data = {}

# ----------------------------------------------------
# 2. МОДЕЛЬ АУЫСТЫРУ (КНОПКАЛАРМЕН)
# ----------------------------------------------------
@bot.message_handler(commands=['mode'])
def change_mode(message):
    # Әдемі кнопкалар жасаймыз
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    btn1 = types.InlineKeyboardButton("🚀 Flash 2.5 (Жылдам)", callback_data="set_flash")
    btn2 = types.InlineKeyboardButton("🧠 Pro 2.5 (Ақылды)", callback_data="set_pro")
    btn3 = types.InlineKeyboardButton("🧪 Gemini 3 (Су жаңа)", callback_data="set_gemini3")
    
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, 
                     f"Қазіргі модель: **{current_model_name}**\n"
                     "Ауыстыру үшін төмендегі кнопканы бас:", 
                     reply_markup=markup)

# Кнопка басылғанда істейтін функция
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global current_model_name, model
    
    chat_id = call.message.chat.id
    
    if call.data == "set_flash":
        current_model_name = "gemini-2.5-flash"
        text = "✅ Режим: Gemini 2.5 Flash (Жылдамдыққа қосылды)"
    elif call.data == "set_pro":
        current_model_name = "gemini-2.5-pro"
        text = "✅ Режим: Gemini 2.5 Pro (Сапаға қосылды)"
    elif call.data == "set_gemini3":
        current_model_name = "gemini-3-pro-preview"
        text = "✅ Режим: Gemini 3 Pro (Экспериментке қосылды)"
        
    # Модельді жаңартамыз
    model = genai.GenerativeModel(current_model_name)
    
    # Хабарламаны өзгертеміз (кнопканы алып тастаймыз)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text)

# ----------------------------------------------------
# 3. НЕГІЗГІ ФУНКЦИЯЛАР
# ----------------------------------------------------

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = []
    
    bot.send_message(chat_id, 
        "Сәлем! 👋 Бұл ең мықты бот болды.\n\n"
        "🎛 **/mode** -> Модельді ауыстыру (Flash/Pro/Gemini 3)\n"
        "🤖 **/ai [сұрақ]** -> Сұрақ қою\n"
        "📝 **Жай сөз** -> Шаруа қосу\n"
        "📋 **/show** -> Тізімді көру\n"
        "🗑 **/clear** -> Тазалау"
    )

@bot.message_handler(commands=['ai'])
def ask_ai(message):
    chat_id = message.chat.id
    question = message.text[4:].strip()

    if len(question) < 2:
        bot.send_message(chat_id, "Сұрақты жаз! Мысалы: /ai Сәлем")
        return

    # Қай модель жауап беріп жатқанын ескертеміз
    wait_msg = bot.send_message(chat_id, f"🤖 [{current_model_name}] ойланып жатыр...")

    try:
        response = model.generate_content(question)
        answer = response.text
        
        # parse_mode алып тастадым (қате шықпас үшін)
        bot.send_message(chat_id, answer)
        bot.delete_message(chat_id, wait_msg.message_id)
        
    except Exception as e:
        bot.send_message(chat_id, f"Қате: {e}")

# --- ТІЗІМДЕР (TODO LIST) ---
@bot.message_handler(commands=['show'])
def show_tasks(message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id]:
        tasks = user_data[chat_id]
        text = "📝 ШАРУАЛАР:\n"
        for i, task in enumerate(tasks, 1):
            text += f"{i}. {task}\n"
        bot.send_message(chat_id, text)
    else:
        bot.send_message(chat_id, "Тізім бос!")

@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data[chat_id].clear()
        bot.send_message(chat_id, "Тізім тазартылды!")

@bot.message_handler(content_types=['text'])
def add_task(message):
    chat_id = message.chat.id
    text = message.text
    
    if text.startswith('/'): return
    if chat_id not in user_data: user_data[chat_id] = []
        
    user_data[chat_id].append(text)
    bot.send_message(chat_id, f"✅ Қосылды: {text}")

print("Бот дайын! Telegram-ға кір.")
bot.infinity_polling()
