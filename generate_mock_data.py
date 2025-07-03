#!/usr/bin/env python3
"""
Mock Data Generator for KICKAI

This script generates realistic test data for the KICKAI system including:
- Teams with human-readable IDs
- Players with registration data
- Matches with scheduling
- Team members and bot mappings
- Registration statuses and onboarding data

Usage:
    python generate_mock_data.py
"""

import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.firebase_client import get_firebase_client
from src.database.models import (
    Team, TeamStatus, Player, PlayerPosition, PlayerRole, OnboardingStatus,
    TeamMember, BotMapping, Match, MatchStatus
)
from src.utils.id_generator import generate_team_id, generate_player_id, generate_match_id
from src.core.config import ConfigurationManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockDataGenerator:
    """Generates comprehensive mock data for KICKAI testing."""
    
    def __init__(self):
        self.firebase_client = get_firebase_client()
        self.config = ConfigurationManager()
        
        # Mock data templates
        self.team_names = [
            "BP Hatters FC",
            "Liverpool Legends",
            "Manchester United Elite",
            "Arsenal Gunners",
            "Chelsea Blues",
            "Tottenham Hotspur",
            "Manchester City Sky Blues",
            "Everton Toffees",
            "Leeds United Whites",
            "Newcastle United Magpies",
            "Aston Villa Lions",
            "West Ham United Hammers",
            "Crystal Palace Eagles",
            "Brighton & Hove Albion Seagulls",
            "Southampton Saints",
            "Leicester City Foxes"
        ]
        
        self.first_names = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
            "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark",
            "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
            "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob",
            "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
            "Brandon", "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander",
            "Patrick", "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam",
            "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle", "Walter", "Ethan",
            "Jeremy", "Harold", "Carl", "Keith", "Roger", "Gerald", "Christian", "Terry",
            "Sean", "Arthur", "Austin", "Noah", "Lawrence", "Jesse", "Joe", "Bryan",
            "Billy", "Jordan", "Albert", "Dylan", "Bruce", "Willie", "Gabriel", "Alan",
            "Juan", "Logan", "Wayne", "Roy", "Ralph", "Randy", "Eugene", "Vincent",
            "Russell", "Elijah", "Louis", "Bobby", "Philip", "Johnny"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
            "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
            "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
            "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
            "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
            "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson", "Watson",
            "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz",
            "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
            "Ross", "Foster", "Jimenez"
        ]
        
        self.phone_numbers = [
            "+447700900001", "+447700900002", "+447700900003", "+447700900004", "+447700900005",
            "+447700900006", "+447700900007", "+447700900008", "+447700900009", "+447700900010",
            "+447700900011", "+447700900012", "+447700900013", "+447700900014", "+447700900015",
            "+447700900016", "+447700900017", "+447700900018", "+447700900019", "+447700900020",
            "+447700900021", "+447700900022", "+447700900023", "+447700900024", "+447700900025",
            "+447700900026", "+447700900027", "+447700900028", "+447700900029", "+447700900030",
            "+447700900031", "+447700900032", "+447700900033", "+447700900034", "+447700900035",
            "+447700900036", "+447700900037", "+447700900038", "+447700900039", "+447700900040",
            "+447700900041", "+447700900042", "+447700900043", "+447700900044", "+447700900045",
            "+447700900046", "+447700900047", "+447700900048", "+447700900049", "+447700900050"
        ]
        
        self.positions = list(PlayerPosition)
        self.roles = list(PlayerRole)
        self.onboarding_statuses = list(OnboardingStatus)
        
        # Generated data storage
        self.generated_teams = []
        self.generated_players = []
        self.generated_matches = []
        self.generated_members = []
        self.generated_bot_mappings = []
    
    async def generate_all_data(self):
        """Generate all mock data."""
        logger.info("🚀 Starting mock data generation...")
        
        try:
            # Generate teams first
            await self.generate_teams()
            
            # Generate players for each team
            await self.generate_players()
            
            # Generate matches
            await self.generate_matches()
            
            # Generate team members
            await self.generate_team_members()
            
            # Generate bot mappings
            await self.generate_bot_mappings()
            
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
            # Generate 15-25 players per team
            num_players = random.randint(15, 25)
            
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
                        position=random.choice(self.positions),
                        role=random.choice(self.roles),
                        fa_registered=random.choice([True, False]),
                        onboarding_status=random.choice(self.onboarding_statuses),
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
        
        # Generate matches for the next 6 months
        start_date = datetime.now()
        end_date = start_date + timedelta(days=180)
        
        for i in range(50):  # Generate 50 matches
            try:
                # Select random teams
                home_team = random.choice(self.generated_teams)
                away_team = random.choice([t for t in self.generated_teams if t.id != home_team.id])
                
                # Generate random date
                match_date = start_date + timedelta(days=random.randint(1, 180))
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
    
    async def generate_team_members(self):
        """Generate team member relationships."""
        logger.info("👥 Generating team members...")
        
        for team in self.generated_teams:
            # Get players for this team
            team_players = [p for p in self.generated_players if p.team_id == team.id]
            
            for player in team_players:
                try:
                    # Create team member relationship
                    member = TeamMember(
                        team_id=team.id,
                        user_id=player.player_id,
                        role=player.role.value,
                        permissions=["read", "write"],
                        joined_at=player.created_at
                    )
                    
                    # Save to database
                    saved_member = await self.firebase_client.add_team_member(
                        team.id, player.player_id, player.role.value
                    )
                    self.generated_members.append(saved_member)
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed to create team member {player.name}: {e}")
    
    async def generate_bot_mappings(self):
        """Generate bot mappings for teams."""
        logger.info("🤖 Generating bot mappings...")
        
        for team in self.generated_teams:
            try:
                # Generate bot mapping
                bot_mapping = BotMapping(
                    team_name=team.name,
                    bot_username=f"kickai_{team.name.lower().replace(' ', '_')}_bot",
                    chat_id=f"-100{random.randint(1000000000, 9999999999)}",
                    bot_token=f"bot_token_{team.name.lower().replace(' ', '_')}",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # Save to database
                saved_mapping = await self.firebase_client.create_bot_mapping(bot_mapping)
                self.generated_bot_mappings.append(saved_mapping)
                
                logger.info(f"  ✅ Created bot mapping for team: {team.name}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to create bot mapping for {team.name}: {e}")
    
    def print_summary(self):
        """Print a summary of generated data."""
        print("\n" + "="*60)
        print("📊 MOCK DATA GENERATION SUMMARY")
        print("="*60)
        print(f"🏟️  Teams Generated: {len(self.generated_teams)}")
        print(f"👥 Players Generated: {len(self.generated_players)}")
        print(f"⚽ Matches Generated: {len(self.generated_matches)}")
        print(f"👥 Team Members Generated: {len(self.generated_members)}")
        print(f"🤖 Bot Mappings Generated: {len(self.generated_bot_mappings)}")
        
        print("\n🏟️  Sample Teams:")
        for team in self.generated_teams[:5]:
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
    """Main function to run the mock data generator."""
    print("🚀 KICKAI Mock Data Generator")
    print("="*50)
    
    # Check environment setup
    print("🔧 Checking environment setup...")
    
    # Try to load from .env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print("  ✅ Found .env file")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print("  ⚠️  No .env file found")
    
    # Check Firebase credentials
    firebase_creds = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if not firebase_creds:
        print("  ❌ FIREBASE_CREDENTIALS_JSON not found in environment")
        print("  📝 Please set up Firebase credentials:")
        print("     1. Copy your Firebase service account JSON")
        print("     2. Set it as FIREBASE_CREDENTIALS_JSON environment variable")
        print("     3. Or add it to your .env file")
        print("  🔗 For testing, you can use the Railway environment variables")
        return
    
    print("  ✅ Firebase credentials found")
    
    try:
        generator = MockDataGenerator()
        await generator.generate_all_data()
        
    except Exception as e:
        logger.error(f"❌ Failed to generate mock data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 