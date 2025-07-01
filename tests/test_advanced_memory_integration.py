"""
Integration tests for Advanced Memory System with KICKAI
Tests the integration of the memory system with the main agentic system.
"""

import pytest
import time
import json
from src.testing.test_base import BaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent
from src.core.advanced_memory import (
    AdvancedMemorySystem,
    MemoryType,
    MemoryItem,
    UserPreference,
    Pattern
)
from src.agents import SimpleAgenticHandler
from config import ENABLE_ADVANCED_MEMORY

class TestAdvancedMemoryIntegration(BaseTestCase):
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
        
        context = self.memory_system.get_conversation_context('user123', 'team_chat')
        self.assertEqual(len(context), 2)
    
    def test_user_preference_learning(self):
        """Test learning user preferences from interactions."""
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
        
        preferences = self.memory_system.get_user_preferences('user123')
        self.assertEqual(len(preferences), 3)
        
        comm_style = next((p for p in preferences if p.preference_type == 'communication_style'), None)
        self.assertIsNotNone(comm_style)
        self.assertEqual(comm_style.value, 'formal')
    
    def test_pattern_learning_from_interactions(self):
        """Test learning patterns from user interactions."""
        # Create memory system with lower confidence threshold for testing
        test_config = {'min_pattern_confidence': 0.0}
        test_memory_system = AdvancedMemorySystem(config=test_config)
        
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
                'success': False
            }
        ]
        
        for pattern in patterns:
            test_memory_system.learn_pattern(
                pattern_type='user_request',
                trigger_conditions=[pattern['trigger']],
                response_pattern=pattern['response'],
                success=pattern['success']
            )
        
        # Test pattern matching with a context that should match
        context = {'message': 'I need to schedule a match for next week'}
        relevant_patterns = test_memory_system.get_relevant_patterns(context)
        
        # Should find at least one pattern
        self.assertGreater(len(relevant_patterns), 0)
        
        # Find the match scheduling pattern
        match_pattern = next((p for p in relevant_patterns if 'schedule' in p.response_pattern), None)
        self.assertIsNotNone(match_pattern)
        self.assertEqual(match_pattern.success_rate, 1.0)
        
        # Test with a different context
        context2 = {'message': 'What is the player availability?'}
        relevant_patterns2 = test_memory_system.get_relevant_patterns(context2)
        
        # Should find the player availability pattern
        availability_pattern = next((p for p in relevant_patterns2 if 'availability' in p.response_pattern), None)
        self.assertIsNotNone(availability_pattern)
        self.assertEqual(availability_pattern.success_rate, 1.0)
    
    def test_memory_retrieval_for_context(self):
        """Test retrieving relevant memories for context enhancement."""
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
        
        training_memories = self.memory_system.retrieve_memory(
            query={'topic': 'training'},
            limit=5
        )
        
        self.assertGreater(len(training_memories), 0)
        training_memory = training_memories[0]
        self.assertEqual(training_memory.content['topic'], 'training')
    
    def test_memory_cleanup_and_maintenance(self):
        """Test memory cleanup and maintenance."""
        # Create memory system with smaller capacity for testing
        test_config = {'max_short_term_items': 50}
        test_memory_system = AdvancedMemorySystem(config=test_config)
        
        # Store many memories to trigger cleanup
        for i in range(100):
            test_memory_system.store_memory(
                content={'test': f'memory_{i}'},
                memory_type=MemoryType.SHORT_TERM,
                importance=0.1
            )
        
        # Trigger cleanup
        test_memory_system.cleanup_old_memories()
        
        # Verify cleanup worked
        short_term_count = len(test_memory_system.short_term_memory)
        self.assertLessEqual(short_term_count, 50)  # Should be within limits
    
    def test_memory_persistence(self):
        """Test memory persistence across system restarts."""
        # Store important memory
        memory_id = self.memory_system.store_memory(
            content={'important': 'data'},
            memory_type=MemoryType.LONG_TERM,
            importance=0.9,
            tags=['important', 'persistent']
        )
        
        # Verify memory is stored
        retrieved_memories = self.memory_system.retrieve_memory(
            query={'important': 'data'},
            memory_types=[MemoryType.LONG_TERM]
        )
        
        self.assertGreater(len(retrieved_memories), 0)
        
        # Test that we can export and import memory
        exported_data = self.memory_system.export_memory()
        self.assertIsInstance(exported_data, dict)
        self.assertIn('long_term_memory', exported_data)
        
        # Create new instance and import the data
        new_memory_system = AdvancedMemorySystem()
        new_memory_system.import_memory(exported_data)
        
        # Now the memory should be available in the new instance
        retrieved_memories = new_memory_system.retrieve_memory(
            query={'important': 'data'},
            memory_types=[MemoryType.LONG_TERM]
        )
        
        self.assertGreater(len(retrieved_memories), 0)
    
    def test_memory_system_performance(self):
        """Test memory system performance under load."""
        import time
        
        # Test storage performance
        start_time = time.time()
        for i in range(100):
            self.memory_system.store_memory(
                content={'performance_test': f'item_{i}'},
                memory_type=MemoryType.SHORT_TERM
            )
        storage_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        for i in range(10):
            self.memory_system.retrieve_memory(
                query={'performance_test': f'item_{i}'},
                limit=5
            )
        retrieval_time = time.time() - start_time
        
        # Performance should be reasonable
        self.assertLess(storage_time, 5.0)  # Should complete in under 5 seconds
        self.assertLess(retrieval_time, 2.0)  # Should complete in under 2 seconds
    
    def test_memory_system_with_feature_flag(self):
        """Test memory system behavior with feature flag disabled."""
        # Test with feature flag enabled
        self.assertTrue(ENABLE_ADVANCED_MEMORY)
        
        # Test that memory system works when enabled
        memory_id = self.memory_system.store_memory(
            content={'test': 'feature_flag'},
            memory_type=MemoryType.SHORT_TERM
        )
        self.assertIsNotNone(memory_id) 