#!/usr/bin/env python3
"""
KICKAI Shared Enums - Single Source of Truth

This module contains all shared enums used across the KICKAI system.
This is the ONLY place where these enums should be defined to prevent circular imports.
"""

from enum import Enum


class ChatType(Enum):
    """Chat types for permission checking and role assignment."""
    MAIN = "main_chat"
    LEADERSHIP = "leadership_chat"
    PRIVATE = "private"


class PermissionLevel(Enum):
    """Permission levels for commands."""
    PUBLIC = "public"
    PLAYER = "player"
    LEADERSHIP = "leadership"
    ADMIN = "admin"
    SYSTEM = "system"


class CommandType(Enum):
    """Types of commands supported by the system."""
    PLAYER_MANAGEMENT = "player_management"
    MATCH_MANAGEMENT = "match_management"
    PAYMENT_MANAGEMENT = "payment_management"
    TEAM_ADMINISTRATION = "team_administration"
    SYSTEM_OPERATION = "system_operation"
    HELP = "help"


class AgentRole(Enum):
    """CrewAI agent roles."""
    MESSAGE_PROCESSOR = "message_processor"
    TEAM_MANAGER = "team_manager"
    PLAYER_COORDINATOR = "player_coordinator"
    FINANCE_MANAGER = "finance_manager"
    PERFORMANCE_ANALYST = "performance_analyst"
    LEARNING_AGENT = "learning_agent"
    ONBOARDING_AGENT = "onboarding_agent"
    COMMAND_FALLBACK_AGENT = "command_fallback_agent"
    AVAILABILITY_MANAGER = "availability_manager"
    SQUAD_SELECTOR = "squad_selector"
    COMMUNICATION_MANAGER = "communication_manager"


class AIProvider(Enum):
    """AI providers for different environments."""
    OLLAMA = "ollama"
    GEMINI = "gemini"
    OPENAI = "openai"


class TeamStatus(Enum):
    """Team status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class PaymentType(Enum):
    """Payment types."""
    MATCH_FEE = "match_fee"
    MEMBERSHIP_FEE = "membership_fee"
    FINE = "fine"
    REFUND = "refund"


class PaymentStatus(Enum):
    """Payment status values."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ExpenseCategory(Enum):
    """Expense categories."""
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    TRANSPORTATION = "transportation"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class HealthStatus(Enum):
    """System health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """System component types."""
    DATABASE = "database"
    TELEGRAM = "telegram"
    AI_SERVICE = "ai_service"
    PAYMENT_GATEWAY = "payment_gateway"
    NOTIFICATION_SERVICE = "notification_service"


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
    FAIL = "fail"
    WARN = "warn"


class CheckCategory(Enum):
    """Health check categories."""
    CONNECTIVITY = "connectivity"
    FUNCTIONALITY = "functionality"
    PERFORMANCE = "performance"
    SECURITY = "security"


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
    PAYMENT_DATA = "payment_data"
    SYSTEM_CONFIG = "system_config"


class IDType(Enum):
    """ID generation types."""
    PLAYER = "player"
    TEAM = "team"
    MATCH = "match"
    PAYMENT = "payment"
    EXPENSE = "expense"
    MESSAGE = "message"


class ApplicationState(Enum):
    """Application state values."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error" 