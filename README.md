# Discord Task & Note Manager Bot

AI-powered Discord bot for task management, note-taking, and intelligent conversation analysis using Google's Gemini API.

## Features

- 🤖 **AI-Powered Responses** - Ask questions with conversation context using Gemini
- ✅ **Task Management** - Create, track, and manage tasks with status and priorities
- 📝 **Note Taking** - Store and search notes with tags
- 💬 **Message Monitoring** - Automatically collects messages from selected channels
- 📊 **Smart Summaries** - Summarize conversations and analyze tasks/notes
- 💾 **Auto-Save** - Persistent storage with automatic backups

## Quick Start

### 1. Get Your API Keys

#### Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it
3. Go to "Bot" section → Click "Add Bot"
4. **IMPORTANT**: Enable these under "Privileged Gateway Intents":
   - ✅ **MESSAGE CONTENT INTENT** (required!)
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
5. Click "Reset Token" → Copy the token

#### Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file:

```bash
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
COMMAND_PREFIX="!g "

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Bot Configuration
MESSAGE_BUFFER_SIZE=500
MONITORED_CHANNELS=channel_id_1,channel_id_2,channel_id_3
ENABLE_PERSISTENCE=true
PERSISTENCE_FILE=data/bot_data.json
```

**How to get Channel IDs:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click on a channel → Copy Channel ID
3. Add multiple channel IDs separated by commas

### 4. Invite Bot to Your Server

1. Go to https://discord.com/developers/applications
2. Select your application → "OAuth2" → "URL Generator"
3. Select scopes: ✅ `bot`
4. Select permissions:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Read Message History
   - ✅ Embed Links
   - ✅ Attach Files
5. Copy the generated URL and open in browser
6. Select your server and authorize

### 5. Run the Bot

```bash
python bot.py
```

You should see:
```
✅ Bot is ready! Logged in as YourBot#1234
✅ Monitoring X channels
```

## Commands

All commands start with `!g ` (note the space after !g)

### General
```
!g commands          # Show all commands
!g stats             # Show bot statistics
!g save              # Manually save data
```

### Tasks
```
!g task add <title> | <description>    # Create a task
!g task list [status]                  # List tasks
!g task done <id>                      # Mark task as done
!g task delete <id>                    # Delete a task
```

### Notes
```
!g note add <title> | <content>    # Create a note
!g note list                       # List all notes
!g note search <query>             # Search notes
!g note delete <id>                # Delete a note
```

### AI
```
!g ask <question>           # Ask AI with conversation context
!g summarize [limit]        # Summarize recent messages
!g analyze tasks            # Get AI insights on your tasks
!g analyze notes            # Get AI insights on your notes
```

## Deploy for 24/7 Operation

### Option 1: Railway (Recommended - Free Tier)

1. **Initialize Git & Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-repo-url
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to https://railway.app
   - Sign up/Login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Add Environment Variables in Railway**
   - Click "Variables" tab
   - Add these variables:
     - `DISCORD_TOKEN` = your_token
     - `GEMINI_API_KEY` = your_key
     - `COMMAND_PREFIX` = `"!g "`
     - `MONITORED_CHANNELS` = your_channel_ids
     - `MESSAGE_BUFFER_SIZE` = `500`
     - `ENABLE_PERSISTENCE` = `true`
     - `PERSISTENCE_FILE` = `data/bot_data.json`
     - `GEMINI_MODEL` = `gemini-2.5-flash`

4. **Deploy**
   - Railway will automatically deploy
   - Check logs to verify bot is running

### Option 2: Docker

```bash
# Build and run
docker build -t discord-bot .
docker run -d --name discord-bot --env-file .env discord-bot

# Or use Docker Compose
docker-compose up -d
```

### Option 3: VPS/Server with systemd

Create `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Task Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot
```

## Troubleshooting

**Bot doesn't respond:**
- ✅ Enable MESSAGE CONTENT INTENT in Discord Developer Portal
- ✅ Verify command prefix is `"!g "` (with space and quotes)
- ✅ Check you're in a monitored channel
- ✅ Verify bot has message permissions

**Bot can't see messages:**
- ✅ Enable MESSAGE CONTENT INTENT
- ✅ Check channel IDs are correct
- ✅ Verify "Read Message History" permission

**Gemini API errors:**
- ✅ Verify API key is correct
- ✅ Check API quota limits

**Data not persisting:**
- ✅ Check `ENABLE_PERSISTENCE=true`
- ✅ Verify `data/` directory exists

## Project Structure

```
.
├── bot.py                  # Main bot application
├── config.py               # Configuration management
├── message_buffer.py       # Message collection
├── task_note_manager.py    # Task/note management
├── gemini_service.py       # Gemini AI integration
├── persistence.py          # Data persistence
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── Procfile               # Railway deployment
├── Dockerfile             # Docker configuration
└── data/                  # Persistent storage
    └── bot_data.json
```

## Requirements

- Python 3.11+
- Discord Bot Token
- Google Gemini API Key

---

**Built with**: Python, discord.py, Google Gemini AI

