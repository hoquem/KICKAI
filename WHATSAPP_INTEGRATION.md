# WhatsApp Integration Documentation

## Overview

The KICKAI system now includes comprehensive WhatsApp integration using the Twilio WhatsApp API. This allows the CrewAI agents to send messages, polls, and announcements directly to the team's WhatsApp group.

## Features Implemented

### ✅ WhatsApp Tools Available

1. **SendWhatsAppMessageTool** - Send general messages to the team
2. **SendWhatsAppPollTool** - Send polls with multiple options
3. **SendAvailabilityPollTool** - Send match availability polls
4. **SendSquadAnnouncementTool** - Announce selected squad for matches
5. **SendPaymentReminderTool** - Send payment reminders to players

### ✅ Agent Integration

- **Communications Officer Agent** - Primary user of WhatsApp tools
- **Manager Agent** - Can send announcements and coordinate via WhatsApp
- **Finance Agent** - Can send payment reminders via WhatsApp

## Setup Instructions

### 1. Twilio Account Setup

1. **Create Twilio Account**
   - Go to [Twilio Console](https://console.twilio.com/)
   - Sign up for a free account
   - Verify your phone number

2. **Enable WhatsApp Sandbox**
   - In Twilio Console, go to Messaging → Try it out → Send a WhatsApp message
   - Follow instructions to join your WhatsApp sandbox
   - Note your sandbox phone number (format: `whatsapp:+1234567890`)

3. **Get API Credentials**
   - In Twilio Console, go to Settings → API Keys
   - Copy your Account SID and Auth Token
   - Keep these secure - they're your API credentials

### 2. Environment Configuration

Add the following variables to your `.env` file:

```bash
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=whatsapp:+1234567890
TEAM_WHATSAPP_GROUP=your_team_whatsapp_group_id_here
```

### 3. WhatsApp Group Setup

For testing, you can use the Twilio sandbox. For production:

1. **Business WhatsApp Account** (Recommended)
   - Apply for WhatsApp Business API through Twilio
   - Get a dedicated WhatsApp phone number
   - Set up your team group

2. **Sandbox Testing** (Development)
   - Use Twilio's WhatsApp sandbox for testing
   - Join the sandbox with your personal WhatsApp
   - Test messages will be sent to your personal number

## Usage Examples

### 1. Basic Message Sending

```python
from src.tools.whatsapp_tools import SendWhatsAppMessageTool

# Initialize the tool
message_tool = SendWhatsAppMessageTool()

# Send a message
result = message_tool._run("Hello team! Match tomorrow at 2 PM.")
print(result)
```

### 2. Availability Poll

```python
from src.tools.whatsapp_tools import SendAvailabilityPollTool

# Initialize the tool
poll_tool = SendAvailabilityPollTool()

# Send availability poll
result = poll_tool._run(
    fixture_details="vs. Red Dragons FC",
    match_date="Sunday, 15th December",
    match_time="2:00 PM",
    location="Central Park"
)
print(result)
```

### 3. Squad Announcement

```python
from src.tools.whatsapp_tools import SendSquadAnnouncementTool

# Initialize the tool
squad_tool = SendSquadAnnouncementTool()

# Announce squad
result = squad_tool._run(
    fixture_details="vs. Red Dragons FC",
    match_date="Sunday, 15th December",
    match_time="2:00 PM",
    starters=["John Smith", "Mike Johnson", "David Wilson", ...],
    substitutes=["Tom Brown", "Alex Davis", "Chris Miller"]
)
print(result)
```

### 4. Payment Reminder

```python
from src.tools.whatsapp_tools import SendPaymentReminderTool

# Initialize the tool
reminder_tool = SendPaymentReminderTool()

# Send payment reminder
result = reminder_tool._run(
    unpaid_players=["John Smith", "Mike Johnson"],
    amount=15.00,
    fixture_details="vs. Red Dragons FC"
)
print(result)
```

## Testing

### Run the Test Script

```bash
python test_whatsapp_integration.py
```

This will:
- Check environment variables
- Test tool initialization
- Verify agent integration
- Provide setup guidance

### Manual Testing

1. **Set up your environment variables**
2. **Run the test script** to verify setup
3. **Test individual tools** with small messages
4. **Monitor Twilio console** for message delivery

## Integration with CrewAI Agents

The WhatsApp tools are automatically available to:

- **Communications Officer Agent** - Primary messaging agent
- **Manager Agent** - Can send announcements and coordinate
- **Finance Agent** - Can send payment reminders

### Example Agent Usage

```python
from src.agents import communications_agent

# The agent can now use WhatsApp tools automatically
# When you ask it to send a message, it will use the appropriate WhatsApp tool
```

## Message Templates

### Availability Poll Template
```
⚽ MATCH AVAILABILITY POLL

Fixture: vs. Red Dragons FC
Date: Sunday, 15th December
Time: 2:00 PM
Location: Central Park

Are you available for this match?

1. ✅ Yes, I'm in!
2. ❌ No, can't make it
3. 🤔 Maybe, will confirm later

Reply with 1, 2, or 3.
```

### Squad Announcement Template
```
🏆 SQUAD ANNOUNCEMENT

Fixture: vs. Red Dragons FC
Date: Sunday, 15th December
Time: 2:00 PM

📋 STARTING XI:
1. John Smith
2. Mike Johnson
3. David Wilson
...

🔄 SUBSTITUTES:
1. Tom Brown
2. Alex Davis
3. Chris Miller

🎯 Good luck, team! Let's get the win! 💪
```

### Payment Reminder Template
```
💰 PAYMENT REMINDER

Fixture: vs. Red Dragons FC
Amount: £15.00

The following players still need to pay:
• John Smith
• Mike Johnson

Please arrange payment as soon as possible. Thanks!
```

## Troubleshooting

### Common Issues

1. **"Missing required Twilio environment variables"**
   - Check your `.env` file has all required variables
   - Ensure no extra spaces or quotes around values

2. **"Twilio error: Authentication failed"**
   - Verify your Account SID and Auth Token
   - Check your Twilio account is active

3. **"Team WhatsApp group not configured"**
   - Set the `TEAM_WHATSAPP_GROUP` environment variable
   - Use your WhatsApp group ID or phone number

4. **Messages not delivered**
   - Check Twilio console for delivery status
   - Verify your WhatsApp number is properly configured
   - Ensure you've joined the Twilio sandbox (for testing)

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Twilio Console Monitoring

- Monitor message delivery in Twilio Console
- Check for any error messages or delivery failures
- Review usage and costs in the billing section

## Cost Considerations

### Twilio Pricing (as of 2024)
- **WhatsApp Sandbox**: Free for testing
- **WhatsApp Business API**: Pay per message
- **Message costs**: Varies by country and message type

### Cost Optimization
- Use sandbox for development and testing
- Batch messages when possible
- Monitor usage in Twilio console
- Set up billing alerts

## Security Best Practices

1. **Environment Variables**
   - Never commit API keys to version control
   - Use `.env` file for local development
   - Use secure environment variables in production

2. **API Key Management**
   - Rotate API keys regularly
   - Use least privilege principle
   - Monitor API usage for anomalies

3. **Message Content**
   - Validate message content before sending
   - Avoid sending sensitive information
   - Respect WhatsApp's terms of service

## Next Steps

### Immediate
1. Set up your Twilio account and sandbox
2. Configure environment variables
3. Test the integration with the test script
4. Try sending a test message

### Future Enhancements
1. **Webhook Integration** - Receive incoming messages
2. **Message Templates** - Pre-approved message formats
3. **Scheduled Messages** - Send messages at specific times
4. **Message History** - Track sent and received messages
5. **Analytics** - Message delivery and engagement metrics

## Support

- **Twilio Documentation**: [WhatsApp API Guide](https://www.twilio.com/docs/whatsapp)
- **KICKAI Issues**: Create issues in the GitHub repository
- **Twilio Support**: Available through Twilio console

---

**Note**: This integration is part of KICKAI feature KAI-002 and follows the development workflow outlined in the README.md file. 