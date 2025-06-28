#!/usr/bin/env python3
"""
Health Check for Railway Deployment
Simple HTTP server to respond to Railway health checks
"""

import os
import time
import threading
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'KICKAI Telegram Bot',
        'environment': os.getenv('RAILWAY_ENVIRONMENT', 'development')
    })

@app.route('/')
def root():
    """Root endpoint."""
    return jsonify({
        'message': 'KICKAI Telegram Bot is running',
        'status': 'operational',
        'timestamp': time.time()
    })

def run_health_server():
    """Run the health check server in a separate thread."""
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def start_health_server():
    """Start health server in background thread."""
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    return health_thread

if __name__ == "__main__":
    run_health_server() 