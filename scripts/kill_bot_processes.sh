#!/bin/bash

# KICKAI Bot Process Killer
# This script kills all bot-related processes

echo "🔍 Searching for KICKAI bot processes..."

# Find and kill bot processes
BOT_PROCESSES=$(ps aux | grep -E "(run_telegram_bot|railway_main|railway_web|7693359073)" | grep -v grep | awk '{print $2}')

if [ -z "$BOT_PROCESSES" ]; then
    echo "✅ No bot processes found running"
else
    echo "🚨 Found bot processes: $BOT_PROCESSES"
    echo "💀 Killing bot processes..."
    
    for pid in $BOT_PROCESSES; do
        echo "   Killing process $pid..."
        kill -9 $pid 2>/dev/null
    done
    
    echo "✅ Bot processes killed"
fi

# Check for any remaining processes
REMAINING=$(ps aux | grep -E "(run_telegram_bot|railway_main|railway_web|7693359073)" | grep -v grep)

if [ -z "$REMAINING" ]; then
    echo "✅ All bot processes successfully terminated"
else
    echo "⚠️  Some processes may still be running:"
    echo "$REMAINING"
fi

echo "🎯 Bot process cleanup complete!" 