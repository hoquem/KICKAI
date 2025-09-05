"""
Entry point discovery for registries.

This module provides utilities for discovering registry items
from setuptools entry points.
"""

from typing import Any

import pkg_resources
from loguru import logger


class EntryPointDiscovery:
    """Discovers items from setuptools entry points."""

    @staticmethod
    def discover_tools() -> dict[str, Any]:
        """Discover tools from entry points."""
        tools = {}

        for entry_point in pkg_resources.iter_entry_points("kickai.tools"):
            try:
                tool = entry_point.load()
                tools[entry_point.name] = tool
                logger.info(f"✅ Discovered tool: {entry_point.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load tool {entry_point.name}: {e}")

        return tools

    @staticmethod
    def discover_commands() -> dict[str, Any]:
        """Discover commands from entry points."""
        commands = {}

        for entry_point in pkg_resources.iter_entry_points("kickai.commands"):
            try:
                command = entry_point.load()
                commands[entry_point.name] = command
                logger.info(f"✅ Discovered command: {entry_point.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load command {entry_point.name}: {e}")

        return commands

    @staticmethod
    def discover_services() -> dict[str, Any]:
        """Discover services from entry points."""
        services = {}

        for entry_point in pkg_resources.iter_entry_points("kickai.services"):
            try:
                service_class = entry_point.load()
                services[entry_point.name] = service_class
                logger.info(f"✅ Discovered service: {entry_point.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load service {entry_point.name}: {e}")

        return services

    @staticmethod
    def list_all_entry_points() -> dict[str, list[str]]:
        """List all available entry points."""
        entry_points = {}

        for group in ["kickai.tools", "kickai.commands", "kickai.services"]:
            entry_points[group] = []
            for entry_point in pkg_resources.iter_entry_points(group):
                entry_points[group].append(entry_point.name)

        return entry_points
