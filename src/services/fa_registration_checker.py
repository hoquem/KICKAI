#!/usr/bin/env python3
"""
FA Registration Checker Service

This service periodically checks the FA website to verify if players have been
registered with the Football Association. It scrapes the BP Hatters FC team page
to check player registration status.
"""

import asyncio
import aiohttp
import re
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging

from services.player_service import PlayerService
from services.team_service import TeamService
from database.models_improved import Player, FixtureData
from database.firebase_client import get_firebase_client
from services.interfaces.fa_registration_checker_interface import IFARegistrationChecker

class FARegistrationChecker(IFARegistrationChecker):
    """Service to check FA registration status for players."""
    
    def __init__(self, player_service: PlayerService, team_service: TeamService, team_id: str):
        self.player_service = player_service
        self.team_service = team_service
        self.team_id = team_id
        self.fa_team_url: Optional[str] = None
        self.fa_fixtures_url: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._db = get_firebase_client()

    async def _load_fa_urls(self):
        team = await self.team_service.get_team(self.team_id)
        if team:
            self.fa_team_url = team.fa_team_url
            self.fa_fixtures_url = team.fa_fixtures_url
        else:
            logging.warning(f"Team {self.team_id} not found. Cannot load FA URLs.")

    async def __aenter__(self):
        """Async context manager entry."""
        await self._load_fa_urls()
        if not self.fa_team_url or not self.fa_fixtures_url:
            raise RuntimeError(f"FA URLs not configured for team {self.team_id}")
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def scrape_team_page(self) -> Dict[str, bool]:
        """
        Scrape the FA team page to get registered players.
        
        Returns:
            Dict mapping player names to registration status (True = registered)
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        try:
            logging.info(f"🔍 Scraping FA team page: {self.fa_team_url}")
            
            async with self.session.get(self.fa_team_url) as response:
                if response.status != 200:
                    logging.error(f"❌ Failed to fetch FA team page: {response.status}")
                    return {}
                    
                html = await response.text()
                
            # Parse the HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract player names from the team page
            # The FA site structure may vary, so we'll look for common patterns
            registered_players = set()
            
            # Look for player names in various possible locations
            # This is a generic approach - may need adjustment based on actual FA site structure
            player_elements = soup.find_all(['td', 'div', 'span'], string=re.compile(r'[A-Z][a-z]+ [A-Z][a-z]+'))
            
            for element in player_elements:
                text = element.get_text().strip()
                if len(text.split()) >= 2:  # At least first and last name
                    registered_players.add(text.lower())
            
            logging.info(f"✅ Found {len(registered_players)} registered players on FA site")
            logging.debug(f"Registered players: {list(registered_players)}")
            
            return {name: True for name in registered_players}
            
        except Exception as e:
            logging.error(f"❌ Error scraping FA team page: {e}")
            return {}
    
    async def check_player_registration(self, team_id: str) -> Dict[str, bool]:
        """
        Check FA registration status for all players in a team.
        
        Args:
            team_id: The team ID to check players for
            
        Returns:
            Dict mapping player IDs to registration status updates
        """
        try:
            # Get all players that need FA registration check
            players = await self.player_service.get_team_players(team_id)
            
            # Filter players that are not yet FA registered
            players_to_check = [
                p for p in players 
                if not p.is_fa_registered() and p.is_onboarding_complete()
            ]
            
            if not players_to_check:
                logging.info("✅ No players need FA registration check")
                return {}
            
            logging.info(f"🔍 Checking FA registration for {len(players_to_check)} players")
            
            # Scrape FA website
            fa_registered_players = await self.scrape_team_page()
            
            # Check each player against FA data
            updates = {}
            for player in players_to_check:
                player_name = player.name.lower()
                
                # Check if player is found in FA registered list
                is_registered = player_name in fa_registered_players
                
                if is_registered and not player.is_fa_registered():
                    logging.info(f"✅ Player {player.name} is now FA registered!")
                    updates[player.id] = True
                    
                    # Update player in database
                    await self.player_service.update_player(
                        player.id,
                        fa_registered=True,
                        fa_registration_date=datetime.now()
                    )
                    
            if updates:
                logging.info(f"✅ Updated {len(updates)} players as FA registered")
            else:
                logging.info("ℹ️ No new FA registrations found")
                
            return updates
            
        except Exception as e:
            logging.error(f"❌ Error checking FA registration: {e}")
            return {}
    
    async def scrape_fixtures(self) -> List[Dict]:
        """
        Scrape fixtures and match results from FA website.
        
        Returns:
            List of fixture/match data
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        try:
            logging.info(f"🔍 Scraping FA fixtures page: {self.fa_fixtures_url}")
            
            async with self.session.get(self.fa_fixtures_url) as response:
                if response.status != 200:
                    logging.error(f"❌ Failed to fetch FA fixtures page: {response.status}")
                    return []
                    
                html = await response.text()
                
            # Parse the HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            fixtures = []
            
            # Look for fixture data in tables or other structures
            # This is a generic approach - may need adjustment based on actual FA site structure
            fixture_elements = soup.find_all(['tr', 'div'], class_=re.compile(r'fixture|match|result'))
            
            for element in fixture_elements:
                text = element.get_text().strip()
                if any(keyword in text.lower() for keyword in ['vs', 'v', 'home', 'away', 'result']):
                    fixtures.append({
                        'text': text,
                        'timestamp': datetime.now().isoformat()
                    })
            
            logging.info(f"✅ Found {len(fixtures)} fixtures/results on FA site")
            
            # Save fixtures to Firestore
            await self._save_fixture_data(fixtures)

            return fixtures
            
        except Exception as e:
            logging.error(f"❌ Error scraping FA fixtures: {e}")
            return []

    async def _save_fixture_data(self, fixtures: List[Dict]) -> None:
        """Saves scraped fixture data to Firestore."""
        try:
            for fixture_dict in fixtures:
                # Create FixtureData object
                fixture = FixtureData(
                    team_id=self.team_id,
                    fixture_text=fixture_dict['text'],
                    fixture_date=datetime.fromisoformat(fixture_dict['timestamp'])
                )
                # Save to Firestore
                await self._db.create_document('fixtures', fixture.to_dict(), fixture.id)
            logging.info(f"✅ Saved {len(fixtures)} fixtures to Firestore.")
        except Exception as e:
            logging.error(f"❌ Error saving fixture data to Firestore: {e}")


async def run_fa_registration_check(team_id: str, player_service: PlayerService, team_service: TeamService) -> Dict[str, bool]:
    """Run a single FA registration check for a team."""
    async with FARegistrationChecker(player_service, team_service, team_id) as checker:
        return await checker.check_player_registration(team_id)


async def run_fa_fixtures_check(team_id: str, player_service: PlayerService, team_service: TeamService) -> List[Dict]:
    """Run FA fixtures check for a team."""
    async with FARegistrationChecker(player_service, team_service, team_id) as checker:
        return await checker.scrape_fixtures()


# Global instances - now team-specific
_fa_registration_checker_instances: dict[str, FARegistrationChecker] = {}

def get_fa_registration_checker(team_id: Optional[str] = None):
    """Get a FA registration checker instance for the specified team."""
    global _fa_registration_checker_instances
    
    # Use default team ID if not provided
    if not team_id:
        import os
        team_id = os.getenv('DEFAULT_TEAM_ID', 'KAI')
    
    # Return existing instance if available for this team
    if team_id in _fa_registration_checker_instances:
        return _fa_registration_checker_instances[team_id]
    
    # Create new instance for this team
    from services.player_service import get_player_service
    from services.team_service import get_team_service
    from core.settings import get_settings
    
    config = get_settings()
    
    player_service = get_player_service(team_id=team_id)
    team_service = get_team_service(team_id=team_id)
    
    fa_checker = FARegistrationChecker(player_service, team_service, team_id)
    _fa_registration_checker_instances[team_id] = fa_checker
    
    logging.info(f"Created new FARegistrationChecker instance for team: {team_id}")
    return fa_checker 