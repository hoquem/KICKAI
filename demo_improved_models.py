#!/usr/bin/env python3
"""
Demonstration of Improved Models with OOP Principles

This script demonstrates the improved models with:
- Base classes and inheritance
- Validation and error handling
- Factory methods
- Business logic methods
- Serialization/deserialization
- Integration between models
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.models_improved import (
    Player, Team, TeamMember, Match, BotMapping, ModelFactory,
    PlayerPosition, PlayerRole, OnboardingStatus, TeamStatus, MatchStatus
)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_section(title: str):
    """Print a formatted section."""
    print(f"\n--- {title} ---")


def demo_base_model_functionality():
    """Demonstrate base model functionality."""
    print_header("Base Model Functionality")
    
    # Create a team using the base model
    team = Team.create("Demo Team FC", "A demonstration team")
    print(f"Created team: {team.get_display_name()}")
    print(f"Team ID: {team.id}")
    print(f"Created at: {team.created_at}")
    print(f"Updated at: {team.updated_at}")
    
    # Update the team
    team.update(description="Updated description")
    print(f"Updated team: {team.get_display_name()}")
    print(f"New updated at: {team.updated_at}")
    
    # Serialize to dict
    team_dict = team.to_dict()
    print(f"Serialized team keys: {list(team_dict.keys())}")
    
    # Deserialize from dict
    restored_team = Team.from_dict(team_dict)
    print(f"Restored team: {restored_team.get_display_name()}")
    print(f"Restored team ID: {restored_team.id}")


def demo_validation_and_error_handling():
    """Demonstrate validation and error handling."""
    print_header("Validation and Error Handling")
    
    print_section("Valid Player Creation")
    try:
        player = Player.create("John Smith", "+447123456789", "team-123")
        print(f"✅ Created player: {player.get_display_name()}")
        print(f"   Player ID: {player.player_id}")
        print(f"   Position: {player.get_position_display()}")
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    print_section("Invalid Player Creation")
    try:
        player = Player.create("", "+447123456789", "team-123")
        print(f"✅ Created player: {player.get_display_name()}")
    except ValueError as e:
        print(f"❌ Expected error: {e}")
    
    try:
        player = Player.create("John", "invalid-phone", "team-123")
        print(f"✅ Created player: {player.get_display_name()}")
    except ValueError as e:
        print(f"❌ Expected error: {e}")
    
    try:
        player = Player.create("John", "+447123456789", "team-123", email="invalid-email")
        print(f"✅ Created player: {player.get_display_name()}")
    except ValueError as e:
        print(f"❌ Expected error: {e}")


def demo_factory_methods():
    """Demonstrate factory methods."""
    print_header("Factory Methods")
    
    print_section("Model Factory")
    
    # Create using ModelFactory
    player = ModelFactory.create_player(
        "Factory Player",
        "+447123456789",
        "team-123",
        position=PlayerPosition.STRIKER,
        role=PlayerRole.CAPTAIN
    )
    print(f"✅ Created via factory: {player.get_display_name()}")
    print(f"   Position: {player.get_position_display()}")
    print(f"   Role: {player.role.value}")
    
    team = ModelFactory.create_team(
        "Factory Team",
        "Created via factory",
        status=TeamStatus.ACTIVE
    )
    print(f"✅ Created via factory: {team.get_display_name()}")
    
    match = ModelFactory.create_match(
        "team-123",
        "Opponent FC",
        datetime.now() + timedelta(days=7),
        home_away="home"
    )
    print(f"✅ Created via factory: {match.get_display_name()}")


def demo_business_logic():
    """Demonstrate business logic methods."""
    print_header("Business Logic Methods")
    
    print_section("Player Onboarding Status")
    player = Player.create("Test Player", "+447123456789", "team-123")
    print(f"Player: {player.get_display_name()}")
    print(f"Onboarding complete: {player.is_onboarding_complete()}")
    print(f"Match eligible: {player.is_match_eligible()}")
    
    # Complete onboarding
    player.onboarding_status = OnboardingStatus.COMPLETED
    player.match_eligible = True
    print(f"After completion:")
    print(f"  Onboarding complete: {player.is_onboarding_complete()}")
    print(f"  Match eligible: {player.is_match_eligible()}")
    
    print_section("FA Registration")
    player.fa_registered = True
    player.fa_eligible = True
    print(f"FA registered: {player.is_fa_registered()}")
    
    player.fa_registered = False
    print(f"After unregistering: {player.is_fa_registered()}")
    
    print_section("Team Member Roles")
    member = TeamMember.create("team-123", player.id, ["player", "captain"])
    print(f"Member: {member.get_display_name()}")
    print(f"Is player: {member.is_player()}")
    print(f"Has leadership role: {member.has_any_leadership_role()}")
    print(f"Has captain role: {member.has_role('captain')}")
    print(f"Can access main chat: {member.can_access_chat('main_chat')}")
    print(f"Can access leadership chat: {member.can_access_chat('leadership_chat')}")
    
    print_section("Match Status")
    match = Match.create("team-123", "Opponent", datetime.now() + timedelta(days=7))
    print(f"Match: {match.get_display_name()}")
    print(f"Is finished: {match.is_finished()}")
    print(f"Is home match: {match.is_home_match()}")
    
    match.status = MatchStatus.COMPLETED
    print(f"After completion: {match.is_finished()}")


def demo_enum_functionality():
    """Demonstrate enum functionality."""
    print_header("Enum Functionality")
    
    print_section("Player Positions")
    for position in PlayerPosition:
        display_name = PlayerPosition.get_display_name(position)
        print(f"  {position.value}: {display_name}")
    
    print_section("Player Roles")
    for role in PlayerRole:
        is_leadership = PlayerRole.is_leadership_role(role)
        print(f"  {role.value}: {'Leadership' if is_leadership else 'Player'}")
    
    print_section("Onboarding Status")
    for status in OnboardingStatus:
        is_completed = OnboardingStatus.is_completed(status)
        is_in_progress = OnboardingStatus.is_in_progress(status)
        print(f"  {status.value}: Completed={is_completed}, In Progress={is_in_progress}")
    
    print_section("Team Status")
    for status in TeamStatus:
        is_active = TeamStatus.is_active(status)
        print(f"  {status.value}: Active={is_active}")
    
    print_section("Match Status")
    for status in MatchStatus:
        is_finished = MatchStatus.is_finished(status)
        print(f"  {status.value}: Finished={is_finished}")


def demo_integration():
    """Demonstrate model integration."""
    print_header("Model Integration")
    
    print_section("Complete Workflow")
    
    # 1. Create team
    team = Team.create("Integration Team", "Complete workflow demonstration")
    print(f"1. Created team: {team.get_display_name()}")
    
    # 2. Create players
    player1 = Player.create("Alice Johnson", "+447123456789", team.id)
    player2 = Player.create("Bob Smith", "+447123456790", team.id)
    print(f"2. Created players:")
    print(f"   {player1.get_display_name()}")
    print(f"   {player2.get_display_name()}")
    
    # 3. Complete player onboarding
    player1.onboarding_status = OnboardingStatus.COMPLETED
    player1.match_eligible = True
    player1.fa_registered = True
    player2.onboarding_status = OnboardingStatus.COMPLETED
    player2.match_eligible = True
    print(f"3. Completed onboarding for both players")
    
    # 4. Create team members
    member1 = TeamMember.create(team.id, player1.id, ["player", "captain"])
    member2 = TeamMember.create(team.id, player2.id, ["player"])
    print(f"4. Created team members:")
    print(f"   {member1.get_display_name()}")
    print(f"   {member2.get_display_name()}")
    
    # 5. Schedule matches
    home_match = Match.create(team.id, "Home Opponent", datetime.now() + timedelta(days=7))
    away_match = Match.create(team.id, "Away Opponent", datetime.now() + timedelta(days=14), home_away="away")
    print(f"5. Scheduled matches:")
    print(f"   {home_match.get_display_name()}")
    print(f"   {away_match.get_display_name()}")
    
    # 6. Verify relationships and status
    print(f"6. Verification:")
    print(f"   Players eligible for matches: {player1.is_match_eligible()}, {player2.is_match_eligible()}")
    print(f"   Captain has leadership role: {member1.has_any_leadership_role()}")
    print(f"   Regular player has leadership role: {member2.has_any_leadership_role()}")
    print(f"   Home match is home: {home_match.is_home_match()}")
    print(f"   Away match is home: {away_match.is_home_match()}")
    print(f"   Matches finished: {home_match.is_finished()}, {away_match.is_finished()}")


def demo_serialization():
    """Demonstrate serialization and deserialization."""
    print_header("Serialization and Deserialization")
    
    print_section("Player Serialization")
    player = Player.create("Serial Player", "+447123456789", "team-123")
    player.onboarding_status = OnboardingStatus.COMPLETED
    player.match_eligible = True
    
    # Serialize
    player_dict = player.to_dict()
    print(f"Serialized keys: {list(player_dict.keys())}")
    print(f"Position (serialized): {player_dict['position']}")
    print(f"Role (serialized): {player_dict['role']}")
    print(f"Onboarding status (serialized): {player_dict['onboarding_status']}")
    
    # Deserialize
    restored_player = Player.from_dict(player_dict)
    print(f"Restored player: {restored_player.get_display_name()}")
    print(f"Position (restored): {restored_player.position}")
    print(f"Role (restored): {restored_player.role}")
    print(f"Onboarding status (restored): {restored_player.onboarding_status}")
    
    print_section("Team Serialization")
    team = Team.create("Serial Team", "Serialization test")
    team_dict = team.to_dict()
    restored_team = Team.from_dict(team_dict)
    print(f"Original team: {team.get_display_name()}")
    print(f"Restored team: {restored_team.get_display_name()}")
    print(f"Statuses match: {team.status == restored_team.status}")


def main():
    """Run all demonstrations."""
    print("🚀 KICKAI Improved Models Demonstration")
    print("This demonstrates the improved models with great OOP principles!")
    
    try:
        demo_base_model_functionality()
        demo_validation_and_error_handling()
        demo_factory_methods()
        demo_business_logic()
        demo_enum_functionality()
        demo_integration()
        demo_serialization()
        
        print_header("Demonstration Complete")
        print("✅ All demonstrations completed successfully!")
        print("\nKey improvements demonstrated:")
        print("  • Base classes with common functionality")
        print("  • Proper validation and error handling")
        print("  • Factory methods for easy creation")
        print("  • Business logic methods")
        print("  • Enum functionality with helper methods")
        print("  • Model integration and relationships")
        print("  • Serialization/deserialization")
        print("  • Type safety and documentation")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 