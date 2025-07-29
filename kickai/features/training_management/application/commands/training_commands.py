#!/usr/bin/env python3
"""
Training Management Commands

This module registers all training management related commands with the command registry.
Each feature maintains its own command definitions for clean separation.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command
from kickai.core.enums import ChatType

# ============================================================================
# TRAINING MANAGEMENT COMMANDS
# ============================================================================


@command(
    name="/scheduletraining",
    description="Schedule a training session (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="training_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/scheduletraining", "/scheduletraining Technical 2024-01-15 18:00 90"],
    parameters={
        "session_type": "Training session type (Technical, Tactical, Fitness, Match Practice, Recovery)",
        "date": "Training date (YYYY-MM-DD)",
        "time": "Training time (HH:MM)",
        "duration": "Duration in minutes",
        "location": "Training location",
        "focus_areas": "Focus areas (e.g., Passing, Shooting, Fitness)",
    },
    help_text="""
⚽ Schedule Training (Leadership Only)

Schedule a new training session for the team.

Usage:
• /scheduletraining - Start training scheduling process
• /scheduletraining [type] [date] [time] [duration] [location] [focus] - Schedule with details

Session Types:
• Technical - Skills training (passing, shooting, dribbling)
• Tactical - Game understanding and positioning
• Fitness - Conditioning and strength training
• Match Practice - Small-sided games and match scenarios
• Recovery - Light training and recovery sessions

Examples:
/scheduletraining Technical 2024-01-15 18:00 90 "Main Pitch" "Passing, Shooting"
/scheduletraining Fitness 2024-01-17 19:00 60 "Gym" "Strength, Endurance"
/scheduletraining Match Practice 2024-01-20 14:00 120 "Training Ground" "Small-sided games"

What happens:
1. New training session is created
2. Session is announced to all players
3. Attendance tracking is enabled
4. Players can mark their availability

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_scheduletraining_command(update, context, **kwargs):
    """Handle /scheduletraining command."""
    # This will be handled by the agent system
    return None


@command(
    name="/listtrainings",
    description="List upcoming training sessions",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="training_management",
    chat_type=ChatType.MAIN,
    examples=["/listtrainings", "/listtrainings this week", "/listtrainings today"],
    parameters={
        "period": "Optional time period (today, this week, next week, all)",
    },
    help_text="""
📅 List Training Sessions

View upcoming training sessions for the team.

Usage:
• /listtrainings - Show all upcoming training sessions
• /listtrainings today - Show today's training sessions
• /listtrainings this week - Show this week's training sessions
• /listtrainings next week - Show next week's training sessions
• /listtrainings all - Show all training sessions (including past)

What you'll see:
• Training session details (type, date, time, location)
• Focus areas for each session
• Session status (scheduled, in progress, completed)
• Your attendance status for each session

💡 Tip: Use this to plan your training schedule and mark attendance early.
    """,
)
async def handle_listtrainings_command(update, context, **kwargs):
    """Handle /listtrainings command."""
    # This will be handled by the agent system
    return None


@command(
    name="/marktraining",
    description="Mark attendance for a training session",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="training_management",
    chat_type=ChatType.MAIN,
    examples=["/marktraining", "/marktraining yes", "/marktraining no TRAIN123"],
    parameters={
        "status": "Attendance status (yes, no, maybe)",
        "training_id": "Optional training session ID",
    },
    help_text="""
✅ Mark Training Attendance

Mark your attendance for an upcoming training session.

Usage:
• /marktraining - Start attendance marking process
• /marktraining yes - Confirm attendance for next training
• /marktraining no - Decline attendance for next training
• /marktraining maybe - Mark as tentative for next training
• /marktraining yes TRAIN123 - Mark attendance for specific session

Attendance Options:
• ✅ Yes - Confirmed attendance
• ❌ No - Cannot attend
• ❔ Maybe - Tentative (will confirm later)

What happens:
1. Your attendance is recorded
2. Team leadership is notified
3. You receive confirmation
4. Training planning is updated

💡 Tip: Mark attendance early to help with training planning and equipment setup.
    """,
)
async def handle_marktraining_command(update, context, **kwargs):
    """Handle /marktraining command."""
    # This will be handled by the agent system
    return None


@command(
    name="/canceltraining",
    description="Cancel a training session (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="training_management",
    chat_type=ChatType.LEADERSHIP,
    examples=["/canceltraining", "/canceltraining TRAIN123", "/canceltraining TRAIN123 Bad weather"],
    parameters={
        "training_id": "Training session ID to cancel",
        "reason": "Optional reason for cancellation",
    },
    help_text="""
❌ Cancel Training Session (Leadership Only)

Cancel a scheduled training session.

Usage:
• /canceltraining - Start cancellation process
• /canceltraining TRAIN123 - Cancel specific training session
• /canceltraining TRAIN123 [reason] - Cancel with reason

Examples:
/canceltraining TRAIN123
/canceltraining TRAIN123 Bad weather conditions
/canceltraining TRAIN123 Pitch unavailable

What happens:
1. Training session is marked as cancelled
2. All players are notified of cancellation
3. Attendance tracking is disabled
4. Reason is recorded for future reference

💡 Note: This command is only available in the leadership chat.
    """,
)
async def handle_canceltraining_command(update, context, **kwargs):
    """Handle /canceltraining command."""
    # This will be handled by the agent system
    return None


@command(
    name="/trainingstats",
    description="Show training statistics and attendance",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="training_management",
    chat_type=ChatType.MAIN,
    examples=["/trainingstats", "/trainingstats this month", "/trainingstats TRAIN123"],
    parameters={
        "period": "Optional time period (this week, this month, all)",
        "training_id": "Optional specific training session ID",
    },
    help_text="""
📊 Training Statistics

View training statistics and attendance information.

Usage:
• /trainingstats - Show your personal training statistics
• /trainingstats this week - Show this week's training stats
• /trainingstats this month - Show this month's training stats
• /trainingstats TRAIN123 - Show stats for specific training session

What you'll see:
• Your attendance rate and history
• Upcoming training sessions
• Training session details and focus areas
• Team attendance summary (if leadership)

Personal Stats:
• Total training sessions attended
• Attendance percentage
• Recent training history
• Upcoming training schedule

💡 Tip: Use this to track your training commitment and plan your schedule.
    """,
)
async def handle_trainingstats_command(update, context, **kwargs):
    """Handle /trainingstats command."""
    # This will be handled by the agent system
    return None


@command(
    name="/mytrainings",
    description="Show my training schedule and history",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.PLAYER,
    feature="training_management",
    chat_type=ChatType.MAIN,
    examples=["/mytrainings", "/mytrainings upcoming", "/mytrainings history"],
    parameters={
        "view": "Optional view type (upcoming, history, all)",
    },
    help_text="""
🏃‍♂️ My Training Schedule

View your personal training schedule and history.

Usage:
• /mytrainings - Show your training overview
• /mytrainings upcoming - Show upcoming training sessions
• /mytrainings history - Show past training sessions
• /mytrainings all - Show all training sessions

What you'll see:
• Upcoming training sessions you're confirmed for
• Training sessions you need to respond to
• Your training attendance history
• Training session details and focus areas

Personal Overview:
• Next training session details
• Your attendance status for upcoming sessions
• Recent training history and attendance
• Training commitment statistics

💡 Tip: Use this to stay organized with your training schedule and track your progress.
    """,
)
async def handle_mytrainings_command(update, context, **kwargs):
    """Handle /mytrainings command."""
    # This will be handled by the agent system
    return None 