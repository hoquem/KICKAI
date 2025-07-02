#!/usr/bin/env python3
"""
Railway Main Entry Point for KICKAI
Deployment timestamp: 2024-12-19 19:15 UTC - Signal Fix
Version: 1.4.5-signal-fix
FORCE DEPLOYMENT: 2024-12-19 19:15 UTC - Fix signal handling in main thread
"""

# --- MONKEY-PATCH MUST BE FIRST - before any other imports ---
import httpx

# --- Monkey-patch to remove 'proxy' and 'proxies' kwargs from httpx.Client/AsyncClient ---
_original_client_init = httpx.Client.__init__
def _patched_client_init(self, *args, **kwargs):
    kwargs.pop("proxy", None)
    kwargs.pop("proxies", None)
    _original_client_init(self, *args, **kwargs)

_original_async_client_init = httpx.AsyncClient.__init__
def _patched_async_client_init(self, *args, **kwargs):
    kwargs.pop("proxy", None)
    kwargs.pop("proxies", None)
    _original_async_client_init(self, *args, **kwargs)

# Apply monkey patches
httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init

# --- Now safe to import other modules ---
import os
import sys
import logging
import time
import threading
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('railway.log')
    ]
)
logger = logging.getLogger(__name__)

def start_simple_health_server():
    """Start a simple health check server for Railway monitoring."""
    logger.info("🏥 Starting health server initialization...")
    
    try:
        logger.info("📦 Importing Flask...")
        from flask import Flask, jsonify
        import threading
        logger.info("✅ Flask imported successfully")
        
        app = Flask(__name__)
        logger.info("✅ Flask app created")
        
        @app.route('/health')
        def health_check():
            """Health check endpoint for Railway."""
            logger.info("🏥 Health check request received")
            return jsonify({
                'status': 'healthy',
                'timestamp': time.time(),
                'service': 'KICKAI Telegram Bot',
                'environment': os.getenv('RAILWAY_ENVIRONMENT', 'development'),
                'version': '1.4.5-signal-fix'
            })
        
        @app.route('/')
        def root():
            """Root endpoint."""
            logger.info("🏠 Root request received")
            return jsonify({
                'message': 'KICKAI Telegram Bot is running',
                'status': 'operational',
                'timestamp': time.time()
            })
        
        def run_server():
            try:
                port = int(os.getenv('PORT', 8080))
                logger.info(f"🏥 Starting Flask server on port {port}")
                logger.info(f"🏥 Server will bind to 0.0.0.0:{port}")
                
                # Test if port is available
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    logger.error(f"❌ Port {port} is already in use by another process")
                    logger.error("❌ This will prevent the health server from starting")
                    logger.error("❌ Check if another Flask server is running")
                    return
                else:
                    logger.info(f"✅ Port {port} is available")
                
                # Use a different port if 8080 is taken
                if port == 8080 and result == 0:
                    alternative_port = 8081
                    logger.info(f"🔄 Trying alternative port {alternative_port}")
                    port = alternative_port
                
                app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
                logger.info("✅ Flask server started successfully")
                
            except OSError as e:
                if "Address already in use" in str(e):
                    logger.error(f"❌ Port {port} is already in use")
                    logger.error("❌ This prevents the health server from starting")
                    logger.error("❌ The bot may still work but health checks will fail")
                else:
                    logger.error(f"❌ Flask server failed to start: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
            except Exception as e:
                logger.error(f"❌ Flask server failed to start: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
        
        logger.info("🧵 Creating health server thread...")
        health_thread = threading.Thread(target=run_server, daemon=True)
        logger.info("🧵 Starting health server thread...")
        health_thread.start()
        
        # Wait a moment to see if thread starts successfully
        time.sleep(1)
        if health_thread.is_alive():
            logger.info("✅ Health server thread is alive")
        else:
            logger.error("❌ Health server thread died immediately")
            return None
        
        logger.info("✅ Health server started for Railway")
        return health_thread
        
    except Exception as e:
        logger.error(f"❌ Health server failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

def start_telegram_bot():
    """Start Telegram bot in the main thread (signals only work in main thread)."""
    try:
        logger.info("🤖 Importing Telegram bot...")
        from run_telegram_bot import main as run_bot
        logger.info("✅ Telegram bot imported successfully")
        logger.info("🤖 Starting Telegram bot with match management...")
        
        # Run bot directly in main thread (signals only work in main thread)
        run_bot()
        
    except Exception as e:
        logger.error(f"❌ Telegram bot failed: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

def main():
    """Main entry point for Railway deployment."""
    try:
        # === FIREBASE DEBUG CODE ===
        logger.info("🔍 FIREBASE CREDENTIALS DEBUG - STARTING")
        logger.info("=" * 80)
        
        # List all Firebase environment variables
        firebase_vars = [k for k in os.environ.keys() if 'FIREBASE' in k.upper()]
        logger.info(f"🔍 Found {len(firebase_vars)} Firebase-related environment variables:")
        
        for var in sorted(firebase_vars):
            value = os.getenv(var, '')
            logger.info(f"   {var}: {'SET' if value else 'NOT SET'} (length: {len(value)})")
            if value and len(value) > 100:
                logger.info(f"      Preview: {value[:50]}...{value[-50:]}")
            elif value and len(value) > 0:
                logger.info(f"      Value: {value}")
        
        # Test base64 credentials
        logger.info("\n" + "=" * 60)
        logger.info("🔑 TESTING BASE64 ENCODED CREDENTIALS")
        logger.info("=" * 60)
        
        firebase_creds_b64 = os.getenv('FIREBASE_CREDENTIALS_B64')
        if not firebase_creds_b64:
            logger.error("❌ FIREBASE_CREDENTIALS_B64 not found")
        else:
            logger.info(f"✅ Found FIREBASE_CREDENTIALS_B64 (length: {len(firebase_creds_b64)})")
            logger.info(f"   Preview: {firebase_creds_b64[:50]}...{firebase_creds_b64[-50:]}")
            
            try:
                # Decode base64
                logger.info("🔄 Decoding base64...")
                import base64
                decoded_bytes = base64.b64decode(firebase_creds_b64)
                logger.info(f"✅ Decoded successfully (bytes: {len(decoded_bytes)})")
                
                # Convert to string
                decoded_str = decoded_bytes.decode('utf-8')
                logger.info(f"✅ Converted to string (chars: {len(decoded_str)})")
                logger.info(f"   Preview: {decoded_str[:100]}...")
                
                # Parse JSON
                logger.info("🔄 Parsing JSON...")
                import json
                creds_dict = json.loads(decoded_str)
                logger.info(f"✅ JSON parsed successfully")
                logger.info(f"   Project ID: {creds_dict.get('project_id', 'NOT FOUND')}")
                logger.info(f"   Client Email: {creds_dict.get('client_email', 'NOT FOUND')}")
                logger.info(f"   Private Key Length: {len(creds_dict.get('private_key', ''))}")
                
                # Check private key format
                private_key = creds_dict.get('private_key', '')
                if private_key:
                    logger.info(f"   Private Key Preview: {private_key[:50]}...{private_key[-50:]}")
                    if '-----BEGIN PRIVATE KEY-----' in private_key:
                        logger.info("✅ Private key has correct PEM format")
                    else:
                        logger.warning("⚠️ Private key may not have correct PEM format")
                    
                    # Check for truncation
                    if len(private_key) < 1000:
                        logger.warning("⚠️ Private key seems too short (possible truncation)")
                    else:
                        logger.info("✅ Private key length looks reasonable")
                
            except Exception as e:
                logger.error(f"❌ Base64 decoding failed: {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
        
        # Test JSON credentials
        logger.info("\n" + "=" * 60)
        logger.info("📄 TESTING JSON CREDENTIALS")
        logger.info("=" * 60)
        
        firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        if not firebase_creds_json:
            logger.error("❌ FIREBASE_CREDENTIALS_JSON not found")
        else:
            logger.info(f"✅ Found FIREBASE_CREDENTIALS_JSON (length: {len(firebase_creds_json)})")
            logger.info(f"   Preview: {firebase_creds_json[:100]}...")
            
            try:
                # Parse JSON
                logger.info("🔄 Parsing JSON...")
                creds_dict = json.loads(firebase_creds_json)
                logger.info(f"✅ JSON parsed successfully")
                logger.info(f"   Project ID: {creds_dict.get('project_id', 'NOT FOUND')}")
                logger.info(f"   Client Email: {creds_dict.get('client_email', 'NOT FOUND')}")
                logger.info(f"   Private Key Length: {len(creds_dict.get('private_key', ''))}")
                
            except Exception as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                logger.error(f"   Error type: {type(e).__name__}")
                import traceback
                logger.error(f"   Traceback: {traceback.format_exc()}")
        
        # Test individual variables
        logger.info("\n" + "=" * 60)
        logger.info("🔧 TESTING INDIVIDUAL ENVIRONMENT VARIABLES")
        logger.info("=" * 60)
        
        project_id = os.getenv('FIREBASE_PROJECT_ID')
        client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
        private_key = os.getenv('FIREBASE_PRIVATE_KEY')
        
        logger.info(f"📝 Project ID: {project_id or 'NOT SET'}")
        logger.info(f"📝 Client Email: {client_email or 'NOT SET'}")
        logger.info(f"📝 Private Key: {'SET' if private_key else 'NOT SET'} (length: {len(private_key) if private_key else 0})")
        
        if private_key:
            logger.info(f"   Private Key Preview: {private_key[:50]}...{private_key[-50:]}")
            if '-----BEGIN PRIVATE KEY-----' in private_key:
                logger.info("✅ Private key has correct PEM format")
            else:
                logger.warning("⚠️ Private key may not have correct PEM format")
        
        # Test Firebase Admin import
        logger.info("\n" + "=" * 60)
        logger.info("🔥 TESTING FIREBASE ADMIN SDK")
        logger.info("=" * 60)
        
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            logger.info("✅ Firebase Admin SDK imported successfully")
            
            # Check if app is already initialized
            try:
                app = firebase_admin.get_app()
                logger.info("✅ Firebase app already initialized")
            except ValueError:
                logger.info("🔄 No Firebase app initialized yet")
                
        except ImportError as e:
            logger.error(f"❌ Firebase Admin SDK import failed: {e}")
        except Exception as e:
            logger.error(f"❌ Firebase Admin SDK error: {e}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 FIREBASE DEBUG SUMMARY")
        logger.info("=" * 80)
        logger.info("✅ Environment variables checked")
        logger.info("✅ Base64 credentials tested")
        logger.info("✅ JSON credentials tested")
        logger.info("✅ Individual variables tested")
        logger.info("✅ Firebase Admin SDK tested")
        logger.info("🎯 Firebase debug completed!")
        logger.info("=" * 80)
        # === END FIREBASE DEBUG CODE ===
        
        logger.info("🚀 Starting KICKAI on Railway...")
        logger.info("📅 Deployment timestamp: 2024-12-19 19:15 UTC")
        logger.info("🏆 Version: 1.4.5-signal-fix")
        logger.info("🏆 Match Management System: ACTIVE")
        logger.info("🏥 Enhanced Logging: ACTIVE")
        
        # Log environment info
        logger.info(f"🌍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'development')}")
        logger.info(f"🔢 Port: {os.getenv('PORT', '8080')}")
        logger.info(f"🐍 Python version: {sys.version}")
        logger.info(f"📁 Working directory: {os.getcwd()}")
        
        # Start health server first (for Railway health checks)
        logger.info("🏥 Starting health server...")
        health_thread = start_simple_health_server()
        if not health_thread:
            logger.error("❌ Health server failed to start")
            sys.exit(1)
        
        # Wait a moment for health server to start
        logger.info("⏳ Waiting for health server to start...")
        time.sleep(5)
        
        # Check if health server is still alive
        if health_thread.is_alive():
            logger.info("✅ Health server thread is still alive")
        else:
            logger.error("❌ Health server thread died")
            sys.exit(1)
        
        # Start Telegram bot in the main thread
        logger.info("🤖 Starting Telegram bot...")
        start_telegram_bot()
        
        logger.info("✅ KICKAI system started successfully!")
        logger.info("🏥 Health endpoint: /health")
        logger.info("🤖 Telegram bot: Running in main thread")
        
        # Bot will handle the main thread, no need for infinite loop
        
    except Exception as e:
        logger.error(f"❌ Failed to start KICKAI: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    # FORCE DEPLOYMENT: 2024-12-19 16:40 UTC - Firebase Fix + Dependencies
