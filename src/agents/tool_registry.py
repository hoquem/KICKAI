from features.player_registration.domain.tools.player_tools import TOOL_REGISTRY as PLAYER_TOOLS
from features.communication.domain.tools.communication_tools import TOOL_REGISTRY as COMMUNICATION_TOOLS
from features.system_infrastructure.domain.tools.logging_tools import TOOL_REGISTRY as LOGGING_TOOLS
from features.player_registration.domain.tools.registration_tools import TOOL_REGISTRY as REGISTRATION_TOOLS

ALL_TOOL_REGISTRIES = [PLAYER_TOOLS, COMMUNICATION_TOOLS, LOGGING_TOOLS, REGISTRATION_TOOLS]

GLOBAL_TOOL_REGISTRY = {}
for registry in ALL_TOOL_REGISTRIES:
    GLOBAL_TOOL_REGISTRY.update(registry)

__all__ = ["GLOBAL_TOOL_REGISTRY"] 