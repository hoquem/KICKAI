#!/bin/bash

# KICKAI Bot Stop Script
# This script safely stops the bot using PID file and process management

BOT_PID_FILE="logs/bot.pid"
BOT_SCRIPT="run_bot_local.py"
MAX_WAIT_TIME=30  # Maximum time to wait for process termination

echo "🛑 KICKAI Bot Stop Script"
echo "========================="

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

# Stop bot using PID file
if [ -f "$BOT_PID_FILE" ]; then
    PID=$(cat "$BOT_PID_FILE" 2>/dev/null)
    if [ -n "$PID" ]; then
        if is_process_running "$PID"; then
            echo "🛑 Stopping bot process $PID..."
            
            # Send SIGTERM for graceful shutdown
            kill "$PID" 2>/dev/null || true
            
            # Wait for graceful shutdown
            local wait_count=0
            while [ $wait_count -lt $MAX_WAIT_TIME ]; do
                if ! is_process_running "$PID"; then
                    echo "✅ Bot stopped gracefully"
                    break
                fi
                echo "   Waiting for graceful shutdown... ($((MAX_WAIT_TIME - wait_count))s remaining)"
                sleep 1
                wait_count=$((wait_count + 1))
            done
            
            # Force kill if still running
            if is_process_running "$PID"; then
                echo "⚠️  Force killing bot process $PID..."
                kill -9 "$PID" 2>/dev/null || true
                sleep 2
                
                if is_process_running "$PID"; then
                    echo "❌ Failed to stop bot process $PID"
                else
                    echo "✅ Bot force stopped"
                fi
            fi
        else
            echo "⚠️  PID file exists but process $PID is not running"
        fi
        
        # Remove PID file
        rm -f "$BOT_PID_FILE"
        echo "🧹 PID file removed"
    else
        echo "⚠️  PID file exists but is empty"
        rm -f "$BOT_PID_FILE"
    fi
else
    echo "📁 No PID file found: $BOT_PID_FILE"
fi

# Check for any remaining bot processes
PIDS=$(get_bot_pids)
if [ -n "$PIDS" ]; then
    echo "⚠️  Found remaining bot processes: $PIDS"
    echo "🛑 Stopping remaining processes..."
    
    for PID in $PIDS; do
        if is_process_running "$PID"; then
            echo "   Stopping process $PID..."
            kill "$PID" 2>/dev/null || true
            sleep 1
            
            if is_process_running "$PID"; then
                echo "   Force killing process $PID..."
                kill -9 "$PID" 2>/dev/null || true
            fi
        fi
    done
    
    sleep 2
    
    # Final check
    FINAL_PIDS=$(get_bot_pids)
    if [ -n "$FINAL_PIDS" ]; then
        echo "❌ Warning: Some processes may still be running: $FINAL_PIDS"
    else
        echo "✅ All bot processes stopped"
    fi
else
    echo "✅ No bot processes found"
fi

echo ""
echo "✅ Bot stop operation completed" 