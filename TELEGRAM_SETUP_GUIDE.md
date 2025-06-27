# Telegram Setup Guide for KICKAI

This guide will help you set up Telegram integration for your KICKAI team management system.

## 🚀 Why Telegram?

Telegram is the perfect platform for team management because:

- ✅ **Instant Setup**: No approval process, create bot in 5 minutes
- ✅ **Group Support**: Full group messaging from day one
- ✅ **Interactive Polls**: Native poll support with real-time voting
- ✅ **Rich Formatting**: HTML support for professional messages
- ✅ **Bot Commands**: Interactive commands like `/availability`, `/squad`
- ✅ **No Costs**: Completely free messaging
- ✅ **Better Privacy**: More control over data and settings
- ✅ **Cross-platform**: Works on all devices

## 📱 Step-by-Step Setup

### Step 1: Create Your Telegram Bot

1. **Open Telegram** on your phone or desktop
2. **Search for @BotFather** in Telegram
3. **Send the command**: `/newbot`
4. **Choose a name** for your bot (e.g., "Your Team Name Team Manager")
5. **Choose a username** for your bot (e.g., "yourteam_bot")
6. **Copy the bot token** that BotFather gives you

**Example:**
```
Bot name: BP Hatters FC Team Manager
Username: bphatters_bot
Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Step 2: Create Your Team Group

1. **Create a new Telegram group**
   - Open Telegram
   - Tap the pencil icon (New Message)
   - Select "New Group"
   - Add at least one other person (you can add yourself with another account)
   - Name the group (e.g., "BP Hatters FC")

2. **Add your bot to the group**
   - In the group, tap the group name at the top
   - Select "Add members" or "Invite to group"
   - Search for your bot username (e.g., `@bphatters_bot`)
   - Add the bot to the group

3. **Make the bot an admin** (required for polls)
   - In the group, tap the group name at the top
   - Select "Edit" or tap the three dots menu
   - Choose "Manage group" or "Group settings"
   - Find "Members" section
   - Tap on your bot's name
   - Select "Add as admin" or "Make admin"
   - Grant these permissions:
     - ✅ **Send Messages**
     - ✅ **Pin Messages**
     - ✅ **Delete Messages** (optional)
     - ✅ **Invite Users** (optional)

### Step 3: Get Your Group Chat ID

1. **Send a message** in your group (any message)
2. **Use this command** to get the chat ID:
   ```bash
   curl -s "https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates" | python -m json.tool
   ```
3. **Look for the chat ID** in the response (it will be a negative number for groups)

**Example response:**
```json
{
  "ok": true,
  "result": [
    {
      "message": {
        "chat": {
          "id": -1234567890,
          "title": "BP Hatters FC",
          "type": "group"
        }
      }
    }
  ]
}
```

### Step 4: Configure Your Environment

1. **Open your `.env` file**
2. **Add these variables**:
   ```bash
   # Telegram Configuration
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_group_chat_id_here
   TEAM_NAME=Your Team Name
   ```

**Example:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1234567890
TEAM_NAME=BP Hatters FC
```

### Step 5: Test Your Setup

1. **Run the test script**:
   ```bash
   python test_telegram_features.py
   ```

2. **Check the results** - you should see:
   - ✅ Bot connected successfully
   - ✅ Chat access successful
   - ✅ All message types working
   - ✅ Team name being used in messages

## 🎯 What You'll Get

Once set up, your team will have access to:

### 📱 Team Communications
- **Squad Announcements**: Professional squad lists with formatting
- **Match Updates**: Fixture details and match information
- **Team News**: General announcements and updates

### 📊 Interactive Features
- **Availability Polls**: Players can vote on their availability
- **Team Polls**: Vote on match times, tactics, etc.
- **Quick Responses**: Buttons for common actions

### 💰 Payment Management
- **Payment Reminders**: Automated reminders for match fees
- **Payment Tracking**: Track who has paid and who hasn't
- **Financial Updates**: Payment status and fee information

### 🤖 Bot Commands
- `/availability` - Check your availability status
- `/squad` - View current squad for next match
- `/fixtures` - See upcoming fixtures
- `/payments` - Check payment status

## 🔧 Troubleshooting

### Bot Not Responding
- Check that the bot token is correct
- Ensure the bot is added to the group
- Verify the bot has permission to send messages

### Polls Not Working
- Make sure the bot is an admin in the group
- Check that the bot has "Send Messages" permission
- Verify you're using a group chat (not private chat)

### Messages Not Sending
- Check your internet connection
- Verify the chat ID is correct
- Ensure the bot token is valid

### Team Name Not Showing
- Check that `TEAM_NAME` is set in your `.env` file
- Verify your team exists in the database
- Check the database connection

## 📋 Example Messages

### Squad Announcement
```
🏆 BP Hatters FC - Squad Announcement

⚽ Match: vs Thunder FC
📅 Date: Sunday, July 7th
🕐 Time: 2:00 PM

👥 Starting XI:
1. John Smith (GK)
2. Mike Johnson (RB)
3. David Wilson (CB)
...

🔄 Substitutes:
1. Dan Anderson
2. Ryan White
3. Matt Harris

💪 Good luck, lads!
Please arrive 30 minutes before kickoff for warm-up.
```

### Availability Poll
```
⚽ Availability: vs Thunder FC

📅 Date: Sunday, July 7th
🕐 Time: 2:00 PM
📍 Location: Central Park

Please vote for your availability!
```

### Payment Reminder
```
💰 BP Hatters FC - Payment Reminder

⚽ Match: vs Thunder FC
💷 Amount: £15.00 per player

📋 Players who haven't paid:
• John Smith
• Mike Johnson
• David Wilson

⏰ Please pay by Friday to avoid late fees.

💳 Payment Methods:
• Bank transfer (details in pinned message)
• Cash to team captain
• PayPal (contact admin)

Thank you for your prompt payment!
```

## 🎉 Next Steps

1. **Invite your team members** to the Telegram group
2. **Test all features** with your team
3. **Customize messages** to match your team's style
4. **Set up automated reminders** for regular tasks
5. **Start using KICKAI** for team management!

## 📞 Support

If you need help:
1. Check this guide again
2. Run the test scripts to verify your setup
3. Check the error messages in the test output
4. Review your environment variables
5. Ensure your bot has the correct permissions

---

**Happy team managing!** ⚽🤖 