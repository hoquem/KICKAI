#!/usr/bin/env python3
"""
Integration tests for Advanced Memory System with KICKAI
Tests the integration of the memory system with the main agentic system.
"""

import unittest
import time
import json
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.advanced_memory import (
    AdvancedMemorySystem,
    MemoryType,
    MemoryItem,
    UserPreference,
    Pattern
)
from src.simple_agentic_handler import SimpleAgenticHandler
from config import ENABLE_ADVANCED_MEMORY

class TestAdvancedMemoryIntegration(unittest.TestCase):
    """Test integration of Advanced Memory System with KICKAI."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_system = AdvancedMemorySystem()
        self.config = {
            'enable_advanced_memory': True,
            'memory_config': {
                'max_short_term_items': 50,
                'max_long_term_items': 200,
                'pattern_learning_enabled': True
            }
        }
    
    def test_memory_system_initialization(self):
        """Test that memory system initializes correctly."""
        self.assertIsNotNone(self.memory_system)
        self.assertTrue(ENABLE_ADVANCED_MEMORY)
    
    def test_conversation_memory_storage(self):
        """Test storing conversation memories."""
        # Simulate a conversation
        conversation_data = [
            {
                'user_id': 'user123',
                'chat_id': 'team_chat',
                'message': 'When is our next match?',
                'response': 'Your next match is on Saturday at 2pm',
                'timestamp': time.time()
            },
            {
                'user_id': 'user123',
                'chat_id': 'team_chat',
                'message': 'Who is playing?',
                'response': 'The full squad will be available',
                'timestamp': time.time()
            }
        ]
        
        # Store conversation memories
        for conv in conversation_data:
            memory_id = self.memory_system.store_memory(
                content={
                    'message': conv['message'],
                    'response': conv['response'],
                    'conversation_id': conv['chat_id']
                },
                memory_type=MemoryType.EPISODIC,
                user_id=conv['user_id'],
                chat_id=conv['chat_id'],
                importance=0.8,
                tags=['conversation', 'match_info']
            )
            self.assertIsNotNone(memory_id)
        
        # Retrieve conversation context
        context = self.memory_system.get_conversation_context('user123', 'team_chat')
        self.assertEqual(len(context), 2)
    
    def test_user_preference_learning(self):
        """Test learning user preferences from interactions."""
        # Simulate user interactions that reveal preferences
        interactions = [
            {'user_id': 'user123', 'preference': 'communication_style', 'value': 'formal'},
            {'user_id': 'user123', 'preference': 'response_length', 'value': 'detailed'},
            {'user_id': 'user123', 'preference': 'notification_frequency', 'value': 'high'}
        ]
        
        for interaction in interactions:
            self.memory_system.learn_user_preference(
                user_id=interaction['user_id'],
                preference_type=interaction['preference'],
                value=interaction['value'],
                confidence=0.8
            )
        
        # Retrieve user preferences
        preferences = self.memory_system.get_user_preferences('user123')
        self.assertEqual(len(preferences), 3)
        
        # Check specific preference
        comm_style = next((p for p in preferences if p.preference_type == 'communication_style'), None)
        self.assertIsNotNone(comm_style)
        self.assertEqual(comm_style.value, 'formal')
    
    def test_pattern_learning_from_interactions(self):
        """Test learning patterns from user interactions."""
        # Simulate repeated interaction patterns
        patterns = [
            {
                'trigger': 'match schedule',
                'response': 'I can help you schedule a match',
                'success': True
            },
            {
                'trigger': 'player availability',
                'response': 'Let me check player availability',
                'success': True
            },
            {
                'trigger': 'training schedule',
                'response': 'Training is scheduled for 7pm',
                'success': False  # User wasn't satisfied
            }
        ]
        
        for pattern in patterns:
            self.memory_system.learn_pattern(
                pattern_type='user_request',
                trigger_conditions=[pattern['trigger']],
                response_pattern=pattern['response'],
                success=pattern['success']
            )
        
        # Test pattern retrieval
        context = {'message': 'I need to schedule a match'}
        relevant_patterns = self.memory_system.get_relevant_patterns(context)
        
        # Should find the match scheduling pattern
        self.assertGreater(len(relevant_patterns), 0)
        match_pattern = next((p for p in relevant_patterns if 'schedule' in p.response_pattern), None)
        self.assertIsNotNone(match_pattern)
        self.assertEqual(match_pattern.success_rate, 1.0)
    
    def test_memory_retrieval_for_context(self):
        """Test retrieving relevant memories for context enhancement."""
        # Store various types of memories
        memories = [
            {
                'content': {'topic': 'training', 'info': 'Practice at 7pm on Tuesdays'},
                'type': MemoryType.SEMANTIC,
                'importance': 0.9,
                'tags': ['training', 'schedule']
            },
            {
                'content': {'topic': 'match', 'info': 'Last match was against Arsenal'},
                'type': MemoryType.EPISODIC,
                'importance': 0.8,
                'tags': ['match', 'arsenal']
            },
            {
                'content': {'topic': 'player', 'info': 'John is injured'},
                'type': MemoryType.SHORT_TERM,
                'importance': 0.7,
                'tags': ['player', 'injury']
            }
        ]
        
        for memory in memories:
            self.memory_system.store_memory(
                content=memory['content'],
                memory_type=memory['type'],
                importance=memory['importance'],
                tags=memory['tags']
            )
        
        # Retrieve memories for training context
        training_memories = self.memory_system.retrieve_memory(
            query={'topic': 'training'},
            limit=5
        )
        
        self.assertGreater(len(training_memories), 0)
        training_memory = training_memories[0]
        self.assertEqual(training_memory.content['topic'], 'training')
    
    def test_memory_cleanup_and_maintenance(self):
        """Test memory cleanup and maintenance."""
        # Fill memory with test data
        for i in range(10):
            self.memory_system.store_memory(
                content={'test': f'data_{i}', 'importance': 0.3},
                memory_type=MemoryType.SHORT_TERM,
                importance=0.3
            )
        
        # Store one important memory
        self.memory_system.store_memory(
            content={'test': 'important_data', 'importance': 0.9},
            memory_type=MemoryType.SHORT_TERM,
            importance=0.9
        )
        
        # Get initial stats
        initial_stats = self.memory_system.get_memory_stats()
        
        # Perform cleanup
        self.memory_system.cleanup_memory()
        
        # Get final stats
        final_stats = self.memory_system.get_memory_stats()
        
        # Important memory should be preserved
        important_memories = self.memory_system.retrieve_memory(
            query={'test': 'important_data'},
            memory_types=[MemoryType.SHORT_TERM]
        )
        
        self.assertGreater(len(important_memories), 0)
    
    def test_memory_persistence(self):
        """Test memory persistence across sessions."""
        # Store test data
        test_data = {
            'conversation': {
                'user_id': 'user123',
                'message': 'Test message',
                'response': 'Test response'
            },
            'preference': {
                'user_id': 'user123',
                'type': 'test_preference',
                'value': 'test_value'
            },
            'pattern': {
                'type': 'test_pattern',
                'trigger': 'test_trigger',
                'response': 'test_response'
            }
        }
        
        # Store memories
        self.memory_system.store_memory(
            content=test_data['conversation'],
            memory_type=MemoryType.EPISODIC,
            user_id=test_data['conversation']['user_id']
        )
        
        self.memory_system.learn_user_preference(
            user_id=test_data['preference']['user_id'],
            preference_type=test_data['preference']['type'],
            value=test_data['preference']['value']
        )
        
        self.memory_system.learn_pattern(
            pattern_type=test_data['pattern']['type'],
            trigger_conditions=[test_data['pattern']['trigger']],
            response_pattern=test_data['pattern']['response'],
            success=True
        )
        
        # Export memory
        exported_data = self.memory_system.export_memory()
        
        # Create new memory system and import
        new_memory_system = AdvancedMemorySystem()
        new_memory_system.import_memory(exported_data)
        
        # Verify data persistence
        self.assertGreater(len(new_memory_system.episodic_memory), 0)
        self.assertGreater(len(new_memory_system.get_user_preferences('user123')), 0)
        self.assertGreater(len(new_memory_system.patterns), 0)
    
    def test_memory_system_performance(self):
        """Test memory system performance with larger datasets."""
        # Store larger dataset
        start_time = time.time()
        
        for i in range(100):
            self.memory_system.store_memory(
                content={'index': i, 'data': f'data_{i}'},
                memory_type=MemoryType.SHORT_TERM,
                importance=0.5 + (i % 10) * 0.05
            )
        
        storage_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        
        for i in range(10):
            self.memory_system.retrieve_memory(
                query={'index': i},
                limit=5
            )
        
        retrieval_time = time.time() - start_time
        
        # Performance should be reasonable
        self.assertLess(storage_time, 1.0)  # Should store 100 items in under 1 second
        self.assertLess(retrieval_time, 0.5)  # Should retrieve in under 0.5 seconds
        
        # Get stats
        stats = self.memory_system.get_memory_stats()
        self.assertEqual(stats['short_term_count'], 100)
    
    def test_memory_system_with_feature_flag(self):
        """Test memory system behavior with feature flag."""
        # Test that memory system works when feature is enabled
        if ENABLE_ADVANCED_MEMORY:
            # Store memory
            memory_id = self.memory_system.store_memory(
                content={'test': 'feature_flag_test'},
                memory_type=MemoryType.SHORT_TERM
            )
            
            # Retrieve memory
            results = self.memory_system.retrieve_memory(
                query={'test': 'feature_flag_test'}
            )
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].content['test'], 'feature_flag_test')
        else:
            # If disabled, system should still work but not store memories
            self.assertIsNotNone(self.memory_system)

if __name__ == '__main__':
    # Run integration tests
    unittest.main(verbosity=2) 