#!/usr/bin/env python3
"""
Setup script for KICKAI package

This enables proper package installation and import resolution
for both development and production environments.
"""

from setuptools import setup, find_packages

setup(
    name="kickai",
    version="0.1.0",
    description="AI-powered Telegram bot for Sunday league football team management",
    author="KICKAI Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "telethon>=1.28.5",
        "pydantic>=2.0.0",
        "typer>=0.9.0",
        "firebase-admin>=6.2.0",
        "google-cloud-firestore>=2.11.0",
        "crewai>=0.11.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.1",
        "pytest-mock>=3.12.0",
        "ruff>=0.1.0",
        "mypy>=1.5.0",
        "pre-commit>=3.3.0",
    ],
    extras_require={
        "dev": [
            "ruff>=0.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.0",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.1",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
        ]
    },
    entry_points={
        'console_scripts': [
            'kickai-bot=kickai.cli:main',
        ],
        'kickai.tools': [
            'register_player=kickai.features.player_registration.domain.tools.registration_tools:register_player',
            'add_team_member=kickai.features.team_administration.domain.tools.team_tools:add_team_member',
            'send_message=kickai.features.communication.domain.tools.communication_tools:send_message',
        ],
        'kickai.commands': [
            'add=kickai.features.player_registration.application.commands.player_commands:handle_add',
            'status=kickai.features.player_registration.application.commands.player_commands:handle_status',
            'list=kickai.features.player_registration.application.commands.player_commands:handle_list',
        ],
        'kickai.services': [
            'player_service=kickai.features.player_registration.domain.services.player_service:PlayerService',
            'team_service=kickai.features.team_administration.domain.services.team_service:TeamService',
        ],
    }
) 