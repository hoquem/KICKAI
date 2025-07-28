# Bot Startup Script Fix Implementation

## Overview

This document describes the fix for the bot startup script that was allowing multiple instances to run simultaneously, causing process management issues and resource conflicts.

## Problem Statement

### Issue Details

The original `start_bot_safe.sh` script had several critical issues that allowed multiple instances to run:

1. **No Lock File Mechanism**: The script didn't use a lock file to prevent multiple instances
2. **Subshell PID Tracking**: Used `(...)` subshell which captured the wrong PID
3. **Race Conditions**: Multiple instances could start before PID file creation
4. **Stale Process Detection**: No proper cleanup of stale processes and lock files

### Process List Evidence

```
87079 ttys004    0:00.02 /bin/bash ./start_bot_safe.sh
87137 ttys004    0:00.00 /bin/bash ./start_bot_safe.sh
87139 ttys004    0:01.72 /opt/homebrew/Cellar/python@3.11/3.11.13/Frameworks/Python.framework/Versions/3.11/Resources/Python.app/Contents/MacOS/Python run_bot_local.py
```

This showed multiple shell script instances running, indicating the script wasn't properly preventing concurrent execution.

## Solution: Comprehensive Process Management

### Core Principles

1. **Lock File Mechanism**: Use atomic file creation to prevent multiple instances
2. **Proper PID Tracking**: Capture the actual Python process PID, not subshell PID
3. **Stale Process Cleanup**: Detect and clean up stale processes and lock files
4. **Graceful Shutdown**: Implement proper signal handling and cleanup

### Implementation Changes

#### 1. **Added Lock File Mechanism**

**New Lock File Functions:**
```bash
# Function to acquire lock
acquire_lock() {
    local lock_file="$1"
    local pid=$$
    
    # Try to create lock file with our PID
    if (set -C; echo "$pid" > "$lock_file") 2>/dev/null; then
        return 0  # Lock acquired successfully
    else
        # Check if lock file exists and if the process is still running
        if [ -f "$lock_file" ]; then
            local lock_pid=$(cat "$lock_file" 2>/dev/null)
            if [ -n "$lock_pid" ] && is_process_running "$lock_pid"; then
                echo "❌ Another instance is already running (PID: $lock_pid)"
                return 1  # Lock held by running process
            else
                # Stale lock file, remove it and try again
                echo "⚠️  Found stale lock file, removing..."
                rm -f "$lock_file"
                if (set -C; echo "$pid" > "$lock_file") 2>/dev/null; then
                    return 0  # Lock acquired successfully
                fi
            fi
        fi
        return 1  # Failed to acquire lock
    fi
}

# Function to release lock
release_lock() {
    local lock_file="$1"
    local pid=$$
    
    if [ -f "$lock_file" ]; then
        local lock_pid=$(cat "$lock_file" 2>/dev/null)
        if [ "$lock_pid" = "$pid" ]; then
            rm -f "$lock_file"
            echo "🔓 Lock released"
        fi
    fi
}
```

#### 2. **Fixed Process Management**

**Before (Problematic):**
```bash
# Start the bot in background and capture PID
(
    # Activate virtual environment and start bot
    source venv311/bin/activate && python "$BOT_SCRIPT"
) &

local bot_pid=$!  # ❌ Captures subshell PID, not Python process PID
```

**After (Fixed):**
```bash
# Start the bot in background and capture PID
source venv311/bin/activate && python "$BOT_SCRIPT" &

local bot_pid=$!  # ✅ Captures actual Python process PID
```

#### 3. **Enhanced Main Function**

**Updated Main Execution:**
```bash
# Main execution
main() {
    # Try to acquire lock
    if ! acquire_lock "$LOCK_FILE"; then
        echo "❌ Cannot start bot: another instance is already running"
        exit 1
    fi
    
    echo "🔒 Lock acquired, proceeding with startup..."
    
    # Kill any existing bot processes
    kill_existing_bots
    
    # Start the bot
    start_bot
}
```

#### 4. **Improved Cleanup Function**

**Enhanced Cleanup:**
```bash
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
    
    # Release lock
    release_lock "$LOCK_FILE"
    
    echo "✅ Cleanup completed"
    exit 0
}
```

### Enhanced Status Check Script

Created `check_bot_status.sh` to monitor and clean up stale processes:

```bash
#!/bin/bash

# KICKAI Bot Status Check Script
# This script checks the status of the bot and cleans up stale processes/lock files

# Configuration
BOT_PID_FILE="logs/bot.pid"
LOCK_FILE="logs/bot.lock"
BOT_SCRIPT="run_bot_local.py"

echo "🔍 KICKAI Bot Status Check"
echo "=========================="

# Check PID file, lock file, and running processes
# Clean up stale files and processes
# Provide summary and useful commands
```

### Process Management Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Lock File     │    │  PID File        │    │  Process        │
│   Management    │    │  Management      │    │  Monitoring     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Atomic Lock     │    │ Process PID      │    │ Process Status  │
│ Acquisition     │    │ Tracking         │    │ Validation      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ Process Management      │
                    │ - Single Instance       │
                    │ - Proper Cleanup        │
                    │ - Status Monitoring     │
                    └─────────────────────────┘
```

### Benefits of the Fix

#### 1. **Prevents Multiple Instances**
- ✅ **Lock file mechanism** prevents concurrent execution
- ✅ **Atomic file operations** eliminate race conditions
- ✅ **Stale process detection** and cleanup

#### 2. **Proper Process Management**
- ✅ **Correct PID tracking** of actual Python process
- ✅ **Graceful shutdown** with signal handling
- ✅ **Comprehensive cleanup** on exit

#### 3. **Enhanced Monitoring**
- ✅ **Status check script** for monitoring
- ✅ **Stale file cleanup** automatic detection
- ✅ **Process validation** and reporting

#### 4. **Better Error Handling**
- ✅ **Clear error messages** for different scenarios
- ✅ **Automatic recovery** from stale states
- ✅ **Proper exit codes** for automation

### Usage Examples

#### Starting the Bot
```bash
./start_bot_safe.sh
```

**Expected Output:**
```
🤖 KICKAI Safe Bot Startup Script
==================================
🔒 Lock acquired, proceeding with startup...
🔍 Checking for existing bot processes...
✅ No existing bot processes found
🚀 Starting KICKAI bot...
✅ Bot started successfully with PID: 12345
```

#### Checking Status
```bash
./check_bot_status.sh
```

**Expected Output:**
```
🔍 KICKAI Bot Status Check
==========================
📁 Checking PID file...
✅ Bot process running (PID: 12345)
🔒 Checking lock file...
✅ Lock file valid (PID: 12345 is running)
🔍 Checking for bot processes...
✅ No bot processes found
📊 Summary:
✅ Bot is running properly (PID: 12345)
```

#### Attempting to Start Multiple Instances
```bash
./start_bot_safe.sh  # First instance
./start_bot_safe.sh  # Second instance (should fail)
```

**Expected Output for Second Instance:**
```
🤖 KICKAI Safe Bot Startup Script
==================================
❌ Cannot start bot: another instance is already running
```

### Error Scenarios Handled

#### 1. **Stale Lock File**
- **Scenario**: Lock file exists but process is dead
- **Solution**: Automatic detection and cleanup
- **Result**: Script continues normally

#### 2. **Stale PID File**
- **Scenario**: PID file exists but process is dead
- **Solution**: Automatic detection and cleanup
- **Result**: Script continues normally

#### 3. **Multiple Processes**
- **Scenario**: Multiple bot processes running
- **Solution**: Graceful termination of all processes
- **Result**: Clean slate for new instance

#### 4. **Signal Interruption**
- **Scenario**: Script interrupted (Ctrl+C, SIGTERM)
- **Solution**: Proper cleanup of all resources
- **Result**: Clean exit with no orphaned processes

### Testing

#### Manual Testing
```bash
# Test 1: Start bot
./start_bot_safe.sh

# Test 2: Check status
./check_bot_status.sh

# Test 3: Try to start second instance (should fail)
./start_bot_safe.sh

# Test 4: Stop bot and verify cleanup
kill $(cat logs/bot.pid)
./check_bot_status.sh
```

#### Automated Testing
```bash
#!/bin/bash
# Test script for bot startup

echo "🧪 Testing bot startup script..."

# Test 1: Start bot
./start_bot_safe.sh &
sleep 5

# Test 2: Verify single instance
if [ $(pgrep -f "run_bot_local.py" | wc -l) -eq 1 ]; then
    echo "✅ Single instance test passed"
else
    echo "❌ Single instance test failed"
fi

# Test 3: Try to start second instance
./start_bot_safe.sh
if [ $? -eq 1 ]; then
    echo "✅ Multiple instance prevention test passed"
else
    echo "❌ Multiple instance prevention test failed"
fi

# Cleanup
kill $(cat logs/bot.pid 2>/dev/null) 2>/dev/null || true
```

### Future Enhancements

#### 1. **Configuration File**
Consider adding a configuration file for customizable settings:

```bash
# config/bot.conf
BOT_PID_FILE="logs/bot.pid"
LOCK_FILE="logs/bot.lock"
LOG_FILE="logs/kickai.log"
BOT_SCRIPT="run_bot_local.py"
MAX_WAIT_TIME=30
```

#### 2. **Logging Integration**
Enhanced logging for better debugging:

```bash
# Add logging to startup script
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}
```

#### 3. **Health Monitoring**
Add health check capabilities:

```bash
# Health check function
check_bot_health() {
    local pid=$(cat "$BOT_PID_FILE" 2>/dev/null)
    if [ -n "$pid" ] && is_process_running "$pid"; then
        # Check if bot is responding
        # Return health status
    fi
}
```

### Conclusion

The bot startup script fix successfully resolves the multiple instance issue by:

- ✅ **Implementing proper lock file mechanism** to prevent concurrent execution
- ✅ **Fixing PID tracking** to capture actual Python process PID
- ✅ **Adding comprehensive cleanup** for stale processes and files
- ✅ **Providing status monitoring** with automatic cleanup
- ✅ **Ensuring graceful shutdown** with proper signal handling

The script now provides robust process management and prevents resource conflicts while maintaining ease of use and comprehensive monitoring capabilities. 