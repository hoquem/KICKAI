#!/usr/bin/env python3
"""
Team Management Tools for KICKAI
Provides tools for creating teams, managing roles, and inviting members.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from crewai.tools import BaseTool
from supabase import create_client, Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Get Supabase client with proper error handling."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("Missing Supabase environment variables")
    
    return create_client(url, key)


class TeamManagementTools(BaseTool):
    """Tool for managing teams, roles, and memberships."""
    
    name: str = "Team Management Tool"
    description: str = "A tool to manage teams, roles, and member invitations"
    
    def _run(self, command: str, **kwargs) -> str:
        supabase = get_supabase_client()
        
        if command == 'create_team':
            return self._create_team(supabase, **kwargs)
        elif command == 'add_team_member':
            return self._add_team_member(supabase, **kwargs)
        elif command == 'get_team_members':
            return self._get_team_members(supabase, **kwargs)
        elif command == 'update_member_role':
            return self._update_member_role(supabase, **kwargs)
        elif command == 'get_team_info':
            return self._get_team_info(supabase, **kwargs)
        elif command == 'list_teams':
            return self._list_teams(supabase)
        else:
            return "Error: Unknown command. Available commands: 'create_team', 'add_team_member', 'get_team_members', 'update_member_role', 'get_team_info', 'list_teams'."

    def _create_team(self, supabase: Client, name: str, admin_phone: str, admin_name: str, 
                    telegram_group: str, description: str = "") -> str:
        """Create a new team with an admin."""
        try:
            # First, create the team
            team_response = supabase.table('teams').insert({
                'name': name,
                'description': description,
                'telegram_group': telegram_group,
                'created_by': admin_phone,
                'is_active': True
            }).execute()
            
            if not team_response.data:
                return "Error: Failed to create team"
            
            team = team_response.data[0]
            team_id = team['id']
            
            # Add the admin as a team member with admin role
            member_response = supabase.table('team_members').insert({
                'team_id': team_id,
                'player_id': None,  # Will be linked when player is created
                'phone_number': admin_phone,
                'name': admin_name,
                'role': 'admin',
                'is_active': True,
                'joined_at': 'now()'
            }).execute()
            
            if not member_response.data:
                return f"Team created but failed to add admin. Team ID: {team_id}"
            
            return f"Team '{name}' created successfully! Team ID: {team_id}, Admin: {admin_name}"
            
        except Exception as e:
            return f"Error creating team: {str(e)}"

    def _add_team_member(self, supabase: Client, team_id: str, phone_number: str, 
                        name: str, role: str = 'player', invited_by: Optional[str] = None) -> str:
        """Add a new member to a team."""
        try:
            # Check if team exists
            team_response = supabase.table('teams').select('*').eq('id', team_id).execute()
            if not team_response.data:
                return f"Error: Team with ID {team_id} not found"
            
            # Check if member already exists
            existing_member = supabase.table('team_members').select('*').eq('team_id', team_id).eq('phone_number', phone_number).execute()
            if existing_member.data:
                return f"Error: Member {name} already exists in this team"
            
            # Prepare member data
            member_data = {
                'team_id': team_id,
                'phone_number': phone_number,
                'name': name,
                'role': role,
                'is_active': True,
                'joined_at': 'now()'
            }
            
            # Add invited_by if provided
            if invited_by:
                member_data['invited_by'] = invited_by
            
            # Add the member
            member_response = supabase.table('team_members').insert(member_data).execute()
            
            if not member_response.data:
                return "Error: Failed to add team member"
            
            member = member_response.data[0]
            return f"Successfully added {name} as {role} to team. Member ID: {member['id']}"
            
        except Exception as e:
            return f"Error adding team member: {str(e)}"

    def _get_team_members(self, supabase: Client, team_id: str) -> str:
        """Get all members of a team."""
        try:
            response = supabase.table('team_members').select('*').eq('team_id', team_id).eq('is_active', True).execute()
            
            if not response.data:
                return f"No active members found for team {team_id}"
            
            members = response.data
            result = f"Team Members ({len(members)}):\n"
            
            for member in members:
                result += f"- {member['name']} ({member['role']}) - {member['phone_number']}\n"
            
            return result
            
        except Exception as e:
            return f"Error getting team members: {str(e)}"

    def _update_member_role(self, supabase: Client, team_id: str, phone_number: str, 
                           new_role: str, updated_by: str) -> str:
        """Update a member's role in a team."""
        try:
            # Check if member exists
            member_response = supabase.table('team_members').select('*').eq('team_id', team_id).eq('phone_number', phone_number).execute()
            if not member_response.data:
                return f"Error: Member not found in team"
            
            # Update the role
            update_response = supabase.table('team_members').update({
                'role': new_role,
                'updated_by': updated_by,
                'updated_at': 'now()'
            }).eq('team_id', team_id).eq('phone_number', phone_number).execute()
            
            if not update_response.data:
                return "Error: Failed to update member role"
            
            member = update_response.data[0]
            return f"Successfully updated {member['name']} role to {new_role}"
            
        except Exception as e:
            return f"Error updating member role: {str(e)}"

    def _get_team_info(self, supabase: Client, team_id: str) -> str:
        """Get detailed information about a team."""
        try:
            # Get team info
            team_response = supabase.table('teams').select('*').eq('id', team_id).execute()
            if not team_response.data:
                return f"Error: Team with ID {team_id} not found"
            
            team = team_response.data[0]
            
            # Get member count
            members_response = supabase.table('team_members').select('*').eq('team_id', team_id).eq('is_active', True).execute()
            member_count = len(members_response.data) if members_response.data else 0
            
            result = f"Team: {team['name']}\n"
            result += f"Description: {team['description']}\n"
            result += f"Members: {member_count}\n"
            result += f"Telegram Group: {team['telegram_group']}\n"
            result += f"Created: {team['created_at']}\n"
            result += f"Status: {'Active' if team['is_active'] else 'Inactive'}"
            
            return result
            
        except Exception as e:
            return f"Error getting team info: {str(e)}"

    def _list_teams(self, supabase: Client) -> str:
        """List all teams."""
        try:
            response = supabase.table('teams').select('*').eq('is_active', True).execute()
            
            if not response.data:
                return "No active teams found"
            
            teams = response.data
            result = f"Active Teams ({len(teams)}):\n"
            
            for team in teams:
                result += f"- {team['name']} (ID: {team['id']}) - {team['description']}\n"
            
            return result
            
        except Exception as e:
            return f"Error listing teams: {str(e)}"


def get_team_management_tools() -> List[BaseTool]:
    """Get all team management tools."""
    return [TeamManagementTools()] 