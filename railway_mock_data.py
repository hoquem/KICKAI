#!/usr/bin/env python3
"""
Railway Mock Data Generator

This script is designed to run directly in the Railway environment
to generate mock data for testing.
"""

import os
import sys
import asyncio
import random
import logging
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, '/app/src')

# Set environment to testing
os.environ['ENVIRONMENT'] = 'testing'

from src.database.firebase_client import get_firebase_client
from src.database.models import (
    Team, TeamStatus, Player, PlayerPosition, PlayerRole, OnboardingStatus,
    TeamMember, BotMapping, Match, MatchStatus
)
from src.utils.id_generator import generate_team_id, generate_player_id, generate_match_id

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RailwayMockDataGenerator:
    """Mock data generator for Railway environment."""
    
    def __init__(self):
        self.firebase_client = get_firebase_client()
        
        # Mock data templates
        self.team_names = [
            "BP Hatters FC",
            "Liverpool Legends",
            "Manchester United Elite",
            "Arsenal Gunners",
            "Chelsea Blues",
            "Tottenham Hotspur",
            "Manchester City Sky Blues",
            "Everton Toffees"
        ]
        
        self.first_names = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
            "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"
        ]
        
        self.phone_numbers = [
            "+447700900001", "+447700900002", "+447700900003", "+447700900004", "+447700900005",
            "+447700900006", "+447700900007", "+447700900008", "+447700900009", "+447700900010"
        ]
        
        # Generated data storage
        self.generated_teams = []
        self.generated_players = []
        self.generated_matches = []
    
    async def generate_all_data(self):
        """Generate all mock data."""
        logger.info("🚀 Starting Railway mock data generation...")
        
        try:
            # Generate teams first
            await self.generate_teams()
            
            # Generate players for each team
            await self.generate_players()
            
            # Generate matches
            await self.generate_matches()
            
            logger.info("✅ All mock data generated successfully!")
            self.print_summary()
            
        except Exception as e:
            logger.error(f"❌ Error generating mock data: {e}")
            raise
    
    async def generate_teams(self):
        """Generate teams with human-readable IDs."""
        logger.info("🏟️ Generating teams...")
        
        for team_name in self.team_names:
            try:
                # Generate human-readable team ID
                team_id = generate_team_id(team_name)
                
                # Create team object
                team = Team(
                    id=team_id,
                    name=team_name,
                    description=f"Professional football team: {team_name}",
                    status=TeamStatus.ACTIVE,
                    settings={
                        "max_players": random.randint(20, 30),
                        "training_days": ["Monday", "Wednesday", "Friday"],
                        "home_ground": f"{team_name} Stadium",
                        "founded_year": random.randint(1880, 2000)
                    }
                )
                
                # Save to database
                saved_team_id = await self.firebase_client.create_team(team)
                team.id = saved_team_id
                self.generated_teams.append(team)
                
                logger.info(f"  ✅ Created team: {team_name} (ID: {team_id}, Saved ID: {saved_team_id})")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to create team {team_name}: {e}")
    
    async def generate_players(self):
        """Generate players for each team."""
        logger.info("👥 Generating players...")
        
        for team in self.generated_teams:
            # Generate 10-15 players per team
            num_players = random.randint(10, 15)
            
            for i in range(num_players):
                try:
                    # Generate player data
                    first_name = random.choice(self.first_names)
                    last_name = random.choice(self.last_names)
                    name = f"{first_name} {last_name}"
                    
                    # Generate human-readable player ID
                    existing_ids = {p.player_id for p in self.generated_players if p.team_id == team.id}
                    player_id = generate_player_id(first_name, last_name, existing_ids)
                    
                    # Create player object
                    player = Player(
                        player_id=player_id,
                        name=name,
                        phone=random.choice(self.phone_numbers),
                        email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                        team_id=team.id,
                        position=random.choice(list(PlayerPosition)),
                        role=random.choice(list(PlayerRole)),
                        fa_registered=random.choice([True, False]),
                        onboarding_status=random.choice(list(OnboardingStatus)),
                        invite_link=f"https://t.me/kickai_bot?start={player_id}",
                        created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                        updated_at=datetime.now()
                    )
                    
                    # Save to database
                    saved_player = await self.firebase_client.create_player(player)
                    self.generated_players.append(saved_player)
                    
                    logger.info(f"  ✅ Created player: {name} ({player_id}) for team {team.name}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed to create player {name}: {e}")
    
    async def generate_matches(self):
        """Generate matches between teams."""
        logger.info("⚽ Generating matches...")
        
        # Generate matches for the next 3 months
        start_date = datetime.now()
        
        for i in range(20):  # Generate 20 matches
            try:
                # Select random teams
                home_team = random.choice(self.generated_teams)
                away_team = random.choice([t for t in self.generated_teams if t.id != home_team.id])
                
                # Generate random date
                match_date = start_date + timedelta(days=random.randint(1, 90))
                date_str = match_date.strftime("%d/%m/%Y")
                time_str = f"{random.randint(10, 20):02d}:{random.choice(['00', '15', '30', '45'])}"
                
                # Generate human-readable match ID
                match_id = generate_match_id(home_team.name, away_team.name, date_str, time_str)
                
                # Create match object
                match = Match(
                    id=match_id,
                    team_id=home_team.id,
                    opponent=away_team.name,
                    date=match_date,
                    location=f"{home_team.name} Stadium",
                    status=MatchStatus.SCHEDULED,
                    home_away="home",
                    competition="League Match",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # Save to database
                saved_match = await self.firebase_client.create_match(match)
                self.generated_matches.append(saved_match)
                
                logger.info(f"  ✅ Created match: {home_team.name} vs {away_team.name} on {date_str} ({match_id})")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to create match: {e}")
    
    def print_summary(self):
        """Print a summary of generated data."""
        print("\n" + "="*60)
        print("📊 RAILWAY MOCK DATA GENERATION SUMMARY")
        print("="*60)
        print(f"🏟️  Teams Generated: {len(self.generated_teams)}")
        print(f"👥 Players Generated: {len(self.generated_players)}")
        print(f"⚽ Matches Generated: {len(self.generated_matches)}")
        
        print("\n🏟️  Generated Teams:")
        for team in self.generated_teams:
            print(f"  - {team.name} (ID: {team.id})")
        
        print("\n👥 Sample Players:")
        for player in self.generated_players[:5]:
            print(f"  - {player.name} ({player.player_id}) - {player.position.value}")
        
        print("\n⚽ Sample Matches:")
        for match in self.generated_matches[:5]:
            print(f"  - Team {match.team_id} vs {match.opponent} on {match.date.strftime('%d/%m/%Y')}")
        
        print("\n✅ Mock data generation complete!")
        print("="*60)


async def main():
    """Main function."""
    print("🚀 Railway Mock Data Generator")
    print("="*50)
    
    try:
        generator = RailwayMockDataGenerator()
        await generator.generate_all_data()
        
    except Exception as e:
        logger.error(f"❌ Failed to generate mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 