#!/bin/bash

# KICKAI Bot Status Check Script
# This script checks the status of the bot and cleans up stale processes/lock files

set -e

# Configuration
BOT_PID_FILE="logs/bot.pid"
LOCK_FILE="logs/bot.lock"
BOT_SCRIPT="run_bot_local.py"

echo "🔍 KICKAI Bot Status Check"
echo "=========================="

# Function to check if a process is running
is_process_running() {
    local pid=$1
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0  # Process is running
    else
        return 1  # Process is not running
    fi
}

# Function to get bot process IDs
get_bot_pids() {
    ps aux | grep python | grep "$BOT_SCRIPT" | grep -v grep | awk '{print $2}' | tr '\n' ' '
}

# Check PID file
echo "📁 Checking PID file..."
if [ -f "$BOT_PID_FILE" ]; then
    pid=$(cat "$BOT_PID_FILE" 2>/dev/null)
    if [ -n "$pid" ]; then
        if is_process_running "$pid"; then
            echo "✅ Bot process running (PID: $pid)"
        else
            echo "⚠️  Stale PID file found (PID: $pid not running)"
            echo "🧹 Cleaning up stale PID file..."
            rm -f "$BOT_PID_FILE"
        fi
    else
        echo "⚠️  PID file exists but is empty"
        echo "🧹 Cleaning up empty PID file..."
        rm -f "$BOT_PID_FILE"
    fi
else
    echo "ℹ️  No PID file found"
fi

# Check lock file
echo ""
echo "🔒 Checking lock file..."
if [ -f "$LOCK_FILE" ]; then
    lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ -n "$lock_pid" ]; then
        if is_process_running "$lock_pid"; then
            echo "✅ Lock file valid (PID: $lock_pid is running)"
        else
            echo "⚠️  Stale lock file found (PID: $lock_pid not running)"
            echo "🧹 Cleaning up stale lock file..."
            rm -f "$LOCK_FILE"
        fi
    else
        echo "⚠️  Lock file exists but is empty"
        echo "🧹 Cleaning up empty lock file..."
        rm -f "$LOCK_FILE"
    fi
else
    echo "ℹ️  No lock file found"
fi

# Check for any bot processes
echo ""
echo "🔍 Checking for bot processes..."
pids=$(get_bot_pids)
if [ -n "$pids" ]; then
    echo "⚠️  Found bot processes: $pids"
    for pid in $pids; do
        if is_process_running "$pid"; then
            echo "   ✅ Process $pid is running"
        else
            echo "   ❌ Process $pid is not running (zombie?)"
        fi
    done
else
    echo "✅ No bot processes found"
fi

# Summary
echo ""
echo "📊 Summary:"
if [ -f "$BOT_PID_FILE" ] && [ -f "$LOCK_FILE" ]; then
    pid=$(cat "$BOT_PID_FILE" 2>/dev/null)
    lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ "$pid" = "$lock_pid" ] && is_process_running "$pid"; then
        echo "✅ Bot is running properly (PID: $pid)"
    else
        echo "⚠️  Bot status unclear - check logs for details"
    fi
else
    echo "ℹ️  Bot is not running"
fi

echo ""
echo "💡 Commands:"
echo "   Start bot: ./start_bot_safe.sh"
echo "   Monitor logs: tail -f logs/kickai.log"
echo "   Stop bot: kill \$(cat logs/bot.pid)" 