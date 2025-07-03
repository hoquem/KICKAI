#!/usr/bin/env python3
"""
Simple Mock Data Generator for KICKAI

This script generates realistic test data for the KICKAI system.
It's designed to work with the current environment setup.
"""

import asyncio
import random
import logging
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleMockDataGenerator:
    """Simple mock data generator for testing."""
    
    def __init__(self):
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
    
    def generate_team_data(self):
        """Generate sample team data."""
        print("🏟️  Sample Team Data:")
        print("=" * 40)
        
        for team_name in self.team_names:
            from src.utils.id_generator import generate_team_id
            team_id = generate_team_id(team_name)
            print(f"  {team_name:<25} -> {team_id}")
    
    def generate_player_data(self):
        """Generate sample player data."""
        print("\n👥 Sample Player Data:")
        print("=" * 40)
        
        existing_ids = set()
        for i in range(20):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            
            from src.utils.id_generator import generate_player_id
            player_id = generate_player_id(first_name, last_name, existing_ids)
            
            print(f"  {first_name:<12} {last_name:<12} -> {player_id}")
    
    def generate_match_data(self):
        """Generate sample match data."""
        print("\n⚽ Sample Match Data:")
        print("=" * 40)
        
        for i in range(10):
            home_team = random.choice(self.team_names)
            away_team = random.choice([t for t in self.team_names if t != home_team])
            
            # Generate random date
            match_date = datetime.now() + timedelta(days=random.randint(1, 90))
            date_str = match_date.strftime("%d/%m/%Y")
            time_str = f"{random.randint(10, 20):02d}:{random.choice(['00', '15', '30', '45'])}"
            
            from src.utils.id_generator import generate_match_id
            match_id = generate_match_id(home_team, away_team, date_str, time_str)
            
            print(f"  {home_team:<20} vs {away_team:<20} on {date_str} @ {time_str} -> {match_id}")
    
    def generate_all_sample_data(self):
        """Generate all sample data."""
        print("🚀 KICKAI Sample Data Generator")
        print("=" * 50)
        
        try:
            self.generate_team_data()
            self.generate_player_data()
            self.generate_match_data()
            
            print("\n✅ Sample data generation complete!")
            print("\n📝 To add this data to Firebase:")
            print("   1. Set up Firebase credentials in your environment")
            print("   2. Run: python generate_mock_data.py")
            print("   3. Or use the Railway deployment with proper credentials")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate sample data: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function."""
    generator = SimpleMockDataGenerator()
    generator.generate_all_sample_data()


if __name__ == "__main__":
    main() 