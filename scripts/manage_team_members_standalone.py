#!/usr/bin/env python3
"""
Standalone Team Member Management Script

This script:
1. Reads the kickai_teams collection to get all teams and their settings
2. Connects to Firestore using bot configuration from .env
3. Allows user to select a team
4. Provides options to add/remove/view/update team members
5. Shows team member list in the bot's leadership chat after changes

Usage:
    python scripts/manage_team_members_standalone.py
"""

import asyncio
import os
import sys
import json
import warnings
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Suppress Firestore warnings about positional arguments
warnings.filterwarnings("ignore", message="Detected filter using positional arguments")

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
from kickai.utils.user_id_generator import generate_user_id

# Direct Firestore imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud import firestore as firestore_client
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    print("❌ Firebase Admin SDK not available. Please install: pip install firebase-admin")


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
    """Represents a team member (administrator/manager)."""
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
    
    # Contact information
    phone_number: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    
    # Metadata
    source: Optional[str] = None
    sync_version: Optional[str] = None


@dataclass
class TelegramMember:
    """Represents a member from Telegram chat."""
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    is_admin: bool
    join_date: Optional[str]


class StandaloneFirebaseClient:
    """Simple Firebase client for team management."""
    
    def __init__(self):
        self.db = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection."""
        try:
            # Check if Firebase app is already initialized
            try:
                firebase_admin.get_app()
                logger.info("✅ Using existing Firebase app")
            except ValueError:
                logger.info("🔄 Initializing new Firebase app...")
                
                # Get credentials from environment
                firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
                firebase_creds_file = os.getenv('FIREBASE_CREDENTIALS_FILE')
                
                if firebase_creds_json:
                    try:
                        creds_dict = json.loads(firebase_creds_json)
                        cred = credentials.Certificate(creds_dict)
                        logger.info("✅ Credentials created from JSON string")
                    except Exception as e:
                        raise RuntimeError(f"Failed to create credentials from JSON: {e}")
                elif firebase_creds_file:
                    try:
                        cred = credentials.Certificate(firebase_creds_file)
                        logger.info(f"✅ Credentials created from file: {firebase_creds_file}")
                    except Exception as e:
                        raise RuntimeError(f"Failed to load credentials from file {firebase_creds_file}: {e}")
                else:
                    raise RuntimeError("No Firebase credentials found. Please set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_FILE environment variables.")
                
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase app initialized")
            
            # Get Firestore client
            self.db = firestore.client()
            logger.info("✅ Firestore client ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase: {e}")
            raise
    
    async def query_documents(self, collection: str, filters: List[tuple] = None) -> List[Dict[str, Any]]:
        """Query documents from Firestore."""
        try:
            coll_ref = self.db.collection(collection)
            
            # Apply filters - using where() method but suppressing the warning
            if filters:
                for field, operator, value in filters:
                    coll_ref = coll_ref.where(field, operator, value)
            
            # Get documents
            docs = coll_ref.stream()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying documents from {collection}: {e}")
            raise
    
    async def add_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> None:
        """Add a document to Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.set(data)
            logger.info(f"✅ Added document {document_id} to {collection}")
            
        except Exception as e:
            logger.error(f"Error adding document to {collection}: {e}")
            raise
    
    async def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> None:
        """Update a document in Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            logger.info(f"✅ Updated document {document_id} in {collection}")
            
        except Exception as e:
            logger.error(f"Error updating document in {collection}: {e}")
            raise
    
    async def delete_document(self, collection: str, document_id: str) -> None:
        """Delete a document from Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.delete()
            logger.info(f"✅ Deleted document {document_id} from {collection}")
            
        except Exception as e:
            logger.error(f"Error deleting document from {collection}: {e}")
            raise


class TeamMemberManager:
    """Handles team member management operations."""
    
    def __init__(self):
        if not FIRESTORE_AVAILABLE:
            raise RuntimeError("Firebase Admin SDK not available")
        
        self.firebase_client = StandaloneFirebaseClient()
        self.current_team: Optional[Team] = None
        self.current_bot: Optional[Bot] = None
        
        logger.info("Initialized TeamMemberManager")
    
    async def get_all_teams(self) -> List[Team]:
        """Get all teams from the kickai_teams collection."""
        try:
            logger.info("Fetching teams from Firestore...")
            teams_data = await self.firebase_client.query_documents("kickai_teams")
            
            teams = []
            for team_data in teams_data:
                settings = team_data.get('settings', {})
                team = Team(
                    id=team_data.get('id', ''),
                    name=team_data.get('name', 'Unknown Team'),
                    bot_token=team_data.get('bot_token'),
                    main_chat_id=team_data.get('main_chat_id'),
                    leadership_chat_id=team_data.get('leadership_chat_id'),
                    settings=settings
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
                collection_name,
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
                    updated_at=member_data.get('updated_at'),
                    
                    # Contact information
                    phone_number=member_data.get('phone_number'),
                    email=member_data.get('email'),
                    emergency_contact=member_data.get('emergency_contact'),
                    
                    # Metadata
                    source=member_data.get('source'),
                    sync_version=member_data.get('sync_version')
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
            
            # Show additional fields if available
            if member.phone_number:
                print(f"     Phone: {member.phone_number}")
            if member.email:
                print(f"     Email: {member.email}")
            if member.emergency_contact:
                print(f"     Emergency: {member.emergency_contact}")
            if member.source:
                print(f"     Source: {member.source}")
            
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
                collection_name,
                doc_id,
                member_data
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
                collection_name,
                member.id,
                update_data
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
                collection_name,
                member.id
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
    
    async def get_telegram_chat_members(self) -> List[TelegramMember]:
        """Get all human members from the Telegram leadership chat (excluding bots)."""
        if not self.current_bot or not self.current_team.leadership_chat_id:
            print("❌ Bot not configured or leadership chat ID missing.")
            return []
        
        try:
            chat_members = await self.current_bot.get_chat_administrators(
                chat_id=self.current_team.leadership_chat_id
            )
            
            members = []
            for member in chat_members:
                # Skip bot accounts
                if member.user.is_bot:
                    logger.info(f"Skipping bot account: {member.user.username} ({member.user.id})")
                    continue
                
                full_name = f"{member.user.first_name or ''} {member.user.last_name or ''}".strip()
                if not full_name:
                    full_name = member.user.first_name or "Unknown"
                
                telegram_member = TelegramMember(
                    telegram_id=member.user.id,
                    username=member.user.username,
                    first_name=member.user.first_name,
                    last_name=member.user.last_name,
                    full_name=full_name,
                    is_admin=member.status in ['creator', 'administrator'],
                    join_date=None  # Telegram API doesn't provide join date easily
                )
                members.append(telegram_member)
            
            logger.info(f"Found {len(members)} human members in Telegram leadership chat")
            return members
            
        except Exception as e:
            logger.error(f"Error fetching Telegram chat members: {e}")
            print(f"❌ Error fetching Telegram chat members: {e}")
            return []
    
    async def synchronize_team_members(self) -> None:
        """Main synchronization workflow between Telegram and Firestore."""
        print("\n🔄 SYNCHRONIZING TEAM MEMBERS")
        print("=" * 50)
        
        # Get members from both sources
        telegram_members = await self.get_telegram_chat_members()
        firestore_members = await self.get_team_members()
        
        print(f"📊 Analysis Results:")
        print(f"   Telegram Leadership Chat: {len(telegram_members)} members")
        print(f"   Firestore Database: {len(firestore_members)} members")
        
        # Create lookup dictionaries
        telegram_lookup = {member.telegram_id: member for member in telegram_members}
        firestore_lookup = {member.telegram_id: member for member in firestore_members if member.telegram_id}
        
        # Categorize members
        telegram_only = []
        firestore_only = []
        synchronized = []
        
        # Find Telegram-only members
        for telegram_member in telegram_members:
            if str(telegram_member.telegram_id) not in firestore_lookup:
                telegram_only.append(telegram_member)
            else:
                synchronized.append((telegram_member, firestore_lookup[str(telegram_member.telegram_id)]))
        
        # Find Firestore-only members
        for firestore_member in firestore_members:
            if firestore_member.telegram_id and int(firestore_member.telegram_id) not in telegram_lookup:
                firestore_only.append(firestore_member)
        
        # Display results
        print(f"\n📋 Member Categories:")
        print(f"   🔵 Telegram Only: {len(telegram_only)} members")
        print(f"   🟡 Firestore Only: {len(firestore_only)} members")
        print(f"   🟢 Synchronized: {len(synchronized)} members")
        
        # Process Telegram-only members
        if telegram_only:
            print(f"\n🔵 TELEGRAM-ONLY MEMBERS (Add to Firestore)")
            print("-" * 50)
            for i, member in enumerate(telegram_only, 1):
                admin_badge = "👑" if member.is_admin else "👤"
                username = f"@{member.username}" if member.username else "No username"
                print(f"{i}. {admin_badge} {member.full_name} ({username})")
            
            choice = input(f"\nAdd all {len(telegram_only)} members to Firestore? (y/n): ").strip().lower()
            if choice == 'y':
                for member in telegram_only:
                    await self.add_telegram_member_to_firestore(member)
        
        # Process Firestore-only members
        if firestore_only:
            print(f"\n🟡 FIRESTORE-ONLY MEMBERS")
            print("-" * 50)
            for i, member in enumerate(firestore_only, 1):
                status_icon = "✅" if member.status == "active" else "❌"
                username = f"@{member.username}" if member.username else "No username"
                print(f"{i}. {status_icon} {member.full_name} ({username}) - {member.role}")
            
            print(f"\nOptions for each member:")
            print("1. Remove from Firestore")
            print("2. Keep in Firestore (skip)")
            
            for member in firestore_only:
                choice = input(f"\nAction for {member.full_name}? (1=remove, 2=skip): ").strip()
                if choice == '1':
                    await self.remove_team_member_by_id(member.id)
                    print(f"✅ Removed {member.full_name} from Firestore")
                else:
                    print(f"⏭️  Skipped {member.full_name}")
        
        # Process synchronized members
        if synchronized:
            print(f"\n🟢 SYNCHRONIZED MEMBERS")
            print("-" * 50)
            for i, (telegram_member, firestore_member) in enumerate(synchronized, 1):
                admin_badge = "👑" if telegram_member.is_admin else "👤"
                status_icon = "✅" if firestore_member.status == "active" else "❌"
                print(f"{i}. {admin_badge} {telegram_member.full_name}")
                print(f"   Telegram: Admin={telegram_member.is_admin}")
                print(f"   Firestore: Role={firestore_member.role}, Status={status_icon}")
            
            choice = input(f"\nUpdate synchronized members? (y/n): ").strip().lower()
            if choice == 'y':
                for telegram_member, firestore_member in synchronized:
                    await self.update_synchronized_member(telegram_member, firestore_member)
        
        print(f"\n✅ Synchronization complete!")
    
    async def add_telegram_member_to_firestore(self, telegram_member: TelegramMember) -> None:
        """Add a Telegram member to Firestore."""
        try:
            # Generate user_id using the standardized function
            user_id = generate_user_id(telegram_member.telegram_id)
            
            # Determine role based on admin status
            role = "Club Administrator" if telegram_member.is_admin else "Team Member"
            
            # Create team member data with improved structure
            current_time = datetime.now().isoformat()
            member_data = {
                # Primary identifier (remove redundant 'id' field)
                "user_id": user_id,
                "team_id": self.current_team.id,
                
                # Telegram-specific data
                "telegram_id": str(telegram_member.telegram_id),
                "username": telegram_member.username,
                "first_name": telegram_member.first_name,
                "last_name": telegram_member.last_name,
                "full_name": telegram_member.full_name,
                
                # Role and status
                "role": role,
                "status": "active",
                "is_admin": telegram_member.is_admin,  # Keep for backward compatibility
                
                # Contact information (to be filled later)
                "phone_number": None,
                "email": None,
                "emergency_contact": None,
                
                # Timestamps (consistent)
                "created_at": current_time,
                "updated_at": current_time,
                
                # Metadata
                "source": "telegram_sync",
                "sync_version": "1.0"
            }
            
            # Add to Firestore
            collection_name = f"kickai_{self.current_team.id}_team_members"
            await self.firebase_client.add_document(collection_name, user_id, member_data)
            
            print(f"✅ Added {telegram_member.full_name} to Firestore as {role}")
            
        except Exception as e:
            logger.error(f"Error adding Telegram member to Firestore: {e}")
            print(f"❌ Error adding {telegram_member.full_name}: {e}")
    
    async def remove_team_member_by_id(self, member_id: str) -> None:
        """Remove a team member from Firestore by ID."""
        try:
            collection_name = f"kickai_{self.current_team.id}_team_members"
            await self.firebase_client.delete_document(collection_name, member_id)
            logger.info(f"Removed team member {member_id} from Firestore")
        except Exception as e:
            logger.error(f"Error removing team member {member_id}: {e}")
            print(f"❌ Error removing team member: {e}")
    
    async def update_synchronized_member(self, telegram_member: TelegramMember, firestore_member: TeamMember) -> None:
        """Update a synchronized member's information."""
        try:
            # Update admin status if different
            if telegram_member.is_admin != firestore_member.is_admin:
                update_data = {
                    "is_admin": telegram_member.is_admin,
                    "updated_at": datetime.now().isoformat()
                }
                
                collection_name = f"kickai_{self.current_team.id}_team_members"
                await self.firebase_client.update_document(collection_name, firestore_member.id, update_data)
                
                print(f"✅ Updated admin status for {telegram_member.full_name}")
            
        except Exception as e:
            logger.error(f"Error updating synchronized member: {e}")
            print(f"❌ Error updating {telegram_member.full_name}: {e}")
    
    def show_menu(self) -> str:
        """Show the main menu."""
        print(f"\n🎯 TEAM MEMBER MANAGEMENT - {self.current_team.name}")
        print("=" * 60)
        print("1. Synchronize Team Members")
        print("2. View Current Members")
        print("3. Add Team Member")
        print("4. Update Team Member")
        print("5. Remove Team Member")
        print("6. Exit")
        print("-" * 60)
        
        return input("Select option (1-6): ").strip()
    
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
                    # Synchronize team members
                    await self.synchronize_team_members()
                    
                elif choice == '2':
                    # View current members
                    members = await self.get_team_members()
                    self.display_team_members(members)
                    
                elif choice == '3':
                    # Add team member
                    success = await self.add_team_member()
                    if success:
                        members = await self.get_team_members()
                        await self.send_team_members_to_leadership_chat(members)
                    
                elif choice == '4':
                    # Update team member
                    members = await self.get_team_members()
                    success = await self.update_team_member(members)
                    if success:
                        updated_members = await self.get_team_members()
                        await self.send_team_members_to_leadership_chat(updated_members)
                    
                elif choice == '5':
                    # Remove team member
                    members = await self.get_team_members()
                    success = await self.remove_team_member(members)
                    if success:
                        updated_members = await self.get_team_members()
                        await self.send_team_members_to_leadership_chat(updated_members)
                    
                elif choice == '6':
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
    
    if not FIRESTORE_AVAILABLE:
        print("❌ Firebase Admin SDK not available.")
        print("   Please install: pip install firebase-admin")
        return
    
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