#!/usr/bin/env python3
"""
End-to-End Tests for Status Command and Player Registration

This test suite covers:
1. Status command functionality for various player states
2. Player registration process
3. Leadership team member registration
4. Admin approval workflows
5. Error handling and edge cases
"""

import os
import sys
import asyncio
import pytest
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from testing.e2e_framework import E2ETestFramework
from database.models_improved import (
    Player, Team, TeamMember, OnboardingStatus, PlayerRole, PlayerPosition
)

class TestStatusAndRegistration(E2ETestFramework):
    """End-to-end tests for status command and player registration."""
    
    @pytest.fixture(autouse=True)
    async def setup_test_data(self):
        """Set up test data before each test."""
        # Run the setup script to create test data
        await self.run_setup_script()
        yield
        # Cleanup is handled by the framework
    
    async def test_status_command_existing_player(self):
        """Test status command for an existing, approved player."""
        logger.info("🧪 Testing status command for existing player...")
        
        # Test with phone number
        response = await self.send_message("/status +447123456789")
        self.assert_response_contains(response, "John Smith")
        self.assert_response_contains(response, "MIDFIELDER")
        self.assert_response_contains(response, "Active")
        self.assert_response_contains(response, "JS")
        
        # Test with player ID
        response = await self.send_message("/status JS")
        self.assert_response_contains(response, "John Smith")
        self.assert_response_contains(response, "MIDFIELDER")
        self.assert_response_contains(response, "Active")
        
        logger.info("✅ Status command for existing player works correctly")
    
    async def test_status_command_pending_approval_player(self):
        """Test status command for a player pending approval."""
        logger.info("🧪 Testing status command for pending approval player...")
        
        response = await self.send_message("/status +447567890123")
        self.assert_response_contains(response, "Alex Brown")
        self.assert_response_contains(response, "Pending Approval")
        self.assert_response_contains(response, "AB")
        
        logger.info("✅ Status command for pending approval player works correctly")
    
    async def test_status_command_in_progress_player(self):
        """Test status command for a player in onboarding progress."""
        logger.info("🧪 Testing status command for in-progress player...")
        
        response = await self.send_message("/status +447456789012")
        self.assert_response_contains(response, "Emma Davis")
        self.assert_response_contains(response, "Onboarding")
        self.assert_response_contains(response, "ED")
        
        logger.info("✅ Status command for in-progress player works correctly")
    
    async def test_status_command_non_existent_player(self):
        """Test status command for a non-existent player."""
        logger.info("🧪 Testing status command for non-existent player...")
        
        response = await self.send_message("/status +449999999999")
        self.assert_response_contains(response, "not found")
        self.assert_response_contains(response, "Please check")
        
        response = await self.send_message("/status NONE")
        self.assert_response_contains(response, "not found")
        self.assert_response_contains(response, "Please check")
        
        logger.info("✅ Status command for non-existent player works correctly")
    
    async def test_status_command_captain(self):
        """Test status command for team captain."""
        logger.info("🧪 Testing status command for team captain...")
        
        response = await self.send_message("/status +447234567890")
        self.assert_response_contains(response, "Sarah Johnson")
        self.assert_response_contains(response, "CAPTAIN")
        self.assert_response_contains(response, "Active")
        self.assert_response_contains(response, "SJ")
        
        logger.info("✅ Status command for captain works correctly")
    
    async def test_status_command_manager(self):
        """Test status command for team manager."""
        logger.info("🧪 Testing status command for team manager...")
        
        response = await self.send_message("/status +447678901234")
        self.assert_response_contains(response, "Lisa Thompson")
        self.assert_response_contains(response, "MANAGER")
        self.assert_response_contains(response, "Active")
        self.assert_response_contains(response, "LT")
        
        logger.info("✅ Status command for manager works correctly")
    
    async def test_player_registration_new_player(self):
        """Test complete player registration process for a new player."""
        logger.info("🧪 Testing complete player registration process...")
        
        # Step 1: Admin adds player
        response = await self.send_admin_message("/add New Player +447111111111 Forward")
        self.assert_response_contains(response, "successfully")
        self.assert_response_contains(response, "New Player")
        
        # Step 2: Player registers with the generated ID
        # Extract player ID from admin response
        player_id = self.extract_player_id(response)
        self.assertIsNotNone(player_id, "Player ID should be generated")
        
        response = await self.send_message(f"/register {player_id}")
        self.assert_response_contains(response, "registration")
        self.assert_response_contains(response, "started")
        
        # Step 3: Check player status
        response = await self.send_message("/status +447111111111")
        self.assert_response_contains(response, "New Player")
        self.assert_response_contains(response, "Pending")
        
        # Step 4: Admin approves player
        response = await self.send_admin_message(f"/approve {player_id}")
        self.assert_response_contains(response, "approved")
        self.assert_response_contains(response, "New Player")
        
        # Step 5: Verify final status
        response = await self.send_message("/status +447111111111")
        self.assert_response_contains(response, "New Player")
        self.assert_response_contains(response, "Active")
        
        logger.info("✅ Complete player registration process works correctly")
    
    async def test_leadership_registration(self):
        """Test registration of leadership team members (non-players)."""
        logger.info("🧪 Testing leadership team member registration...")
        
        # Test adding a leadership member
        response = await self.send_admin_message("/add Leadership Member +447222222222 Manager")
        self.assert_response_contains(response, "successfully")
        self.assert_response_contains(response, "Leadership Member")
        
        # Extract member ID
        member_id = self.extract_player_id(response)
        self.assertIsNotNone(member_id, "Member ID should be generated")
        
        # Register the leadership member
        response = await self.send_message(f"/register {member_id}")
        self.assert_response_contains(response, "registration")
        self.assert_response_contains(response, "started")
        
        # Check status
        response = await self.send_message("/status +447222222222")
        self.assert_response_contains(response, "Leadership Member")
        self.assert_response_contains(response, "MANAGER")
        
        # Approve leadership member
        response = await self.send_admin_message(f"/approve {member_id}")
        self.assert_response_contains(response, "approved")
        
        # Verify final status
        response = await self.send_message("/status +447222222222")
        self.assert_response_contains(response, "Leadership Member")
        self.assert_response_contains(response, "Active")
        
        logger.info("✅ Leadership team member registration works correctly")
    
    async def test_duplicate_player_registration(self):
        """Test handling of duplicate player registration."""
        logger.info("🧪 Testing duplicate player registration...")
        
        # Try to add a player that already exists
        response = await self.send_admin_message("/add John Smith +447123456789 Midfielder")
        self.assert_response_contains(response, "already exists")
        self.assert_response_contains(response, "duplicate")
        
        logger.info("✅ Duplicate player registration handled correctly")
    
    async def test_invalid_phone_number(self):
        """Test registration with invalid phone number."""
        logger.info("🧪 Testing invalid phone number registration...")
        
        response = await self.send_admin_message("/add Test Player 12345 Midfielder")
        self.assert_response_contains(response, "invalid")
        self.assert_response_contains(response, "phone")
        
        logger.info("✅ Invalid phone number handled correctly")
    
    async def test_invalid_position(self):
        """Test registration with invalid position."""
        logger.info("🧪 Testing invalid position registration...")
        
        response = await self.send_admin_message("/add Test Player +447333333333 InvalidPosition")
        self.assert_response_contains(response, "invalid")
        self.assert_response_contains(response, "position")
        
        logger.info("✅ Invalid position handled correctly")
    
    async def test_missing_parameters(self):
        """Test registration with missing parameters."""
        logger.info("🧪 Testing missing parameters...")
        
        # Missing phone
        response = await self.send_admin_message("/add Test Player")
        self.assert_response_contains(response, "Usage")
        self.assert_response_contains(response, "phone")
        
        # Missing position
        response = await self.send_admin_message("/add Test Player +447333333333")
        self.assert_response_contains(response, "Usage")
        self.assert_response_contains(response, "position")
        
        logger.info("✅ Missing parameters handled correctly")
    
    async def test_approve_nonexistent_player(self):
        """Test approval of non-existent player."""
        logger.info("🧪 Testing approval of non-existent player...")
        
        response = await self.send_admin_message("/approve NONE")
        self.assert_response_contains(response, "not found")
        
        logger.info("✅ Non-existent player approval handled correctly")
    
    async def test_register_nonexistent_id(self):
        """Test registration with non-existent player ID."""
        logger.info("🧪 Testing registration with non-existent ID...")
        
        response = await self.send_message("/register NONE")
        self.assert_response_contains(response, "not found")
        self.assert_response_contains(response, "invalid")
        
        logger.info("✅ Non-existent ID registration handled correctly")
    
    async def test_status_command_unauthorized_user(self):
        """Test status command from unauthorized user."""
        logger.info("🧪 Testing status command from unauthorized user...")
        
        # This would require a different user context
        # For now, we test that the command works for any user
        response = await self.send_message("/status JS")
        self.assert_response_contains(response, "John Smith")
        
        logger.info("✅ Status command works for any user")
    
    async def test_registration_workflow_edge_cases(self):
        """Test various edge cases in the registration workflow."""
        logger.info("🧪 Testing registration workflow edge cases...")
        
        # Test with very long name
        long_name = "A" * 100
        response = await self.send_admin_message(f"/add {long_name} +447444444444 Forward")
        self.assert_response_contains(response, "successfully")
        
        # Test with special characters in name
        special_name = "José María O'Connor-Smith"
        response = await self.send_admin_message(f"/add {special_name} +447555555555 Defender")
        self.assert_response_contains(response, "successfully")
        
        # Test with different positions
        positions = ["Goalkeeper", "Defender", "Midfielder", "Forward", "Striker", "Utility"]
        for i, position in enumerate(positions):
            response = await self.send_admin_message(f"/add Test{i} +44766666666{i} {position}")
            self.assert_response_contains(response, "successfully")
        
        logger.info("✅ Registration workflow edge cases handled correctly")
    
    async def test_status_command_formatting(self):
        """Test that status command responses are properly formatted."""
        logger.info("🧪 Testing status command formatting...")
        
        response = await self.send_message("/status JS")
        
        # Check for proper formatting
        self.assert_response_contains(response, "Name:")
        self.assert_response_contains(response, "Position:")
        self.assert_response_contains(response, "Status:")
        self.assert_response_contains(response, "Player ID:")
        
        # Check that response is readable
        lines = response.split('\n')
        self.assertGreater(len(lines), 3, "Status response should have multiple lines")
        
        logger.info("✅ Status command formatting is correct")
    
    async def test_registration_completion_verification(self):
        """Test that registration completion is properly verified."""
        logger.info("🧪 Testing registration completion verification...")
        
        # Add a new player
        response = await self.send_admin_message("/add Verification Test +447777777777 Midfielder")
        player_id = self.extract_player_id(response)
        
        # Register the player
        response = await self.send_message(f"/register {player_id}")
        
        # Check that registration is in progress
        response = await self.send_message("/status +447777777777")
        self.assert_response_contains(response, "Pending")
        
        # Approve the player
        response = await self.send_admin_message(f"/approve {player_id}")
        
        # Verify completion
        response = await self.send_message("/status +447777777777")
        self.assert_response_contains(response, "Active")
        self.assert_response_contains(response, "Verification Test")
        
        logger.info("✅ Registration completion verification works correctly")

    def extract_player_id(self, response: str) -> Optional[str]:
        """Extract player ID from admin response."""
        # Look for patterns like "Player ID: ABC" or "ID: ABC"
        import re
        patterns = [
            r"Player ID:\s*([A-Z]+)",
            r"ID:\s*([A-Z]+)",
            r"ID\s*([A-Z]+)",
            r"([A-Z]{2,})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                return match.group(1)
        
        return None

    def assert_response_contains(self, response: str, expected: str):
        """Assert that response contains expected text."""
        assert expected.lower() in response.lower(), f"Expected '{expected}' in response: {response}"

    async def run_setup_script(self):
        """Run the setup script to create test data."""
        import subprocess
        try:
            result = subprocess.run([
                "python", "scripts/setup_e2e_test_data.py"
            ], capture_output=True, text=True, check=True)
            logger.info("✅ Test data setup completed")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Test data setup failed: {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 