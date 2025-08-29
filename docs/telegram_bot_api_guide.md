# Telegram Bot API Comprehensive Guide

*A complete reference for developing Telegram bots, specifically tailored for the KICKAI football team management system.*

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Getting Started with BotFather](#getting-started-with-botfather)
3. [Authentication and Security](#authentication-and-security)
4. [Message Handling](#message-handling)
5. [Chat Management](#chat-management)
6. [Advanced Features](#advanced-features)
7. [Integration Patterns](#integration-patterns)
8. [Security and Best Practices](#security-and-best-practices)
9. [Production Deployment](#production-deployment)
10. [KICKAI-Specific Implementation](#kickai-specific-implementation)

## Core Concepts

### What is the Telegram Bot API?

The Telegram Bot API is an HTTP-based interface that allows developers to create programs that use Telegram messages for interaction. It's a REST API that serves as an intermediary between your bot code and Telegram's servers.

**Key characteristics:**
- HTTP-based REST API
- All requests must use HTTPS
- Handles MTProto encryption automatically
- Free for both users and developers
- Supports over 10 million active bots

### API Endpoint Structure

All API calls follow this pattern:
```
https://api.telegram.org/bot<TOKEN>/METHOD_NAME
```

Example:
```
https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendMessage
```

### Bot Capabilities

**What bots can do:**
- Send and receive messages
- Manage groups and channels
- Process payments
- Host Mini Apps (JavaScript applications)
- Handle inline queries
- Manage files up to 20MB
- Create custom keyboards and interfaces

**What bots cannot do:**
- Initiate conversations with users
- See 'last seen' or online status
- Access messages in groups without proper permissions (Privacy Mode)
- Send more than 30 messages per second (rate limited)

## Getting Started with BotFather

### Creating a New Bot

1. **Contact @BotFather**
   - Open Telegram and search for `@BotFather`
   - Send `/start` to begin

2. **Create Bot**
   - Send `/newbot` command
   - Choose a name for your bot (e.g., "KICKAI Team Manager")
   - Choose a username ending in "bot" (e.g., "kickai_team_bot")

3. **Receive Token**
   - BotFather will provide a unique token: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
   - **CRITICAL**: Store this token securely - it's your bot's unique identifier

### Essential BotFather Commands

```bash
/mybots          # List all your bots
/token           # Regenerate bot token
/setname         # Change bot name
/setdescription  # Set bot description
/setuserpic      # Set bot profile picture
/setcommands     # Set bot command list
/setprivacy      # Configure Privacy Mode
/deletebot       # Delete a bot
```

### Setting Bot Commands

Configure your bot's command menu:
```bash
/setcommands

# Then provide command list:
start - Start the bot
help - Get help information
register - Register as a player
squad - View squad selection
availability - Set availability status
admin - Admin panel (for authorized users)
```

## Authentication and Security

### Token Management

**Environment Variables** (Recommended):
```python
import os
from typing import Optional

def get_bot_token() -> Optional[str]:
    """Retrieve bot token from environment variables."""
    return os.getenv('TELEGRAM_BOT_TOKEN')

# Usage
TOKEN = get_bot_token()
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
```

**Configuration File** (Alternative):
```python
# config.py
import json
from pathlib import Path

def load_config() -> dict:
    """Load configuration from secure JSON file."""
    config_path = Path("config/bot_credentials.json")
    if not config_path.exists():
        raise FileNotFoundError("Bot configuration file not found")
    
    with open(config_path) as f:
        return json.load(f)

config = load_config()
TOKEN = config['telegram_bot_token']
```

### Security Best Practices

1. **Never hardcode tokens** in source code
2. **Use HTTPS** for all API calls (enforced by Telegram)
3. **Implement input validation** for all user inputs
4. **Set up webhook secrets** for production deployments
5. **Use IP whitelisting** when possible (Telegram IPs: 149.154.167.197-233)

## Message Handling

### Webhook vs Polling

#### Polling (getUpdates)

**Advantages:**
- Simple to implement
- Good for development and testing
- No SSL certificate required
- Works behind NAT/firewalls

**Implementation:**
```python
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

async def start(update: Update, context) -> None:
    """Handle /start command."""
    await update.message.reply_text('Welcome to KICKAI Team Manager!')

async def handle_message(update: Update, context) -> None:
    """Handle regular messages."""
    user_message = update.message.text
    response = process_team_message(user_message)
    await update.message.reply_text(response)

def main():
    """Start the bot with polling."""
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
```

#### Webhooks

**Advantages:**
- Real-time updates
- More efficient for high-traffic bots
- Reduces server load
- Better for production environments

**Requirements:**
- Valid SSL certificate
- Public IP address or domain
- Supported ports: 443, 80, 88, 8443

**Implementation:**
```python
from telegram.ext import Application
from flask import Flask, request
import json

# Flask app for webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates."""
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return 'OK'

async def setup_webhook():
    """Set up webhook with Telegram."""
    webhook_url = "https://your-domain.com/webhook"
    await bot.set_webhook(
        url=webhook_url,
        secret_token="your-secret-token"  # Optional but recommended
    )

# Initialize application
application = Application.builder().token(TOKEN).build()
```

### Message Types and Handling

#### Text Messages
```python
async def handle_text(update: Update, context) -> None:
    """Handle text messages."""
    text = update.message.text
    telegram_id = update.effective_user.id
    
    # Process based on content
    if text.startswith('/'):
        # Command handling
        await handle_command(update, context)
    else:
        # Natural language processing
        response = process_natural_language(text, telegram_id)
        await update.message.reply_text(response)
```

#### File Handling
```python
async def handle_document(update: Update, context) -> None:
    """Handle document uploads."""
    document = update.message.document
    
    # Get file info
    file = await context.bot.get_file(document.file_id)
    
    # Download file (max 20MB)
    await file.download_to_drive(f'uploads/{document.file_name}')
    
    await update.message.reply_text(f'Document {document.file_name} received!')

# Add handler
application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
```

#### Photo Handling
```python
async def handle_photo(update: Update, context) -> None:
    """Handle photo uploads."""
    photo = update.message.photo[-1]  # Get highest resolution
    
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive(f'photos/{photo.file_id}.jpg')
    
    await update.message.reply_text('Photo received and saved!')

application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
```

### Rate Limits and Error Handling

#### Rate Limits
- **Individual chats**: 1 message per second (bursts allowed)
- **Groups**: 20 messages per minute maximum
- **Bulk notifications**: 30 messages per second
- **Paid broadcasting**: Up to 1000 messages per second (costs 0.1 Stars per message over 30/second)

#### Error Handling Implementation
```python
from telegram.error import TelegramError, RetryAfter, TimedOut
import asyncio
import logging

async def send_message_with_retry(bot, chat_id: int, text: str, max_retries: int = 3):
    """Send message with automatic retry on rate limits."""
    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id=chat_id, text=text)
        except RetryAfter as e:
            # Rate limited - wait and retry
            wait_time = e.retry_after
            logging.warning(f"Rate limited. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except TimedOut:
            # Network timeout - retry with backoff
            wait_time = 2 ** attempt
            logging.warning(f"Timeout. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except TelegramError as e:
            logging.error(f"Telegram error: {e}")
            break
    
    raise Exception(f"Failed to send message after {max_retries} attempts")
```

## Chat Management

### Chat Types

Telegram supports four chat types:
- **Private**: Direct messages with users
- **Group**: Basic groups (up to 200 members)
- **Supergroup**: Large groups (up to 200,000 members)
- **Channel**: Broadcast channels

```python
from telegram import ChatType

async def handle_chat_type(update: Update, context) -> None:
    """Handle different chat types differently."""
    chat_type = update.effective_chat.type
    
    if chat_type == ChatType.PRIVATE:
        # Handle private chat
        await handle_private_chat(update, context)
    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        # Handle group chats
        await handle_group_chat(update, context)
    elif chat_type == ChatType.CHANNEL:
        # Handle channel posts
        await handle_channel_post(update, context)
```

### Group Administration

#### Bot Permissions in Groups

```python
from telegram import ChatMember

async def check_bot_permissions(update: Update, context) -> None:
    """Check bot's permissions in the current chat."""
    chat_id = update.effective_chat.id
    bot_id = context.bot.id
    
    try:
        bot_member = await context.bot.get_chat_member(chat_id, bot_id)
        
        if bot_member.status == ChatMember.ADMINISTRATOR:
            # Bot is admin - can see all messages
            permissions = bot_member
            print(f"Admin rights: {permissions}")
        else:
            # Bot is regular member - Privacy Mode applies
            print("Bot is regular member")
    except Exception as e:
        print(f"Error checking permissions: {e}")
```

#### Managing Group Members

```python
async def kick_user(update: Update, context) -> None:
    """Kick a user from the group (admin only)."""
    # Check if user is admin
    if not await is_user_admin(update, context):
        await update.message.reply_text("❌ Admin privileges required!")
        return
    
    # Get user to kick
    if context.args and context.args[0].isdigit():
        telegram_id = int(context.args[0])
        try:
            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=telegram_id
            )
            await update.message.reply_text(f"✅ User {telegram_id} has been removed.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

async def is_user_admin(update: Update, context) -> bool:
    """Check if user is admin in the current chat."""
    telegram_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        member = await context.bot.get_chat_member(chat_id, telegram_id)
        return member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except:
        return False
```

### Privacy Mode and Group Behavior

**Privacy Mode ON (Default):**
- Bot only sees messages that mention it (@bot_username)
- Bot only sees commands sent to it
- Bot sees all service messages (user joins, leaves, etc.)

**Privacy Mode OFF:**
- Bot sees ALL messages in the group
- Required for advanced group management features

Configure via @BotFather:
```
/mybots → Select bot → Bot Settings → Group Privacy → Turn off
```

## Advanced Features

### Inline Keyboards

Create interactive buttons that don't send messages:

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def show_squad_selection(update: Update, context) -> None:
    """Show squad selection with inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("⚽ Available", callback_data='squad_available'),
            InlineKeyboardButton("❌ Unavailable", callback_data='squad_unavailable')
        ],
        [
            InlineKeyboardButton("❓ Maybe", callback_data='squad_maybe'),
            InlineKeyboardButton("🏥 Injured", callback_data='squad_injured')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "⚽ **Squad Selection for Saturday's Match**\n\nPlease select your availability:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_squad_callback(update: Update, context) -> None:
    """Handle squad selection callbacks."""
    query = update.callback_query
    await query.answer()  # Important: acknowledge the callback
    
    data = query.data
    telegram_id = update.effective_user.id
    username = update.effective_user.username
    
    # Process selection
    status_map = {
        'squad_available': '✅ Available',
        'squad_unavailable': '❌ Unavailable', 
        'squad_maybe': '❓ Maybe',
        'squad_injured': '🏥 Injured'
    }
    
    status = status_map.get(data, 'Unknown')
    
    # Update database
    update_player_availability(telegram_id, data.replace('squad_', ''))
    
    # Edit message to show selection
    await query.edit_message_text(
        f"✅ **Squad Selection Updated**\n\n@{username}: {status}"
    )

# Add callback handler
application.add_handler(CallbackQueryHandler(handle_squad_callback, pattern='^squad_'))
```

### Reply Keyboards

Create custom keyboard with predefined options:

```python
from telegram import ReplyKeyboardMarkup, KeyboardButton

async def show_main_menu(update: Update, context) -> None:
    """Show main menu with reply keyboard."""
    keyboard = [
        [KeyboardButton("⚽ Squad Selection"), KeyboardButton("📅 Next Match")],
        [KeyboardButton("👥 Team Stats"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("📍 Send Location", request_location=True)],
        [KeyboardButton("📞 Share Contact", request_contact=True)]
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Choose an option..."
    )
    
    await update.message.reply_text(
        "🏆 **KICKAI Team Manager**\n\nSelect an option:",
        reply_markup=reply_markup
    )

# Handle keyboard responses
async def handle_keyboard_response(update: Update, context) -> None:
    """Handle reply keyboard responses."""
    text = update.message.text
    
    if text == "⚽ Squad Selection":
        await show_squad_selection(update, context)
    elif text == "📅 Next Match":
        await show_next_match(update, context)
    elif text == "👥 Team Stats":
        await show_team_stats(update, context)
    elif text == "⚙️ Settings":
        await show_settings(update, context)
```

### File Uploads and Downloads

#### Uploading Files

```python
async def send_match_report(update: Update, context) -> None:
    """Send match report as PDF."""
    # Generate report
    report_path = generate_match_report_pdf()
    
    # Send document
    with open(report_path, 'rb') as document:
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=document,
            filename="match_report.pdf",
            caption="📊 Match Report - Liverpool vs Arsenal"
        )

async def send_team_photo(update: Update, context) -> None:
    """Send team photo."""
    with open('team_photos/latest.jpg', 'rb') as photo:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption="📸 Team photo from today's training!"
        )
```

#### Downloading Files

```python
async def save_uploaded_document(update: Update, context) -> None:
    """Save uploaded documents to server."""
    if not update.message.document:
        return
    
    document = update.message.document
    
    # Check file size (20MB limit)
    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text("❌ File too large! Maximum size is 20MB.")
        return
    
    # Check file type
    allowed_types = ['.pdf', '.doc', '.docx', '.jpg', '.png']
    if not any(document.file_name.lower().endswith(ext) for ext in allowed_types):
        await update.message.reply_text("❌ File type not allowed!")
        return
    
    try:
        # Get file
        file = await context.bot.get_file(document.file_id)
        
        # Create safe filename
        safe_filename = f"{uuid.uuid4()}_{document.file_name}"
        file_path = f"uploads/{safe_filename}"
        
        # Download
        await file.download_to_drive(file_path)
        
        await update.message.reply_text(f"✅ File saved as {document.file_name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error saving file: {e}")
```

### Commands and Message Parsing

#### Command Parsing

```python
from telegram.ext import CommandHandler

async def register_player(update: Update, context) -> None:
    """Register a new player."""
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Usage: /register <name> <position>\n"
            "Example: /register 'John Doe' midfielder"
        )
        return
    
    player_name = args[0]
    position = args[1].lower()
    telegram_id = update.effective_user.id
    
    # Validate position
    valid_positions = ['goalkeeper', 'defender', 'midfielder', 'forward']
    if position not in valid_positions:
        await update.message.reply_text(
            f"❌ Invalid position! Valid positions: {', '.join(valid_positions)}"
        )
        return
    
    # Register player
    success = register_player_in_db(telegram_id, player_name, position)
    
    if success:
        await update.message.reply_text(
            f"✅ Welcome {player_name}!\n"
            f"Position: {position.title()}\n"
            f"You can now participate in squad selections."
        )
    else:
        await update.message.reply_text("❌ Registration failed. Please try again.")

# Add command handler
application.add_handler(CommandHandler("register", register_player))
```

#### Natural Language Processing Integration

```python
async def process_natural_language(update: Update, context) -> None:
    """Process natural language messages."""
    text = update.message.text.lower()
    telegram_id = update.effective_user.id
    
    # Simple keyword matching (replace with AI/NLP service)
    if any(word in text for word in ['available', 'can play', 'ready']):
        await handle_availability_yes(update, context)
    elif any(word in text for word in ['unavailable', 'cannot play', 'busy']):
        await handle_availability_no(update, context)
    elif any(word in text for word in ['next match', 'when', 'fixture']):
        await show_next_match(update, context)
    elif any(word in text for word in ['help', 'commands', 'what can']):
        await show_help(update, context)
    else:
        # Forward to AI system (KICKAI CrewAI integration)
        response = await process_with_ai_system(text, telegram_id)
        await update.message.reply_text(response)
```

## Integration Patterns

### Python-telegram-bot Library (Recommended)

#### Modern Async Implementation (v20+)

```python
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application, 
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler,
    CallbackQueryHandler,
    filters
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class KICKAIBot:
    """Main bot class for KICKAI team management."""
    
    def __init__(self, token: str):
        self.token = token
        self.application = ApplicationBuilder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up all bot handlers."""
        # Commands
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("register", self.register))
        self.application.add_handler(CommandHandler("squad", self.squad_selection))
        
        # Messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Callbacks
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Files
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start(self, update: Update, context) -> None:
        """Handle /start command."""
        user = update.effective_user
        await update.message.reply_html(
            f"⚽ Welcome {user.mention_html()}!\n\n"
            f"🏆 <b>KICKAI Team Manager</b>\n"
            f"Your AI-powered football team assistant.\n\n"
            f"Type /help to see available commands."
        )
    
    async def handle_message(self, update: Update, context) -> None:
        """Handle regular text messages."""
        # Integration with KICKAI AI system
        response = await self.process_with_kickai(update, context)
        await update.message.reply_text(response)
    
    async def process_with_kickai(self, update: Update, context) -> str:
        """Process message with KICKAI AI system."""
        # This would integrate with your CrewAI system
        message_text = update.message.text
        user_id = update.effective_user.id
        
        # Call KICKAI agent system
        # response = await kickai_agent_system.process_message(message_text, user_id)
        
        return f"🤖 AI Response: Processed '{message_text}'"
    
    async def error_handler(self, update: Update, context) -> None:
        """Handle errors."""
        logger.error(f"Exception while handling update: {context.error}")
    
    def run(self):
        """Run the bot."""
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# Usage
if __name__ == '__main__':
    bot = KICKAIBot(TOKEN)
    bot.run()
```

### Webhook Implementation with Flask/FastAPI

#### Flask Integration

```python
from flask import Flask, request, jsonify
from telegram import Update
import asyncio
import threading

app = Flask(__name__)

class WebhookBot:
    """Webhook-based bot implementation."""
    
    def __init__(self, token: str, webhook_url: str):
        self.token = token
        self.webhook_url = webhook_url
        self.application = ApplicationBuilder().token(token).build()
        self._setup_handlers()
    
    async def setup_webhook(self):
        """Set webhook URL."""
        await self.application.bot.set_webhook(
            url=self.webhook_url,
            secret_token="your-secret-token"
        )
    
    def _setup_handlers(self):
        """Setup handlers."""
        self.application.add_handler(CommandHandler("start", self.start))
        # ... other handlers
    
    async def process_update(self, update_data: dict):
        """Process incoming update."""
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update)

# Global bot instance
webhook_bot = WebhookBot(TOKEN, "https://your-domain.com/webhook")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook updates."""
    try:
        update_data = request.get_json()
        
        # Verify secret token if set
        secret_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
        if secret_token != "your-secret-token":
            return "Unauthorized", 401
        
        # Process update in background
        asyncio.run(webhook_bot.process_update(update_data))
        
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook URL."""
    asyncio.run(webhook_bot.setup_webhook())
    return jsonify({"status": "webhook set"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
```

#### FastAPI Integration (Modern Alternative)

```python
from fastapi import FastAPI, Request, HTTPException, Header
from telegram import Update
import asyncio

app = FastAPI(title="KICKAI Telegram Bot")

class FastAPIBot:
    """FastAPI-based webhook bot."""
    
    def __init__(self, token: str):
        self.token = token
        self.application = ApplicationBuilder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup bot handlers."""
        # Add handlers here
        pass

bot = FastAPIBot(TOKEN)

@app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    """Handle webhook updates."""
    # Verify secret token
    if x_telegram_bot_api_secret_token != "your-secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Process update
    update_data = await request.json()
    update = Update.de_json(update_data, bot.application.bot)
    await bot.application.process_update(update)
    
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "bot": "running"}
```

### Error Handling and Retry Strategies

```python
import asyncio
import logging
from typing import Optional
from telegram.error import TelegramError, RetryAfter, TimedOut, BadRequest

class RobustMessageSender:
    """Robust message sender with retry logic."""
    
    def __init__(self, bot, max_retries: int = 3):
        self.bot = bot
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
    
    async def send_message_with_retry(
        self, 
        chat_id: int, 
        text: str, 
        **kwargs
    ) -> Optional[int]:
        """Send message with automatic retry on failures."""
        
        for attempt in range(self.max_retries):
            try:
                message = await self.bot.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    **kwargs
                )
                return message.message_id
                
            except RetryAfter as e:
                # Rate limited - wait and retry
                wait_time = e.retry_after + 1  # Add buffer
                self.logger.warning(f"Rate limited. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except TimedOut:
                # Network timeout - exponential backoff
                wait_time = 2 ** attempt
                self.logger.warning(f"Timeout. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except BadRequest as e:
                # Bad request - don't retry
                self.logger.error(f"Bad request: {e}")
                break
                
            except TelegramError as e:
                # Other Telegram errors
                if "chat not found" in str(e).lower():
                    self.logger.error("Chat not found - user may have blocked bot")
                    break
                else:
                    self.logger.error(f"Telegram error: {e}")
                    await asyncio.sleep(2 ** attempt)
        
        self.logger.error(f"Failed to send message after {self.max_retries} attempts")
        return None

# Usage
sender = RobustMessageSender(context.bot)
message_id = await sender.send_message_with_retry(
    chat_id=telegram_id,
    text="Your message here"
)
```

## Security and Best Practices

### Token Security

#### Environment Variables

```bash
# .env file
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
WEBHOOK_SECRET_TOKEN=your-webhook-secret
DATABASE_URL=postgresql://user:pass@host:5432/kickai
ADMIN_USER_IDS=123456789,987654321
```

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management."""
    
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    WEBHOOK_SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL')
    ADMIN_USER_IDS = [int(id) for id in os.getenv('ADMIN_USER_IDS', '').split(',') if id]
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        # Add other validations

# Usage
Config.validate()
```

### Input Validation and Sanitization

```python
import re
from typing import Optional
from html import escape

class InputValidator:
    """Input validation and sanitization."""
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 4096) -> str:
        """Sanitize text input."""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        # Escape HTML
        return escape(text)
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate Telegram username format."""
        if not username:
            return False
        pattern = r'^[a-zA-Z0-9_]{5,32}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_command_args(args: list, expected_count: int) -> bool:
        """Validate command arguments."""
        return len(args) == expected_count
    
    @staticmethod
    def extract_telegram_id(text: str) -> Optional[int]:
        """Extract Telegram ID from text safely."""
        try:
            # Extract numbers from text
            numbers = re.findall(r'\d+', text)
            if numbers:
                telegram_id = int(numbers[0])
                # Validate Telegram user ID range
                if 1 <= telegram_id <= 2**63 - 1:
                    return telegram_id
        except ValueError:
            pass
        return None

# Usage in handlers
async def register_player(update: Update, context) -> None:
    """Register player with input validation."""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ Invalid arguments")
        return
    
    # Sanitize inputs
    name = InputValidator.sanitize_text(context.args[0])
    position = InputValidator.sanitize_text(context.args[1].lower())
    
    # Validate
    if not name or len(name) < 2:
        await update.message.reply_text("❌ Name must be at least 2 characters")
        return
    
    # Continue processing...
```

### User Authorization

```python
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

def require_admin(func):
    """Decorator to require admin privileges."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = update.effective_user.id
        
        # Check if user is admin
        if telegram_id not in Config.ADMIN_USER_IDS:
            await update.message.reply_text("❌ Admin privileges required!")
            return
        
        return await func(update, context)
    return wrapper

def require_registration(func):
    """Decorator to require user registration."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_id = update.effective_user.id
        
        # Check if user is registered
        if not is_user_registered(telegram_id):
            await update.message.reply_text(
                "❌ Please register first using /register <name> <position>"
            )
            return
        
        return await func(update, context)
    return wrapper

# Usage
@require_admin
async def admin_panel(update: Update, context) -> None:
    """Admin panel (admin only)."""
    await update.message.reply_text("🔧 Admin Panel\n...")

@require_registration  
async def set_availability(update: Update, context) -> None:
    """Set availability (registered users only)."""
    # Handle availability setting
    pass
```

### Rate Limiting Implementation

```python
import asyncio
from collections import defaultdict, deque
from time import time
from typing import Dict, Deque

class RateLimiter:
    """Rate limiter for bot operations."""
    
    def __init__(self):
        # Track requests per user per minute
        self.user_requests: Dict[int, Deque[float]] = defaultdict(deque)
        # Track global requests per second
        self.global_requests: Deque[float] = deque()
    
    def check_user_rate_limit(self, telegram_id: int, limit: int = 20) -> bool:
        """Check if user is within rate limit (20 requests/minute)."""
        now = time()
        user_queue = self.user_requests[telegram_id]
        
        # Remove old requests (older than 1 minute)
        while user_queue and user_queue[0] < now - 60:
            user_queue.popleft()
        
        # Check limit
        if len(user_queue) >= limit:
            return False
        
        # Add current request
        user_queue.append(now)
        return True
    
    def check_global_rate_limit(self, limit: int = 30) -> bool:
        """Check global rate limit (30 requests/second)."""
        now = time()
        
        # Remove old requests (older than 1 second)
        while self.global_requests and self.global_requests[0] < now - 1:
            self.global_requests.popleft()
        
        # Check limit
        if len(self.global_requests) >= limit:
            return False
        
        # Add current request
        self.global_requests.append(now)
        return True

# Global rate limiter
rate_limiter = RateLimiter()

def rate_limited(user_limit: int = 20, global_limit: int = 30):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            telegram_id = update.effective_user.id
            
            # Check user rate limit
            if not rate_limiter.check_user_rate_limit(telegram_id, user_limit):
                await update.message.reply_text(
                    "⏰ Too many requests! Please wait a minute."
                )
                return
            
            # Check global rate limit
            if not rate_limiter.check_global_rate_limit(global_limit):
                await update.message.reply_text(
                    "🚦 System busy! Please try again in a moment."
                )
                return
            
            return await func(update, context)
        return wrapper
    return decorator

# Usage
@rate_limited(user_limit=10)  # 10 requests per minute per user
async def search_players(update: Update, context) -> None:
    """Search players (rate limited)."""
    # Handle search
    pass
```

## Production Deployment

### Railway Deployment (Recommended for KICKAI)

#### railway.json Configuration

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false
  }
}
```

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')"

# Run application
CMD ["python", "run_bot_production.py"]
```

#### Production Bot Script

```python
# run_bot_production.py
import os
import logging
import asyncio
from kickai_bot import KICKAIBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionBot(KICKAIBot):
    """Production-ready bot with enhanced error handling."""
    
    async def setup_production_features(self):
        """Setup production-specific features."""
        # Setup webhook if URL provided
        webhook_url = os.getenv('WEBHOOK_URL')
        if webhook_url:
            await self.setup_webhook(webhook_url)
        
        # Setup health check endpoint
        await self.setup_health_check()
    
    async def setup_webhook(self, url: str):
        """Setup webhook for production."""
        try:
            await self.application.bot.set_webhook(
                url=url,
                secret_token=os.getenv('WEBHOOK_SECRET_TOKEN'),
                drop_pending_updates=True
            )
            logger.info(f"Webhook set to {url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    
    async def error_handler(self, update, context):
        """Enhanced error handler for production."""
        logger.error(f"Exception while handling update: {context.error}", 
                    exc_info=context.error)
        
        # Send error notification to admin
        admin_telegram_ids = os.getenv('ADMIN_USER_IDS', '').split(',')
        if admin_telegram_ids:
            error_msg = f"🚨 Bot Error:\n{str(context.error)[:500]}"
            for admin_telegram_id in admin_telegram_ids:
                try:
                    await context.bot.send_message(
                        chat_id=int(admin_telegram_id),
                        text=error_msg
                    )
                except:
                    pass

async def main():
    """Main entry point."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable required")
    
    bot = ProductionBot(token)
    await bot.setup_production_features()
    
    # Choose deployment method
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        # Webhook mode
        logger.info("Starting bot in webhook mode")
        await bot.run_webhook()
    else:
        # Polling mode
        logger.info("Starting bot in polling mode")
        bot.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
```

### Environment Variables for Production

```bash
# Railway environment variables
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://your-app.railway.app/webhook
WEBHOOK_SECRET_TOKEN=your_webhook_secret
DATABASE_URL=postgresql://...
ADMIN_USER_IDS=123456789,987654321

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
REDIS_URL=redis://...
```

### Health Monitoring

```python
from flask import Flask, jsonify
import asyncio
import threading

# Health check endpoint
health_app = Flask(__name__)

@health_app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        # Check bot status
        bot_status = check_bot_health()
        # Check database connection
        db_status = check_database_health()
        
        if bot_status and db_status:
            return jsonify({
                "status": "healthy",
                "bot": "running",
                "database": "connected"
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "bot": "running" if bot_status else "error",
                "database": "connected" if db_status else "error"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

def run_health_server():
    """Run health check server in separate thread."""
    health_app.run(host='0.0.0.0', port=8001, debug=False)

# Start health server
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()
```

### Performance Optimization

```python
import asyncio
from asyncio import Queue
import time

class MessageQueue:
    """Queue system for managing message sending."""
    
    def __init__(self, bot, max_per_second: int = 25):
        self.bot = bot
        self.max_per_second = max_per_second
        self.queue = Queue()
        self.last_sent = 0
        self.running = True
    
    async def add_message(self, chat_id: int, text: str, **kwargs):
        """Add message to queue."""
        await self.queue.put({
            'chat_id': chat_id,
            'text': text,
            'kwargs': kwargs
        })
    
    async def process_queue(self):
        """Process message queue with rate limiting."""
        while self.running:
            try:
                # Get message from queue
                message_data = await asyncio.wait_for(
                    self.queue.get(), 
                    timeout=1.0
                )
                
                # Rate limiting
                time_since_last = time.time() - self.last_sent
                min_interval = 1.0 / self.max_per_second
                
                if time_since_last < min_interval:
                    await asyncio.sleep(min_interval - time_since_last)
                
                # Send message
                await self.bot.send_message(**message_data)
                self.last_sent = time.time()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")

# Global message queue
message_queue = MessageQueue(bot)

# Start queue processor
asyncio.create_task(message_queue.process_queue())
```

## KICKAI-Specific Implementation

### Integration with CrewAI System

```python
from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.types import TelegramMessage
from kickai.core.enums import ChatType

class KICKAITelegramBot:
    """KICKAI-specific Telegram bot implementation."""
    
    def __init__(self, token: str, team_id: str = "KTI"):
        self.token = token
        self.team_id = team_id
        self.application = ApplicationBuilder().token(token).build()
        self.agentic_router = AgenticMessageRouter(team_id)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup KICKAI-specific handlers."""
        # Commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        self.application.add_handler(CommandHandler("squad", self.squad_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Messages - route through KICKAI AI system
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_ai_message)
        )
        
        # Contact sharing for registration
        self.application.add_handler(
            MessageHandler(filters.CONTACT, self.handle_contact_share)
        )
    
    async def start_command(self, update: Update, context) -> None:
        """Handle /start with KICKAI branding."""
        user = update.effective_user
        
        # Check if user is registered
        if self.is_user_registered(user.id):
            message = f"⚽ Welcome back, {user.first_name}!\n\n🏆 KICKAI Team Manager is ready to assist you."
        else:
            message = (
                f"⚽ Welcome to KICKAI Team Manager!\n\n"
                f"🤖 I'm your AI-powered football team assistant.\n"
                f"📝 To get started, please register using /register\n\n"
                f"Type /help for available commands."
            )
        
        await update.message.reply_text(message)
    
    async def handle_ai_message(self, update: Update, context) -> None:
        """Route message through KICKAI AI system."""
        # Create TelegramMessage object
        telegram_message = TelegramMessage(
            telegram_id=update.effective_user.id,
            text=update.message.text,
            chat_id=str(update.effective_chat.id),
            chat_type=self._get_chat_type(update.effective_chat.type),
            team_id=self.team_id,
            username=update.effective_user.username or update.effective_user.first_name
        )
        
        try:
            # Process through KICKAI AI system
            response = await self.agentic_router.route_message(telegram_message)
            
            # Send response
            await update.message.reply_text(
                response,
                parse_mode='Markdown' if self._contains_markdown(response) else None
            )
        except Exception as e:
            logger.error(f"Error processing AI message: {e}")
            await update.message.reply_text(
                "🤖 Sorry, I'm having trouble processing your request. Please try again or use /help for commands."
            )
    
    async def register_command(self, update: Update, context) -> None:
        """Handle player registration."""
        if not context.args or len(context.args) < 2:
            keyboard = [[KeyboardButton("📞 Share Contact", request_contact=True)]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "📝 **Player Registration**\n\n"
                "Please share your contact information to complete registration:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Process registration with args
        name = " ".join(context.args[:-1])
        position = context.args[-1].lower()
        
        # Validate and register through KICKAI system
        result = await self.register_player(
            telegram_id=update.effective_user.id,
            name=name,
            position=position,
            phone=None  # Will be added via contact share
        )
        
        await update.message.reply_text(result)
    
    async def handle_contact_share(self, update: Update, context) -> None:
        """Handle contact sharing for registration."""
        contact = update.message.contact
        
        # Verify it's user's own contact
        if contact.user_id != update.effective_user.id:
            await update.message.reply_text("❌ Please share your own contact information.")
            return
        
        # Process registration
        result = await self.register_player(
            telegram_id=contact.user_id,
            name=f"{contact.first_name} {contact.last_name or ''}".strip(),
            position="player",  # Default position
            phone=contact.phone_number
        )
        
        # Remove custom keyboard
        await update.message.reply_text(
            result,
            reply_markup=ReplyKeyboardRemove()
        )
    
    async def register_player(self, telegram_id: int, name: str, position: str, phone: str = None) -> str:
        """Register player through KICKAI system."""
        # Create registration message for AI system
        registration_data = {
            "action": "register",
            "telegram_id": telegram_id,
            "name": name,
            "position": position,
            "phone": phone
        }
        
        # Process through KICKAI registration agent
        # This would call your player registration tools
        return f"✅ Welcome {name}! Registration completed."
    
    def _get_chat_type(self, telegram_chat_type) -> ChatType:
        """Convert Telegram chat type to KICKAI ChatType."""
        if telegram_chat_type == "private":
            return ChatType.PRIVATE
        elif telegram_chat_type in ["group", "supergroup"]:
            return ChatType.MAIN  # or LEADERSHIP based on chat ID
        else:
            return ChatType.MAIN
    
    def _contains_markdown(self, text: str) -> bool:
        """Check if text contains Markdown formatting."""
        markdown_chars = ['**', '*', '_', '`', '[', ']']
        return any(char in text for char in markdown_chars)
    
    def is_user_registered(self, telegram_id: int) -> bool:
        """Check if user is registered in KICKAI system."""
        # This would check your database
        return False  # Placeholder

# Usage in main application
async def main():
    """Main application entry point."""
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TEAM_ID = os.getenv('KICKAI_TEAM_ID', 'KTI')
    
    bot = KICKAITelegramBot(TOKEN, TEAM_ID)
    
    logger.info(f"Starting KICKAI Telegram Bot for team {TEAM_ID}")
    bot.application.run_polling(allowed_updates=Update.ALL_TYPES)
```

### Database Integration

```python
from kickai.database.repositories import PlayerRepository, TeamRepository

class KICKAIBotDatabase:
    """Database operations for KICKAI bot."""
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.player_repo = PlayerRepository()
        self.team_repo = TeamRepository()
    
    async def register_player(self, telegram_id: int, name: str, position: str, phone: str = None) -> dict:
        """Register new player."""
        player_data = {
            "telegram_id": telegram_id,
            "name": name,
            "position": position,
            "phone": phone,
            "team_id": self.team_id,
            "status": "active"
        }
        
        try:
            player_id = await self.player_repo.create_player(player_data)
            return {"success": True, "player_id": player_id}
        except Exception as e:
            logger.error(f"Error registering player: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_player_by_telegram_id(self, telegram_id: int) -> dict:
        """Get player by Telegram ID."""
        return await self.player_repo.get_by_telegram_id(telegram_id)
    
    async def update_availability(self, telegram_id: int, availability: str) -> bool:
        """Update player availability."""
        try:
            await self.player_repo.update_availability(telegram_id, availability)
            return True
        except Exception as e:
            logger.error(f"Error updating availability: {e}")
            return False
```

This comprehensive guide provides all the necessary information for implementing a robust Telegram bot for the KICKAI system, covering everything from basic concepts to advanced production deployment strategies.