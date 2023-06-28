import poe
import os
import telebot
from dotenv import load_dotenv

load_dotenv()
token = "m87UlQ4NDefo_CAwj-9kCQ%3D%3D"
bot_token = "6031689793:AAFyTehAoEqEXcrpGwajl-R4Zed5HYYzfTQ"
adminId = 6113550151

bot = telebot.TeleBot(bot_token)
client = poe.Client(token)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, "<b>Welcome!</b> ✨\n<i>Send any query or ask questions.</i>", parse_mode="HTML")


@bot.message_handler(func=lambda message: True)
def claude(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        for chunk in client.send_message(
        chatbot="capybara",
        message=message.text,
        with_chat_break="false",
        timeout=20,
        ):
            pass
        bot.reply_to(message, chunk["text"])
    except Exception as e:
        bot.reply_to(message, f"Oops! Something went wrong. {e}")

    

bot.polling()
