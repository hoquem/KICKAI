# Multi-Team Testing Guide for KICKAI

This guide will help you create a new team, become the admin, and test the KICKAI system with real people interacting via Telegram. You'll be able to test role-based interactions, team management, and the complete workflow.

## 🎯 **Overview**

The KICKAI system supports multiple teams, each with their own:
- **Team members** with different roles (admin, manager, captain, player)
- **Telegram group** for team communications
- **Fixtures and availability** tracking
- **Payment management**

## 🚀 **Quick Start**

### **Phase 1: Create Your Team**

1. **Run the quick setup script**:
   ```bash
   python quick_team_setup.py
   ```

2. **Enter your details**:
   - Team name (e.g., "Sunday Warriors")
   - Your phone number (you'll be the admin)
   - Your name
   - Telegram group ID (you'll create this next)

3. **The script will**:
   - Create your team in the database
   - Make you the admin
   - Show you the next steps

### **Phase 2: Telegram Group Setup**

#### Step 1: Create Telegram Group

1. **Open Telegram** and create a new group
2. **Name it** something like "Sunday Warriors - KICKAI"
3. **Add your bot** to the group (the one you created for KICKAI)
4. **Make the bot an admin** (optional, but recommended)

#### Step 2: Get Group Chat ID

1. **Send a message** in your new group
2. **Visit this URL** (replace with your bot token):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
3. **Look for** `"chat":{"id":-123456789}` - this is your chat ID
4. **Copy the chat ID** (it will be a negative number)

#### Step 3: Update Environment

Add to your `.env` file:
```bash
# Update with your new team's Telegram group
TELEGRAM_CHAT_ID=your_new_telegram_group_chat_id
```

### **Phase 3: Test the System**

1. **Test Telegram messaging**:
   ```bash
   python test_telegram_features.py
   ```

2. **Test CrewAI agents**:
   ```bash
   python test_crewai_ollama_correct.py
   ```

3. **Add sample data**:
   ```bash
   python test_sample_data.py
   ```

## 👥 **Adding Real Team Members**

### **Method 1: Using the Team Management Tools**

1. **Get your team ID** (from the team creation result)
2. **Add members** using the team management tools:
   ```python
   from src.tools.team_management_tools import TeamManagementTools
   
   tool = TeamManagementTools()
   
   # Add a manager
   result = tool._run('add_team_member',
                     team_id='your-team-id',
                     phone_number='+1234567890',
                     name='Sarah Manager',
                     role='manager')
   ```

### **Method 2: Direct Database Insert**

```sql
-- Add team members directly
INSERT INTO team_members (team_id, phone_number, name, role, is_active, joined_at)
VALUES 
('your-team-id', '+1234567890', 'Sarah Manager', 'manager', true, now()),
('your-team-id', '+1234567891', 'Mike Captain', 'captain', true, now()),
('your-team-id', '+1234567892', 'Alex Player', 'player', true, now());
```

## 🧪 **Testing Scenarios**

### **Test 1: Basic Messaging**

1. **Send a team announcement**:
   ```python
   from src.tools.telegram_tools import SendTelegramMessageTool
   
   tool = SendTelegramMessageTool()
   result = tool._run("Welcome to the team! Our first match is this Sunday.")
   ```

2. **Expected result**: Message appears in your Telegram group

### **Test 2: Interactive Polls**

1. **Send an availability poll**:
   ```python
   from src.tools.telegram_tools import SendAvailabilityPollTool
   
   tool = SendAvailabilityPollTool()
   result = tool._run("vs Red Lions", "Sunday 2pm", "2:00 PM", "Central Park")
   ```

2. **Expected result**: Poll appears in Telegram group with voting options

### **Test 3: Squad Announcements**

1. **Send a squad announcement**:
   ```python
   from src.tools.telegram_tools import SendSquadAnnouncementTool
   
   tool = SendSquadAnnouncementTool()
   starters = ["John (GK)", "Mike (RB)", "David (CB)", "Tom (CB)", "Alex (LB)"]
   substitutes = ["Ryan", "Kevin", "Mark"]
   
   result = tool._run("vs Blue Eagles", "Sunday 3pm", "3:00 PM", starters, substitutes)
   ```

2. **Expected result**: Formatted squad announcement appears in group

### **Test 4: Payment Reminders**

1. **Send a payment reminder**:
   ```python
   from src.tools.telegram_tools import SendPaymentReminderTool
   
   tool = SendPaymentReminderTool()
   unpaid_players = ["John Smith", "Mike Johnson"]
   
   result = tool._run(unpaid_players, 15.00, "vs Red Lions (Sunday)")
   ```

2. **Expected result**: Payment reminder appears in group

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Telegram Group Not Found**
   - Ensure the bot is added to the group
   - Check that the chat ID is correct
   - Verify the bot has permission to send messages

2. **Messages Not Appearing**
   - Check your `.env` file has the correct `TELEGRAM_CHAT_ID`
   - Ensure the bot token is valid
   - Verify the group is active

3. **Team Not Found**
   - Check that the team was created successfully
   - Verify the team ID is correct
   - Ensure you're using the right database

### **Debug Steps**

1. **Test Telegram connection**:
   ```bash
   python test_telegram_features.py
   ```

2. **Check team creation**:
   ```bash
   python test_team_setup.py
   ```

3. **Verify database**:
   ```bash
   python test_database_setup.py
   ```

## 📊 **Expected Results**

When everything is working correctly, you should see:

1. **Team created** in the database with your details
2. **Message sent** to Telegram group
3. **Poll sent** to Telegram group with voting options
4. **Squad announcement** sent to Telegram with formatting
5. **Payment reminder** sent to Telegram group

## 🎯 **Next Steps**

Once your team is set up and working:

1. **Invite real team members** to your Telegram group
2. **Test role-based interactions** with different team members
3. **Create real fixtures** and test availability polling
4. **Use the CrewAI agents** for automated team management
5. **Customize messages** and features for your team's needs

## ✅ **Checklist**

- [ ] Team created in database
- [ ] Telegram group set up
- [ ] Bot added to group
- [ ] Chat ID configured in .env
- [ ] Basic messaging working
- [ ] Interactive polls working
- [ ] Squad announcements working
- [ ] Payment reminders working
- [ ] Real team members invited
- [ ] CrewAI agents tested

**You're now ready to use KICKAI with your real team!** 🚀 