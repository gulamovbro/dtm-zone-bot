import telebot
from telebot import types
from groq import Groq
import os
import time
from flask import Flask
from threading import Thread

# SOZLAMALAR
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
app = Flask('')

# Foydalanuvchi ma'lumotlari ombori
user_data = {}

@app.route('/')
def home(): return "DTM Zone Bot is running!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# AI orqali test generatsiya qilish (Yaxshilangan variant)
def get_ai_test(subject, count=10):
    prompt = (f"Sen O'zbekiston DTM ekspertisan. {subject} fanidan {count} ta murakkab test tuz. "
              "Format: Savol matni, ostida A, B, C, D variantlar. "
              "Faqat o'zbek tilida yoz. Eng oxirida 'KALIT:' deb to'g'ri javoblarni yoz.")
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768", # Kattaroq va aqlliroq model
            temperature=0.6,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "⚠️ AI hozirda band. Iltimos, birozdan so'ng 'Testni boshlash' tugmasini qayta bosing."

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    user_data[uid] = {'step': 'name', 'score': 0, 'm1': '', 'm2': ''}
    bot.send_message(uid, "Assalomu alaykum! DTM Imtihon Simulyatoriga xush kelibsiz.\n\nIsm va familiyangizni kiriting:")

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'name')
def name_step(message):
    uid = message.chat.id
    user_data[uid]['name'] = message.text
    user_data[uid]['step'] = 'major1'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Matematika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili")
    bot.send_message(uid, "1-asosiy fanni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'major1')
def major1_step(message):
    uid = message.chat.id
    user_data[uid]['m1'] = message.text
    user_data[uid]['step'] = 'cert1'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Sertifikat bor ✅", "Sertifikat yo'q ❌")
    bot.send_message(uid, f"{message.text} fanidan milliy yoki xalqaro sertifikatingiz bormi?", reply_markup=markup)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'cert1')
def cert1_step(message):
    uid = message.chat.id
    if "bor" in message.text.lower():
        user_data[uid]['score'] += 93.0
        bot.send_message(uid, "Ajoyib! Ushbu fan uchun sizga maksimal 93.0 ball beriladi.")
    
    user_data[uid]['step'] = 'major2'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Matematika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili")
    bot.send_message(uid, "2-asosiy fanni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'major2')
def major2_step(message):
    uid = message.chat.id
    user_data[uid]['m2'] = message.text
    user_data[uid]['step'] = 'ready'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Testni boshlash")
    bot.send_message(uid, "Hamma ma'lumotlar olindi. Tayyor bo'lsangiz testni boshlaymiz!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 Testni boshlash")
def run_test(message):
    uid = message.chat.id
    bot.send_message(uid, "🤖 AI savollarni generatsiya qilmoqda... (10-20 soniya kuting)")
    
    # Savollarni olish
    m1_name = user_data[uid]['m1']
    test_content = get_ai_test(m1_name, 10) # Barqarorlik uchun 10 ta savol
    
    bot.send_message(uid, f"📚 Fan: {m1_name}\n\n{test_content}")
    bot.send_message(uid, "Javoblaringizni `1a2b3c...` shaklida yuboring. Ballni hisoblash va tahlil uchun kamida 1 ta do'stingizni taklif qilishingiz kerak bo'ladi.")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
    
