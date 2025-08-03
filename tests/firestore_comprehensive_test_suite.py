#!/usr/bin/env python3
"""
Comprehensive Firestore Database Test Suite

This script tests all Firestore operations identified in the test specification.
It covers all CRUD operations, queries, batch operations, and error scenarios.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from loguru import logger

# Test result tracking
class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"

@dataclass
class TestResult:
    test_name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class TestReport:
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    test_results: List[TestResult]
    timestamp: datetime
    summary: Dict[str, Any]

class FirestoreComprehensiveTestSuite:
    """Comprehensive test suite for all Firestore operations."""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        self.test_data = {}
        self.team_id = "TEST_TEAM_001"
        self.player_id = "TEST_PLAYER_001"
        self.match_id = "TEST_MATCH_001"
        self.expense_id = "TEST_EXPENSE_001"
        
        # Initialize Firebase client
        try:
            from kickai.database.firebase_client import get_firebase_client
            self.firebase_client = get_firebase_client()
            logger.info("✅ Firebase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Firebase client: {e}")
            raise
    
    async def run_all_tests(self) -> TestReport:
        """Run all test categories and generate report."""
        logger.info("🚀 Starting comprehensive Firestore test suite...")
        
        # Test categories
        test_categories = [
            ("Basic CRUD Operations", self.test_basic_crud_operations),
            ("Player Operations", self.test_player_operations),
            ("Team Operations", self.test_team_operations),
            ("Team Member Operations", self.test_team_member_operations),
            ("Match Operations", self.test_match_operations),
            ("Payment Operations", self.test_payment_operations),
            ("Attendance Operations", self.test_attendance_operations),
            ("Message Operations", self.test_message_operations),
            ("Notification Operations", self.test_notification_operations),
            ("Invite Link Operations", self.test_invite_link_operations),
            ("Health Check Operations", self.test_health_check_operations),
            ("Daily Status Operations", self.test_daily_status_operations),
            ("Query Operations", self.test_query_operations),
            ("Batch Operations", self.test_batch_operations),
            ("Error Handling", self.test_error_handling),
            ("Performance Tests", self.test_performance),
        ]
        
        for category_name, test_func in test_categories:
            logger.info(f"📋 Running {category_name}...")
            try:
                await test_func()
            except Exception as e:
                logger.error(f"❌ Error in {category_name}: {e}")
                self.add_test_result(f"{category_name}_setup", TestStatus.ERROR, 0, str(e))
        
        return self.generate_report()
    
    def add_test_result(self, test_name: str, status: TestStatus, duration: float, 
                       error_message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Add a test result to the collection."""
        result = TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            error_message=error_message,
            details=details
        )
        self.test_results.append(result)
        
        # Log result
        emoji = "✅" if status == TestStatus.PASS else "❌" if status == TestStatus.FAIL else "⏭️" if status == TestStatus.SKIP else "💥"
        logger.info(f"{emoji} {test_name}: {status.value} ({duration:.3f}s)")
        if error_message:
            logger.error(f"   Error: {error_message}")
    
    async def test_basic_crud_operations(self):
        """Test basic CRUD operations."""
        collection_name = f"kickai_{self.team_id}_test_crud"
        
        # Test Create Document
        start_time = time.time()
        try:
            test_data = {"name": "Test Document", "value": 42, "created_at": datetime.now().isoformat()}
            doc_id = await self.firebase_client.create_document(collection_name, test_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_document_success", TestStatus.PASS, duration, 
                                   details={"doc_id": doc_id})
                self.test_data["test_doc_id"] = doc_id
            else:
                self.add_test_result("create_document_success", TestStatus.FAIL, duration, 
                                   "Document creation returned empty ID")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_document_success", TestStatus.ERROR, duration, str(e))
        
        # Test Read Document
        if "test_doc_id" in self.test_data:
            start_time = time.time()
            try:
                doc = await self.firebase_client.get_document(collection_name, self.test_data["test_doc_id"])
                duration = time.time() - start_time
                
                if doc and doc.get("name") == "Test Document":
                    self.add_test_result("get_document_success", TestStatus.PASS, duration)
                else:
                    self.add_test_result("get_document_success", TestStatus.FAIL, duration, 
                                       "Retrieved document doesn't match expected data")
            except Exception as e:
                duration = time.time() - start_time
                self.add_test_result("get_document_success", TestStatus.ERROR, duration, str(e))
        
        # Test Update Document
        if "test_doc_id" in self.test_data:
            start_time = time.time()
            try:
                update_data = {"value": 100, "updated_at": datetime.now().isoformat()}
                success = await self.firebase_client.update_document(collection_name, self.test_data["test_doc_id"], update_data)
                duration = time.time() - start_time
                
                if success:
                    self.add_test_result("update_document_success", TestStatus.PASS, duration)
                else:
                    self.add_test_result("update_document_success", TestStatus.FAIL, duration, 
                                       "Document update failed")
            except Exception as e:
                duration = time.time() - start_time
                self.add_test_result("update_document_success", TestStatus.ERROR, duration, str(e))
        
        # Test Delete Document
        if "test_doc_id" in self.test_data:
            start_time = time.time()
            try:
                success = await self.firebase_client.delete_document(collection_name, self.test_data["test_doc_id"])
                duration = time.time() - start_time
                
                if success:
                    self.add_test_result("delete_document_success", TestStatus.PASS, duration)
                else:
                    self.add_test_result("delete_document_success", TestStatus.FAIL, duration, 
                                       "Document deletion failed")
            except Exception as e:
                duration = time.time() - start_time
                self.add_test_result("delete_document_success", TestStatus.ERROR, duration, str(e))
    
    async def test_player_operations(self):
        """Test player-related operations."""
        collection_name = f"kickai_{self.team_id}_players"
        
        # Test Create Player
        start_time = time.time()
        try:
            player_data = {
                "id": self.player_id,
                "name": "Test Player",
                "phone": "+1234567890",
                "position": "Forward",
                "status": "active",
                "team_id": self.team_id,
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, player_data, self.player_id)
            duration = time.time() - start_time
            
            if doc_id == self.player_id:
                self.add_test_result("create_player_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_player_success", TestStatus.FAIL, duration, 
                                   "Player creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_player_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Player by ID
        start_time = time.time()
        try:
            player = await self.firebase_client.get_player(self.player_id, self.team_id)
            duration = time.time() - start_time
            
            if player and player.get("name") == "Test Player":
                self.add_test_result("get_player_by_id_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_player_by_id_success", TestStatus.FAIL, duration, 
                                   "Player retrieval failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_player_by_id_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Player by Phone
        start_time = time.time()
        try:
            player = await self.firebase_client.get_player_by_phone("+1234567890", self.team_id)
            duration = time.time() - start_time
            
            if player and player.get("id") == self.player_id:
                self.add_test_result("get_player_by_phone_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_player_by_phone_success", TestStatus.FAIL, duration, 
                                   "Player retrieval by phone failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_player_by_phone_success", TestStatus.ERROR, duration, str(e))
        
        # Test Update Player
        start_time = time.time()
        try:
            update_data = {"position": "Midfielder", "updated_at": datetime.now().isoformat()}
            success = await self.firebase_client.update_player(self.player_id, update_data, self.team_id)
            duration = time.time() - start_time
            
            if success:
                self.add_test_result("update_player_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("update_player_success", TestStatus.FAIL, duration, 
                                   "Player update failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("update_player_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get All Players
        start_time = time.time()
        try:
            players = await self.firebase_client.get_players_by_team(self.team_id)
            duration = time.time() - start_time
            
            if isinstance(players, list) and len(players) > 0:
                self.add_test_result("get_all_players_success", TestStatus.PASS, duration, 
                                   details={"count": len(players)})
            else:
                self.add_test_result("get_all_players_success", TestStatus.FAIL, duration, 
                                   "No players found")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_all_players_success", TestStatus.ERROR, duration, str(e))
    
    async def test_team_operations(self):
        """Test team-related operations."""
        collection_name = "kickai_teams"
        
        # Test Create Team (Minimal - No Bot Config or Extra Data)
        start_time = time.time()
        try:
            team_data = {
                "id": self.team_id,
                "name": "Test Team",
                "status": "active",
                "created_at": datetime.now().isoformat()
                # Note: Excluding bot configuration, chat IDs, league info, etc.
                # Only essential team identification and status
            }
            doc_id = await self.firebase_client.create_document(collection_name, team_data, self.team_id)
            duration = time.time() - start_time
            
            if doc_id == self.team_id:
                self.add_test_result("create_team_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_team_success", TestStatus.FAIL, duration, 
                                   "Team creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_team_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Team by ID
        start_time = time.time()
        try:
            team = await self.firebase_client.get_team(self.team_id)
            duration = time.time() - start_time
            
            if team and team.get("name") == "Test Team":
                self.add_test_result("get_team_by_id_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_team_by_id_success", TestStatus.FAIL, duration, 
                                   "Team retrieval failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_team_by_id_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Team by Name
        start_time = time.time()
        try:
            team = await self.firebase_client.get_team_by_name("Test Team")
            duration = time.time() - start_time
            
            if team and team.get("id") == self.team_id:
                self.add_test_result("get_team_by_name_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_team_by_name_success", TestStatus.FAIL, duration, 
                                   "Team retrieval by name failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_team_by_name_success", TestStatus.ERROR, duration, str(e))
    
    async def test_team_member_operations(self):
        """Test team member operations."""
        collection_name = f"kickai_{self.team_id}_team_members"
        
        # Test Create Team Member
        start_time = time.time()
        try:
            member_data = {
                "user_id": "TEST_USER_001",
                "team_id": self.team_id,
                "name": "Test Member",
                "role": "admin",
                "telegram_id": "123456789",
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, member_data, "TEST_USER_001")
            duration = time.time() - start_time
            
            if doc_id == "TEST_USER_001":
                self.add_test_result("create_team_member_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_team_member_success", TestStatus.FAIL, duration, 
                                   "Team member creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_team_member_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Team Members
        start_time = time.time()
        try:
            members = await self.firebase_client.get_team_members_by_team(self.team_id)
            duration = time.time() - start_time
            
            if isinstance(members, list) and len(members) > 0:
                self.add_test_result("get_team_members_success", TestStatus.PASS, duration, 
                                   details={"count": len(members)})
            else:
                self.add_test_result("get_team_members_success", TestStatus.FAIL, duration, 
                                   "No team members found")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_team_members_success", TestStatus.ERROR, duration, str(e))
    
    async def test_match_operations(self):
        """Test match-related operations."""
        collection_name = f"kickai_{self.team_id}_matches"
        
        # Test Create Match
        start_time = time.time()
        try:
            match_data = {
                "id": self.match_id,
                "team_id": self.team_id,
                "opponent": "Opponent Team",
                "date": datetime.now().isoformat(),
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, match_data, self.match_id)
            duration = time.time() - start_time
            
            if doc_id == self.match_id:
                self.add_test_result("create_match_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_match_success", TestStatus.FAIL, duration, 
                                   "Match creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_match_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Match
        start_time = time.time()
        try:
            match = await self.firebase_client.get_match(self.match_id, self.team_id)
            duration = time.time() - start_time
            
            if match and match.get("opponent") == "Opponent Team":
                self.add_test_result("get_match_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_match_success", TestStatus.FAIL, duration, 
                                   "Match retrieval failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_match_success", TestStatus.ERROR, duration, str(e))
    
    async def test_payment_operations(self):
        """Test payment-related operations."""
        collection_name = f"kickai_{self.team_id}_payments"
        
        # Test Create Expense
        start_time = time.time()
        try:
            expense_data = {
                "id": self.expense_id,
                "team_id": self.team_id,
                "description": "Test Expense",
                "amount": 100.50,
                "category": "equipment",
                "created_by": "TEST_USER_001",
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, expense_data, self.expense_id)
            duration = time.time() - start_time
            
            if doc_id == self.expense_id:
                self.add_test_result("create_expense_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_expense_success", TestStatus.FAIL, duration, 
                                   "Expense creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_expense_success", TestStatus.ERROR, duration, str(e))
        
        # Test Get Expense
        start_time = time.time()
        try:
            expense = await self.firebase_client.get_document(collection_name, self.expense_id)
            duration = time.time() - start_time
            
            if expense and expense.get("description") == "Test Expense":
                self.add_test_result("get_expense_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_expense_success", TestStatus.FAIL, duration, 
                                   "Expense retrieval failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_expense_success", TestStatus.ERROR, duration, str(e))
    
    async def test_attendance_operations(self):
        """Test attendance-related operations."""
        collection_name = f"kickai_{self.team_id}_attendance"
        
        # Test Create Attendance
        start_time = time.time()
        try:
            attendance_data = {
                "id": f"{self.team_id}_{self.match_id}_{self.player_id}",
                "team_id": self.team_id,
                "match_id": self.match_id,
                "player_id": self.player_id,
                "status": "present",
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, attendance_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_attendance_success", TestStatus.PASS, duration)
                self.test_data["attendance_id"] = doc_id
            else:
                self.add_test_result("create_attendance_success", TestStatus.FAIL, duration, 
                                   "Attendance creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_attendance_success", TestStatus.ERROR, duration, str(e))
    
    async def test_message_operations(self):
        """Test message-related operations."""
        collection_name = f"kickai_{self.team_id}_messages"
        
        # Test Create Message
        start_time = time.time()
        try:
            message_data = {
                "content": "Test message",
                "sender_id": "TEST_USER_001",
                "conversation_id": "TEST_CONV_001",
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, message_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_message_success", TestStatus.PASS, duration)
                self.test_data["message_id"] = doc_id
            else:
                self.add_test_result("create_message_success", TestStatus.FAIL, duration, 
                                   "Message creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_message_success", TestStatus.ERROR, duration, str(e))
    
    async def test_notification_operations(self):
        """Test notification-related operations."""
        collection_name = f"kickai_{self.team_id}_notifications"
        
        # Test Create Notification
        start_time = time.time()
        try:
            notification_data = {
                "title": "Test Notification",
                "message": "This is a test notification",
                "recipient_id": "TEST_USER_001",
                "type": "info",
                "read": False,
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, notification_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_notification_success", TestStatus.PASS, duration)
                self.test_data["notification_id"] = doc_id
            else:
                self.add_test_result("create_notification_success", TestStatus.FAIL, duration, 
                                   "Notification creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_notification_success", TestStatus.ERROR, duration, str(e))
    
    async def test_invite_link_operations(self):
        """Test invite link operations."""
        collection_name = f"kickai_{self.team_id}_invite_links"
        
        # Test Create Invite Link
        start_time = time.time()
        try:
            invite_data = {
                "type": "player",
                "team_id": self.team_id,
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
                "used": False,
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, invite_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_invite_link_success", TestStatus.PASS, duration)
                self.test_data["invite_id"] = doc_id
            else:
                self.add_test_result("create_invite_link_success", TestStatus.FAIL, duration, 
                                   "Invite link creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_invite_link_success", TestStatus.ERROR, duration, str(e))
    
    async def test_health_check_operations(self):
        """Test health check operations."""
        collection_name = f"kickai_{self.team_id}_health_checks"
        
        # Test Create Health Check
        start_time = time.time()
        try:
            health_data = {
                "status": "healthy",
                "team_id": self.team_id,
                "timestamp": datetime.now().isoformat(),
                "details": {"players": 10, "matches": 5}
            }
            doc_id = await self.firebase_client.create_document(collection_name, health_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_health_check_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_health_check_success", TestStatus.FAIL, duration, 
                                   "Health check creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_health_check_success", TestStatus.ERROR, duration, str(e))
    
    async def test_daily_status_operations(self):
        """Test daily status operations."""
        collection_name = f"kickai_{self.team_id}_daily_status"
        
        # Test Create Daily Status
        start_time = time.time()
        try:
            status_data = {
                "team_id": self.team_id,
                "date": datetime.now().date().isoformat(),
                "status": "active",
                "notes": "Test daily status",
                "created_at": datetime.now().isoformat()
            }
            doc_id = await self.firebase_client.create_document(collection_name, status_data)
            duration = time.time() - start_time
            
            if doc_id:
                self.add_test_result("create_daily_status_success", TestStatus.PASS, duration)
            else:
                self.add_test_result("create_daily_status_success", TestStatus.FAIL, duration, 
                                   "Daily status creation failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("create_daily_status_success", TestStatus.ERROR, duration, str(e))
    
    async def test_query_operations(self):
        """Test query operations."""
        collection_name = f"kickai_{self.team_id}_players"
        
        # Test Query with Filters
        start_time = time.time()
        try:
            filters = [{"field": "status", "operator": "==", "value": "active"}]
            results = await self.firebase_client.query_documents(collection_name, filters)
            duration = time.time() - start_time
            
            if isinstance(results, list):
                self.add_test_result("query_with_filters_success", TestStatus.PASS, duration, 
                                   details={"result_count": len(results)})
            else:
                self.add_test_result("query_with_filters_success", TestStatus.FAIL, duration, 
                                   "Query with filters failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("query_with_filters_success", TestStatus.ERROR, duration, str(e))
        
        # Test Query with Limit
        start_time = time.time()
        try:
            results = await self.firebase_client.query_documents(collection_name, limit=5)
            duration = time.time() - start_time
            
            if isinstance(results, list) and len(results) <= 5:
                self.add_test_result("query_with_limit_success", TestStatus.PASS, duration, 
                                   details={"result_count": len(results)})
            else:
                self.add_test_result("query_with_limit_success", TestStatus.FAIL, duration, 
                                   "Query with limit failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("query_with_limit_success", TestStatus.ERROR, duration, str(e))
    
    async def test_batch_operations(self):
        """Test batch operations."""
        # Test Batch Create
        start_time = time.time()
        try:
            operations = [
                {
                    "type": "create",
                    "collection": f"kickai_{self.team_id}_test_batch",
                    "data": {"name": "Batch Doc 1", "value": 1}
                },
                {
                    "type": "create",
                    "collection": f"kickai_{self.team_id}_test_batch",
                    "data": {"name": "Batch Doc 2", "value": 2}
                }
            ]
            results = await self.firebase_client.execute_batch(operations)
            duration = time.time() - start_time
            
            if isinstance(results, list) and len(results) == 2:
                self.add_test_result("batch_create_success", TestStatus.PASS, duration, 
                                   details={"created_count": len(results)})
                self.test_data["batch_doc_ids"] = results
            else:
                self.add_test_result("batch_create_success", TestStatus.FAIL, duration, 
                                   "Batch create failed")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("batch_create_success", TestStatus.ERROR, duration, str(e))
    
    async def test_error_handling(self):
        """Test error handling scenarios."""
        # Test Get Non-existent Document
        start_time = time.time()
        try:
            result = await self.firebase_client.get_document("kickai_test_collection", "non_existent_id")
            duration = time.time() - start_time
            
            if result is None:
                self.add_test_result("get_nonexistent_document_handling", TestStatus.PASS, duration)
            else:
                self.add_test_result("get_nonexistent_document_handling", TestStatus.FAIL, duration, 
                                   "Should return None for non-existent document")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("get_nonexistent_document_handling", TestStatus.ERROR, duration, str(e))
        
        # Test Invalid Collection
        start_time = time.time()
        try:
            result = await self.firebase_client.get_document("", "test_id")
            duration = time.time() - start_time
            self.add_test_result("invalid_collection_handling", TestStatus.FAIL, duration, 
                               "Should handle invalid collection name")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("invalid_collection_handling", TestStatus.PASS, duration, 
                               "Correctly handled invalid collection")
    
    async def test_performance(self):
        """Test performance scenarios."""
        # Test Multiple Concurrent Reads
        start_time = time.time()
        try:
            tasks = []
            for i in range(5):
                task = self.firebase_client.get_document(f"kickai_{self.team_id}_players", self.player_id)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            success_count = sum(1 for r in results if r is not None and not isinstance(r, Exception))
            if success_count == 5:
                self.add_test_result("concurrent_reads_success", TestStatus.PASS, duration, 
                                   details={"success_count": success_count})
            else:
                self.add_test_result("concurrent_reads_success", TestStatus.FAIL, duration, 
                                   f"Only {success_count}/5 concurrent reads succeeded")
        except Exception as e:
            duration = time.time() - start_time
            self.add_test_result("concurrent_reads_success", TestStatus.ERROR, duration, str(e))
    
    def generate_report(self) -> TestReport:
        """Generate comprehensive test report."""
        total_duration = time.time() - self.start_time
        
        # Count results by status
        passed = sum(1 for r in self.test_results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.test_results if r.status == TestStatus.FAIL)
        skipped = sum(1 for r in self.test_results if r.status == TestStatus.SKIP)
        errors = sum(1 for r in self.test_results if r.status == TestStatus.ERROR)
        
        # Calculate success rate
        total_tests = len(self.test_results)
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        # Generate summary
        summary = {
            "success_rate": f"{success_rate:.2f}%",
            "average_test_duration": sum(r.duration for r in self.test_results) / total_tests if total_tests > 0 else 0,
            "slowest_test": max(self.test_results, key=lambda x: x.duration).test_name if self.test_results else None,
            "fastest_test": min(self.test_results, key=lambda x: x.duration).test_name if self.test_results else None,
            "test_categories": {
                "basic_crud": sum(1 for r in self.test_results if "crud" in r.test_name.lower()),
                "player_ops": sum(1 for r in self.test_results if "player" in r.test_name.lower()),
                "team_ops": sum(1 for r in self.test_results if "team" in r.test_name.lower()),
                "payment_ops": sum(1 for r in self.test_results if "expense" in r.test_name.lower() or "payment" in r.test_name.lower()),
                "query_ops": sum(1 for r in self.test_results if "query" in r.test_name.lower()),
                "batch_ops": sum(1 for r in self.test_results if "batch" in r.test_name.lower()),
                "error_handling": sum(1 for r in self.test_results if "error" in r.test_name.lower() or "handling" in r.test_name.lower()),
                "performance": sum(1 for r in self.test_results if "performance" in r.test_name.lower() or "concurrent" in r.test_name.lower()),
            }
        }
        
        return TestReport(
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total_duration=total_duration,
            test_results=self.test_results,
            timestamp=datetime.now(),
            summary=summary
        )

async def main():
    """Main test execution function."""
    # Setup logging
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
    logger.add("logs/firestore_test_suite.log", rotation="10 MB", retention="7 days")
    
    logger.info("🚀 Starting Firestore Comprehensive Test Suite")
    
    try:
        # Run test suite
        test_suite = FirestoreComprehensiveTestSuite()
        report = await test_suite.run_all_tests()
        
        # Generate and save report
        await generate_test_report(report)
        
        # Exit with appropriate code
        if report.failed > 0 or report.errors > 0:
            logger.error(f"❌ Test suite completed with {report.failed} failures and {report.errors} errors")
            sys.exit(1)
        else:
            logger.success(f"✅ Test suite completed successfully! {report.passed}/{report.total_tests} tests passed")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"💥 Test suite failed to run: {e}")
        sys.exit(1)

async def generate_test_report(report: TestReport):
    """Generate and save detailed test report."""
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Generate report filename
    timestamp = report.timestamp.strftime("%Y%m%d_%H%M%S")
    report_filename = f"reports/firestore_test_report_{timestamp}.json"
    
    # Convert report to dict
    report_dict = {
        "metadata": {
            "timestamp": report.timestamp.isoformat(),
            "total_tests": report.total_tests,
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
            "errors": report.errors,
            "total_duration": report.total_duration,
            "success_rate": report.summary["success_rate"]
        },
        "summary": report.summary,
        "test_results": [
            {
                "test_name": r.test_name,
                "status": r.status.value,
                "duration": r.duration,
                "error_message": r.error_message,
                "details": r.details
            }
            for r in report.test_results
        ]
    }
    
    # Save JSON report
    with open(report_filename, 'w') as f:
        json.dump(report_dict, f, indent=2)
    
    # Generate human-readable report
    human_report_filename = f"reports/firestore_test_report_{timestamp}.md"
    with open(human_report_filename, 'w') as f:
        f.write(generate_markdown_report(report))
    
    logger.info(f"📊 Test report saved to {report_filename}")
    logger.info(f"📊 Human-readable report saved to {human_report_filename}")

def generate_markdown_report(report: TestReport) -> str:
    """Generate markdown test report."""
    return f"""# Firestore Database Test Report

## Executive Summary

- **Test Date**: {report.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
- **Total Tests**: {report.total_tests}
- **Passed**: {report.passed} ✅
- **Failed**: {report.failed} ❌
- **Skipped**: {report.skipped} ⏭️
- **Errors**: {report.errors} 💥
- **Success Rate**: {report.summary['success_rate']}
- **Total Duration**: {report.total_duration:.2f} seconds

## Test Results by Category

{generate_category_summary(report)}

## Detailed Test Results

{generate_detailed_results(report)}

## Performance Metrics

- **Average Test Duration**: {report.summary['average_test_duration']:.3f} seconds
- **Slowest Test**: {report.summary['slowest_test'] or 'N/A'}
- **Fastest Test**: {report.summary['fastest_test'] or 'N/A'}

## Recommendations

{generate_recommendations(report)}
"""

def generate_category_summary(report: TestReport) -> str:
    """Generate category summary for markdown report."""
    categories = report.summary.get('test_categories', {})
    summary = []
    
    for category, count in categories.items():
        if count > 0:
            summary.append(f"- **{category.replace('_', ' ').title()}**: {count} tests")
    
    return '\n'.join(summary) if summary else "No categorized tests found."

def generate_detailed_results(report: TestReport) -> str:
    """Generate detailed test results for markdown report."""
    results = []
    
    for result in report.test_results:
        status_emoji = "✅" if result.status == TestStatus.PASS else "❌" if result.status == TestStatus.FAIL else "⏭️" if result.status == TestStatus.SKIP else "💥"
        results.append(f"- {status_emoji} **{result.test_name}** ({result.duration:.3f}s)")
        if result.error_message:
            results.append(f"  - Error: {result.error_message}")
        if result.details:
            results.append(f"  - Details: {result.details}")
    
    return '\n'.join(results)

def generate_recommendations(report: TestReport) -> str:
    """Generate recommendations based on test results."""
    recommendations = []
    
    if report.failed > 0:
        recommendations.append("- 🔧 **Fix Failed Tests**: Address the failed tests to improve reliability")
    
    if report.errors > 0:
        recommendations.append("- 🐛 **Fix Errors**: Resolve system errors that prevented tests from running")
    
    if report.summary['average_test_duration'] > 1.0:
        recommendations.append("- ⚡ **Performance Optimization**: Consider optimizing slow tests")
    
    if report.passed / report.total_tests < 0.8:
        recommendations.append("- 📈 **Improve Test Coverage**: Add more comprehensive test cases")
    
    if not recommendations:
        recommendations.append("- 🎉 **Excellent Results**: All tests are passing with good performance")
    
    return '\n'.join(recommendations)

if __name__ == "__main__":
    asyncio.run(main()) 