# 🚀 GitHub Repo Announcer – Telegram Bot

A Telegram bot that monitors a specified GitHub user for **new public repositories** and announces them with a stylish message and inline buttons in a channel and to all private chats.

## Features

- 🔍 Checks for new public repositories **every second** (using GitHub’s ETag to avoid rate limits)
- 📢 Sends a formatted announcement to a Telegram channel and all known private chats
- 🔘 Inline buttons: `View on GitHub`, `Star this Repository`, `Follow Developer`
- 🤖 Says "Hello" on startup
- 🧠 Remembers past repositories, so **only truly new repos** are announced (even after restarts)
- 🧑‍🤝‍🧑 Automatically collects all private chat IDs that message the bot

## Requirements

- Python 3.7+
- `pyTelegramBotAPI`
- `requests`

Install the dependencies:

```bash
pip install pyTelegramBotAPI requests
```

## Setup

1. **Get a Telegram Bot Token**  
   Talk to [@BotFather](https://t.me/BotFather) on Telegram, create a new bot, and copy the API token.

2. **Get a GitHub Personal Access Token** (optional but highly recommended)  
   - Go to [GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)  
   - Generate a new token (no scopes needed)  
   - Copy it.

3. **Add your tokens to the script**  
   Open `bot.py` (or whatever you name the script) and replace:
   - `TELEGRAM_TOKEN` – your bot token from BotFather
   - `CHANNEL` – the channel username (e.g., `@roomshayan`) where announcements will be posted
   - `GITHUB_USER` – the GitHub username to monitor (e.g., `shayanghad0`)
   - `GITHUB_TOKEN` – your GitHub token (or set it as an environment variable `GITHUB_TOKEN`)

4. **Make sure the bot is an admin of the channel** (if the channel is private).  
   If it’s a public channel, just having the bot inside it is enough.

5. **Run the script**  
   ```bash
   python bot.py
   ```

## How It Works

- On the **first run**, the script fetches all existing public repositories of the monitored user and stores their IDs silently – no old repos will be announced.
- Then it starts a background thread for the Telegram bot and the main loop checks GitHub every second.
- When a new repository appears, the bot sends a pre‑styled message with inline buttons to:
  - The configured channel
  - Every private chat that has ever messaged the bot (persistent across restarts)
- The bot also replies to `/start` and `/help` with a welcome message.

## Configuration Files

- `known_repos.json` – stores the IDs of already‑seen repositories.  
  Delete this file if you want to re‑announce all existing repos (not recommended).
- `pv_chats.json` – stores the IDs of private chats that will receive notifications.  
  Automatically populated when someone sends a message to the bot.

## Customisation

- Change the announcement text by editing the `announcement` variable inside `check_github()`.
- Modify the inline buttons by changing the `keyboard` section.

## Running 24/7

To keep the bot running permanently, you can use:
- `screen` or `tmux` on Linux
- `nohup` (e.g., `nohup python bot.py &`)
- A VPS or cloud service (AWS, DigitalOcean, PythonAnywhere, etc.)

## License

This project is provided as-is for personal use. Modify and share freely.


---

Just place this file in your project directory and push it to GitHub (if you want).  
The bot itself doesn’t need the README, but it’s good practice for any public repository. 😊
