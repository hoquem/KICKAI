#!/usr/bin/env python3
"""
Service Interfaces Example

This script demonstrates how to use service interfaces and mocks
for dependency injection and testing.
"""

import asyncio
import logging
from typing import Dict, Any

# Import interfaces
from src.services.interfaces import (
    IPlayerService, ITeamService, IFARegistrationChecker
)

# Import mock implementations
from src.services.mocks import (
    MockPlayerService, MockTeamService, MockFARegistrationChecker
)

# Import models
from src.database.models import PlayerPosition, OnboardingStatus


class PlayerOnboardingService:
    """
    Example service that demonstrates dependency injection using interfaces.
    
    This service orchestrates the player onboarding process by coordinating
    between different services through their interfaces.
    """
    
    def __init__(self,
                 player_service: IPlayerService,
                 team_service: ITeamService,
                 fa_checker: IFARegistrationChecker):
        self.player_service = player_service
        self.team_service = team_service
        self.fa_checker = fa_checker
        self.logger = logging.getLogger(__name__)
    
    async def onboard_new_player(self, 
                                name: str, 
                                phone: str, 
                                team_id: str,
                                position: PlayerPosition = PlayerPosition.UTILITY) -> Dict[str, Any]:
        """
        Complete onboarding process for a new player.
        
        Args:
            name: Player's full name
            phone: Player's phone number
            team_id: ID of the team to join
            position: Player's preferred position
            
        Returns:
            Dictionary containing onboarding results
        """
        self.logger.info(f"Starting onboarding for {name}")
        
        try:
            # Step 1: Create player record
            player = await self.player_service.create_player(
                name=name,
                phone=phone,
                team_id=team_id,
                position=position
            )
            self.logger.info(f"Created player: {player.name} ({player.id})")
            
            # Step 2: Update onboarding status to in progress
            player = await self.player_service.update_onboarding_status(
                player.id, OnboardingStatus.IN_PROGRESS
            )
            self.logger.info(f"Updated onboarding status: {player.onboarding_status}")
            
            # Step 3: Add player to team
            member = await self.team_service.add_team_member(
                team_id=team_id,
                user_id=player.id,
                role="player"
            )
            self.logger.info(f"Added player to team: {member.user_id}")
            
            # Step 4: Check FA registration status
            fa_updates = await self.fa_checker.check_player_registration(team_id)
            self.logger.info(f"FA registration updates: {len(fa_updates)} players")
            
            # Step 5: Complete onboarding
            player = await self.player_service.update_onboarding_status(
                player.id, OnboardingStatus.COMPLETED
            )
            self.logger.info(f"Completed onboarding for {player.name}")
            
            # Step 6: Get final team info
            team = await self.team_service.get_team(team_id)
            team_members = await self.team_service.get_team_members(team_id)
            
            return {
                "success": True,
                "player": {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position.value,
                    "onboarding_status": player.onboarding_status.value,
                    "fa_registered": player.fa_registered
                },
                "team": {
                    "id": team.id if team else "unknown",
                    "name": team.name if team else "unknown",
                    "member_count": len(team_members)
                },
                "fa_updates": fa_updates
            }
            
        except Exception as e:
            self.logger.error(f"Onboarding failed for {name}: {e}")
            return {
                "success": False,
                "error": str(e)
            }


async def demonstrate_with_mocks():
    """Demonstrate using interfaces with mock implementations."""
    print("=== Demonstrating Service Interfaces with Mocks ===\n")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create mock services
    player_service = MockPlayerService()
    team_service = MockTeamService()
    fa_checker = MockFARegistrationChecker(player_service)
    
    # Create the onboarding service with injected dependencies
    onboarding_service = PlayerOnboardingService(
        player_service=player_service,
        team_service=team_service,
        fa_checker=fa_checker
    )
    
    # Create a team first
    team = await team_service.create_team("KICKAI Team", "Example team for demonstration")
    print(f"Created team: {team.name} ({team.id})")
    
    # Set up some FA registered players for the mock
    fa_checker.set_registered_players(["John Smith", "Jane Doe"])
    
    # Onboard a new player
    result = await onboarding_service.onboard_new_player(
        name="John Smith",
        phone="07123456789",
        team_id=team.id,
        position=PlayerPosition.MIDFIELDER
    )
    
    print(f"\nOnboarding result: {result}")
    
    if result["success"]:
        print(f"✅ Successfully onboarded {result['player']['name']}")
        print(f"   Position: {result['player']['position']}")
        print(f"   Team: {result['team']['name']}")
        print(f"   FA Registered: {result['player']['fa_registered']}")
        print(f"   Team Members: {result['team']['member_count']}")
    else:
        print(f"❌ Onboarding failed: {result['error']}")
    
    # Demonstrate getting team players
    team_players = await player_service.get_team_players(team.id)
    print(f"\nTeam players: {len(team_players)}")
    for player in team_players:
        print(f"  - {player.name} ({player.position.value})")
    
    # Demonstrate getting team members
    team_members = await team_service.get_team_members(team.id)
    print(f"\nTeam members: {len(team_members)}")
    for member in team_members:
        print(f"  - User {member.user_id} (roles: {member.roles})")


async def demonstrate_with_real_services():
    """Demonstrate using interfaces with real service implementations."""
    print("\n=== Demonstrating Service Interfaces with Real Services ===\n")
    
    # Note: This would use real service implementations
    # For now, we'll just show the structure
    
    print("To use real services, you would:")
    print("1. Import the real service implementations")
    print("2. Initialize them with real data stores")
    print("3. Inject them into the onboarding service")
    print("4. The rest of the code remains exactly the same!")
    
    print("\nExample:")
    print("""
    from src.services.player_service import PlayerService
    from src.services.team_service import TeamService
    from src.services.fa_registration_checker import FARegistrationChecker
    
    # Initialize with real data stores
    player_service = PlayerService(data_store=real_firebase_client)
    team_service = TeamService(data_store=real_firebase_client)
    fa_checker = FARegistrationChecker(player_service)
    
    # Use exactly the same onboarding service
    onboarding_service = PlayerOnboardingService(
        player_service=player_service,
        team_service=team_service,
        fa_checker=fa_checker
    )
    """)


def demonstrate_testing_benefits():
    """Demonstrate the testing benefits of using interfaces."""
    print("\n=== Testing Benefits of Service Interfaces ===\n")
    
    print("1. **Easy Mocking**: Create mock implementations for testing")
    print("   - No need to set up real databases")
    print("   - No external dependencies")
    print("   - Predictable behavior")
    print("   - Fast test execution")
    
    print("\n2. **Dependency Injection**: Services depend on interfaces, not concrete implementations")
    print("   - Easy to swap implementations")
    print("   - Easy to test in isolation")
    print("   - Easy to inject test doubles")
    
    print("\n3. **Contract Enforcement**: Interfaces define clear contracts")
    print("   - All implementations must provide the same methods")
    print("   - Type safety and IDE support")
    print("   - Clear documentation of expected behavior")
    
    print("\n4. **Test Isolation**: Each service can be tested independently")
    print("   - Mock dependencies to focus on the service under test")
    print("   - Control test data and scenarios")
    print("   - Test error conditions easily")


async def main():
    """Main demonstration function."""
    print("Service Interfaces and Dependency Injection Demonstration")
    print("=" * 60)
    
    # Demonstrate with mocks
    await demonstrate_with_mocks()
    
    # Demonstrate with real services
    await demonstrate_with_real_services()
    
    # Show testing benefits
    demonstrate_testing_benefits()
    
    print("\n" + "=" * 60)
    print("Demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main()) 