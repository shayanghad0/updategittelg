import time
import threading
import json
import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========== CONFIGURATION ==========
TELEGRAM_TOKEN = ""
CHANNEL = ""
GITHUB_USER = ""
GITHUB_TOKEN = ""
# ===================================

bot = telebot.TeleBot(TELEGRAM_TOKEN)

KNOWN_REPOS_FILE = "known_repos.json"
PV_CHATS_FILE = "pv_chats.json"

def load_json(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

known_repo_ids = set(load_json(KNOWN_REPOS_FILE, []))
private_chats = set(load_json(PV_CHATS_FILE, []))

# ---- Telegram handlers ----
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I'm monitoring @shayanghad0's public repos.")
    if message.chat.type == "private":
        private_chats.add(message.chat.id)
        save_json(PV_CHATS_FILE, list(private_chats))

@bot.message_handler(func=lambda message: True)
def catch_all_messages(message):
    if message.chat.type == "private":
        private_chats.add(message.chat.id)
        save_json(PV_CHATS_FILE, list(private_chats))

# ---- Startup "Hello" ----
def say_hello():
    hello_text = "Hello! Bot started – now monitoring @shayanghad0 for new public repos."
    try:
        bot.send_message(CHANNEL, hello_text)
    except Exception as e:
        print(f"Failed to send hello to channel: {e}")
    for chat_id in private_chats.copy():
        try:
            bot.send_message(chat_id, hello_text)
        except Exception as e:
            print(f"Failed to send hello to {chat_id}: {e}")

# ---- Preload existing repos (runs once, silently) ----
def preload_existing_repos():
    """Fetch all current public repos and mark them as known (no announcement)."""
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?type=public&per_page=100"
    headers = {
        "User-Agent": "RepoMonitorBot",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            repos = resp.json()
            ids = [repo["id"] for repo in repos]
            save_json(KNOWN_REPOS_FILE, ids)
            return set(ids)
    except Exception as e:
        print(f"Error preloading repos: {e}")
    return set()

# ---- GitHub monitoring (every 1 second) ----
etag = None

def check_github():
    global etag, known_repo_ids
    url = f"https://api.github.com/users/{GITHUB_USER}/repos?type=public&sort=created&per_page=5"
    headers = {
        "User-Agent": "RepoMonitorBot",
        "Authorization": f"token {GITHUB_TOKEN}"
    }
    if etag:
        headers["If-None-Match"] = etag

    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"GitHub request error: {e}")
        return

    if resp.status_code == 304:
        return
    elif resp.status_code == 403:
        print("GitHub rate limit hit. Waiting 60 seconds...")
        time.sleep(60)
        return
    elif resp.status_code != 200:
        print(f"GitHub API error {resp.status_code}: {resp.text}")
        return

    new_etag = resp.headers.get("ETag")
    if new_etag:
        etag = new_etag

    repos = resp.json()
    new_repos = []
    for repo in repos:
        rid = repo["id"]
        if rid not in known_repo_ids:
            known_repo_ids.add(rid)
            new_repos.append(repo)

    if new_repos:
        save_json(KNOWN_REPOS_FILE, list(known_repo_ids))

        for repo in new_repos:
            repo_name = repo['name']
            repo_full_name = repo['full_name']
            repo_url = repo['html_url']
            description = repo.get('description') or ''

            announcement = (
                f"🚀 The new repository of shayan!!\n\n"
                f"{repo_name}\n"
                + (f"{description}\n" if description else "")
                + f"\n{repo_url}\n\n"
                "⭐️ Star The Project Please For More Code ⭐️\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📌 Repository: {repo_full_name}\n"
                "👨‍💻 Developer: @shayanghad0\n"
                "⭐️ Stars: Support the project!\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━"
            )

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("📦 View on GitHub", url=repo_url))
            keyboard.add(InlineKeyboardButton("⭐️ Star this Repository", url=repo_url))
            keyboard.add(InlineKeyboardButton("🔗 Follow Developer", url="https://github.com/shayanghad0"))

            # Send to channel
            try:
                bot.send_message(CHANNEL, announcement, reply_markup=keyboard)
            except Exception as e:
                print(f"Channel send error: {e}")

            # Send to all known private chats
            for chat_id in private_chats.copy():
                try:
                    bot.send_message(chat_id, announcement, reply_markup=keyboard)
                except Exception as e:
                    print(f"PV send error to {chat_id}: {e}")

            print(f"Announced: {repo_full_name}")

# ---- Main loop ----
def github_polling():
    while True:
        check_github()
        time.sleep(1)

if __name__ == "__main__":
    # On first run, silently register all existing repos so they won't be announced
    if not os.path.exists(KNOWN_REPOS_FILE):
        print("First run – loading existing repositories silently...")
        known_repo_ids = preload_existing_repos()
        print(f"Marked {len(known_repo_ids)} existing repos as known.")
    else:
        known_repo_ids = set(load_json(KNOWN_REPOS_FILE, []))

    say_hello()

    bot_thread = threading.Thread(target=bot.infinity_polling, daemon=True)
    bot_thread.start()

    github_polling()
