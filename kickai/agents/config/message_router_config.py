#!/usr/bin/env python3
"""
Configuration for the Agentic Message Router.

Centralizes all constants, messages, and configuration values.
"""

# RATE LIMITING
DEFAULT_MAX_CONCURRENT = 10
DEFAULT_MAX_REQUESTS_PER_MINUTE = 60
DEFAULT_CLEANUP_INTERVAL = 300  # 5 minutes
DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 0.1
DEFAULT_EXPONENTIAL_BACKOFF_FACTOR = 2
RATE_LIMIT_WINDOW_SECONDS = 60

# PHONE VALIDATION
PHONE_NUMBER_MAX_LENGTH = 50
PHONE_NUMBER_MIN_LENGTH = 10
PHONE_NUMBER_MAX_DIGITS = 15
PHONE_NUMBER_MIN_DIGITS = 10
PHONE_ALLOWED_CHARS = set("0123456789+()-. ")

# COMMAND PATTERNS
SLASH_COMMAND_PREFIX = "/"
CLEAR_COMMAND_NAMES = {
    "/help",
    "/ping",
    "/version",
    "/list",
    "/myinfo",
    "/info",
    "/status",
    "/addplayer",
    "/addmember",
    "help",
    "ping",
    "version",
    "list",
    "myinfo",
    "info",
    "status",
    "addplayer",
    "addmember",
}

# FOLLOWUP INDICATORS
FOLLOWUP_INDICATORS = [
    "yes",
    "no",
    "thanks",
    "ok",
    "sure",
    "please",
    "what about",
    "and",
    "also",
    "too",
    "again",
    "it",
    "that",
    "this",
    "them",
    "those",
]

# AMBIGUOUS REFERENCES
AMBIGUOUS_REFS = [
    "it",
    "that",
    "this",
    "them",
    "those",
    "he",
    "she",
    "they",
    "last",
    "previous",
    "next",
    "current",
    "recent",
]

# ERROR MESSAGES
ERROR_MESSAGES = {
    "INVALID_TEAM_ID": "team_id must be a non-empty string, got: {type_name}",
    "INVALID_MESSAGE_TYPE": "Expected TelegramMessage, got {type_name}",
    "INVALID_MESSAGE_TEXT": "Invalid message: missing or empty text",
    "INVALID_USER_ID": "Invalid user ID format",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded for team {team_id}, user {telegram_id}",
    "CONCURRENT_LIMIT_EXCEEDED": "Concurrent request limit exceeded for team {team_id}",
    "SERVICE_INITIALIZATION_FAILED": "Service initialization failed: {error}",
    "USER_REGISTRATION_TIMEOUT": "User registration check timed out for user {telegram_id}",
    "USER_REGISTRATION_ERROR": "Error during user registration check: {error}",
    "PLAYER_LOOKUP_FAILED": "Player lookup failed: {error}",
    "TEAM_MEMBER_LOOKUP_FAILED": "Team member lookup failed: {error}",
    "NLP_PROCESSING_ERROR": "Error in NLP-enhanced processing: {error}",
    "COMMAND_ANALYSIS_ERROR": "Error in _is_clear_command: {error}",
    "COMMAND_CLARITY_ERROR": "Error in _classify_command_clarity: {error}",
    "COMMAND_EXTRACTION_ERROR": "Error extracting command from text: {error}",
    "COMMAND_REGISTRY_ERROR": "Error finding command in registry: {error}",
    "FOLLOWUP_CHECK_ERROR": "Error checking conversational follow-up: {error}",
    "AMBIGUOUS_REF_CHECK_ERROR": "Error checking ambiguous references: {error}",
    "PHONE_VALIDATION_ERROR": "Phone number validation: disallowed characters in input",
    "NEW_MEMBERS_EXTRACTION_ERROR": "Error extracting new members: {error}",
    "INVITE_LINK_EXTRACTION_ERROR": "Error extracting invite link: {error}",
    "INVITE_ID_EXTRACTION_ERROR": "Error extracting invite ID: {error}",
    "INVITE_CONTEXT_EXTRACTION_ERROR": "Error extracting invite context: {error}",
    "WELCOME_MESSAGE_ERROR": "Error creating enhanced welcome message: {error}",
    "CLEANUP_ERROR": "Error cleaning up request tracker: {error}",
    "RATE_LIMIT_MESSAGE": "⏰ Too many requests. Please wait a moment and try again.",
    "CONCURRENT_LIMIT_MESSAGE": "🚦 System busy. Please try again in a moment.",
    "NO_CONTACT_INFO": "❌ No contact information found in message.",
    "NO_MATCHING_PLAYER": "No matching player record",
    "NO_NEW_MEMBERS": "No new members found in new_chat_members event",
    "NO_NEW_MEMBERS_ERROR": "No new members",
    "INVALID_INVITE_LINK": "❌ Invalid or expired invite link. Please contact team leadership.",
    "INVALID_INVITE_DATA": "❌ Invalid invite data. Please contact team leadership.",
    "INVITE_PROCESSING_ERROR": "❌ Error processing your invitation. Please contact team leadership.",
    "TEAM_MEMBER_INVITE_ERROR": "❌ Error processing your team member invitation. Please contact the team administrator.",
    "NEW_CHAT_MEMBERS_ERROR": "❌ Error processing your join. Please contact team leadership.",
    "PHONE_PROCESSING_ERROR": "❌ Error processing your phone number. Please try again or contact team leadership.",
    "HELP_ERROR": "❌ Sorry, I encountered an error while helping you. Please try again.",
}

# WARNING MESSAGES
WARNING_MESSAGES = {
    "TELEGRAM_ID_TYPE": "telegram_id should be int, got {type_name}",
    "CHAT_TYPE_STRING": "chat_type passed as string '{chat_type}', converting to enum",
    "CHAT_TYPE_NORMALIZATION_FAILED": "Failed to normalize chat_type '{chat_type}': {error}",
    "SERVICE_RETRIEVAL_FAILED": "Service retrieval attempt {attempt} failed: {error}",
    "PLAYER_LOOKUP_FAILED": "Player lookup failed: {error}",
    "TEAM_MEMBER_LOOKUP_FAILED": "Team member lookup failed: {error}",
    "SERVICE_UNAVAILABLE": "Could not get services for registration check: {error}",
    "COMMAND_REGISTRY_UNAVAILABLE": "Command registry not available",
    "INVALID_COMMAND_INPUT": "Invalid input for command analysis: {error}",
    "NO_INVITATION_CONTEXT": "No invitation context found, using default invite_id",
    "NO_INVITE_CONTEXT": "No invite context found in event",
    "PHONE_VALIDATION_ERROR": "Phone number validation: disallowed characters in input",
    "COMMAND_EXTRACTION_ERROR": "Error extracting command: {error}",
    "COMMAND_REGISTRY_ERROR": "Error finding command in registry: {error}",
    "FOLLOWUP_CHECK_ERROR": "Error checking conversational follow-up: {error}",
    "AMBIGUOUS_REF_CHECK_ERROR": "Error checking ambiguous references: {error}",
    "AUTO_ACTIVATION_FAILED": "Auto-activation failed for {username}: {error}",
    "PLAYER_LINKING_FAILED": "Failed to link player {player_name} to user {telegram_id}",
    "NO_AGENT_FOUND": "No agent found for user flow type: {user_flow_type}",
    "NO_COMMAND_AGENT_FOUND": "No command agent found for processing",
}

# LOG MESSAGES
LOG_MESSAGES = {
    "ROUTER_INITIALIZED": "AgenticMessageRouter initialized for team {team_id}",
    "RESOURCE_MANAGER_INITIALIZED": "ResourceManager initialized with max_concurrent={max_concurrent}, max_requests_per_minute={max_requests_per_minute}",
    "MESSAGE_ROUTING": "AgenticMessageRouter: Routing message from {username} in {chat_type}",
    "NEW_CHAT_MEMBERS_DETECTED": "AgenticMessageRouter: Detected new_chat_members event",
    "COMMAND_DETECTED": "AgenticMessageRouter: Detected command: {command}",
    "HELPER_COMMAND_ROUTING": "AgenticMessageRouter: Routing to Helper Agent: {command}",
    "UNREGISTERED_USER_FLOW": "AgenticMessageRouter: Unregistered user flow detected",
    "PHONE_NUMBER_DETECTED": "AgenticMessageRouter: Detected phone number in message from unregistered user",
    "REGISTERED_USER_FLOW": "AgenticMessageRouter: Registered user flow detected",
    "NLP_PROCESSING": "AgenticMessageRouter: Processing with NLP enhancement",
    "DIRECT_ROUTING": "AgenticMessageRouter: Direct routing for clear command",
    "USER_REGISTRATION_STATUS": "AgenticMessageRouter: User registration status - is_registered={is_registered}, is_player={is_player}, is_team_member={is_team_member}",
    "ACTUAL_REGISTRATION_STATUS": "AgenticMessageRouter: Actual registration status - is_player={is_player}, is_team_member={is_team_member}, is_registered={is_registered}",
    "SKIP_NLP_CLEAR_COMMAND": "Skipping NLP for clear command: {text}",
    "NLP_CONVERSATIONAL_FOLLOWUP": "NLP needed for conversational follow-up: {text}",
    "NLP_AMBIGUOUS_REFERENCES": "NLP needed for ambiguous references: {text}",
    "NLP_NATURAL_LANGUAGE": "NLP needed for natural language: {text}",
    "NLP_STARTING": "Starting NLP-enhanced message processing",
    "CONTACT_SHARE_PROCESSING": "AgenticMessageRouter: Processing contact share from {username}",
    "NEW_CHAT_MEMBERS_PROCESSING": "Processing new_chat_members event for auto-activation",
    "NEW_MEMBER_PROCESSING": "Processing new member for auto-activation: {username} (ID: {telegram_id})",
    "AUTO_ACTIVATION_SUCCESS": "Auto-activation successful for {username}: {player_name}",
    "PLAYER_LINKING_SUCCESS": "Successfully linked player {player_name} to user {telegram_id}",
    "TEAM_MEMBER_INVITE_PROCESSING": "Processing team member invite for {member_name}",
    "INVITATION_CONTEXT_FOUND": "Found invitation context with invite_id: {invite_id}",
    "BACKUP_INVITATION_DATA_FOUND": "Found backup invitation data with invite_id: {invite_id}",
    "INVITE_CONTEXT_EXTRACTED": "Extracted invite context: {keys}",
    "BACKUP_INVITE_CONTEXT_EXTRACTED": "Extracted backup invite context: {keys}",
    "FORCE_CLEANUP": "Force cleaned up resources for team {team_id}",
    "REGULAR_CLEANUP": "Cleaned up resources for team {team_id}",
    "ROUTER_SHUTDOWN": "Shutting down AgenticMessageRouter for team {team_id}",
    "ROUTER_SHUTDOWN_COMPLETE": "AgenticMessageRouter shutdown complete for team {team_id}",
    "ROUTER_SHUTDOWN_ERROR": "Error during AgenticMessageRouter shutdown: {error}",
}

# SUCCESS MESSAGES
SUCCESS_MESSAGES = {
    "WELCOME_LEADERSHIP": """👋 Welcome to KICKAI Leadership for {team_id}, {username}!

🤖 KICKAI v{version} - Your AI-powered football team assistant

🤔 You're not registered as a team member yet.

📞 Contact Team Administrator
You need to be added as a team member by the team administrator.

💡 What to do:
1. Contact the team administrator
2. Ask them to add you as a team member using the /addmember command
3. They'll send you an invite link to join the leadership chat
4. Once added, you can access leadership functions

❓ Got here by mistake?
If you're not part of the team leadership, please leave this chat.

Need help? Contact the team administrator.""",
    "WELCOME_MAIN": """👋 Welcome to KICKAI for {team_id}, {username}!

🤖 KICKAI v{version} - Your AI-powered football team assistant

🤔 You're not registered as a player yet.

📞 Contact Team Leadership
You need to be added as a player by someone in the team's leadership.

💬 What to do:
1. Reach out to someone in the team's leadership chat
2. Ask them to add you as a player using the /addplayer command
3. They'll send you an invite link to join the main chat
4. Once added, you can register with your full details

❓ Got here by mistake?
If you're not interested in joining the team, you can leave this chat.

🤖 Need help?
Use /help to see available commands or ask me questions!""",
    "CONTACT_LINKING_SUCCESS": "✅ Successfully linked to your player record: {player_name} ({player_id})",
    "PHONE_LINKING_SUCCESS": "✅ Successfully linked to your player record: {player_name} ({player_id})\n\n🎉 Welcome to the team! You can now use all team features.",
    "PHONE_LINKING_FAILED": "❌ No player record found with that phone number.\n\n💡 What to do:\n1. Make sure you were added by team leadership using /addplayer\n2. Check that the phone number matches what was used when you were added\n3. Contact team leadership if you need help",
    "TEAM_MEMBER_WELCOME": "👋 Welcome to the leadership team, {member_name}!\n\n✅ You have joined the leadership chat.\n\n📋 You can now manage team operations. Try /help to see available commands.",
    "REGULAR_MEMBER_WELCOME_MAIN": "👋 Welcome to the team, {username}!\n\n🤔 I notice you joined without an invite link. Please contact team leadership to get properly registered as a player.",
    "REGULAR_MEMBER_WELCOME_LEADERSHIP": "👋 Welcome to the leadership chat, {username}!\n\n🤔 I notice you joined without an invite link. Please contact the team administrator to get properly registered as a team member.",
    "REGULAR_MEMBER_WELCOME_DEFAULT": "👋 Welcome, {username}!",
    "HELP_RESPONSE": "Help for: {query}\n\nThis is a simplified help response. In production, this would be handled by the CrewAI system.",
    "WELCOME_TEAM": "👋 Welcome to the team!",
    "WELCOME_BACK": "👋 Welcome back, {player_name}!\n\n✅ ACCOUNT LINKED SUCCESSFULLY!\nYour Telegram account is now connected to your player record.\n\n⚽ YOU'RE ALL SET!\n• Your status: ACTIVE \n• Team features: AVAILABLE\n• Ready for team activities!",
    "AUTO_ACTIVATION_WELCOME": "🎉 WELCOME TO THE TEAM, {player_name.upper()}!\n\n✅ AUTO-ACTIVATION SUCCESSFUL!\nYour account has been automatically activated! No manual approval needed.\n\n⚽ YOU'RE READY TO PARTICIPATE!\n• Your status: ACTIVE \n• Team features: UNLOCKED\n• Match selection: AVAILABLE",
    "MAIN_CHAT_GUIDANCE": "\n\n📱 MAIN CHAT FEATURES:\n• `/myinfo` - Check your player status\n• `/list` - See active players for matches\n• `/help` - View all available commands\n• Share availability for upcoming matches\n\n🎯 GET STARTED:\n• Use `/myinfo` to verify your player details\n• Check `/help` for all available commands\n• Stay tuned for match announcements!",
    "LEADERSHIP_CHAT_GUIDANCE": "\n\n👥 LEADERSHIP CHAT ACCESS:\n• `/listmembers` - View full team roster\n• `/addplayer` - Add new players to the team\n• `/announce` - Send team-wide messages\n• Administrative tools and team management\n\n🎯 LEADERSHIP RESPONSIBILITIES:\n• Player management and approvals\n• Team communication coordination\n• Match organization and planning",
    "PRIVATE_CHAT_GUIDANCE": "\n\n💬 PRIVATE CHAT FEATURES:\n• Personal player information\n• Direct communication with team system\n• Private status updates and notifications\n\n🎯 PRIVATE FEATURES:\n• Use `/myinfo` for personal status\n• Private help and support\n• Confidential team communications",
    "KICKAI_FOOTER": "\n\n🤖 KICKAI POWERED TEAM MANAGEMENT\nWelcome to the future of football team organization! \n\nNeed help? Type `/help` anytime! ⚽💪",
    "WELCOME_FALLBACK": "🎉 Welcome to the team, {player_name}!\n\n✅ Your account has been successfully activated! \n\n⚽ You're now ready to participate in all team activities. Type `/help` to see what you can do!",
}
