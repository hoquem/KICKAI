# KICKAI Hosting Investigation & Implementation Plan

## 🎯 Objective
Deploy KICKAI to a reliable, free hosting platform with comprehensive monitoring for testing and production environments.

## 📋 Requirements

### Core Requirements
- **Free tier hosting** for initial deployment
- **Two environments**: Testing and Production
- **24/7 uptime** for Telegram bot polling
- **Database persistence** (Supabase already handles this)
- **Environment variable management**
- **Logging and monitoring**
- **AI response quality monitoring**
- **Easy deployment and rollback**

### Technical Requirements
- **Python 3.9+** support
- **Background process** support (for bot polling)
- **HTTPS** support for webhooks (future)
- **Environment isolation**
- **Resource monitoring** (CPU, memory, disk)
- **Error tracking and alerting**

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   KICKAI Bot    │    │   Supabase      │
│   API           │◄──►│   (Hosted)      │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Monitoring    │
                       │   & Logging     │
                       └─────────────────┘
```

## 🚀 Hosting Options Analysis

### 1. Railway (Recommended)
**Pros:**
- Free tier: $5/month credit (sufficient for testing)
- Easy deployment from GitHub
- Built-in environment variables
- Automatic HTTPS
- Good Python support
- Background process support
- Built-in logging

**Cons:**
- Limited free tier
- No custom domain on free tier

**Setup:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 2. Render
**Pros:**
- Free tier available
- Easy GitHub integration
- Environment variables
- Automatic HTTPS
- Good documentation

**Cons:**
- Free tier has limitations
- Sleep after inactivity (not ideal for bot)

### 3. Heroku
**Pros:**
- Excellent Python support
- Great ecosystem
- Good monitoring

**Cons:**
- No free tier anymore
- Expensive for small projects

### 4. DigitalOcean App Platform
**Pros:**
- Good performance
- Easy scaling
- Good monitoring

**Cons:**
- No free tier
- More complex setup

## 🎯 Recommended Solution: Railway

### Phase 1: Testing Environment Setup

#### 1.1 Project Structure for Deployment
```
KICKAI/
├── Procfile                    # Railway process definition
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Python version
├── .env.example               # Environment template
├── railway.json               # Railway configuration
├── src/
│   ├── main.py                # Entry point
│   ├── bot_runner.py          # Bot runner
│   └── monitoring.py          # Monitoring utilities
└── scripts/
    ├── deploy.sh              # Deployment script
    └── health_check.py        # Health check script
```

#### 1.2 Environment Configuration
```bash
# Required environment variables
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ENVIRONMENT=testing
LOG_LEVEL=INFO
MONITORING_ENABLED=true

# Note: TELEGRAM_BOT_TOKEN is fetched from Supabase database per team
# No need to set it as environment variable
```

#### 1.3 Monitoring Strategy

**System Monitoring:**
- CPU usage
- Memory usage
- Disk usage
- Network activity
- Process status

**Application Monitoring:**
- Bot response times
- Database query performance
- Error rates
- Command success/failure rates
- AI response quality metrics

**AI Response Quality Monitoring:**
- Response relevance scoring
- Response time tracking
- User satisfaction metrics
- Error pattern analysis

## 🔧 Implementation Plan

### Step 1: Prepare Codebase for Deployment
1. Create deployment-specific files
2. Add health check endpoints
3. Implement monitoring hooks
4. Add graceful shutdown handling

### Step 2: Set Up Railway Project
1. Create Railway account
2. Connect GitHub repository
3. Configure environment variables
4. Set up monitoring

### Step 3: Deploy Testing Environment
1. Deploy to Railway
2. Configure monitoring
3. Test bot functionality
4. Validate logging

### Step 4: Implement Monitoring
1. Set up system metrics collection
2. Implement AI response monitoring
3. Configure alerts
4. Create dashboard

### Step 5: Production Environment
1. Create production Railway project
2. Configure production environment
3. Set up CI/CD pipeline
4. Deploy with monitoring

## 📊 Monitoring Implementation

### 1. System Metrics
```python
# monitoring/system_metrics.py
import psutil
import time
from datetime import datetime

class SystemMonitor:
    def collect_metrics(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids())
        }
```

### 2. Application Metrics
```python
# monitoring/app_metrics.py
class AppMonitor:
    def __init__(self):
        self.metrics = {
            'commands_processed': 0,
            'commands_failed': 0,
            'avg_response_time': 0,
            'ai_responses': 0,
            'ai_response_quality': []
        }
    
    def record_command(self, success: bool, response_time: float):
        if success:
            self.metrics['commands_processed'] += 1
        else:
            self.metrics['commands_failed'] += 1
        
        # Update average response time
        current_avg = self.metrics['avg_response_time']
        total_commands = self.metrics['commands_processed'] + self.metrics['commands_failed']
        self.metrics['avg_response_time'] = (current_avg * (total_commands - 1) + response_time) / total_commands
```

### 3. AI Response Quality Monitoring
```python
# monitoring/ai_quality.py
class AIQualityMonitor:
    def __init__(self):
        self.responses = []
    
    def evaluate_response(self, user_input: str, ai_response: str, context: dict):
        quality_score = self._calculate_quality_score(user_input, ai_response, context)
        
        self.responses.append({
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'ai_response': ai_response,
            'quality_score': quality_score,
            'context': context
        })
        
        return quality_score
    
    def _calculate_quality_score(self, user_input: str, ai_response: str, context: dict):
        # Implement quality scoring logic
        # - Relevance to user input
        # - Completeness of response
        # - Appropriate tone for context
        # - Technical accuracy
        pass
```

## 🚀 Deployment Files

### Procfile
```
web: python src/main.py
bot: python src/bot_runner.py
monitor: python src/monitoring.py
```

### railway.json
```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python src/main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### src/main.py
```python
#!/usr/bin/env python3
"""
KICKAI Main Application Entry Point
Handles web server, bot runner, and monitoring for Railway deployment
"""

import os
import threading
import time
import logging
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for monitoring
bot_runner = None
system_metrics = {}
app_metrics = {
    'start_time': time.time(),
    'requests_processed': 0,
    'requests_failed': 0,
    'bot_status': 'stopped'
}

def get_system_metrics():
    """Get basic system metrics."""
    try:
        import psutil
        return {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'process_count': len(psutil.pids())
        }
    except ImportError:
        return {
            'timestamp': time.time(),
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_percent': 0,
            'process_count': 0,
            'note': 'psutil not available'
        }

def start_bot():
    """Start the Telegram bot in a separate thread."""
    global bot_runner, app_metrics
    
    try:
        from src.telegram_command_handler import TelegramCommandHandler
        from run_telegram_bot import TelegramBotRunner
        
        logger.info("Starting Telegram bot...")
        bot_runner = TelegramBotRunner()
        app_metrics['bot_status'] = 'starting'
        
        # Test connection first
        if bot_runner.test_connection():
            app_metrics['bot_status'] = 'running'
            logger.info("Bot started successfully")
            bot_runner.run_polling()
        else:
            app_metrics['bot_status'] = 'failed'
            logger.error("Bot failed to start")
            
    except Exception as e:
        app_metrics['bot_status'] = 'error'
        logger.error(f"Bot error: {e}")

def start_monitoring():
    """Start monitoring in a separate thread."""
    global system_metrics
    
    while True:
        try:
            system_metrics = get_system_metrics()
            logger.debug(f"System metrics: {system_metrics}")
            time.sleep(60)  # Collect metrics every minute
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(60)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    global system_metrics, app_metrics, bot_runner
    
    try:
        # Update request metrics
        app_metrics['requests_processed'] += 1
        
        # Check if bot is running
        bot_status = app_metrics['bot_status']
        if bot_runner:
            try:
                # Try to get bot info to verify it's still running
                bot_runner.test_connection()
                bot_status = 'running'
            except:
                bot_status = 'error'
        
        response = {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime': time.time() - app_metrics['start_time'],
            'bot_status': bot_status,
            'system_metrics': system_metrics,
            'app_metrics': app_metrics,
            'environment': os.getenv('ENVIRONMENT', 'unknown')
        }
        
        return jsonify(response)
        
    except Exception as e:
        app_metrics['requests_failed'] += 1
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/metrics')
def metrics():
    """Detailed metrics endpoint."""
    global system_metrics, app_metrics
    
    return jsonify({
        'system': system_metrics,
        'application': app_metrics,
        'environment': os.getenv('ENVIRONMENT', 'unknown')
    })

@app.route('/')
def home():
    """Home endpoint."""
    return jsonify({
        'service': 'KICKAI Telegram Bot',
        'version': '1.0.0',
        'status': 'running',
        'environment': os.getenv('ENVIRONMENT', 'unknown'),
        'endpoints': {
            'health': '/health',
            'metrics': '/metrics'
        }
    })

@app.route('/bot/status')
def bot_status():
    """Bot status endpoint."""
    global bot_runner, app_metrics
    
    try:
        if bot_runner:
            is_connected = bot_runner.test_connection()
            return jsonify({
                'status': 'connected' if is_connected else 'disconnected',
                'bot_status': app_metrics['bot_status'],
                'timestamp': time.time()
            })
        else:
            return jsonify({
                'status': 'not_initialized',
                'bot_status': app_metrics['bot_status'],
                'timestamp': time.time()
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/bot/restart', methods=['POST'])
def restart_bot():
    """Restart the bot."""
    global bot_runner, app_metrics
    
    try:
        logger.info("Restarting bot...")
        app_metrics['bot_status'] = 'restarting'
        
        # Stop current bot if running
        if bot_runner:
            try:
                # This would need to be implemented in TelegramBotRunner
                pass
            except:
                pass
        
        # Start new bot thread
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        
        return jsonify({
            'status': 'restarting',
            'message': 'Bot restart initiated',
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Bot restart failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.time()
        }), 500

def main():
    """Main function to start all services."""
    logger.info("Starting KICKAI application...")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting web server on {host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    main()
```

## 📈 Monitoring Dashboard

### Key Metrics to Track
1. **System Health**
   - CPU usage < 80%
   - Memory usage < 80%
   - Disk usage < 90%
   - Process uptime

2. **Bot Performance**
   - Commands processed per hour
   - Average response time < 2 seconds
   - Error rate < 5%
   - Successful message deliveries

3. **AI Response Quality**
   - Average quality score > 7/10
   - Response relevance
   - User satisfaction (if available)
   - Error patterns

4. **Database Performance**
   - Query response times
   - Connection pool usage
   - Error rates

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          python -m pytest tests/ -v
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          
      - name: Deploy to Railway (Testing)
        if: github.ref == 'refs/heads/main'
        uses: railway/deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: kickai-testing
          
      - name: Deploy to Railway (Production)
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: railway/deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: kickai-production
```

## 🎯 Success Criteria

### Phase 1 (Testing Environment)
- [ ] Bot runs 24/7 without manual intervention
- [ ] System metrics are collected and logged
- [ ] Health check endpoint responds correctly
- [ ] Environment variables are properly configured
- [ ] Logs are accessible and meaningful
- [ ] Basic monitoring dashboard is functional

### Phase 2 (Production Environment)
- [ ] Production environment is isolated
- [ ] CI/CD pipeline is automated
- [ ] Advanced monitoring is implemented
- [ ] AI response quality monitoring is active
- [ ] Alerting system is configured
- [ ] Backup and recovery procedures are tested

## 🚨 Risk Mitigation

### Technical Risks
1. **Bot crashes**: Implement automatic restart
2. **Memory leaks**: Monitor memory usage and restart if needed
3. **Database connection issues**: Implement connection pooling and retry logic
4. **API rate limits**: Implement rate limiting and backoff strategies

### Operational Risks
1. **Service downtime**: Set up monitoring and alerting
2. **Data loss**: Regular backups and recovery testing
3. **Security**: Environment variable management and access controls

## 📝 Next Steps

1. **Immediate (Week 1)**
   - Set up Railway account and project
   - Create deployment files
   - Deploy testing environment
   - Implement basic monitoring

2. **Short-term (Week 2-3)**
   - Implement AI response quality monitoring
   - Set up alerting system
   - Create monitoring dashboard
   - Test reliability features

3. **Medium-term (Month 1-2)**
   - Deploy production environment
   - Implement CI/CD pipeline
   - Advanced monitoring and analytics
   - Performance optimization

4. **Long-term (Month 2+)**
   - Scale monitoring and alerting
   - Implement advanced AI quality metrics
   - Performance tuning and optimization
   - Documentation and runbooks 