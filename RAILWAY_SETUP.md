# Railway Deployment Quick Guide

## Environment Variables for Railway

**⚠️ IMPORTANT:** Railway syntax is different from local .env file!

Copy this to Railway Variables (Raw Editor):

```
DISCORD_TOKEN=your_discord_token_here
GEMINI_API_KEY=your_gemini_api_key_here
COMMAND_PREFIX=!g 
GEMINI_MODEL=gemini-2.5-flash
MESSAGE_BUFFER_SIZE=500
MONITORED_CHANNELS=channel_id_1,channel_id_2,channel_id_3
ENABLE_PERSISTENCE=true
PERSISTENCE_FILE=data/bot_data.json
```

## Key Differences from Local

| Setting | Local (.env) | Railway |
|---------|--------------|---------|
| COMMAND_PREFIX | `"!g "` (with quotes) | `!g ` (no quotes) |

**Why?** Railway passes environment variables directly without processing quotes.

## Verification

After deployment, check Railway logs:

✅ **Correct:**
```
Command prefix is: '!g '
Context valid: True
```

❌ **Wrong:**
```
Command prefix is: '"!g "'
Context valid: False
```

If you see the wrong output, remove quotes from COMMAND_PREFIX in Railway Variables.

## Step-by-Step Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin your-repo-url
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to https://railway.app
   - Login with GitHub
   - New Project → Deploy from GitHub repo
   - Select your repository

3. **Add Variables**
   - Click "Variables" tab
   - Click "Raw Editor"
   - Paste the variables above (with your actual values)
   - **Don't use quotes for COMMAND_PREFIX**

4. **Verify**
   - Check "Deployments" tab
   - Click latest deployment → View logs
   - Look for: `Bot is ready! Logged in as YourBot#1234`
   - Test in Discord: `!g commands`

## Common Issues

**Bot doesn't respond:**
- Check logs for `Command prefix is: '"!g "'` (wrong - has extra quotes)
- Fix: Remove quotes from COMMAND_PREFIX in Railway Variables
- Should be: `COMMAND_PREFIX=!g ` (with space, no quotes)

**Bot crashes on startup:**
- Check all environment variables are set
- Verify DISCORD_TOKEN and GEMINI_API_KEY are correct
- Check MONITORED_CHANNELS has valid channel IDs

**Data not persisting:**
- Railway's filesystem is ephemeral
- Data will reset on each deployment
- For permanent storage, consider adding a database (future enhancement)

