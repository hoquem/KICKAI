#!/usr/bin/env python3
"""
System Infrastructure Domain Exceptions

Custom exception hierarchy for system infrastructure operations to provide
specific error types instead of generic Exception handling.
"""

from kickai.core.exceptions import KickAIError


class SystemInfrastructureError(KickAIError):
    """Base exception for system infrastructure errors."""

    pass


class PermissionError(SystemInfrastructureError):
    """Base exception for permission errors."""

    pass


class PermissionServiceUnavailableError(PermissionError):
    """Permission service is not available."""

    def __init__(self, message: str = "Permission service unavailable"):
        super().__init__(message)


class InsufficientPermissionsError(PermissionError):
    """User lacks required permissions for the operation."""

    def __init__(self, telegram_id: str, operation: str, required_permission: str):
        self.telegram_id = telegram_id
        self.operation = operation
        self.required_permission = required_permission
        super().__init__(
            f"User {telegram_id} lacks permission '{required_permission}' for operation: {operation}",
            context={
                "telegram_id": telegram_id,
                "operation": operation,
                "required_permission": required_permission,
            },
        )


class InvalidUserRoleError(PermissionError):
    """Invalid user role specified."""

    def __init__(self, role: str, valid_roles: list[str]):
        self.role = role
        self.valid_roles = valid_roles
        super().__init__(
            f"Invalid user role '{role}'. Valid roles: {', '.join(valid_roles)}",
            context={"role": role, "valid_roles": valid_roles},
        )


class UserNotFoundError(PermissionError):
    """User not found in permission system."""

    def __init__(self, telegram_id: str, team_id: str):
        self.telegram_id = telegram_id
        self.team_id = team_id
        super().__init__(
            f"User {telegram_id} not found in team {team_id}",
            context={"telegram_id": telegram_id, "team_id": team_id},
        )


class ChatAccessDeniedError(PermissionError):
    """User cannot access the specified chat type."""

    def __init__(self, telegram_id: str, chat_type: str, required_role: str):
        self.telegram_id = telegram_id
        self.chat_type = chat_type
        self.required_role = required_role
        super().__init__(
            f"User {telegram_id} cannot access {chat_type} chat. Required role: {required_role}",
            context={
                "telegram_id": telegram_id,
                "chat_type": chat_type,
                "required_role": required_role,
            },
        )


class BotStatusError(SystemInfrastructureError):
    """Base exception for bot status errors."""

    pass


class BotStatusServiceUnavailableError(BotStatusError):
    """Bot status service is not available."""

    def __init__(self, message: str = "Bot status service unavailable"):
        super().__init__(message)


class SystemHealthCheckFailedError(BotStatusError):
    """System health check failed."""

    def __init__(self, component: str, details: str):
        self.component = component
        self.details = details
        super().__init__(
            f"Health check failed for {component}: {details}",
            context={"component": component, "details": details},
        )


class ServiceDependencyError(BotStatusError):
    """Required service dependency is not available."""

    def __init__(self, service_name: str, dependency_name: str):
        self.service_name = service_name
        self.dependency_name = dependency_name
        super().__init__(
            f"Service {service_name} dependency unavailable: {dependency_name}",
            context={"service_name": service_name, "dependency_name": dependency_name},
        )


class MetricsCollectionError(BotStatusError):
    """Failed to collect system metrics."""

    def __init__(self, metric_type: str, reason: str):
        self.metric_type = metric_type
        self.reason = reason
        super().__init__(
            f"Failed to collect {metric_type} metrics: {reason}",
            context={"metric_type": metric_type, "reason": reason},
        )


class ConfigurationError(SystemInfrastructureError):
    """Base exception for configuration errors."""

    pass


class MissingConfigurationError(ConfigurationError):
    """Required configuration is missing."""

    def __init__(self, config_key: str, component: str = ""):
        self.config_key = config_key
        self.component = component
        message = f"Missing required configuration: {config_key}"
        if component:
            message += f" for {component}"
        super().__init__(message, context={"config_key": config_key, "component": component})


class InvalidConfigurationError(ConfigurationError):
    """Configuration value is invalid."""

    def __init__(self, config_key: str, config_value: str, reason: str):
        self.config_key = config_key
        self.config_value = config_value
        self.reason = reason
        super().__init__(
            f"Invalid configuration for {config_key}='{config_value}': {reason}",
            context={"config_key": config_key, "config_value": config_value, "reason": reason},
        )


class SystemInitializationError(SystemInfrastructureError):
    """System initialization failed."""

    def __init__(self, component: str, reason: str):
        self.component = component
        self.reason = reason
        super().__init__(
            f"System initialization failed for {component}: {reason}",
            context={"component": component, "reason": reason},
        )


class DatabaseConnectionError(SystemInfrastructureError):
    """Database connection failed."""

    def __init__(self, database_name: str, connection_details: str):
        self.database_name = database_name
        self.connection_details = connection_details
        super().__init__(
            f"Database connection failed for {database_name}: {connection_details}",
            context={"database_name": database_name, "connection_details": connection_details},
        )


class ExternalServiceError(SystemInfrastructureError):
    """External service is unavailable."""

    def __init__(self, service_name: str, endpoint: str, error_details: str):
        self.service_name = service_name
        self.endpoint = endpoint
        self.error_details = error_details
        super().__init__(
            f"External service {service_name} unavailable at {endpoint}: {error_details}",
            context={
                "service_name": service_name,
                "endpoint": endpoint,
                "error_details": error_details,
            },
        )


class ResourceExhaustionError(SystemInfrastructureError):
    """System resources are exhausted."""

    def __init__(self, resource_type: str, current_usage: str, limit: str):
        self.resource_type = resource_type
        self.current_usage = current_usage
        self.limit = limit
        super().__init__(
            f"Resource exhaustion for {resource_type}: {current_usage}/{limit}",
            context={
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit,
            },
        )


class SecurityValidationError(SystemInfrastructureError):
    """Security validation failed."""

    def __init__(self, validation_type: str, user_id: str, details: str):
        self.validation_type = validation_type
        self.user_id = user_id
        self.details = details
        super().__init__(
            f"Security validation failed for {validation_type} by user {user_id}: {details}",
            context={"validation_type": validation_type, "user_id": user_id, "details": details},
        )


class PermissionCheckError(PermissionError):
    """Error checking user permissions."""

    def __init__(self, details: str = "Permission check failed"):
        self.details = details
        super().__init__(f"Permission check error: {details}")
