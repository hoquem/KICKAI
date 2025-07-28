# Bot Startup Rules & Implementation

## 🚀 Ground Rules

### **Bot Startup Rules:**
1. **Always use `run_bot_local.py`** to start the bot locally
2. **Set `PYTHONPATH=src`** for all bot operations
3. **Improve `run_bot_local.py`** to:
   - Check for running bot instances
   - Kill existing instances before starting new ones
   - Prevent multiple bot conflicts
4. **Always use `.env` file** for local development
5. **Never modify `.env` directly** without explicit confirmation
6. **Always log to both console and `logs/kickai.log`** for local development

## 🔧 Implementation Details

### **Process Management Features**

#### **Process Detection**
- **Function:** `find_existing_bot_processes()`
- **Purpose:** Scans for existing Python processes running `run_bot_local.py`
- **Detection:** Looks for processes with `run_bot_local.py` in command line
- **Safety:** Excludes current process from detection

#### **Graceful Process Termination**
- **Function:** `kill_process_gracefully(process, timeout=10)`
- **Strategy:** 
  1. Send SIGTERM (graceful termination)
  2. Wait up to 10 seconds for graceful shutdown
  3. Force kill with SIGKILL if needed
- **Logging:** Detailed logging of termination attempts

#### **Lock File Mechanism**
- **File:** `bot.lock` in project root
- **Content:** Current process PID
- **Purpose:** Prevent multiple bot instances
- **Cleanup:** Automatic removal on shutdown

#### **Startup Sequence**
1. **Environment Setup**
   - Set `PYTHONPATH=src` if not already set
   - Load `.env` file
   - Initialize logging (console + file)

2. **Process Cleanup**
   - Check for existing lock file
   - Detect and kill conflicting processes
   - Create new lock file

3. **System Validation**
   - Run comprehensive health checks
   - Validate LLM connectivity
   - Check bot configurations

4. **Bot Startup**
   - Initialize multi-bot manager
   - Start all configured bots
   - Begin LLM health monitoring

### **Error Handling**

#### **Conflict Resolution**
- **Telegram Conflict Error:** `Conflict: terminated by other getUpdates request`
- **Solution:** Process management prevents multiple instances
- **Fallback:** Force kill if graceful termination fails

#### **Lock File Scenarios**
- **Stale Lock:** Remove if process no longer exists
- **Invalid Lock:** Clean up corrupted lock files
- **Permission Issues:** Log warnings, continue if possible

## 📁 File Structure

```
KICKAI/
├── run_bot_local.py          # Main bot startup script
├── start_bot.sh              # Convenience startup script
├── test_process_management.py # Process management tests
├── bot.lock                  # Lock file (created at runtime)
├── .env                      # Environment configuration
└── docs/
    └── BOT_STARTUP_RULES.md  # This documentation
```

## 🧪 Testing

### **Process Management Test**
```bash
# Run the test script
python test_process_management.py
```

**Test Coverage:**
- ✅ psutil functionality
- ✅ Lock file creation/removal
- ✅ Process detection
- ✅ Graceful termination simulation

### **Manual Testing**
```bash
# Start bot with process management
./start_bot.sh

# Or directly
source venv311/bin/activate
export PYTHONPATH=src
python run_bot_local.py
```

## 🔍 Monitoring

### **Log Messages**
- `🔍 Checking for existing bot instances...`
- `⚠️ Found existing bot lock file`
- `🛑 Attempting to kill process {pid} gracefully...`
- `🔒 Created lock file: bot.lock`
- `🔧 Process ID: {pid}`
- `🔧 PYTHONPATH: {path}`
- `📝 Logging configured for local development`
- `📄 Console output: INFO level and above`
- `📁 File output: logs/kickai.log (DEBUG level and above)`

### **Status Indicators**
- `✅` Success operations
- `⚠️` Warnings (non-critical)
- `❌` Errors (critical)
- `🔍` Information/scanning
- `🛑` Termination operations
- `🔒` Lock file operations

## 🚨 Troubleshooting

### **Common Issues**

#### **Multiple Bot Instances**
```bash
# Check for running processes
ps aux | grep run_bot_local.py

# Kill manually if needed
pkill -f run_bot_local.py
```

#### **Stale Lock File**
```bash
# Remove stale lock file
rm bot.lock
```

#### **Permission Issues**
```bash
# Check file permissions
ls -la run_bot_local.py
chmod +x run_bot_local.py
```

### **Environment Issues**
```bash
# Verify PYTHONPATH
echo $PYTHONPATH

# Set manually if needed
export PYTHONPATH=src
```

## 📋 Dependencies

### **Required Packages**
```txt
psutil==6.1.0          # Process management
python-dotenv==1.0.0   # Environment loading
```

### **Installation**
```bash
# Install dependencies
pip install -r requirements-local.txt
```

## 🔄 Future Enhancements

### **Potential Improvements**
1. **Process Monitoring Dashboard**
   - Real-time status of bot processes
   - Health metrics and alerts

2. **Automatic Recovery**
   - Restart failed bot instances
   - Self-healing mechanisms

3. **Configuration Validation**
   - Pre-flight checks for bot configuration
   - Environment validation

4. **Performance Optimization**
   - Resource usage monitoring
   - Memory leak detection

## 📞 Support

For issues with bot startup:
1. Check this documentation
2. Run `test_process_management.py`
3. Review logs in `logs/kickai.log`
4. Check for conflicting processes
5. Verify `.env` configuration 