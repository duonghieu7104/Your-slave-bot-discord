# Discord Task & Note Manager Bot with Gemini AI

A powerful Discord bot that helps you manage tasks, notes, and leverages Google's Gemini AI to provide intelligent assistance based on your conversation history and project plans.

## Table of Contents

- [0. Introduction](#0-introduction)
  - [Features](#features)
  - [Demo](#demo)
  - [Prerequisites](#prerequisites)
  - [Project Structure](#project-structure)
- [1. Run Locally](#1-run-locally)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Bot](#running-the-bot)
- [2. Run with Docker](#2-run-with-docker)
  - [Using Docker](#using-docker)
  - [Using Docker Compose](#using-docker-compose)
- [3. Deploy to Railway](#3-deploy-to-railway)
  - [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Deployment](#deployment)
- [Commands Reference](#commands-reference)
- [Troubleshooting](#troubleshooting)

---

## 0. Introduction

### Features

- **Task Management**: Create, track, and manage tasks with priorities and due dates
- **Note Taking**: Store and search through notes with tags
- **AI-Powered Assistance**: 
  - Ask questions with context from your notes and plans
  - Chat directly with Gemini AI without context
  - Summarize conversations
  - Analyze tasks and notes
- **Smart Channel System**:
  - Context Channels: Messages are stored and used as AI context (notes, plans, documentation)
  - Command Channels: Bot responds to commands only (messages not stored)
- **Message Buffer**: Automatically fetches and stores messages from context channels
- **Data Persistence**: Saves tasks and notes to JSON file

### Demo

> Add your screenshots and video links here

**Screenshots:**
- [Add screenshot of bot commands]
- [Add screenshot of task management]
- [Add screenshot of AI responses]

**Video Demo:**
- [Add video link here]

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token - [Create one here](https://discord.com/developers/applications)
- Google Gemini API Key - [Get one here](https://makersuite.google.com/app/apikey)
- Docker (optional, for containerized deployment)
- Railway account (optional, for cloud deployment)

### Project Structure

```
Your-slave/
├── bot.py                 # Main bot implementation
├── config.py             # Configuration management
├── gemini_service.py     # Gemini AI integration
├── message_buffer.py     # Message buffering system
├── task_note_manager.py  # Task and note management
├── persistence.py        # Data persistence
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create from .env.example)
├── .env.example         # Environment variables template
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── Procfile            # Railway deployment configuration
├── railway.json        # Railway configuration
├── README.md           # This file
└── data/               # Data storage directory
    └── bot_data.json   # Persisted tasks and notes
```

---

## 1. Run Locally

### Installation

**Step 1: Clone the Repository**

```bash
git clone <your-repo-url>
cd Your-slave
```

**Step 2: Install Dependencies**

```bash
pip install -r requirements.txt
```

### Configuration

**Step 1: Create Environment File**

```bash
cp .env.example .env
```

**Step 2: Edit `.env` File**

Open `.env` and configure the following:

```env
# Discord Bot Token
DISCORD_TOKEN=your_discord_token_here

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Bot Configuration
COMMAND_PREFIX="!g "
GEMINI_MODEL=gemini-2.5-flash
MESSAGE_BUFFER_SIZE=500

# Context Channels: Messages from these channels are read and used as context for Gemini AI
# These should be your notes, plans, documentation channels
CONTEXT_CHANNELS=channel_id_1,channel_id_2,channel_id_3

# Command Channels: Bot responds to commands here, but messages are NOT used as context
# These are your bot interaction channels
COMMAND_CHANNELS=channel_id_4,channel_id_5,channel_id_6

ENABLE_PERSISTENCE=true
PERSISTENCE_FILE=data/bot_data.json
```

**Important Notes:**
- For local development, use `COMMAND_PREFIX="!g "` (WITH quotes and space)
- Get channel IDs by enabling Developer Mode in Discord (User Settings → Advanced → Developer Mode), then right-click channel → Copy ID

### Running the Bot

**Start the bot:**

```bash
python bot.py
```

**Expected output:**

```
================================================================================
Bot is ready! Logged in as YourBot#1234
================================================================================
CONTEXT CHANNELS (notes/plans - used for AI): 3
   - 1234567890 (#project-notes)
   - 9876543210 (#planning)
   - 5555555555 (#documentation)
COMMAND CHANNELS (bot commands only): 2
   - 1111111111 (#bot-commands)
   - 2222222222 (#general)
Command prefix: !g 
Buffer size: 500
================================================================================
Fetching old messages from context channels...
Total messages fetched: 150
================================================================================
```

**Test the bot in Discord:**

```
!g commands
```

---

## 2. Run with Docker

### Using Docker

**Step 1: Build the Docker Image**

```bash
docker build -t discord-bot .
```

**Step 2: Run the Container**

```bash
docker run -d --name discord-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  discord-bot
```

**Step 3: View Logs**

```bash
docker logs -f discord-bot
```

**Step 4: Stop the Container**

```bash
docker stop discord-bot
docker rm discord-bot
```

### Using Docker Compose

**Step 1: Start the Bot**

```bash
docker-compose up -d
```

**Step 2: View Logs**

```bash
docker-compose logs -f
```

**Step 3: Stop the Bot**

```bash
docker-compose down
```

**Step 4: Restart the Bot**

```bash
docker-compose restart
```

---

## 3. Deploy to Railway

### Setup

**Step 1: Create Railway Account**

Go to [railway.app](https://railway.app) and sign up with GitHub

**Step 2: Create New Project**

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your repository

### Environment Variables

**Step 1: Go to Variables Tab**

In your Railway project, click on the "Variables" tab

**Step 2: Add Environment Variables**

Click "Raw Editor" and paste the following:

```
DISCORD_TOKEN=your_discord_token_here
GEMINI_API_KEY=your_gemini_api_key_here
COMMAND_PREFIX=!g 
GEMINI_MODEL=gemini-2.5-flash
MESSAGE_BUFFER_SIZE=500
CONTEXT_CHANNELS=channel_id_1,channel_id_2,channel_id_3
COMMAND_CHANNELS=channel_id_4,channel_id_5,channel_id_6
ENABLE_PERSISTENCE=true
PERSISTENCE_FILE=data/bot_data.json
```

**CRITICAL DIFFERENCES from Local:**

| Variable | Local (.env file) | Railway (Variables) |
|----------|-------------------|---------------------|
| COMMAND_PREFIX | `COMMAND_PREFIX="!g "` (WITH quotes) | `COMMAND_PREFIX=!g ` (NO quotes) |
| Other variables | Same syntax | Same syntax |

**Why?**
- Local: `python-dotenv` strips trailing whitespace unless quoted
- Railway: Environment variables are literal, quotes become part of the value

### Deployment

**Step 1: Deploy**

Railway will automatically deploy after you add environment variables

**Step 2: Monitor Deployment**

Click on "Deployments" tab to see build logs

**Step 3: Verify Bot is Running**

Check the logs for:

```
================================================================================
Bot is ready! Logged in as YourBot#1234
================================================================================
CONTEXT CHANNELS (notes/plans - used for AI): 3
COMMAND CHANNELS (bot commands only): 2
Command prefix: !g
================================================================================
```

**Step 4: Test in Discord**

```
!g commands
```

---

## Commands Reference

### Task Commands

```
!g task add <title> | <description>    # Add a new task
!g task list [status]                  # List tasks (filter by status)
!g task done <id>                      # Mark task as done
!g task delete <id>                    # Delete a task
```

### Note Commands

```
!g note add <title> | <content>        # Add a new note
!g note list                           # List all notes
!g note search <query>                 # Search notes
!g note delete <id>                    # Delete a note
```

### AI Commands

```
!g ask <question>                      # Ask with context from notes/plans
!g chat <prompt>                       # Chat with Gemini (no context)
!g summarize [limit]                   # Summarize recent messages
!g analyze tasks                       # Analyze your tasks
!g analyze notes                       # Analyze your notes
```

### Utility Commands

```
!g stats                               # Show bot statistics
!g buffer [limit]                      # Show buffered messages
!g save                                # Manually save data
!g monitor <channel_id>                # Add channel to monitoring
```

---

## Troubleshooting

### Bot doesn't respond to commands

**Problem:** Command prefix mismatch

**Solution:**

Check your environment configuration:

**Local (.env):**
```env
COMMAND_PREFIX="!g "
```
(WITH quotes, WITH space after !g)

**Railway (Variables):**
```
COMMAND_PREFIX=!g
```
(NO quotes, WITH space after !g)

**Verify in logs:**
```
Command prefix is: '!g '
```
Should show space, no extra quotes

### Bot can't see messages

**Problem:** Missing permissions or wrong channel IDs

**Solution:**

1. Check bot permissions in Discord:
   - Read Messages
   - Send Messages
   - Embed Links
   - Read Message History

2. Verify channel IDs:
   - Enable Developer Mode in Discord
   - Right-click channel → Copy ID
   - Check `CONTEXT_CHANNELS` and `COMMAND_CHANNELS` in `.env`

3. Check logs:
```
CONTEXT CHANNELS (notes/plans - used for AI): 3
   - 1234567890 (#your-channel-name)
```

### No messages in buffer

**Problem:** Bot not fetching old messages

**Solution:**

1. Check that channels are in `CONTEXT_CHANNELS` (not `COMMAND_CHANNELS`)
2. Verify bot has "Read Message History" permission
3. Check logs for:
```
Fetching old messages from context channels...
Total messages fetched: 150
```

### Gemini API errors

**Problem:** Invalid API key or quota exceeded

**Solution:**

1. Verify API key at [Google AI Studio](https://makersuite.google.com/)
2. Check API quota and limits
3. Ensure model name is correct: `gemini-2.5-flash`
4. Check logs for specific error messages

### Railway deployment fails

**Problem:** Build or runtime errors

**Solution:**

1. Check Railway deployment logs
2. Verify all environment variables are set correctly
3. Ensure `COMMAND_PREFIX` has NO quotes in Railway
4. Check that `requirements.txt` is up to date
5. Verify `Procfile` exists and is correct:
```
worker: python bot.py
```

---

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

