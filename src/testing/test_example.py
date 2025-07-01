"""
Example Tests for KICKAI Testing Infrastructure

This file demonstrates how to use the new test base classes, fixtures, and utilities.
"""

import pytest
import pytest_asyncio
from .test_base import BaseTestCase, AsyncBaseTestCase, IntegrationTestCase
from .test_utils import MockTool, MockLLM, MockAgent
from .test_fixtures import TestDataFactory, SampleData


class TestPlayerUtils(BaseTestCase):
    def setup_test_data(self):
        self.player_data = TestDataFactory.create_player_data(name="Test User", phone="07123456789")

    def test_player_name(self):
        assert self.player_data.name == "Test User"

    def test_player_phone(self):
        assert self.player_data.phone.startswith("07")

    def test_mock_tool(self):
        tool = self.create_mock_tool(name="test_tool", return_value="success")
        result = tool._run()
        assert result == "success"


@pytest.mark.asyncio
class TestAsyncPlayerUtils(AsyncBaseTestCase):
    @pytest_asyncio.fixture(autouse=True)
    async def async_setup(self):
        self.test_context = self.test_context if hasattr(self, 'test_context') else None
        self.player_data = TestDataFactory.create_player_data(name="Async User", phone="07999999999")

    async def test_async_player_name(self):
        assert self.player_data.name == "Async User"

    async def test_async_mock_llm(self):
        llm = self.create_mock_llm(responses=["response1", "response2"])
        result = llm.invoke("prompt1")
        assert result == "response1"


@pytest.mark.integration
class TestIntegrationPlayerFlow(IntegrationTestCase):
    def setup_test_data(self):
        self.scenario = SampleData.PLAYERS["john_smith"]

    def test_integration_player_onboarding(self):
        assert self.scenario.onboarding_status.value == "completed"

    def test_integration_player_telegram(self):
        assert self.scenario.telegram_username == "johnsmith" 