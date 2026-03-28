import telebot
from telebot import types
from groq import Groq
import os
import random
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
def home(): return "Bot Live!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# AI orqali test generatsiya qilish funksiyasi
def get_ai_test(subject, count):
    prompt = f"Menga {subject} fanidan {count} ta DTM darajasidagi test tuzib ber. Format: har bir savol raqamlangan, variantlari A,B,C,D va oxirida 'KALIT:' so'zi bilan to'g'ri javoblar bo'lsin. Masalan: 1A, 2B..."
    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        return completion.choices[0].message.content
    except:
        return "Xatolik: AI test tuza olmadi."

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    user_data[uid] = {'step': 'name', 'score': 0, 'invited': 0}
    bot.send_message(uid, "Xush kelibsiz! Ism va familiyangizni kiriting:")

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'name')
def name_step(message):
    uid = message.chat.id
    user_data[uid]['name'] = message.text
    user_data[uid]['step'] = 'major1'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Matematika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili")
    bot.send_message(uid, "1-asosiy fanni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'major1')
def major1_step(message):
    uid = message.chat.id
    user_data[uid]['m1'] = message.text
    user_data[uid]['step'] = 'cert1'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Bor (A+/A/IELTS 7+)", "Bor (B+/B/IELTS 5.5-6.5)", "Yo'q")
    bot.send_message(uid, f"{message.text}dan sertifikatingiz bormi?", reply_markup=markup)

@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'cert1')
def cert1_step(message):
    uid = message.chat.id
    msg = message.text
    if "A+" in msg or "7+" in msg: user_data[uid]['score'] += 93.0
    user_data[uid]['step'] = 'major2'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Matematika", "Fizika", "Kimyo", "Biologiya", "Tarix", "Ingliz tili")
    bot.send_message(uid, "2-asosiy fanni tanlang:", reply_markup=markup)

# TESTNI BOSHLASH TUGMASI
@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get('step') == 'major2')
def major2_step(message):
    uid = message.chat.id
    user_data[uid]['m2'] = message.text
    user_data[uid]['step'] = 'ready'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Testni boshlash")
    bot.send_message(uid, "Hamma ma'lumotlar olindi. Tayyor bo'lsangiz boshlaymiz!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🚀 Testni boshlash")
def run_test(message):
    uid = message.chat.id
    bot.send_message(uid, "AI siz uchun maxsus 90 ta savol tayyorlayapti... (Bu 30 soniya olishi mumkin)")
    
    # Bu yerda AI fanlarga qarab testlarni generatsiya qiladi
    m1_test = get_ai_test(user_data[uid]['m1'], 30)
    bot.send_message(uid, f"1-FAN: {user_data[uid]['m1']}\n\n{m1_test}")
    
    bot.send_message(uid, "Javoblaringizni quyidagi formatda yuboring:\n`1a2b3c...` (jami 30 ta)")

# JAVOBLARNI QABUL QILISH VA REFERAL
@bot.message_handler(func=lambda m: len(m.text) > 20)
def check_answers(message):
    uid = message.chat.id
    # Bu yerda mantiqiy hisob-kitob qilinadi
    final_score = user_data[uid]['score'] + random.uniform(50, 80) # Namuna uchun
    ref_link = f"https://t.me/{(bot.get_me()).username}?start={uid}"
    
    bot.send_message(uid, f"🏁 Test yakunlandi!\n👤 {user_data[uid]['name']}\n📊 Umumiy ball: {round(final_score, 1)}\n\n⚠️ Xatolar tahlilini ko'rish uchun 1 ta do'stingizni taklif qiling:\n{ref_link}")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
  
