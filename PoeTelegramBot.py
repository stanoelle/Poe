import logging
import os
import json
import random
import time
import shutil
from BingImageCreator import ImageGen
from dotenv import load_dotenv
from telebot import TeleBot, types

# Load environment variables from .env file
load_dotenv()

# Get environment variables
TELEGRAM_TOKEN = "6179975944:AAEgrJwmzF0urBQOMYOVhGyosAFGoGYTc14"
POE_COOKIE = "m87UlQ4NDefo_CAwj-9kCQ%3D%3D"
ALLOWED_USERS = os.getenv("ALLOWED_USERS")
ALLOWED_CHATS = os.getenv("ALLOWED_CHATS")

# Retrieve the Bing auth_cookie from the environment variables
auth_cookie = os.getenv("BING_AUTH_COOKIE")

# Check if environment variables are set
if not TELEGRAM_TOKEN:
    raise ValueError("Telegram bot token not set")
if not POE_COOKIE:
    raise ValueError("POE.com cookie not set")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Set the logging level to a higher level (e.g., WARNING) to suppress INFO messages
logging.getLogger("httpx").setLevel(logging.WARNING)

# Initialize the POE client
poe.logger.setLevel(logging.INFO)

poe_headers = os.getenv("POE_HEADERS")
if poe_headers:
    poe.headers = json.loads(poe_headers)

client = poe.Client(POE_COOKIE)

# Get the default model from the .env file
default_model = os.getenv("DEFAULT_MODEL")

# Set the default model
selected_model = default_model if default_model else "capybara"

bot = TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if ALLOWED_CHATS and str(chat_id) not in ALLOWED_CHATS.split(",") and str(user_id) not in ALLOWED_USERS.split(","):
        # Deny access if the user is not in the allowed users list and the chat is not in the allowed chats list
        bot.send_message(
            chat_id=chat_id,
            text="Sorry, you are not allowed to use this bot. If you are the one who set up this bot, add your Telegram UserID to the \"ALLOWED_USERS\" environment variable in your .env file, or use it in the \"ALLOWED_CHATS\" you specified."
        )
        return

    bot.send_message(
        chat_id=chat_id,
        text="I'm a Poe.com Telegram Bot. Use /help for a list of commands.",
    )

@bot.message_handler(commands=["purge"])
def purge(message):
    try:
        # Purge the entire conversation
        client.purge_conversation(selected_model)

        # Remove the chat log file
        if os.path.isfile(chat_log_file):
            os.remove(chat_log_file)

        bot.send_message(
            chat_id=message.chat.id,
            text="Conversation purged. Chat log file deleted.",
        )
    except Exception as e:
        handle_error(message, e)

@bot.message_handler(commands=["reset"])
def reset(message):
    try:
        # Clear the context
        client.send_chat_break(selected_model)

        # Remove the chat log file
        if os.path.isfile(chat_log_file):
            os.remove(chat_log_file)

        bot.send_message(
            chat_id=message.chat.id,
            text="Context cleared. Chat log file deleted.",
        )
    except Exception as e:
        handle_error(message, e)

@bot.message_handler(commands=["select"])
def select(message):
    try:
        # Get the list of available models
        models = client.get_models()

        # Create a keyboard with the available models
        keyboard = types.InlineKeyboardMarkup()
        for model in models:
            button = types.InlineKeyboardButton(
                text=model, callback_data=f"select_model_{model}"
            )
            keyboard.add(button)

        bot.send_message(
            chat_id=message.chat.id,
            text="Please select a model:",
            reply_markup=keyboard,
        )
    except Exception as e:
        handle_error(message, e)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_model_"))
def callback_select_model(call):
    try:
        model = call.data.split("_", 2)[-1]
        global selected_model
        selected_model = model
        bot.send_message(
            chat_id=call.message.chat.id,
            text=f"Selected model: {model}",
        )
    except Exception as e:
        handle_error(call.message, e)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if ALLOWED_CHATS and str(chat_id) not in ALLOWED_CHATS.split(",") and str(user_id) not in ALLOWED_USERS.split(","):
        # Deny access if the user is not in the allowed users list and the chat is not in the allowed chats list
        bot.send_message(
            chat_id=chat_id,
            text="Sorry, you are not allowed to use this bot. If you are the one who set up this bot, add your Telegram UserID to the \"ALLOWED_USERS\" environment variable in your .env file, or use it in the \"ALLOWED_CHATS\" you specified."
        )
        return

    # Process the message using the POE API
    response = client.send_message(selected_model, message.text)

    # Get the response text from the POE API response
    response_text = response[0]["text_new"]

    # Send the response back to the user
    bot.send_message(chat_id=chat_id, text=response_text)

bot.polling()
