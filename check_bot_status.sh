#!/bin/bash

# KICKAI Bot Status Checker
echo "🤖 KICKAI Bot Status Checker"
echo "============================"

# Check for running bot processes
PIDS=$(ps aux | grep python | grep run_bot_local | grep -v grep | awk '{print $2}')

if [ -n "$PIDS" ]; then
    echo "✅ Bot is RUNNING"
    echo "📊 Process IDs: $PIDS"
    echo ""
    echo "📝 Recent logs:"
    echo "==============="
    tail -10 kickai_nlp_test.log 2>/dev/null || echo "No log file found"
else
    echo "❌ Bot is NOT RUNNING"
    echo ""
    echo "💡 To start the bot, run: ./start_bot_safe.sh"
fi

echo ""
echo "🔍 To monitor logs in real-time, run: tail -f kickai_nlp_test.log" 