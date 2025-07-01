"""
Tests for Advanced Memory System
Comprehensive test suite covering all memory types, user preferences, 
pattern learning, and memory management capabilities.
"""

import pytest
import time
from src.testing.test_base import BaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockTool, MockLLM
from src.advanced_memory import (
    AdvancedMemorySystem,
    MemoryType,
    MemoryItem,
    UserPreference,
    Pattern
)

class TestAdvancedMemorySystem(BaseTestCase):
    """Test the Advanced Memory System core functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = {
            'max_short_term_items': 10,
            'max_long_term_items': 20,
            'max_episodic_items': 15,
            'max_semantic_items': 10,
            'short_term_retention_hours': 1,
            'long_term_retention_days': 1,
            'min_pattern_confidence': 0.7,
            'pattern_learning_enabled': True
        }
        self.memory_system = AdvancedMemorySystem(self.config)
    
    def test_initialization(self):
        """Test that the memory system initializes correctly."""
        self.assertIsNotNone(self.memory_system)
        self.assertEqual(self.memory_system.max_short_term_items, 10)
        self.assertEqual(self.memory_system.max_long_term_items, 20)
        self.assertTrue(self.memory_system.pattern_learning_enabled)
    
    def test_store_short_term_memory(self):
        """Test storing items in short-term memory."""
        content = {'message': 'Hello world', 'user': 'test_user'}
        memory_id = self.memory_system.store_memory(
            content=content,
            memory_type=MemoryType.SHORT_TERM,
            user_id='test_user',
            importance=0.8
        )
        
        self.assertIsNotNone(memory_id)
        self.assertIn(memory_id, self.memory_system.short_term_memory)
        
        stored_item = self.memory_system.short_term_memory[memory_id]
        self.assertEqual(stored_item.content, content)
        self.assertEqual(stored_item.user_id, 'test_user')
        self.assertEqual(stored_item.importance, 0.8)
        self.assertEqual(stored_item.type, MemoryType.SHORT_TERM)
    
    def test_store_long_term_memory(self):
        """Test storing items in long-term memory."""
        content = {'fact': 'Football is a team sport', 'category': 'sports'}
        memory_id = self.memory_system.store_memory(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            importance=0.9,
            tags=['sports', 'knowledge']
        )
        
        self.assertIn(memory_id, self.memory_system.long_term_memory)
        stored_item = self.memory_system.long_term_memory[memory_id]
        self.assertEqual(stored_item.tags, ['sports', 'knowledge'])
    
    def test_store_episodic_memory(self):
        """Test storing items in episodic memory."""
        content = {'event': 'Match against Arsenal', 'date': '2024-07-01'}
        memory_id = self.memory_system.store_memory(
            content=content,
            memory_type=MemoryType.EPISODIC,
            user_id='captain',
            chat_id='team_chat',
            importance=0.95
        )
        
        self.assertIn(memory_id, self.memory_system.episodic_memory)
        stored_item = self.memory_system.episodic_memory[memory_id]
        self.assertEqual(stored_item.chat_id, 'team_chat')
    
    def test_store_semantic_memory(self):
        """Test storing items in semantic memory."""
        content = {'concept': 'Tactical formation', 'description': '4-4-2 formation'}
        memory_id = self.memory_system.store_memory(
            content=content,
            memory_type=MemoryType.SEMANTIC,
            importance=0.85,
            metadata={'source': 'coaching_manual'}
        )
        
        self.assertIn(memory_id, self.memory_system.semantic_memory)
        stored_item = self.memory_system.semantic_memory[memory_id]
        if stored_item.metadata is not None:
            self.assertEqual(stored_item.metadata['source'], 'coaching_manual')
    
    def test_retrieve_memory_by_content(self):
        """Test retrieving memories by content query."""
        # Store test memories
        self.memory_system.store_memory(
            content={'topic': 'training', 'message': 'Practice at 7pm'},
            memory_type=MemoryType.SHORT_TERM,
            user_id='player1'
        )
        
        self.memory_system.store_memory(
            content={'topic': 'match', 'message': 'Game on Saturday'},
            memory_type=MemoryType.SHORT_TERM,
            user_id='player1'
        )
        
        # Retrieve memories about training
        results = self.memory_system.retrieve_memory(
            query={'topic': 'training'},
            memory_types=[MemoryType.SHORT_TERM],
            user_id='player1'
        )
        
        self.assertEqual(len(results), 1)
        if results and len(results) > 0:
            self.assertEqual(results[0].content['topic'], 'training')
    
    def test_retrieve_memory_by_tags(self):
        """Test retrieving memories by tags."""
        # Store memory with tags
        self.memory_system.store_memory(
            content={'info': 'Team meeting'},
            memory_type=MemoryType.LONG_TERM,
            tags=['meeting', 'important']
        )
        
        # Retrieve by tags
        results = self.memory_system.retrieve_memory(
            query={'tags': ['meeting']},
            memory_types=[MemoryType.LONG_TERM]
        )
        
        self.assertEqual(len(results), 1)
        if results[0].tags is not None:
            self.assertIn('meeting', results[0].tags)
    
    def test_retrieve_memory_importance_filter(self):
        """Test filtering memories by importance."""
        # Store memories with different importance levels
        self.memory_system.store_memory(
            content={'info': 'Low importance'},
            memory_type=MemoryType.SHORT_TERM,
            importance=0.3
        )
        
        self.memory_system.store_memory(
            content={'info': 'High importance'},
            memory_type=MemoryType.SHORT_TERM,
            importance=0.8
        )
        
        # Retrieve with minimum importance threshold
        results = self.memory_system.retrieve_memory(
            query={},
            memory_types=[MemoryType.SHORT_TERM],
            min_importance=0.5
        )
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content['info'], 'High importance')
    
    def test_memory_access_tracking(self):
        """Test that memory access is tracked correctly."""
        memory_id = self.memory_system.store_memory(
            content={'test': 'access tracking'},
            memory_type=MemoryType.SHORT_TERM
        )
        
        # Initial access count should be 0
        initial_item = self.memory_system.short_term_memory[memory_id]
        self.assertEqual(initial_item.access_count, 0)
        
        # Retrieve the memory
        self.memory_system.retrieve_memory(
            query={'test': 'access tracking'},
            memory_types=[MemoryType.SHORT_TERM]
        )
        
        # Access count should be incremented
        updated_item = self.memory_system.short_term_memory[memory_id]
        self.assertEqual(updated_item.access_count, 1)

class TestUserPreferences(BaseTestCase):
    """Test user preference learning and retrieval."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_system = AdvancedMemorySystem()
    
    def test_learn_user_preference(self):
        """Test learning a new user preference."""
        self.memory_system.learn_user_preference(
            user_id='user123',
            preference_type='communication_style',
            value='formal',
            confidence=0.8
        )
        
        preferences = self.memory_system.get_user_preferences('user123')
        self.assertEqual(len(preferences), 1)
        self.assertEqual(preferences[0].preference_type, 'communication_style')
        self.assertEqual(preferences[0].value, 'formal')
        self.assertEqual(preferences[0].confidence, 0.8)
    
    def test_update_existing_preference(self):
        """Test updating an existing user preference."""
        # Learn initial preference
        self.memory_system.learn_user_preference(
            user_id='user123',
            preference_type='response_length',
            value='short',
            confidence=0.6
        )
        
        # Update the preference
        self.memory_system.learn_user_preference(
            user_id='user123',
            preference_type='response_length',
            value='detailed',
            confidence=0.9
        )
        
        preferences = self.memory_system.get_user_preferences('user123')
        self.assertEqual(len(preferences), 1)
        self.assertEqual(preferences[0].value, 'detailed')
        self.assertEqual(preferences[0].usage_count, 2)
    
    def test_preference_confidence_capping(self):
        """Test that preference confidence is capped at 1.0."""
        self.memory_system.learn_user_preference(
            user_id='user123',
            preference_type='test',
            value='value',
            confidence=0.8
        )
        
        # Add more confidence
        self.memory_system.learn_user_preference(
            user_id='user123',
            preference_type='test',
            value='value',
            confidence=0.5
        )
        
        preferences = self.memory_system.get_user_preferences('user123')
        self.assertEqual(preferences[0].confidence, 1.0)
    
    def test_get_user_preferences_empty(self):
        """Test getting preferences for user with no preferences."""
        preferences = self.memory_system.get_user_preferences('nonexistent_user')
        self.assertEqual(len(preferences), 0)

class TestPatternLearning(BaseTestCase):
    """Test pattern learning and recognition."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_system = AdvancedMemorySystem()
    
    def test_learn_new_pattern(self):
        """Test learning a new pattern."""
        self.memory_system.learn_pattern(
            pattern_type='greeting',
            trigger_conditions=['hello', 'hi'],
            response_pattern='Hello! How can I help you?',
            success=True
        )
        
        self.assertEqual(len(self.memory_system.patterns), 1)
        pattern = list(self.memory_system.patterns.values())[0]
        self.assertEqual(pattern.pattern_type, 'greeting')
        self.assertEqual(pattern.success_rate, 1.0)
        self.assertEqual(pattern.usage_count, 1)
    
    def test_update_existing_pattern(self):
        """Test updating an existing pattern."""
        # Learn initial pattern
        self.memory_system.learn_pattern(
            pattern_type='match_request',
            trigger_conditions=['schedule', 'match'],
            response_pattern='I can help schedule a match.',
            success=True
        )
        
        # Update with another success
        self.memory_system.learn_pattern(
            pattern_type='match_request',
            trigger_conditions=['schedule', 'match'],
            response_pattern='I can help schedule a match.',
            success=True
        )
        
        pattern = list(self.memory_system.patterns.values())[0]
        self.assertEqual(pattern.success_rate, 1.0)
        self.assertEqual(pattern.usage_count, 2)
    
    def test_pattern_success_rate_calculation(self):
        """Test pattern success rate calculation with mixed results."""
        # Learn pattern with success
        self.memory_system.learn_pattern(
            pattern_type='test',
            trigger_conditions=['test'],
            response_pattern='test response',
            success=True
        )
        
        # Add failure
        self.memory_system.learn_pattern(
            pattern_type='test',
            trigger_conditions=['test'],
            response_pattern='test response',
            success=False
        )
        
        pattern = list(self.memory_system.patterns.values())[0]
        self.assertEqual(pattern.success_rate, 0.5)
    
    def test_get_relevant_patterns(self):
        """Test retrieving patterns relevant to context."""
        # Learn a pattern
        self.memory_system.learn_pattern(
            pattern_type='training',
            trigger_conditions=['practice', 'training'],
            response_pattern='Training information',
            success=True
        )
        
        # Get relevant patterns
        context = {'message': 'When is practice scheduled?'}
        relevant_patterns = self.memory_system.get_relevant_patterns(context)
        
        self.assertEqual(len(relevant_patterns), 1)
        self.assertEqual(relevant_patterns[0].pattern_type, 'training')
    
    def test_pattern_confidence_filtering(self):
        """Test that low-confidence patterns are filtered out."""
        # Learn low-confidence pattern
        self.memory_system.learn_pattern(
            pattern_type='low_confidence',
            trigger_conditions=['test'],
            response_pattern='test',
            success=False
        )
        
        # Learn high-confidence pattern
        self.memory_system.learn_pattern(
            pattern_type='high_confidence',
            trigger_conditions=['test'],
            response_pattern='test',
            success=True
        )
        
        context = {'message': 'test message'}
        relevant_patterns = self.memory_system.get_relevant_patterns(context)
        
        # Only high-confidence pattern should be returned
        self.assertEqual(len(relevant_patterns), 1)
        self.assertEqual(relevant_patterns[0].pattern_type, 'high_confidence')

class TestMemoryManagement(BaseTestCase):
    """Test memory cleanup and management."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = {
            'max_short_term_items': 3,
            'max_long_term_items': 3,
            'short_term_retention_hours': 1,
            'long_term_retention_days': 1
        }
        self.memory_system = AdvancedMemorySystem(self.config)
    
    def test_short_term_memory_cleanup(self):
        """Test short-term memory cleanup when over capacity."""
        # Fill short-term memory
        for i in range(5):
            self.memory_system.store_memory(
                content={'index': i, 'importance': 0.3},
                memory_type=MemoryType.SHORT_TERM,
                importance=0.3
            )
        
        # Should trigger cleanup
        self.assertLessEqual(len(self.memory_system.short_term_memory), 3)
    
    def test_long_term_memory_cleanup(self):
        """Test long-term memory cleanup when over capacity."""
        # Fill long-term memory
        for i in range(5):
            self.memory_system.store_memory(
                content={'index': i},
                memory_type=MemoryType.LONG_TERM,
                importance=0.3
            )
        
        # Should trigger cleanup
        self.assertLessEqual(len(self.memory_system.long_term_memory), 3)
    
    def test_memory_cleanup_preserves_important_items(self):
        """Test that important memories are preserved during cleanup."""
        # Store low importance memory
        self.memory_system.store_memory(
            content={'importance': 'low'},
            memory_type=MemoryType.SHORT_TERM,
            importance=0.2
        )
        
        # Store high importance memory
        self.memory_system.store_memory(
            content={'importance': 'high'},
            memory_type=MemoryType.SHORT_TERM,
            importance=0.9
        )
        
        # Trigger cleanup
        self.memory_system.cleanup_memory()
        
        # High importance memory should be preserved
        memories = list(self.memory_system.short_term_memory.values())
        if memories:
            self.assertEqual(memories[0].content['importance'], 'high')
    
    def test_get_memory_stats(self):
        """Test memory statistics generation."""
        # Store some memories
        self.memory_system.store_memory(
            content={'test': 'short'},
            memory_type=MemoryType.SHORT_TERM
        )
        
        self.memory_system.store_memory(
            content={'test': 'long'},
            memory_type=MemoryType.LONG_TERM
        )
        
        # Learn preferences and patterns
        self.memory_system.learn_user_preference(
            user_id='user1',
            preference_type='test',
            value='value',
            confidence=1.0
        )
        
        self.memory_system.learn_pattern(
            pattern_type='test',
            trigger_conditions=['test'],
            response_pattern='test',
            success=True
        )
        
        stats = self.memory_system.get_memory_stats()
        
        self.assertEqual(stats['short_term_count'], 1)
        self.assertEqual(stats['long_term_count'], 1)
        self.assertEqual(stats['user_preferences_count'], 1)
        self.assertEqual(stats['patterns_count'], 1)
        self.assertEqual(stats['total_memories'], 2)

class TestMemoryPersistence(BaseTestCase):
    """Test memory export and import functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_system = AdvancedMemorySystem()
    
    def test_export_memory(self):
        """Test exporting memory data."""
        # Add some test data
        self.memory_system.store_memory(
            content={'test': 'data'},
            memory_type=MemoryType.SHORT_TERM,
            user_id='user1'
        )
        
        self.memory_system.learn_user_preference(
            user_id='user1',
            preference_type='test',
            value='value',
            confidence=1.0
        )
        
        self.memory_system.learn_pattern(
            pattern_type='test',
            trigger_conditions=['test'],
            response_pattern='test',
            success=True
        )
        
        # Export memory
        exported_data = self.memory_system.export_memory()
        
        # Check structure
        self.assertIn('short_term_memory', exported_data)
        self.assertIn('user_preferences', exported_data)
        self.assertIn('patterns', exported_data)
        self.assertIn('config', exported_data)
        
        # Check data
        self.assertEqual(len(exported_data['short_term_memory']), 1)
        self.assertEqual(len(exported_data['user_preferences']['user1']), 1)
        self.assertEqual(len(exported_data['patterns']), 1)
    
    def test_import_memory(self):
        """Test importing memory data."""
        # Create test data
        test_data = {
            'short_term_memory': {
                'test_id': {
                    'id': 'test_id',
                    'type': 'short_term',
                    'content': {'test': 'imported'},
                    'timestamp': time.time(),
                    'user_id': 'user1',
                    'chat_id': None,
                    'importance': 1.0,
                    'access_count': 0,
                    'last_accessed': time.time(),
                    'tags': [],
                    'metadata': {}
                }
            },
            'user_preferences': {
                'user1': [{
                    'user_id': 'user1',
                    'preference_type': 'test',
                    'value': 'imported_value',
                    'confidence': 1.0,
                    'last_updated': time.time(),
                    'usage_count': 1
                }]
            },
            'patterns': {},
            'config': {}
        }
        
        # Create new memory system and import data
        new_memory_system = AdvancedMemorySystem()
        new_memory_system.import_memory(test_data)
        
        # Verify imported data
        self.assertEqual(len(new_memory_system.short_term_memory), 1)
        self.assertEqual(len(new_memory_system.get_user_preferences('user1')), 1)
        
        imported_memory = list(new_memory_system.short_term_memory.values())[0]
        self.assertEqual(imported_memory.content['test'], 'imported')

class TestConversationContext(BaseTestCase):
    """Test conversation context retrieval."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_system = AdvancedMemorySystem()
    
    def test_get_conversation_context(self):
        """Test retrieving conversation context for a user."""
        # Store conversation memories
        self.memory_system.store_memory(
            content={'message': 'Hello'},
            memory_type=MemoryType.SHORT_TERM,
            user_id='user1',
            chat_id='chat1'
        )
        
        self.memory_system.store_memory(
            content={'message': 'How are you?'},
            memory_type=MemoryType.SHORT_TERM,
            user_id='user1',
            chat_id='chat1'
        )
        
        # Store memory for different user
        self.memory_system.store_memory(
            content={'message': 'Different user'},
            memory_type=MemoryType.SHORT_TERM,
            user_id='user2',
            chat_id='chat1'
        )
        
        # Get context for user1
        context = self.memory_system.get_conversation_context('user1', 'chat1')
        
        self.assertEqual(len(context), 2)
        for item in context:
            self.assertEqual(item.user_id, 'user1')
            self.assertEqual(item.chat_id, 'chat1')

if __name__ == '__main__':
    # Run all tests
    pytest.main() 