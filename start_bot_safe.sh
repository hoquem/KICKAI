#!/bin/bash

# KICKAI Safe Bot Startup Script
# This script ensures only one bot instance is running at a time
# with proper process management and logging

set -e  # Exit on any error

# Configuration
BOT_PID_FILE="logs/bot.pid"
LOG_FILE="logs/kickai.log"
BOT_SCRIPT="run_bot_local.py"
MAX_WAIT_TIME=30  # Maximum time to wait for process termination

echo "🤖 KICKAI Safe Bot Startup Script"
echo "=================================="

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

# Function to kill existing bot processes with proper cleanup
kill_existing_bots() {
    echo "🔍 Checking for existing bot processes..."
    
    # Get existing PIDs
    local PIDS=$(get_bot_pids)
    
    if [ -n "$PIDS" ]; then
        echo "⚠️  Found existing bot processes: $PIDS"
        echo "🛑 Initiating graceful shutdown..."
        
        # Send SIGTERM to all processes
        for PID in $PIDS; do
            if is_process_running "$PID"; then
                echo "   Sending SIGTERM to process $PID..."
                kill "$PID" 2>/dev/null || true
            fi
        done
        
        # Wait for graceful shutdown
        local wait_count=0
        while [ $wait_count -lt $MAX_WAIT_TIME ]; do
            local remaining_pids=$(get_bot_pids)
            if [ -z "$remaining_pids" ]; then
                echo "✅ All bot processes terminated gracefully"
                break
            fi
            echo "   Waiting for processes to terminate... ($((MAX_WAIT_TIME - wait_count))s remaining)"
            sleep 1
            wait_count=$((wait_count + 1))
        done
        
        # Force kill remaining processes
        local remaining_pids=$(get_bot_pids)
        if [ -n "$remaining_pids" ]; then
            echo "⚠️  Force killing remaining processes: $remaining_pids"
            for PID in $remaining_pids; do
                if is_process_running "$PID"; then
                    echo "   Force killing process $PID..."
                    kill -9 "$PID" 2>/dev/null || true
                fi
            done
            sleep 2
        fi
        
        # Final check
        local final_pids=$(get_bot_pids)
        if [ -n "$final_pids" ]; then
            echo "❌ Warning: Some processes may still be running: $final_pids"
        else
            echo "✅ All existing bot processes terminated"
        fi
    else
        echo "✅ No existing bot processes found"
    fi
    
    # Clean up PID file if it exists
    if [ -f "$BOT_PID_FILE" ]; then
        local old_pid=$(cat "$BOT_PID_FILE" 2>/dev/null)
        if [ -n "$old_pid" ] && ! is_process_running "$old_pid"; then
            echo "🧹 Cleaning up stale PID file"
            rm -f "$BOT_PID_FILE"
        fi
    fi
}

# Function to start the bot
start_bot() {
    echo "🚀 Starting KICKAI bot..."
    
    # Ensure logs directory exists
    mkdir -p logs
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Please run: python -m venv venv"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo "❌ .env file not found. Please create .env file with your configuration."
        exit 1
    fi
    
    # Check if bot script exists
    if [ ! -f "$BOT_SCRIPT" ]; then
        echo "❌ $BOT_SCRIPT not found in current directory."
        exit 1
    fi
    
    echo "📝 Starting bot with proper process management..."
    echo "=================================="
    
    # Start the bot in background and capture PID
    # Use nohup to detach the process completely
    nohup bash -c "source venv/bin/activate && python $BOT_SCRIPT" > "$LOG_FILE" 2>&1 &
    
    local bot_pid=$!
    echo "$bot_pid" > "$BOT_PID_FILE"
    
    # Wait a moment to see if the process starts successfully
    sleep 3
    
    # Verify the process is still running
    if is_process_running "$bot_pid"; then
        echo "✅ Bot started successfully with PID: $bot_pid"
        echo "📁 PID saved to: $BOT_PID_FILE"
        echo "📝 Logs will be written to: $LOG_FILE"
        echo ""
        echo "💡 Useful commands:"
        echo "   Check status: ./check_bot_status.sh"
        echo "   Monitor logs: tail -f $LOG_FILE"
        echo "   Stop bot: kill \$(cat $BOT_PID_FILE)"
        echo ""
        echo "🤖 Bot is now running in the background (detached)..."
        echo "📊 Use './check_bot_status.sh' to check if it's still running"
        
        # Exit immediately - the bot process is now detached
        return 0
    else
        echo "❌ Bot failed to start or crashed immediately"
        rm -f "$BOT_PID_FILE"
        exit 1
    fi
}

# Function to handle script termination
cleanup() {
    echo ""
    echo "🛑 Shutdown signal received, cleaning up..."
    
    # Remove PID file
    if [ -f "$BOT_PID_FILE" ]; then
        local pid=$(cat "$BOT_PID_FILE" 2>/dev/null)
        if [ -n "$pid" ] && is_process_running "$pid"; then
            echo "🛑 Terminating bot process $pid..."
            kill "$pid" 2>/dev/null || true
            sleep 2
            if is_process_running "$pid"; then
                echo "⚠️  Force killing bot process $pid..."
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$BOT_PID_FILE"
    fi
    
    echo "✅ Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    # Kill any existing bot processes
    kill_existing_bots
    
    # Start the bot
    start_bot
    
    # Exit the script after starting the bot
    echo "✅ Startup script completed successfully"
    exit 0
}

# Run main function
main 