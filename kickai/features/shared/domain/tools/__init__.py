#!/usr/bin/env python3
"""
Shared domain tools for KICKAI system.

This module provides shared tools used across multiple features.
"""

from kickai.features.shared.domain.tools.help_tools import *
from kickai.features.shared.domain.tools.onboarding_tools import (
    detect_registration_context,
    register_team_member_onboarding,
    team_member_guidance,
    validate_registration_data,
)
from kickai.features.shared.domain.tools.progressive_onboarding_tools import (
    get_onboarding_progress,
    progressive_onboarding_step,
)
from kickai.features.shared.domain.tools.role_guidance_tools import (
    compare_positions,
    compare_roles,
    explain_player_position,
    explain_team_role,
    get_role_recommendations,
)
from kickai.features.shared.domain.tools.enhanced_validation_tools import (
    comprehensive_validation,
    validate_name_enhanced,
    validate_phone_enhanced,
    validate_position_enhanced,
    validate_role_enhanced,
)
from kickai.features.shared.domain.tools.dual_role_detection_tools import (
    analyze_dual_role_potential,
    check_role_conflicts,
    detect_existing_registrations,
    execute_dual_registration,
    suggest_dual_registration,
)
from kickai.features.shared.domain.tools.cross_entity_linking_tools import (
    detect_data_conflicts,
    get_cross_entity_insights,
    link_player_member_profiles,
    manage_unified_profile,
    suggest_role_optimization,
    synchronize_profile_data,
)
from kickai.features.shared.domain.tools.smart_recommendations_tools import (
    analyze_team_needs_for_recommendations,
    get_onboarding_path_recommendation,
    get_personalized_welcome_message,
    get_smart_position_recommendations,
    get_smart_role_recommendations,
)

__all__ = [
    # Help tools (from help_tools.py)
    "get_available_commands",
    "get_command_help",
    # Onboarding tools
    "team_member_guidance", 
    "validate_registration_data",
    "register_team_member_onboarding",
    "detect_registration_context",
    # Progressive onboarding tools
    "progressive_onboarding_step",
    "get_onboarding_progress",
    # Role guidance tools
    "explain_player_position",
    "explain_team_role", 
    "compare_positions",
    "compare_roles",
    "get_role_recommendations",
    # Enhanced validation tools
    "validate_name_enhanced",
    "validate_phone_enhanced",
    "validate_position_enhanced", 
    "validate_role_enhanced",
    "comprehensive_validation",
    # Dual role detection tools
    "detect_existing_registrations",
    "analyze_dual_role_potential",
    "suggest_dual_registration",
    "execute_dual_registration",
    "check_role_conflicts",
    # Cross-entity linking tools
    "link_player_member_profiles",
    "detect_data_conflicts",
    "synchronize_profile_data",
    "manage_unified_profile",
    "get_cross_entity_insights",
    "suggest_role_optimization",
    # Smart recommendations tools
    "get_smart_position_recommendations",
    "get_smart_role_recommendations",
    "get_onboarding_path_recommendation",
    "analyze_team_needs_for_recommendations",
    "get_personalized_welcome_message",
]