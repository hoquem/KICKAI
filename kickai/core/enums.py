#!/usr/bin/env python3
"""
KICKAI Shared Enums - Single Source of Truth

This module contains all shared enums used across the KICKAI system.
This is the ONLY place where these enums should be defined to prevent circular imports.
"""

from enum import Enum


class AgentRole(str, Enum):
    """Agent roles in the enhanced 6-Agent CrewAI system with NLP support."""

    # Essential 5-Agent System
    MESSAGE_PROCESSOR = "message_processor"        # Primary interface and routing
    HELP_ASSISTANT = "help_assistant"              # Help system and guidance
    PLAYER_COORDINATOR = "player_coordinator"      # Player management and onboarding
    TEAM_ADMINISTRATOR = "team_administrator"      # Team member management
    SQUAD_SELECTOR = "squad_selector"              # Squad selection and match management
    
    # NLP Enhancement Agent
    NLP_PROCESSOR = "nlp_processor"                # Natural language processing and understanding


class UserRole(str, Enum):
    """User roles in the system."""

    # Player roles
    PLAYER = "player"

    # Team member roles
    TEAM_MEMBER = "team_member"
    TEAM_MANAGER = "team_manager"
    CLUB_ADMINISTRATOR = "club_administrator"
    COACH = "coach"
    ASSISTANT_COACH = "assistant_coach"

    # System roles
    ADMIN = "admin"
    LEADERSHIP = "leadership"


class UserStatus(str, Enum):
    """User status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class ChatType(str, Enum):
    """Chat types for Telegram integration."""

    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"
    MAIN = "main"
    LEADERSHIP = "leadership"


class EntityType(str, Enum):
    """Types of entities that tools can operate on."""

    PLAYER = "player"
    TEAM_MEMBER = "team_member"
    TEAM = "team"
    MATCH = "match"
    BOTH = "both"  # For entities that work with both players and team members
    NEITHER = "neither"


class AIProvider(str, Enum):
    """AI providers supported by the system."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    GOOGLE_GEMINI = "google_gemini"
    HUGGINGFACE = "huggingface"
    MOCK = "mock"
    GROQ = "groq"


class PermissionLevel(Enum):
    """Permission levels for commands."""

    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"
    SYSTEM = "system"


class CommandType(Enum):
    """Types of commands supported by the system."""

    SLASH_COMMAND = "slash_command"
    NATURAL_LANGUAGE = "natural_language"
    PLAYER_MANAGEMENT = "player_management"
    MATCH_MANAGEMENT = "match_management"

    TEAM_ADMINISTRATION = "team_administration"
    SYSTEM_OPERATION = "system_operation"
    HELP = "help"


class PlayerPosition(Enum):
    """Football player positions."""

    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    UTILITY = "utility"
    WINGER = "winger"
    STRIKER = "striker"


class TeamStatus(Enum):
    """Team status values."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"





class ExpenseCategory(Enum):
    """Expense categories."""

    EQUIPMENT = "equipment"
    FACILITY = "facility"
    TRANSPORTATION = "transportation"
    ADMINISTRATIVE = "administrative"
    PITCH_FEES = "pitch_fees"
    REFEREE_FEES = "referee_fees"
    TEAM_MEAL = "team_meal"
    FA_FEES = "fa_fees"
    OTHER = "other"


class HealthStatus(Enum):
    """System health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """System component types."""

    DATABASE = "database"
    TELEGRAM = "telegram"
    AI_SERVICE = "ai_service"

    NOTIFICATION_SERVICE = "notification_service"
    AGENT = "agent"
    TOOL = "tool"
    SERVICE = "service"
    INFRASTRUCTURE = "infrastructure"
    EXTERNAL = "external"


class AlertLevel(Enum):
    """Alert levels for monitoring."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskComplexity(Enum):
    """Task complexity levels."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class CapabilityLevel(Enum):
    """Agent capability levels."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CapabilityCategory(Enum):
    """Agent capability categories."""

    COMMUNICATION = "communication"
    ANALYSIS = "analysis"
    DECISION_MAKING = "decision_making"
    COORDINATION = "coordination"
    LEARNING = "learning"


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""

    VALIDATION = "validation"
    DATABASE = "database"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SYSTEM = "system"


class Environment(Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class CheckStatus(Enum):
    """Health check status."""

    PASS = "pass"
    PASSED = "PASSED"
    FAIL = "fail"
    FAILED = "FAILED"
    WARN = "warn"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"


class CheckCategory(Enum):
    """Health check categories."""

    CONNECTIVITY = "connectivity"
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SYSTEM = "SYSTEM"
    LLM = "LLM"
    AGENT = "AGENT"
    TOOL = "TOOL"
    TASK = "TASK"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    CONFIGURATION = "CONFIGURATION"
    DATABASE = "DATABASE"
    TELEGRAM = "TELEGRAM"


class MemoryType(Enum):
    """Memory storage types."""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryPriority(Enum):
    """Memory priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class CacheNamespace(Enum):
    """Cache namespace types."""

    USER_SESSION = "user_session"
    TEAM_DATA = "team_data"
    MATCH_DATA = "match_data"

    SYSTEM_CONFIG = "system_config"


class IDType(Enum):
    """ID generation types."""

    PLAYER = "player"
    TEAM = "team"
    MATCH = "match"


    MESSAGE = "message"


class ApplicationState(Enum):
    """Application state values."""

    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class TestType(Enum):
    """Types of tests supported."""

    COMMAND = "command"
    NATURAL_LANGUAGE = "natural_language"
    USER_FLOW = "user_flow"
    DATA_VALIDATION = "data_validation"
    INTEGRATION = "integration"
    VALIDATION = "validation"


class RegistryType(Enum):
    """Types of registries supported by the system."""

    TOOL = "tool"
    COMMAND = "command"
    SERVICE = "service"
    AGENT = "agent"
    TASK = "task"
