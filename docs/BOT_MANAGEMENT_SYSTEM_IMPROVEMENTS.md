# Bot Management System Improvements

## Overview

This document describes the improved bot management system that addresses the issues with the original `start_bot_safe.sh` script, including proper process management, logging redirection, and clean restarts.

## Problems with Original Script ❌

### **1. Process Management Issues**
- **Race Conditions:** Insufficient delays between kill and start operations
- **No PID Tracking:** No way to track which process belongs to the bot
- **Incomplete Cleanup:** Old processes not properly terminated
- **No Graceful Shutdown:** Immediate force-kill without graceful termination

### **2. Logging Redirection Problems**
- **Redirection Conflicts:** `tail -f logs/kickai.log` picked up redirection output
- **No Log Management:** No log file rotation or size management
- **Mixed Output:** Console and file output mixed together

### **3. Signal Handling Issues**
- **No Signal Traps:** Script didn't handle SIGINT/SIGTERM properly
- **Orphaned Processes:** Background processes left running
- **No Cleanup:** PID files and temporary files not cleaned up

## Improved Bot Management System ✅

### **New Scripts**

#### **1. `start_bot_safe.sh` - Enhanced Startup Script**
**Features:**
- ✅ **PID File Management:** Tracks bot process with `logs/bot.pid`
- ✅ **Graceful Shutdown:** Sends SIGTERM before SIGKILL
- ✅ **Process Verification:** Checks if processes are actually running
- ✅ **Signal Handling:** Proper SIGINT/SIGTERM handling
- ✅ **Background Execution:** Runs bot in background with proper management
- ✅ **Environment Validation:** Checks venv, .env, and script existence

**Usage:**
```bash
# Start bot with console output
./start_bot_safe.sh

# Start bot with file logging (recommended)
./start_bot_safe.sh > logs/kickai.log 2>&1

# Start bot in background
nohup ./start_bot_safe.sh > logs/kickai.log 2>&1 &
```

#### **2. `stop_bot.sh` - Dedicated Stop Script**
**Features:**
- ✅ **PID File Based:** Uses PID file for targeted stopping
- ✅ **Graceful Shutdown:** Waits for graceful termination
- ✅ **Force Kill Fallback:** SIGKILL if graceful shutdown fails
- ✅ **Process Scanning:** Finds and stops orphaned processes
- ✅ **Cleanup:** Removes PID files and temporary files

**Usage:**
```bash
# Stop bot gracefully
./stop_bot.sh

# Force stop all bot processes
pkill -f run_bot_local.py
```

#### **3. `check_bot_status.sh` - Enhanced Status Checker**
**Features:**
- ✅ **Dual Checking:** Uses both PID file and process scanning
- ✅ **Process Details:** Shows detailed process information
- ✅ **Log File Status:** Shows log file size and recent entries
- ✅ **Helpful Commands:** Provides useful management commands

**Usage:**
```bash
# Check bot status
./check_bot_status.sh

# Monitor logs in real-time
tail -f logs/kickai.log
```

## Configuration Files

### **PID File: `logs/bot.pid`**
- **Purpose:** Tracks the main bot process ID
- **Format:** Single line containing the process ID
- **Location:** `logs/bot.pid`
- **Management:** Automatically created/removed by scripts

### **Log File: `logs/kickai.log`**
- **Purpose:** Main bot log file
- **Location:** `logs/kickai.log`
- **Rotation:** Manual (consider implementing log rotation)
- **Size:** Monitor with `du -h logs/kickai.log`

## Usage Workflow

### **Starting the Bot**
```bash
# 1. Check current status
./check_bot_status.sh

# 2. Start the bot with file logging
./start_bot_safe.sh > logs/kickai.log 2>&1

# 3. Verify the bot started successfully
./check_bot_status.sh

# 4. Monitor logs
tail -f logs/kickai.log
```

### **Stopping the Bot**
```bash
# 1. Stop the bot gracefully
./stop_bot.sh

# 2. Verify the bot stopped
./check_bot_status.sh

# 3. Check for any remaining processes
ps aux | grep run_bot_local
```

### **Restarting the Bot**
```bash
# 1. Stop the bot
./stop_bot.sh

# 2. Wait a moment for cleanup
sleep 2

# 3. Start the bot
./start_bot_safe.sh > logs/kickai.log 2>&1

# 4. Verify restart
./check_bot_status.sh
```

## Troubleshooting

### **Common Issues and Solutions**

#### **1. Bot Won't Start**
```bash
# Check if virtual environment exists
ls -la venv/

# Check if .env file exists
ls -la .env

# Check if run_bot_local.py exists
ls -la run_bot_local.py

# Check for existing processes
./check_bot_status.sh
```

#### **2. Bot Won't Stop**
```bash
# Try graceful stop first
./stop_bot.sh

# Force stop if needed
pkill -f run_bot_local.py

# Check for remaining processes
ps aux | grep run_bot_local
```

#### **3. Log File Issues**
```bash
# Check log file size
du -h logs/kickai.log

# Check log file permissions
ls -la logs/kickai.log

# Clear log file if too large
> logs/kickai.log

# Monitor logs in real-time
tail -f logs/kickai.log
```

#### **4. PID File Issues**
```bash
# Check PID file
cat logs/bot.pid

# Remove stale PID file
rm -f logs/bot.pid

# Check if process is actually running
ps aux | grep $(cat logs/bot.pid 2>/dev/null)
```

### **Debugging Commands**

#### **Process Management**
```bash
# Find all bot processes
ps aux | grep run_bot_local

# Check process tree
pstree -p $(cat logs/bot.pid 2>/dev/null)

# Check process details
ps -p $(cat logs/bot.pid 2>/dev/null) -o pid,ppid,etime,pcpu,pmem,comm
```

#### **Log Analysis**
```bash
# View recent logs
tail -20 logs/kickai.log

# Search for errors
grep -i error logs/kickai.log

# Search for specific patterns
grep "myinfo" logs/kickai.log

# Monitor logs in real-time
tail -f logs/kickai.log | grep -i error
```

## Best Practices

### **1. Always Use File Logging**
```bash
# ✅ Recommended
./start_bot_safe.sh > logs/kickai.log 2>&1

# ❌ Not recommended (console only)
./start_bot_safe.sh
```

### **2. Check Status Before Starting**
```bash
# Always check status first
./check_bot_status.sh

# Only start if not already running
if ! ./check_bot_status.sh | grep -q "RUNNING"; then
    ./start_bot_safe.sh > logs/kickai.log 2>&1
fi
```

### **3. Use Graceful Shutdown**
```bash
# ✅ Recommended
./stop_bot.sh

# ❌ Only use as last resort
pkill -9 -f run_bot_local.py
```

### **4. Monitor Logs Regularly**
```bash
# Monitor in real-time
tail -f logs/kickai.log

# Check for errors
grep -i error logs/kickai.log | tail -10

# Monitor specific commands
tail -f logs/kickai.log | grep -E "(myinfo|list|start)"
```

## Script Configuration

### **Environment Variables**
The scripts use these configuration variables:
```bash
BOT_PID_FILE="logs/bot.pid"
LOG_FILE="logs/kickai.log"
BOT_SCRIPT="run_bot_local.py"
MAX_WAIT_TIME=30  # Maximum time to wait for process termination
```

### **Customization**
You can modify these variables in the scripts:
- **PID File Location:** Change `BOT_PID_FILE` path
- **Log File Location:** Change `LOG_FILE` path
- **Bot Script:** Change `BOT_SCRIPT` to use different startup script
- **Wait Time:** Adjust `MAX_WAIT_TIME` for different environments

## Integration with Development Workflow

### **Development Cycle**
1. **Make Code Changes**
2. **Stop Bot:** `./stop_bot.sh`
3. **Start Bot:** `./start_bot_safe.sh > logs/kickai.log 2>&1`
4. **Monitor:** `tail -f logs/kickai.log`
5. **Test:** Send commands to bot
6. **Repeat:** Go back to step 1

### **Testing Workflow**
```bash
# 1. Start bot
./start_bot_safe.sh > logs/kickai.log 2>&1

# 2. Monitor logs
tail -f logs/kickai.log

# 3. Test commands
# Send /myinfo, /list, /start to bot

# 4. Check for errors
grep -i error logs/kickai.log

# 5. Stop bot
./stop_bot.sh
```

## Conclusion

The improved bot management system provides:

1. **Reliable Process Management:** Proper PID tracking and cleanup
2. **Clean Logging:** No redirection conflicts or mixed output
3. **Graceful Shutdown:** Proper signal handling and cleanup
4. **Easy Monitoring:** Simple status checking and log monitoring
5. **Troubleshooting Tools:** Comprehensive debugging commands

This system resolves the original issues with the `start_bot_safe.sh` script and provides a robust foundation for bot management in development and production environments. 