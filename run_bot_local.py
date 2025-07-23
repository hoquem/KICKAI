#!/usr/bin/env python3
"""
KICKAI Bot Startup Script - Local Development

A clean, robust bot startup script for local development without health check server.
Uses multi-bot manager to load bot configurations from Firestore.
Includes process management to prevent multiple bot instances.
"""

import asyncio
import logging
import os
import signal
import sys
import time
import psutil
import subprocess
from pathlib import Path
from typing import Optional, List

try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Enable nested event loops for environments that already have an event loop running
import nest_asyncio
nest_asyncio.apply()

from core.settings import initialize_settings, get_settings
from database.firebase_client import initialize_firebase_client
from features.team_administration.domain.services.multi_bot_manager import MultiBotManager
from core.dependency_container import get_service, get_singleton, ensure_container_initialized
from src.features.team_administration.domain.interfaces.team_service_interface import ITeamService
from src.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
from core.startup_validator import StartupValidator
from core.logging_config import logger
from features.communication.infrastructure import TelegramBotService
from features.communication.domain.interfaces.telegram_bot_service_interface import TelegramBotServiceInterface

# Configure logging - using the imported logger directly

# Global state
multi_bot_manager: Optional[MultiBotManager] = None
shutdown_event = asyncio.Event()
BOT_PROCESS_NAME = "run_bot_local.py"
LOCK_FILE_PATH = Path("bot.lock")


def find_existing_bot_processes() -> List[psutil.Process]:
    """
    Find existing bot processes that might conflict with this startup.
    
    Returns:
        List of psutil.Process objects for existing bot processes
    """
    existing_processes = []
    current_pid = os.getpid()
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Skip the current process
                if proc.pid == current_pid:
                    continue
                
                # Check if this is a Python process running our bot script
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any(BOT_PROCESS_NAME in arg for arg in cmdline):
                        existing_processes.append(proc)
                        logger.info(f"🔍 Found existing bot process: PID {proc.pid}")
                
                # Also check for processes with similar names that might be bot instances
                elif proc.info['name'] and 'kickai' in proc.info['name'].lower():
                    existing_processes.append(proc)
                    logger.info(f"🔍 Found potential KICKAI process: PID {proc.pid}")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
    except Exception as e:
        logger.warning(f"⚠️ Error scanning for existing processes: {e}")
    
    return existing_processes


def kill_process_gracefully(process: psutil.Process, timeout: int = 10) -> bool:
    """
    Kill a process gracefully, with fallback to force kill.
    
    Args:
        process: psutil.Process to kill
        timeout: Seconds to wait for graceful shutdown
        
    Returns:
        True if process was killed successfully
    """
    try:
        pid = process.pid
        logger.info(f"🛑 Attempting to kill process {pid} gracefully...")
        
        # Try graceful termination first
        process.terminate()
        
        # Wait for graceful shutdown
        try:
            process.wait(timeout=timeout)
            logger.info(f"✅ Process {pid} terminated gracefully")
            return True
        except psutil.TimeoutExpired:
            logger.warning(f"⚠️ Process {pid} didn't terminate gracefully, forcing kill...")
            
            # Force kill if graceful termination failed
            try:
                process.kill()
                process.wait(timeout=5)
                logger.info(f"✅ Process {pid} force killed")
                return True
            except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                logger.error(f"❌ Failed to force kill process {pid}")
                return False
                
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.info(f"ℹ️ Process {process.pid} already terminated: {e}")
        return True
    except Exception as e:
        logger.error(f"❌ Error killing process {process.pid}: {e}")
        return False


def cleanup_existing_bot_instances() -> bool:
    """
    Find and kill existing bot instances to prevent conflicts.
    
    Returns:
        True if cleanup was successful or no conflicts found
    """
    logger.info("🔍 Checking for existing bot instances...")
    
    existing_processes = find_existing_bot_processes()
    
    if not existing_processes:
        logger.info("✅ No existing bot instances found")
        return True
    
    logger.warning(f"⚠️ Found {len(existing_processes)} existing bot process(es)")
    
    # Kill all existing processes
    success_count = 0
    for proc in existing_processes:
        if kill_process_gracefully(proc):
            success_count += 1
    
    if success_count == len(existing_processes):
        logger.info(f"✅ Successfully cleaned up {success_count} existing bot process(es)")
        return True
    else:
        logger.error(f"❌ Failed to clean up {len(existing_processes) - success_count} process(es)")
        return False


def create_lock_file() -> bool:
    """
    Create a lock file to indicate this bot instance is running.
    
    Returns:
        True if lock file was created successfully
    """
    try:
        # Write current PID to lock file
        with open(LOCK_FILE_PATH, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"🔒 Created lock file: {LOCK_FILE_PATH}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create lock file: {e}")
        return False


def remove_lock_file():
    """Remove the lock file when shutting down."""
    try:
        if LOCK_FILE_PATH.exists():
            LOCK_FILE_PATH.unlink()
            logger.info(f"🔓 Removed lock file: {LOCK_FILE_PATH}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to remove lock file: {e}")


def check_lock_file() -> bool:
    """
    Check if a lock file exists and if the process is still running.
    
    Returns:
        True if lock file exists and process is running
    """
    if not LOCK_FILE_PATH.exists():
        return False
    
    try:
        with open(LOCK_FILE_PATH, 'r') as f:
            pid_str = f.read().strip()
            pid = int(pid_str)
        
        # Check if process is still running
        if psutil.pid_exists(pid):
            logger.warning(f"⚠️ Found existing lock file with running process PID {pid}")
            return True
        else:
            logger.info(f"ℹ️ Found stale lock file with non-existent process PID {pid}")
            remove_lock_file()
            return False
            
    except (ValueError, FileNotFoundError) as e:
        logger.warning(f"⚠️ Invalid lock file: {e}")
        remove_lock_file()
        return False


def setup_logging():
    """Configure logging for local development with console output redirected to file."""
    from loguru import logger
    import sys
    import os
    
    # Remove any existing handlers to avoid duplicates
    logger.remove()
    
    # Ensure logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Add console handler with colored output for local development
    # This will be the primary logging destination
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        colorize=True
    )
    
    # Add error handler to stderr for critical errors
    logger.add(
        sys.stderr,
        level="ERROR",
        format="<red>{time:YYYY-MM-DD HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        enqueue=True,
        colorize=True
    )
    
    logger.info("📝 Logging configured for local development")
    logger.info("📄 Console output: INFO level and above")
    logger.info("📁 Console output will be redirected to logs/kickai.log")
    logger.info("🔄 To view logs in real-time: tail -f logs/kickai.log")


def setup_environment():
    """Set up the environment and load configuration."""
    try:
        # Load environment variables
        # from dotenv import load_dotenv # This line is now redundant as load_dotenv is moved to the top
        
        # Initialize settings
        initialize_settings()
        config = get_settings()
        
        # Validate required fields (only Firebase and AI config, not bot tokens)
        errors = config.validate_required_fields()
        if errors:
            logger.error("❌ Configuration errors:")
            for error in errors:
                logger.error(f"   - {error}")
            raise ValueError("Configuration validation failed")
        
        # Configure logging
        setup_logging()
        logger.info("✅ Configuration loaded successfully and logging configured")
        
        # Set up CrewAI logging to redirect to loguru
        from utils.crewai_logging import setup_crewai_logging
        setup_crewai_logging("DEBUG")  # Enable debug logging for CrewAI
        
        # Check if mock services are enabled
        use_mock_datastore = os.getenv('USE_MOCK_DATASTORE', 'false').lower() == 'true'
        
        if use_mock_datastore:
            logger.info("🔧 Mock services enabled - skipping Firebase initialization")
        else:
            # Initialize Firebase only if not using mock services
            initialize_firebase_client(config)
            logger.info("✅ Firebase client initialized")
        
        # Container will be initialized in main function
        logger.info("✅ Environment setup completed")
        
        return config
        
    except Exception as e:
        logger.critical(f"❌ Failed to setup environment: {e}", exc_info=True)
        raise


async def validate_service_registration(container) -> bool:
    """Validate that all required services are properly registered and accessible."""
    try:
        logger.info("🔍 Validating service registration...")
        
        # Debug: Log what services are currently registered
        all_services = container.get_all_services()
        logger.info(f"🔍 Currently registered services: {[cls.__name__ for cls in all_services.keys()]}")
        logger.info(f"🔍 Service count: {len(all_services)}")
        
        # Debug: Log the actual class types
        for cls in all_services.keys():
            logger.info(f"🔍 Registered service type: {cls} (module: {cls.__module__})")
        
        # Import all required service classes
        from src.features.player_registration.domain.services.player_service import PlayerService
        from src.features.team_administration.domain.services.team_member_service import TeamMemberService
        from src.features.team_administration.domain.services.team_service import TeamService
        from src.database.interfaces import DataStoreInterface
        
        # Debug: Log the lookup class types
        logger.info(f"🔍 Looking up PlayerService: {PlayerService} (module: {PlayerService.__module__})")
        logger.info(f"🔍 Looking up TeamMemberService: {TeamMemberService} (module: {TeamMemberService.__module__})")
        logger.info(f"🔍 Looking up TeamService: {TeamService} (module: {TeamService.__module__})")
        logger.info(f"🔍 Looking up DataStoreInterface: {DataStoreInterface} (module: {DataStoreInterface.__module__})")
        
        required_services = [
            (PlayerService, "PlayerService"),
            (TeamMemberService, "TeamMemberService"), 
            (TeamService, "TeamService"),
            (DataStoreInterface, "DataStoreInterface")
        ]
        
        missing_services = []
        for service_class, service_name in required_services:
            try:
                service = container.get_service(service_class)
                if service is None:
                    missing_services.append(service_name)
                    logger.error(f"❌ Service {service_name} is None")
                else:
                    logger.info(f"✅ Service {service_name} is registered and accessible")
            except Exception as e:
                missing_services.append(service_name)
                logger.error(f"❌ Failed to get service {service_name}: {e}")
        
        if missing_services:
            logger.error(f"❌ Missing or inaccessible services: {missing_services}")
            return False
        
        logger.info("✅ All required services are registered and accessible")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service registration validation failed: {e}")
        import traceback
        logger.error(f"❌ Service validation traceback: {traceback.format_exc()}")
        return False


async def validate_tool_registration() -> bool:
    """Validate that all required tools are properly registered and accessible."""
    try:
        logger.info("🔍 Validating tool registration...")
        
        from src.agents.tool_registry import get_tool_registry
        
        # Get the tool registry
        tool_registry = get_tool_registry()
        
        # Debug: Log what tools are actually registered
        all_tools = tool_registry.get_tool_names()
        logger.info(f"🔍 Currently registered tools: {all_tools}")
        logger.info(f"🔍 Tool count: {len(all_tools)}")
        
        # Define required tools for each agent
        required_tools = {
            'message_processor': [
                'send_message', 'send_announcement', 'get_available_commands',
                'get_my_status', 'get_my_team_member_status', 'get_all_players',
                'get_team_members', 'list_team_members_and_players'
            ],
            'player_coordinator': [
                'get_my_status', 'get_player_status', 'get_all_players',
                'approve_player', 'register_player', 'send_message'
            ],
            'team_manager': [
                'get_team_members', 'get_my_team_member_status', 'send_message'
            ]
        }
        
        missing_tools = []
        
        # Check each agent's required tools
        for agent_name, tools in required_tools.items():
            for tool_name in tools:
                tool = tool_registry.get_tool(tool_name)
                if tool is None:
                    missing_tools.append(f"{agent_name}.{tool_name}")
                    logger.error(f"❌ Tool {tool_name} for agent {agent_name} is not registered")
                else:
                    logger.info(f"✅ Tool {tool_name} for agent {agent_name} is registered")
        
        if missing_tools:
            logger.error(f"❌ Missing tools: {missing_tools}")
            return False
        
        logger.info("✅ All required tools are registered")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool registration validation failed: {e}")
        import traceback
        logger.error(f"❌ Tool validation traceback: {traceback.format_exc()}")
        return False


async def pre_initialize_crews() -> bool:
    """Pre-initialize all crews to ensure they are ready before bot startup."""
    try:
        logger.info("🔍 Pre-initializing crews...")
        
        from src.agents.crew_lifecycle_manager import CrewLifecycleManager
        from features.team_administration.domain.services.team_service import TeamService
        from src.core.dependency_container import get_container
        
        # Get team service
        container = get_container()
        team_service = container.get_service(TeamService)
        
        # Get all teams
        teams = await team_service.get_all_teams()
        
        if not teams:
            logger.warning("⚠️ No teams found for crew pre-initialization")
            return True
        
        # Pre-initialize crews for each team
        for team in teams:
            try:
                logger.info(f"🔍 Pre-initializing crew for team: {team.team_id}")
                
                # Create crew lifecycle manager
                lifecycle_manager = CrewLifecycleManager()
                
                # Create team config
                team_config = {
                    'team_id': team.team_id,
                    'bot_token': team.bot_token,
                    'main_chat_id': team.main_chat_id,
                    'leadership_chat_id': team.leadership_chat_id
                }
                
                # Pre-initialize the crew
                crew = await lifecycle_manager.create_crew(team_config)
                
                if crew is None:
                    logger.error(f"❌ Failed to pre-initialize crew for team {team.team_id}")
                    return False
                
                logger.info(f"✅ Crew pre-initialized for team: {team.team_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to pre-initialize crew for team {team.team_id}: {e}")
                return False
        
        logger.info("✅ All crews pre-initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Crew pre-initialization failed: {e}")
        import traceback
        logger.error(f"❌ Crew pre-initialization traceback: {traceback.format_exc()}")
        return False


async def run_system_validation(container=None):
    """Run comprehensive system validation before starting bots."""
    try:
        logger.info("🔍 Running system validation...")
        
        # Get services from the initialized container
        if container is None:
            from src.core.dependency_container import get_container
            container = get_container()
        
        from src.features.team_administration.domain.services.team_service import TeamService
        team_service = container.get_service(TeamService)
        
        # Get team_id from environment or configuration
        # This should be read from Firestore or environment, not hardcoded
        team_id = os.getenv('TEAM_ID')
        if not team_id:
            logger.error("❌ TEAM_ID environment variable not set. Cannot proceed without team configuration.")
            return False
        
        # Get team configuration
        team = await team_service.get_team_by_id(team_id=team_id)
        if not team:
            logger.error(f"❌ Team {team_id} not found in database")
            return False
        
        # Extract bot configuration from team explicit fields (single source of truth)
        bot_config = {
            'bot_token': team.bot_token,
            'main_chat_id': team.main_chat_id,
            'leadership_chat_id': team.leadership_chat_id,
            'team_id': team_id
        }
        
        logger.info(f"🔧 Bot configuration loaded for team {team_id}:")
        logger.info(f"  - bot_token: {bot_config['bot_token'][:10]}..." if bot_config['bot_token'] else "None")
        logger.info(f"  - main_chat_id: {bot_config['main_chat_id']}")
        logger.info(f"  - leadership_chat_id: {bot_config['leadership_chat_id']}")
        
        # Create validator and run checks
        logger.info("🔧 Creating startup validator...")
        try:
            validator = StartupValidator()
            logger.info("🔧 Startup validator created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create startup validator: {e}")
            import traceback
            logger.error(f"❌ Validator creation traceback: {traceback.format_exc()}")
            return False
        context = {
            "team_id": team_id,
            "bot_config": bot_config,
            "src_path": "src"  # Add src_path for tool registration check
        }
        
        logger.info("🔧 Running validation checks...")
        try:
            logger.info("🔧 About to call validator.validate()...")
            report = await validator.validate(context)
            logger.info("🔧 Validation checks completed")
        except Exception as e:
            logger.error(f"❌ Validation execution failed: {e}")
            import traceback
            logger.error(f"❌ Validation execution traceback: {traceback.format_exc()}")
            return False
        
        # Print validation report
        try:
            validator.print_report(report)
        except Exception as e:
            logger.error(f"❌ Failed to print validation report: {e}")
            # Still continue with validation logic
        
        # Check if system is healthy
        if not report.is_healthy():
            logger.error("❌ System validation failed! Critical issues found:")
            for failure in report.critical_failures:
                logger.error(f"   • {failure}")
            
            # CRITICAL: Check specifically for LLM failures
            llm_failures = [check for check in report.checks 
                           if check.category.value == "LLM" and check.status.value == "FAILED"]
            if llm_failures:
                logger.error("🚫 CRITICAL: LLM authentication failed! Bot cannot function without LLM.")
                logger.error("🚫 Please check your API keys and LLM provider configuration.")
                logger.error("🚫 Bot will not start until LLM is working.")
                return False
            
            logger.error("🚫 Cannot start bots due to critical validation failures")
            return False
        
        if report.warnings:
            logger.warning("⚠️ System validation completed with warnings:")
            for warning in report.warnings:
                logger.warning(f"   • {warning}")
            logger.info("💡 Consider addressing warnings for optimal performance")
        
        logger.info("✅ System validation passed! All critical components are healthy")
        return True
        
    except Exception as e:
        logger.error(f"❌ System validation failed with error: {e}")
        return False


async def create_multi_bot_manager(container):
    """Create and configure the multi-bot manager."""
    global multi_bot_manager
    
    try:
        logger.info("🔧 Creating multi-bot manager...")
        
        # Get services from dependency container using proper pattern
        from src.features.team_administration.domain.interfaces.team_service_interface import ITeamService
        from src.database.interfaces import DataStoreInterface
        
        # Use the container parameter passed from main function
        team_service = container.get_service(ITeamService)
        data_store = container.get_service(DataStoreInterface)
        
        logger.info("✅ Got services from dependency container")
        
        # Create multi-bot manager
        logger.info("🔍 About to create MultiBotManager...")
        multi_bot_manager = MultiBotManager(data_store, team_service)
        logger.info("✅ MultiBotManager instance created")
        
        # Load bot configurations from Firestore
        logger.info("🔍 About to load bot configurations...")
        try:
            bot_configs = await multi_bot_manager.load_bot_configurations()
            logger.info(f"🔍 Bot configurations loaded: {len(bot_configs)} found")
        except Exception as e:
            logger.error(f"❌ Exception in load_bot_configurations: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return None
        
        if not bot_configs:
            logger.warning("⚠️ No bot configurations found in teams collection")
            logger.info("💡 You need to create bot configurations in the teams collection")
            return None
        
        logger.info(f"✅ Multi-bot manager created with {len(bot_configs)} bot configurations")
        return multi_bot_manager
        
    except Exception as e:
        logger.error(f"❌ Failed to create multi-bot manager: {e}")
        raise


def flush_and_close_loggers():
    """Flush and close all loggers gracefully, handling BrokenPipeError."""
    import logging
    import sys
    
    # Flush stdout and stderr first
    try:
        sys.stdout.flush()
    except BrokenPipeError:
        pass
    except Exception:
        pass
    
    try:
        sys.stderr.flush()
    except BrokenPipeError:
        pass
    except Exception:
        pass
    
    # Flush and close all logging handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        try:
            handler.flush()
        except BrokenPipeError:
            pass
        except Exception:
            pass
        try:
            handler.close()
        except BrokenPipeError:
            pass
        except Exception:
            pass
    
    # Also flush any remaining loggers
    for logger_name in logging.root.manager.loggerDict:
        logger_obj = logging.getLogger(logger_name)
        for handler in logger_obj.handlers:
            try:
                handler.flush()
            except BrokenPipeError:
                pass
            except Exception:
                pass
            try:
                handler.close()
            except BrokenPipeError:
                pass
            except Exception:
                pass


async def main():
    """Main async entry point with comprehensive startup validation and initialization."""
    global multi_bot_manager
    shutdown_event = asyncio.Event()

    def _signal_handler():
        logger.info("🛑 Received shutdown signal, initiating graceful shutdown...")
        shutdown_event.set()

    try:
        logger.info("🎯 KICKAI Multi-Bot Manager Starting (Local Mode)...")
        logger.info(f"🔧 Process ID: {os.getpid()}")
        logger.info(f"🔧 PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
        
        # Set PYTHONPATH to src if not already set
        if not os.environ.get('PYTHONPATH'):
            os.environ['PYTHONPATH'] = 'src'
            logger.info("🔧 Set PYTHONPATH to 'src'")
        
        # Check for existing bot instances and clean them up
        if check_lock_file():
            logger.warning("⚠️ Found existing bot lock file")
            if not cleanup_existing_bot_instances():
                logger.error("❌ Failed to clean up existing bot instances. Exiting.")
                return
        
        # Create lock file to prevent other instances
        if not create_lock_file():
            logger.error("❌ Failed to create lock file. Exiting.")
            return
        
        # PHASE 1: Environment Setup
        logger.info("🔍 PHASE 1: Environment Setup")
        config = setup_environment()
        logger.info("✅ Environment setup completed")
        
        # PHASE 2: Dependency Container Initialization
        logger.info("🔍 PHASE 2: Dependency Container Initialization")
        from src.core.dependency_container import initialize_container
        container = initialize_container()
        logger.info("✅ Dependency container initialized with all services")
        
        # PHASE 3: Service Registration Validation
        logger.info("🔍 PHASE 3: Service Registration Validation")
        if not await validate_service_registration(container):
            logger.error("❌ Service registration validation failed. Exiting.")
            remove_lock_file()
            return
        logger.info("✅ Service registration validation passed")
        
        # PHASE 4: Command Registry Initialization (includes tool discovery)
        logger.info("🔍 PHASE 4: Command Registry Initialization")
        from core.command_registry_initializer import initialize_command_registry
        command_registry = initialize_command_registry()
        logger.info("✅ Command registry initialized successfully")
        
        # PHASE 5: Tool Registration Validation (skipped - tools discovered during agent creation)
        logger.info("🔍 PHASE 5: Tool Registration Validation (skipped)")
        logger.info("ℹ️ Tools will be discovered during agent creation")
        # if not await validate_tool_registration():
        #     logger.error("❌ Tool registration validation failed. Exiting.")
        #     remove_lock_file()
        #     return
        # logger.info("✅ Tool registration validation passed")
        
        # PHASE 6: Crew Pre-initialization (skipped - crews created on-demand)
        logger.info("🔍 PHASE 6: Crew Pre-initialization (skipped)")
        logger.info("ℹ️ Crews will be created on-demand when needed")
        # if not await pre_initialize_crews():
        #     logger.error("❌ Crew pre-initialization failed. Exiting.")
        #     remove_lock_file()
        #     return
        # logger.info("✅ Crew pre-initialization completed")
        
        # PHASE 7: System Validation
        logger.info("🔍 PHASE 7: System Validation")
        try:
            validation_passed = await run_system_validation(container)
            if not validation_passed:
                logger.error("❌ System validation failed. Exiting.")
                remove_lock_file()
                return
        except Exception as e:
            logger.error(f"❌ System validation failed with exception: {e}")
            import traceback
            logger.error(f"❌ Validation traceback: {traceback.format_exc()}")
            remove_lock_file()
            return
        logger.info("✅ System validation passed")
        
        # PHASE 8: Multi-Bot Manager Creation
        logger.info("🔍 PHASE 8: Multi-Bot Manager Creation")
        manager = await create_multi_bot_manager(container)
        if not manager:
            logger.error("❌ No bot configurations available in teams collection. Exiting.")
            remove_lock_file()
            return
        logger.info("✅ Multi-bot manager created")
        
        # PHASE 9: Bot Startup
        logger.info("🔍 PHASE 9: Bot Startup")
        await manager.start_all_bots()
        logger.info("✅ All bots started successfully")
        
        # PHASE 10: Startup Messages
        logger.info("🔍 PHASE 10: Startup Messages")
        await manager.send_startup_messages()
        logger.info("✅ Startup messages sent")
        
        # PHASE 11: Health Monitoring
        logger.info("🔍 PHASE 11: Health Monitoring")
        from core.llm_health_monitor import start_llm_monitoring
        
        # Create shutdown callback for LLM failures
        async def llm_failure_shutdown():
            logger.error("🚫 LLM failure detected - initiating graceful shutdown...")
            await manager.send_shutdown_messages()
            await manager.stop_all_bots()
            remove_lock_file()
            shutdown_event.set()
        
        # Start monitoring in background
        asyncio.create_task(start_llm_monitoring(llm_failure_shutdown))
        logger.info("✅ LLM health monitoring started")
        
        # PHASE 12: Signal Handling
        logger.info("🔍 PHASE 12: Signal Handling")
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _signal_handler)
            except NotImplementedError:
                signal.signal(sig, lambda s, f: asyncio.create_task(shutdown_event.set()))
        logger.info("✅ Signal handling configured")
        
        # STARTUP COMPLETE
        logger.info("🎉 KICKAI Multi-Bot Manager Startup Complete!")
        logger.info("🤖 Multi-bot manager is running. Press Ctrl+C to exit.")
        logger.info(f"📊 Running bots: {list(manager.bots.keys())}")
        logger.info(f"🔒 Lock file: {LOCK_FILE_PATH}")
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        logger.info("🛑 Shutdown signal received, stopping bots...")
        
        # Graceful shutdown
        from core.llm_health_monitor import stop_llm_monitoring
        await stop_llm_monitoring()
        await manager.send_shutdown_messages()
        await manager.stop_all_bots()
        remove_lock_file()
        logger.info("✅ Multi-bot manager shutdown complete")
        flush_and_close_loggers()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}", exc_info=True)
        remove_lock_file()
        raise


def main_sync():
    """Synchronous entry point."""
    try:
        # Redirect console output to log file for local development
        import sys
        import os
        
        # Ensure logs directory exists
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Redirect stdout and stderr to log file
        log_file_path = "logs/kickai.log"
        
        # Open log file in append mode
        log_file = open(log_file_path, 'a', buffering=1)  # Line buffered
        
        # Save original stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Redirect stdout and stderr to log file
        sys.stdout = log_file
        sys.stderr = log_file
        
        try:
            asyncio.run(main())
        finally:
            # Restore original stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            log_file.close()
            
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main_sync() 