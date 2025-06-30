#!/usr/bin/env python3
"""
Team Management Tools for KICKAI
Provides tools for managing teams, members, and team-related operations.
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from firebase_admin import firestore
from src.tools.firebase_tools import get_firebase_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_firebase_client() -> firestore.Client:
    """Get Firebase client with proper error handling."""
    try:
        return get_firebase_client()
    except Exception as e:
        logger.error(f"Failed to get Firebase client: {e}")
        raise

class TeamManagementTools:
    """Tools for team management operations."""
    
    def __init__(self):
        self.firebase = get_firebase_client()
    
    def create_team(self, **kwargs) -> Dict:
        """Create a new team."""
        return self._create_team(self.firebase, **kwargs)
    
    def add_team_member(self, **kwargs) -> Dict:
        """Add a member to a team."""
        return self._add_team_member(self.firebase, **kwargs)
    
    def get_team_members(self, **kwargs) -> str:
        """Get all members of a team."""
        return self._get_team_members(self.firebase, **kwargs)
    
    def update_member_role(self, **kwargs) -> Dict:
        """Update a member's role in a team."""
        return self._update_member_role(self.firebase, **kwargs)
    
    def get_team_info(self, **kwargs) -> str:
        """Get information about a team."""
        return self._get_team_info(self.firebase, **kwargs)
    
    def list_teams(self) -> str:
        """List all teams."""
        return self._list_teams(self.firebase)
    
    def _create_team(self, firebase, name: str, admin_phone: str, admin_name: str,
                    description: str = "") -> Dict:
        """Create a new team with an admin member."""
        try:
            # Create team document
            team_data = {
                'name': name,
                'description': description,
                'admin_phone': admin_phone,
                'created_at': datetime.now(),
                'is_active': True
            }
            
            team_ref = firebase.collection('teams').document()
            team_ref.set(team_data)
            team_id = team_ref.id
            
            # Add admin as first member
            member_data = {
                'team_id': team_id,
                'phone_number': admin_phone,
                'name': admin_name,
                'role': 'admin',
                'joined_at': datetime.now(),
                'is_active': True
            }
            
            member_ref = firebase.collection('team_members').document()
            member_ref.set(member_data)
            
            logger.info(f"Created team '{name}' with ID {team_id}")
            return {
                'success': True,
                'team_id': team_id,
                'message': f"Team '{name}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create team: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_team_member(self, firebase, team_id: str, phone_number: str,
                        name: str, role: str = 'member') -> Dict:
        """Add a member to a team."""
        try:
            # Verify team exists
            team_ref = firebase.collection('teams').document(team_id)
            team_doc = team_ref.get()
            if not team_doc.exists:
                return {
                    'success': False,
                    'error': f"Team with ID {team_id} not found"
                }
            
            # Check if member already exists
            members_ref = firebase.collection('team_members')
            existing_query = members_ref.where('team_id', '==', team_id).where('phone_number', '==', phone_number)
            existing_docs = existing_query.get()
            
            if existing_docs:
                return {
                    'success': False,
                    'error': f"Member with phone {phone_number} already exists in team"
                }
            
            # Add new member
            member_data = {
                'team_id': team_id,
                'phone_number': phone_number,
                'name': name,
                'role': role,
                'joined_at': datetime.now(),
                'is_active': True
            }
            
            member_ref = firebase.collection('team_members').document()
            member_ref.set(member_data)
            
            logger.info(f"Added member {name} to team {team_id}")
            return {
                'success': True,
                'message': f"Member {name} added successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to add team member: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_team_members(self, firebase, team_id: str) -> str:
        """Get all members of a team."""
        try:
            members_ref = firebase.collection('team_members')
            query = members_ref.where('team_id', '==', team_id).where('is_active', '==', True)
            response = query.get()
            
            if not response:
                return "No members found for this team."
            
            members_list = []
            for doc in response:
                member_data = doc.to_dict()
                members_list.append(
                    f"• {member_data['name']} ({member_data['phone_number']}) - {member_data['role']}"
                )
            
            return f"Team Members:\n" + "\n".join(members_list)
            
        except Exception as e:
            logger.error(f"Failed to get team members: {e}")
            return f"Error retrieving team members: {str(e)}"
    
    def _update_member_role(self, firebase, team_id: str, phone_number: str,
                           new_role: str) -> Dict:
        """Update a member's role in a team."""
        try:
            # Find member document
            members_ref = firebase.collection('team_members')
            query = members_ref.where('team_id', '==', team_id).where('phone_number', '==', phone_number)
            member_docs = query.get()
            
            if not member_docs:
                return {
                    'success': False,
                    'error': f"Member with phone {phone_number} not found in team"
                }
            
            # Update role
            member_doc = member_docs[0]
            member_ref = firebase.collection('team_members').document(member_doc.id)
            member_ref.update({
                'role': new_role,
                'updated_at': datetime.now()
            })
            
            logger.info(f"Updated role for member {phone_number} to {new_role}")
            return {
                'success': True,
                'message': f"Role updated to {new_role}"
            }
            
        except Exception as e:
            logger.error(f"Failed to update member role: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_team_info(self, firebase, team_id: str) -> str:
        """Get information about a team."""
        try:
            # Get team info
            team_ref = firebase.collection('teams').document(team_id)
            team_doc = team_ref.get()
            
            if not team_doc.exists:
                return f"Team with ID {team_id} not found."
            
            team_data = team_doc.to_dict()
            
            # Get member count
            members_ref = firebase.collection('team_members')
            members_query = members_ref.where('team_id', '==', team_id).where('is_active', '==', True)
            members_response = members_query.get()
            member_count = len(list(members_response))
            
            return f"Team: {team_data['name']}\n" \
                   f"Description: {team_data.get('description', 'No description')}\n" \
                   f"Admin: {team_data['admin_phone']}\n" \
                   f"Members: {member_count}\n" \
                   f"Status: {'Active' if team_data.get('is_active', True) else 'Inactive'}"
            
        except Exception as e:
            logger.error(f"Failed to get team info: {e}")
            return f"Error retrieving team info: {str(e)}"
    
    def _list_teams(self, firebase) -> str:
        """List all teams."""
        try:
            teams_ref = firebase.collection('teams')
            query = teams_ref.where('is_active', '==', True)
            response = query.get()
            
            if not response:
                return "No active teams found."
            
            teams_list = []
            for doc in response:
                team_data = doc.to_dict()
                teams_list.append(f"• {team_data['name']} (ID: {doc.id})")
            
            return f"Active Teams:\n" + "\n".join(teams_list)
            
        except Exception as e:
            logger.error(f"Failed to list teams: {e}")
            return f"Error listing teams: {str(e)}"


def get_team_management_tools() -> List[TeamManagementTools]:
    """Get all team management tools."""
    return [TeamManagementTools()] 