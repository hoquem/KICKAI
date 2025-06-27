# Telegram Setup Guide for KICKAI

## 🚀 **Why Telegram for Team Management**

### **✅ Telegram Advantages:**
- **🔓 Open API** - No approval process, instant access
- **👥 Full Group Support** - Works immediately with groups
- **🤖 Bot API** - Easy automation and interactive features
- **📱 Cross-platform** - Works on all devices
- **💬 Rich Features** - Polls, buttons, inline keyboards
- **📊 No Limits** - No sandbox restrictions
- **🆓 Free** - No messaging costs
- **🔒 Privacy** - Better privacy controls

---

## 🛠️ **Step-by-Step Telegram Setup**

### **Step 1: Create a Telegram Bot**

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send `/newbot`** command
4. **Choose a name** for your bot (e.g., "KICKAI Team Manager")
5. **Choose a username** (e.g., "kickai_team_bot")
6. **Save the bot token** - you'll get something like:
   ```
   123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### **Step 2: Create a Team Group**

1. **Create a new group** in Telegram
2. **Add your bot** to the group
3. **Make the bot an admin** (optional, but recommended)
4. **Get the group chat ID**:
   - Send a message in the group
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id":-123456789}` - this is your chat ID

### **Step 3: Update Environment Variables**

Add these to your `.env` file:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_group_chat_id_here

# Keep existing variables
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
# ... other variables
```

### **Step 4: Test Telegram Integration**

Run the Telegram test:

```bash
python test_telegram_features.py
```

---

## 🧪 **Testing Telegram Features**

### **Test Script**

```bash
python test_telegram_features.py
```

This will test:
- ✅ Basic messaging
- ✅ Polls
- ✅ Availability polls
- ✅ Squad announcements
- ✅ Payment reminders

### **Expected Results**

You should see:
- Messages appear in your Telegram group
- Interactive polls that team members can vote on
- Rich formatting with emojis and HTML
- Real-time responses from team members

---

## 🎯 **Telegram Features for Team Management**

### **1. Interactive Polls**
- **Availability polls** - Players can vote Yes/No/Maybe
- **Team decisions** - Vote on match times, locations, etc.
- **Real-time results** - See who voted for what

### **2. Rich Messaging**
- **HTML formatting** - Bold, italic, emojis
- **Squad announcements** - Formatted team lists
- **Payment reminders** - Clear, professional messages

### **3. Group Management**
- **Admin controls** - Manage who can send messages
- **Member management** - Add/remove team members
- **Message history** - Search and reference old messages

### **4. Bot Commands**
- **/availability** - Check who's available
- **/squad** - Show current squad
- **/fixtures** - List upcoming matches
- **/payments** - Check payment status

---

## 📱 **Team Member Onboarding**

### **1. Invite Team Members**

1. **Share the group link** with your team
2. **Ask them to join** the Telegram group
3. **Add them to the system** using the team management tools

### **2. Bot Introduction**

Send this message to introduce the bot:

```
🤖 Welcome to KICKAI Team Manager!

This bot will help us:
• Check availability for matches
• Announce squads
• Send reminders
• Manage team communications

Commands you can use:
/help - Show available commands
/availability - Check your availability
/profile - View your profile
```

### **3. First Test**

Send a test availability poll to get everyone familiar with the system.

---

## 🎯 **Advanced Features**

### **1. Inline Keyboards**
Add interactive buttons to messages:

```python
# Example: Availability buttons
keyboard = [
    [{"text": "✅ Available", "callback_data": "available"}],
    [{"text": "❌ Not Available", "callback_data": "unavailable"}],
    [{"text": "🤔 Maybe", "callback_data": "maybe"}]
]
```

### **2. Webhook Integration**
Set up webhooks to receive responses:

```python
# Handle poll responses
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'poll_answer' in data:
        handle_poll_response(data['poll_answer'])
```

### **3. Scheduled Messages**
Send automatic reminders:

```python
# Daily availability reminder
schedule.every().day.at("09:00").do(send_availability_reminder)
```

---

## 🚀 **Benefits for Your Team**

### **Immediate Benefits:**
- ✅ **Instant setup** - No waiting for approvals
- ✅ **Group messaging** - Works immediately
- ✅ **Interactive polls** - Real-time responses
- ✅ **Rich formatting** - Professional appearance
- ✅ **No costs** - Completely free

### **Long-term Benefits:**
- 🔄 **Easy automation** - Bot handles routine tasks
- 📊 **Better analytics** - Track responses and engagement
- 🎯 **Improved communication** - Clear, organized messaging
- 👥 **Team engagement** - Interactive features increase participation

---

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **Bot not responding**
   - Check bot token is correct
   - Ensure bot is added to group
   - Verify bot has permission to send messages

2. **Messages not appearing**
   - Check chat ID is correct
   - Ensure group is active
   - Verify bot is not blocked

3. **Polls not working**
   - Check bot has admin rights
   - Ensure group allows polls
   - Verify poll options are valid

### **Debug Commands:**

```bash
# Test bot connection
curl "https://api.telegram.org/bot<TOKEN>/getMe"

# Get chat info
curl "https://api.telegram.org/bot<TOKEN>/getChat?chat_id=<CHAT_ID>"

# Send test message
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
     -d "chat_id=<CHAT_ID>" \
     -d "text=Test message"
```

---

## 🎉 **Next Steps**

1. **Set up your Telegram bot** using the guide above
2. **Create your team group** and add the bot
3. **Update your environment variables**
4. **Test the integration** with the test script
5. **Invite your real team members**
6. **Start using Telegram for team management!**

**Telegram will give you a much better experience for team management with immediate group messaging, interactive features, and no approval delays!** 🚀 