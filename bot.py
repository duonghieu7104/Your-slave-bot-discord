"""
Discord Task & Note Manager Bot with Gemini AI
"""
import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional

from config import Config
from message_buffer import MessageBuffer
from task_note_manager import TaskNoteManager, TaskStatus
from gemini_service import GeminiService
from persistence import PersistenceManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskNoteBot(commands.Bot):
    """Discord bot for task and note management with Gemini AI"""
    
    def __init__(self):
        """Initialize the bot"""
        # Validate configuration
        Config.validate()
        
        # Setup bot with intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        
        # Initialize components
        self.message_buffer = MessageBuffer(max_size=Config.MESSAGE_BUFFER_SIZE)
        self.task_manager = TaskNoteManager()
        self.gemini = GeminiService(
            api_key=Config.GEMINI_API_KEY,
            model_name=Config.GEMINI_MODEL
        )
        self.persistence = PersistenceManager(Config.PERSISTENCE_FILE) if Config.ENABLE_PERSISTENCE else None
        
        # Setup monitored channels
        for channel_id in Config.MONITORED_CHANNELS:
            self.message_buffer.add_monitored_channel(channel_id)
        
        # Load persisted data
        self._load_data()
        
        # Auto-save task
        self.auto_save_task = None
    
    def _load_data(self):
        """Load persisted data if available"""
        if not self.persistence:
            return
        
        data = self.persistence.load()
        if data:
            self.task_manager.from_dict(data.get('task_note_data', {}))
            logger.info("Loaded persisted data")
    
    def _save_data(self):
        """Save data to persistence"""
        if not self.persistence:
            return
        
        data = {
            'task_note_data': self.task_manager.to_dict()
        }
        self.persistence.save(data)
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Bot is starting up...")
        
        # Start auto-save task if persistence is enabled
        if self.persistence:
            self.auto_save_task = self.loop.create_task(self._auto_save_loop())
    
    async def _auto_save_loop(self):
        """Auto-save data every 5 minutes"""
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(300)  # 5 minutes
            self._save_data()
            logger.info("Auto-saved data")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        logger.info(f"Monitoring {len(self.message_buffer.monitored_channels)} channels")
        logger.info(f"Command prefix: {Config.COMMAND_PREFIX}")
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore bot's own messages
        if message.author == self.user:
            return

        # Debug logging
        logger.info(f"Message received from {message.author} in channel {message.channel.id}: {message.content[:50]}")

        # Store message in buffer if from monitored channel
        if message.channel.id in self.message_buffer.monitored_channels:
            self.message_buffer.add_message(message)
            logger.info(f"Message stored in buffer (channel is monitored)")
        else:
            logger.warning(f"Channel {message.channel.id} is NOT monitored. Monitored: {self.message_buffer.monitored_channels}")

        # Process commands
        logger.info(f"Processing commands for message: {message.content}")
        logger.info(f"Command prefix is: {repr(self.command_prefix)}")

        # Get context to see if command is recognized
        ctx = await self.get_context(message)
        logger.info(f"Context valid: {ctx.valid}, Command: {ctx.command}, Invoked with: {ctx.invoked_with}")

        await self.process_commands(message)
        logger.info(f"Finished processing commands")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            logger.warning(f"Command not found: {ctx.message.content}")
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            logger.error(f"Missing argument: {error.param.name}")
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        else:
            logger.error(f"Command error: {error}", exc_info=True)
            await ctx.send(f"❌ An error occurred: {str(error)}")


# Create bot instance
bot = TaskNoteBot()


# ===== GENERAL COMMANDS =====

@bot.command(name='commands', aliases=['h'])
async def help_command(ctx):
    """Show help information"""
    logger.info(f"Commands command called by {ctx.author}")
    embed = discord.Embed(
        title="🤖 Task & Note Manager Bot",
        description="AI-powered bot for managing tasks, notes, and conversations",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📝 Task Commands",
        value=(
            "`!g task add <title> | <description>` - Add a task\n"
            "`!g task list [status]` - List tasks\n"
            "`!g task done <id>` - Mark task as done\n"
            "`!g task delete <id>` - Delete a task"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📓 Note Commands",
        value=(
            "`!g note add <title> | <content>` - Add a note\n"
            "`!g note list` - List all notes\n"
            "`!g note search <query>` - Search notes\n"
            "`!g note delete <id>` - Delete a note"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🤖 AI Commands",
        value=(
            "`!g ask <question>` - Ask Gemini anything\n"
            "`!g summarize [limit]` - Summarize recent messages\n"
            "`!g analyze tasks` - Analyze your tasks\n"
            "`!g analyze notes` - Analyze your notes"
        ),
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Utility Commands",
        value=(
            "`!g stats` - Show bot statistics\n"
            "`!g save` - Manually save data\n"
            "`!g monitor <channel_id>` - Add channel to monitoring"
        ),
        inline=False
    )
    
    await ctx.send(embed=embed)


@bot.command(name='stats')
async def stats_command(ctx):
    """Show bot statistics"""
    logger.info(f"Stats command called by {ctx.author}")
    buffer_stats = bot.message_buffer.get_stats()
    task_note_stats = bot.task_manager.get_stats()
    
    embed = discord.Embed(
        title="📊 Bot Statistics",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="💬 Message Buffer",
        value=(
            f"Messages stored: {buffer_stats['total_messages']}/{buffer_stats['max_size']}\n"
            f"Monitored channels: {buffer_stats['monitored_channels']}"
        ),
        inline=False
    )
    
    embed.add_field(
        name="✅ Tasks",
        value=(
            f"Total: {task_note_stats['tasks']['total']}\n"
            f"Todo: {task_note_stats['tasks']['todo']}\n"
            f"In Progress: {task_note_stats['tasks']['in_progress']}\n"
            f"Done: {task_note_stats['tasks']['done']}"
        ),
        inline=True
    )
    
    embed.add_field(
        name="📝 Notes",
        value=f"Total: {task_note_stats['notes']['total']}",
        inline=True
    )
    
    await ctx.send(embed=embed)


@bot.command(name='save')
async def save_command(ctx):
    """Manually save data"""
    if not bot.persistence:
        await ctx.send("❌ Persistence is not enabled")
        return
    
    bot._save_data()
    await ctx.send("✅ Data saved successfully")


@bot.command(name='monitor')
@commands.has_permissions(administrator=True)
async def monitor_command(ctx, channel_id: int):
    """Add a channel to monitoring (Admin only)"""
    bot.message_buffer.add_monitored_channel(channel_id)
    await ctx.send(f"✅ Now monitoring channel <#{channel_id}>")


# ===== TASK COMMANDS =====

@bot.group(name='task', invoke_without_command=True)
async def task_group(ctx):
    """Task management commands"""
    await ctx.send("Use `!g task add`, `!g task list`, `!g task done`, or `!g task delete`")


@task_group.command(name='add')
async def task_add(ctx, *, content: str):
    """Add a new task (format: title | description)"""
    parts = content.split('|', 1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""
    
    task = bot.task_manager.add_task(
        title=title,
        description=description,
        author_id=ctx.author.id
    )
    
    await ctx.send(f"✅ Task #{task['id']} created: **{task['title']}**")


@task_group.command(name='list')
async def task_list(ctx, status: Optional[str] = None):
    """List tasks (optionally filter by status)"""
    tasks = bot.task_manager.get_tasks(status=status)
    
    if not tasks:
        await ctx.send("No tasks found")
        return
    
    embed = discord.Embed(
        title=f"📋 Tasks" + (f" ({status})" if status else ""),
        color=discord.Color.blue()
    )
    
    for task in tasks[:10]:  # Limit to 10 tasks
        status_emoji = {
            'todo': '⏳',
            'in_progress': '🔄',
            'done': '✅',
            'cancelled': '❌'
        }.get(task['status'], '❓')
        
        embed.add_field(
            name=f"{status_emoji} #{task['id']}: {task['title']}",
            value=f"{task['description'][:100]}\nPriority: {task['priority']}",
            inline=False
        )
    
    if len(tasks) > 10:
        embed.set_footer(text=f"Showing 10 of {len(tasks)} tasks")
    
    await ctx.send(embed=embed)


@task_group.command(name='done')
async def task_done(ctx, task_id: int):
    """Mark a task as done"""
    success = bot.task_manager.update_task_status(task_id, TaskStatus.DONE.value)
    
    if success:
        await ctx.send(f"✅ Task #{task_id} marked as done!")
    else:
        await ctx.send(f"❌ Task #{task_id} not found")


@task_group.command(name='delete')
async def task_delete(ctx, task_id: int):
    """Delete a task"""
    success = bot.task_manager.delete_task(task_id)
    
    if success:
        await ctx.send(f"✅ Task #{task_id} deleted")
    else:
        await ctx.send(f"❌ Task #{task_id} not found")


# ===== NOTE COMMANDS =====

@bot.group(name='note', invoke_without_command=True)
async def note_group(ctx):
    """Note management commands"""
    await ctx.send("Use `!g note add`, `!g note list`, `!g note search`, or `!g note delete`")


@note_group.command(name='add')
async def note_add(ctx, *, content: str):
    """Add a new note (format: title | content)"""
    parts = content.split('|', 1)
    title = parts[0].strip()
    note_content = parts[1].strip() if len(parts) > 1 else ""

    note = bot.task_manager.add_note(
        title=title,
        content=note_content,
        author_id=ctx.author.id
    )

    await ctx.send(f"✅ Note #{note['id']} created: **{note['title']}**")


@note_group.command(name='list')
async def note_list(ctx):
    """List all notes"""
    notes = bot.task_manager.get_notes()

    if not notes:
        await ctx.send("No notes found")
        return

    embed = discord.Embed(
        title="📓 Notes",
        color=discord.Color.purple()
    )

    for note in notes[:10]:  # Limit to 10 notes
        embed.add_field(
            name=f"#{note['id']}: {note['title']}",
            value=note['content'][:100] + ("..." if len(note['content']) > 100 else ""),
            inline=False
        )

    if len(notes) > 10:
        embed.set_footer(text=f"Showing 10 of {len(notes)} notes")

    await ctx.send(embed=embed)


@note_group.command(name='search')
async def note_search(ctx, *, query: str):
    """Search notes by content"""
    notes = bot.task_manager.search_notes(query)

    if not notes:
        await ctx.send(f"No notes found matching '{query}'")
        return

    embed = discord.Embed(
        title=f"🔍 Search Results: '{query}'",
        color=discord.Color.purple()
    )

    for note in notes[:5]:
        embed.add_field(
            name=f"#{note['id']}: {note['title']}",
            value=note['content'][:100] + ("..." if len(note['content']) > 100 else ""),
            inline=False
        )

    await ctx.send(embed=embed)


@note_group.command(name='delete')
async def note_delete(ctx, note_id: int):
    """Delete a note"""
    success = bot.task_manager.delete_note(note_id)

    if success:
        await ctx.send(f"✅ Note #{note_id} deleted")
    else:
        await ctx.send(f"❌ Note #{note_id} not found")


# ===== AI COMMANDS =====

@bot.command(name='ask')
async def ask_command(ctx, *, question: str):
    """Ask Gemini AI a question"""
    async with ctx.typing():
        # Get recent messages for context
        recent_messages = bot.message_buffer.get_recent_messages(limit=50)
        context = bot.message_buffer.format_messages_for_context(recent_messages)

        # Generate response
        response = bot.gemini.generate_response(question, context)

        # Split response if too long
        if len(response) > 2000:
            chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(response)


@bot.command(name='summarize')
async def summarize_command(ctx, limit: int = 50):
    """Summarize recent messages"""
    async with ctx.typing():
        messages = bot.message_buffer.get_recent_messages(limit=limit)

        if not messages:
            await ctx.send("No messages to summarize")
            return

        summary = bot.gemini.summarize_messages(messages)
        await ctx.send(f"📝 **Summary of last {len(messages)} messages:**\n\n{summary}")


@bot.command(name='analyze')
async def analyze_command(ctx, target: str):
    """Analyze tasks or notes"""
    async with ctx.typing():
        if target.lower() == 'tasks':
            tasks = bot.task_manager.get_tasks()
            response = bot.gemini.analyze_tasks(tasks, "Provide an overview and insights about these tasks")
            await ctx.send(f"📊 **Task Analysis:**\n\n{response}")

        elif target.lower() == 'notes':
            notes = bot.task_manager.get_notes()
            response = bot.gemini.analyze_notes(notes, "Provide an overview and insights about these notes")
            await ctx.send(f"📊 **Note Analysis:**\n\n{response}")

        else:
            await ctx.send("❌ Please specify 'tasks' or 'notes'")


# ===== RUN BOT =====

def main():
    """Main entry point"""
    try:
        logger.info("Starting bot...")
        bot.run(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        # Save data before exit
        if bot.persistence:
            bot._save_data()
            logger.info("Data saved on exit")


if __name__ == "__main__":
    main()

