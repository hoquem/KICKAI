#!/usr/bin/env python3
"""
Enhanced Team Member Management Script

This script:
1. Reads the kickai_teams collection to get all teams and their settings
2. Connects to Firestore using bot configuration from .env
3. Allows user to select a team
4. Provides options to add/remove/view/update team members
5. Shows team member list in the bot's leadership chat after changes

Usage:
    python scripts/manage_team_members.py
"""

import asyncio
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from telegram import Bot
from telegram.error import TelegramError
from loguru import logger
from kickai.database.firebase_client import FirebaseClient
from kickai.core.settings import get_settings


@dataclass
class Team:
    """Represents a team with its configuration."""
    id: str
    name: str
    bot_token: Optional[str]
    main_chat_id: Optional[str]
    leadership_chat_id: Optional[str]
    settings: Dict[str, Any]


@dataclass
class TeamMember:
    """Represents a team member."""
    id: str
    team_id: str
    user_id: str
    telegram_id: Optional[str]
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    role: str
    status: str
    is_admin: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class TeamMemberManager:
    """Handles team member management operations."""
    
    def __init__(self):
        self.env_config = get_settings()
        self.firebase_client = FirebaseClient()
        self.current_team: Optional[Team] = None
        self.current_bot: Optional[Bot] = None
        
        logger.info("Initialized TeamMemberManager")
    
    async def get_all_teams(self) -> List[Team]:
        """Get all teams from the kickai_teams collection."""
        try:
            logger.info("Fetching teams from Firestore...")
            teams_data = await self.firebase_client.query_documents(
                collection="kickai_teams",
                filters=[]
            )
            
            teams = []
            for team_data in teams_data:
                team = Team(
                    id=team_data.get('id', ''),
                    name=team_data.get('name', 'Unknown Team'),
                    bot_token=team_data.get('bot_token'),
                    main_chat_id=team_data.get('main_chat_id'),
                    leadership_chat_id=team_data.get('leadership_chat_id'),
                    settings=team_data.get('settings', {})
                )
                teams.append(team)
                logger.info(f"Found team: {team.name} (ID: {team.id})")
            
            logger.info(f"Found {len(teams)} teams")
            return teams
            
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            raise
    
    def display_teams(self, teams: List[Team]) -> None:
        """Display teams for user selection."""
        print("\n" + "="*60)
        print("📋 AVAILABLE TEAMS")
        print("="*60)
        
        for i, team in enumerate(teams, 1):
            status = "✅ Configured" if team.bot_token and team.leadership_chat_id else "⚠️ Incomplete"
            print(f"{i:2d}. {team.name}")
            print(f"     ID: {team.id}")
            print(f"     Status: {status}")
            if team.bot_token:
                print(f"     Bot: {team.bot_token[:10]}...")
            if team.leadership_chat_id:
                print(f"     Leadership Chat: {team.leadership_chat_id}")
            print()
    
    def select_team(self, teams: List[Team]) -> Optional[Team]:
        """Let user select a team."""
        while True:
            try:
                choice = input("Select a team (number) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                team_index = int(choice) - 1
                if 0 <= team_index < len(teams):
                    selected_team = teams[team_index]
                    
                    if not selected_team.bot_token or not selected_team.leadership_chat_id:
                        print("⚠️ This team doesn't have complete bot configuration.")
                        print("   Bot token and leadership chat ID are required.")
                        continue
                    
                    return selected_team
                else:
                    print("❌ Invalid selection. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                return None
    
    async def set_current_team(self, team: Team) -> None:
        """Set the current team and initialize bot connection."""
        self.current_team = team
        
        if team.bot_token:
            self.current_bot = Bot(token=team.bot_token)
            logger.info(f"Set current team: {team.name} (ID: {team.id})")
            logger.info(f"Bot token: {team.bot_token[:10]}...")
            logger.info(f"Leadership chat ID: {team.leadership_chat_id}")
    
    async def get_team_members(self) -> List[TeamMember]:
        """Get all team members for the current team."""
        if not self.current_team:
            raise ValueError("No team selected")
        
        try:
            collection_name = f"kickai_{self.current_team.id}_team_members"
            members_data = await self.firebase_client.query_documents(
                collection=collection_name,
                filters=[("team_id", "==", self.current_team.id)]
            )
            
            members = []
            for member_data in members_data:
                member = TeamMember(
                    id=member_data.get('id', ''),
                    team_id=member_data.get('team_id', ''),
                    user_id=member_data.get('user_id', ''),
                    telegram_id=member_data.get('telegram_id'),
                    username=member_data.get('username'),
                    first_name=member_data.get('first_name'),
                    last_name=member_data.get('last_name'),
                    full_name=member_data.get('full_name'),
                    role=member_data.get('role', 'Team Member'),
                    status=member_data.get('status', 'active'),
                    is_admin=member_data.get('is_admin', False),
                    created_at=member_data.get('created_at'),
                    updated_at=member_data.get('updated_at')
                )
                members.append(member)
            
            logger.info(f"Found {len(members)} team members")
            return members
            
        except Exception as e:
            logger.error(f"Error fetching team members: {e}")
            raise
    
    def display_team_members(self, members: List[TeamMember]) -> None:
        """Display team members."""
        print(f"\n👥 TEAM MEMBERS - {self.current_team.name}")
        print("="*60)
        
        if not members:
            print("No team members found.")
            return
        
        for i, member in enumerate(members, 1):
            admin_badge = "👑" if member.is_admin else "👤"
            status_icon = "✅" if member.status == "active" else "❌"
            print(f"{i:2d}. {admin_badge} {member.full_name or f'{member.first_name} {member.last_name}'}")
            print(f"     Role: {member.role}")
            print(f"     Status: {status_icon} {member.status}")
            print(f"     Username: @{member.username}" if member.username else "     Username: Not set")
            print(f"     Telegram ID: {member.telegram_id}" if member.telegram_id else "     Telegram ID: Not set")
            print()
    
    async def add_team_member(self) -> bool:
        """Add a new team member."""
        print("\n➕ ADD TEAM MEMBER")
        print("-" * 30)
        
        try:
            # Get member details
            first_name = input("First name: ").strip()
            last_name = input("Last name: ").strip()
            username = input("Username (without @): ").strip()
            telegram_id = input("Telegram ID: ").strip()
            role = input("Role (Team Member/Team Administrator/Team Owner): ").strip()
            
            if not first_name or not last_name:
                print("❌ First name and last name are required.")
                return False
            
            # Determine admin status
            is_admin = role.lower() in ['team administrator', 'team owner', 'admin']
            
            # Create team member data
            member_data = {
                "team_id": self.current_team.id,
                "user_id": telegram_id or f"user_{datetime.now().timestamp()}",
                "telegram_id": telegram_id if telegram_id else None,
                "username": username if username else None,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}".strip(),
                "role": role or "Team Member",
                "status": "active",
                "is_admin": is_admin,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "registration_source": "team_member_manager_script"
            }
            
            # Add to Firestore
            collection_name = f"kickai_{self.current_team.id}_team_members"
            doc_id = f"{self.current_team.id}_{telegram_id}" if telegram_id else f"{self.current_team.id}_{member_data['user_id']}"
            
            await self.firebase_client.add_document(
                collection=collection_name,
                document_id=doc_id,
                data=member_data
            )
            
            print(f"✅ Added team member: {first_name} {last_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding team member: {e}")
            print(f"❌ Error adding team member: {e}")
            return False
    
    async def update_team_member(self, members: List[TeamMember]) -> bool:
        """Update an existing team member."""
        if not members:
            print("❌ No team members to update.")
            return False
        
        print("\n✏️ UPDATE TEAM MEMBER")
        print("-" * 30)
        
        try:
            # Let user select member
            self.display_team_members(members)
            choice = input("Select member to update (number): ").strip()
            
            member_index = int(choice) - 1
            if not (0 <= member_index < len(members)):
                print("❌ Invalid selection.")
                return False
            
            member = members[member_index]
            print(f"\nUpdating: {member.full_name}")
            
            # Get updated details
            new_role = input(f"Role (current: {member.role}): ").strip()
            new_status = input(f"Status (current: {member.status}): ").strip()
            
            # Update data
            update_data = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if new_role:
                update_data["role"] = new_role
                update_data["is_admin"] = new_role.lower() in ['team administrator', 'team owner', 'admin']
            
            if new_status:
                update_data["status"] = new_status
            
            # Update in Firestore
            collection_name = f"kickai_{self.current_team.id}_team_members"
            await self.firebase_client.update_document(
                collection=collection_name,
                document_id=member.id,
                data=update_data
            )
            
            print(f"✅ Updated team member: {member.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating team member: {e}")
            print(f"❌ Error updating team member: {e}")
            return False
    
    async def remove_team_member(self, members: List[TeamMember]) -> bool:
        """Remove a team member."""
        if not members:
            print("❌ No team members to remove.")
            return False
        
        print("\n🗑️ REMOVE TEAM MEMBER")
        print("-" * 30)
        
        try:
            # Let user select member
            self.display_team_members(members)
            choice = input("Select member to remove (number): ").strip()
            
            member_index = int(choice) - 1
            if not (0 <= member_index < len(members)):
                print("❌ Invalid selection.")
                return False
            
            member = members[member_index]
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to remove {member.full_name}? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled.")
                return False
            
            # Remove from Firestore
            collection_name = f"kickai_{self.current_team.id}_team_members"
            await self.firebase_client.delete_document(
                collection=collection_name,
                document_id=member.id
            )
            
            print(f"✅ Removed team member: {member.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing team member: {e}")
            print(f"❌ Error removing team member: {e}")
            return False
    
    async def send_team_members_to_leadership_chat(self, members: List[TeamMember]) -> None:
        """Send team members list to the leadership chat."""
        if not self.current_bot or not self.current_team.leadership_chat_id:
            print("⚠️ Cannot send to leadership chat - bot not configured.")
            return
        
        try:
            # Create message
            message = f"👥 **Team Members - {self.current_team.name}**\n\n"
            
            if not members:
                message += "No team members found."
            else:
                for i, member in enumerate(members, 1):
                    admin_badge = "👑" if member.is_admin else "👤"
                    status_icon = "✅" if member.status == "active" else "❌"
                    username = f"@{member.username}" if member.username else "No username"
                    
                    message += f"{i}. {admin_badge} **{member.full_name}**\n"
                    message += f"   Role: {member.role}\n"
                    message += f"   Status: {status_icon} {member.status}\n"
                    message += f"   Username: {username}\n\n"
            
            # Send message
            await self.current_bot.send_message(
                chat_id=self.current_team.leadership_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            print("✅ Team members list sent to leadership chat.")
            
        except Exception as e:
            logger.error(f"Error sending to leadership chat: {e}")
            print(f"❌ Error sending to leadership chat: {e}")
    
    def show_menu(self) -> str:
        """Show the main menu."""
        print(f"\n🎯 TEAM MEMBER MANAGEMENT - {self.current_team.name}")
        print("=" * 60)
        print("1. View team members")
        print("2. Add team member")
        print("3. Update team member")
        print("4. Remove team member")
        print("5. Send members list to leadership chat")
        print("6. Change team")
        print("7. Exit")
        print("-" * 60)
        
        return input("Select option (1-7): ").strip()
    
    async def run(self) -> None:
        """Main execution method."""
        logger.info("🚀 Starting Team Member Management Script")
        
        try:
            # Get all teams
            teams = await self.get_all_teams()
            
            if not teams:
                print("❌ No teams found in Firestore.")
                return
            
            # Display teams and let user select
            self.display_teams(teams)
            selected_team = self.select_team(teams)
            
            if not selected_team:
                print("👋 Goodbye!")
                return
            
            # Set current team
            await self.set_current_team(selected_team)
            
            # Main menu loop
            while True:
                choice = self.show_menu()
                
                if choice == '1':
                    # View team members
                    members = await self.get_team_members()
                    self.display_team_members(members)
                    
                elif choice == '2':
                    # Add team member
                    success = await self.add_team_member()
                    if success:
                        members = await self.get_team_members()
                        await self.send_team_members_to_leadership_chat(members)
                    
                elif choice == '3':
                    # Update team member
                    members = await self.get_team_members()
                    success = await self.update_team_member(members)
                    if success:
                        updated_members = await self.get_team_members()
                        await self.send_team_members_to_leadership_chat(updated_members)
                    
                elif choice == '4':
                    # Remove team member
                    members = await self.get_team_members()
                    success = await self.remove_team_member(members)
                    if success:
                        updated_members = await self.get_team_members()
                        await self.send_team_members_to_leadership_chat(updated_members)
                    
                elif choice == '5':
                    # Send to leadership chat
                    members = await self.get_team_members()
                    await self.send_team_members_to_leadership_chat(members)
                    
                elif choice == '6':
                    # Change team
                    self.display_teams(teams)
                    selected_team = self.select_team(teams)
                    if selected_team:
                        await self.set_current_team(selected_team)
                    else:
                        print("👋 Goodbye!")
                        break
                    
                elif choice == '7':
                    # Exit
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid option. Please try again.")
                
                if choice in ['1', '2', '3', '4', '5']:
                    input("\nPress Enter to continue...")
        
        except Exception as e:
            logger.error(f"❌ Error in team member management: {e}")
            print(f"❌ Error: {e}")
        
        finally:
            if self.current_bot:
                await self.current_bot.close()


async def main():
    """Main function."""
    print("🤖 Enhanced Team Member Management Script")
    print("=" * 60)
    
    try:
        # Create and run the manager
        manager = TeamMemberManager()
        await manager.run()
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        print(f"❌ Fatal error: {e}")


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the script
    asyncio.run(main()) 