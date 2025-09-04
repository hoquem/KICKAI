#!/usr/bin/env python3
"""
Command analysis utilities.

Provides intelligent command classification and analysis for the KICKAI system.
"""


from loguru import logger

from kickai.agents.config.message_router_config import (
    AMBIGUOUS_REFS,
    CLEAR_COMMAND_NAMES,
    ERROR_MESSAGES,
    FOLLOWUP_INDICATORS,
    LOG_MESSAGES,
    SLASH_COMMAND_PREFIX,
    WARNING_MESSAGES,
)


class CommandAnalyzer:
    """
    Intelligent command analysis and classification.

    Determines if messages require NLP processing or can be handled directly.
    """

    @staticmethod
    def requires_nlp_processing(text: str, chat_type: str) -> bool:
        """
        Enhanced NLP requirement detection using command registry integration.

        Args:
            text: Message text to analyze
            chat_type: Chat type for context

        Returns:
            True if message needs NLP processing, False for clear commands
        """
        try:
            # ALL business logic here
            # Use the improved clear command detection
            if CommandAnalyzer.is_clear_command(text, chat_type):
                logger.info(LOG_MESSAGES["SKIP_NLP_CLEAR_COMMAND"].format(text=text))
                return False

            # Check if it's a conversational follow-up
            if CommandAnalyzer.is_conversational_followup(text):
                logger.info(LOG_MESSAGES["NLP_CONVERSATIONAL_FOLLOWUP"].format(text=text))
                return True

            # Check if text contains ambiguous references
            if CommandAnalyzer.contains_ambiguous_references(text):
                logger.info(LOG_MESSAGES["NLP_AMBIGUOUS_REFERENCES"].format(text=text))
                return True

            # Default to NLP for natural language queries
            logger.info(LOG_MESSAGES["NLP_NATURAL_LANGUAGE"].format(text=text))
            return True

        except Exception as e:
            logger.error(f"❌ Error in requires_nlp_processing: {e}")
            # Fail safe - assume needs NLP if uncertain
            return True

    @staticmethod
    def is_clear_command(text: str, chat_type: str | None = None) -> bool:
        """
        Registry-based clear command detection with slash-agnostic support.

        Args:
            text: User input text to analyze
            chat_type: Optional chat context for classification

        Returns:
            True if command is clear and doesn't need NLP processing
        """
        try:
            # ALL business logic here
            # Input validation using utility functions
            from kickai.utils.tool_validation import ToolValidationError, validate_string_input

            try:
                validate_string_input(text, "Command text", allow_empty=False)
            except ToolValidationError as e:
                logger.warning(WARNING_MESSAGES["INVALID_COMMAND_INPUT"].format(error=str(e)))
                return False

            # Extract command from text
            command = CommandAnalyzer.extract_command_from_text(text)
            if not command:
                return False

            # Get command registry
            from kickai.core.command_registry_initializer import get_initialized_command_registry

            registry = get_initialized_command_registry()
            if not registry:
                logger.warning(WARNING_MESSAGES["COMMAND_REGISTRY_UNAVAILABLE"])
                return False

            # Query registry with multiple variants
            command_metadata = CommandAnalyzer.find_command_in_registry(registry, command)
            if not command_metadata:
                return False

            # Classify command clarity
            return CommandAnalyzer.classify_command_clarity(command_metadata, text, chat_type)

        except Exception as e:
            logger.error(f"❌ Error in is_clear_command: {e}")
            # Fail safe - assume needs NLP if uncertain
            return False

    @staticmethod
    def extract_command_from_text(text: str) -> str | None:
        """
        Extract the command portion from user text.

        Args:
            text: User input text

        Returns:
            Command string if found, None otherwise
        """
        try:
            # ALL business logic here
            if not text or not text.strip():
                return None

            # Get first word
            first_word = text.strip().split()[0]

            # Handle slash commands and natural references
            if first_word.startswith(SLASH_COMMAND_PREFIX):
                return first_word.lower()

            # For non-slash text, check if it looks like a command
            # (single word that could be a command)
            if len(text.strip().split()) == 1:
                return first_word.lower()

            return None

        except Exception as e:
            logger.error(f"❌ Error in extract_command_from_text: {e}")
            return None

    @staticmethod
    def find_command_in_registry(registry, command: str):
        """
        Find command in registry with multiple variants.

        Args:
            registry: Command registry instance
            command: Command to find

        Returns:
            CommandMetadata if found, None otherwise
        """
        try:
            # ALL business logic here
            # Try both with and without slash for flexibility
            command_variants = [command, f"/{command.lstrip('/')}", command.lstrip("/")]

            for variant in command_variants:
                command_metadata = registry.get_command(variant)
                if command_metadata:
                    return command_metadata

            return None

        except Exception as e:
            logger.error(f"❌ Error in find_command_in_registry: {e}")
            return None

    @staticmethod
    def classify_command_clarity(
        command_metadata, original_text: str, chat_type: str | None = None
    ) -> bool:
        """
        Intelligent command clarity classification based on metadata.

        Args:
            command_metadata: Command metadata from registry
            original_text: Original user input text
            chat_type: Optional chat context

        Returns:
            True if command is considered clear/unambiguous
        """
        try:
            # ALL business logic here
            # System commands are always clear
            if hasattr(command_metadata, "command_type") and command_metadata.command_type:
                if command_metadata.command_type.value in ["system", "utility"]:
                    return True

            # Commands marked as not requiring NLP
            if hasattr(command_metadata, "requires_nlp") and not command_metadata.requires_nlp:
                return True

            # Commands with no required parameters
            if not command_metadata.parameters or getattr(
                command_metadata, "parameter_optional", True
            ):
                return True

            # Self-referential commands without parameters
            if CommandAnalyzer.is_self_referential_command(command_metadata, original_text):
                return True

            # Specific clear commands (extensible via config)
            return CommandAnalyzer.check_specific_clear_commands(command_metadata.name)

        except Exception as e:
            logger.error(f"❌ Error in classify_command_clarity: {e}")
            from kickai.core.exceptions import ValidationError

            raise ValidationError(ERROR_MESSAGES["COMMAND_CLARITY_ERROR"].format(error=e)) from None

    @staticmethod
    def is_self_referential_command(command_metadata, original_text: str) -> bool:
        """
        Check if command is self-referential (e.g., /info without parameters).

        Args:
            command_metadata: Command metadata from registry
            original_text: Original user input text

        Returns:
            True if command is self-referential
        """
        try:
            # ALL business logic here
            text_parts = original_text.strip().split()
            if len(text_parts) == 1 and command_metadata.name.lower() in [
                "info",
                "/info",
                "status",
                "/status",
            ]:
                return True  # Single word info/status commands are clear (self-reference)
            return False

        except Exception as e:
            logger.error(f"❌ Error in is_self_referential_command: {e}")
            return False

    @staticmethod
    def check_specific_clear_commands(command_name: str) -> bool:
        """
        Check if command is in the list of specifically clear commands.

        Args:
            command_name: Command name to check

        Returns:
            True if command is in clear commands list
        """
        try:
            # ALL business logic here
            return command_name.lower() in CLEAR_COMMAND_NAMES

        except Exception as e:
            logger.error(f"❌ Error in check_specific_clear_commands: {e}")
            return False

    @staticmethod
    def is_conversational_followup(text: str) -> bool:
        """
        Check if message is a conversational follow-up that needs context.

        Args:
            text: Message text to analyze

        Returns:
            True if message appears to be a conversational follow-up
        """
        try:
            # ALL business logic here
            text_lower = text.lower().strip()
            return any(indicator in text_lower for indicator in FOLLOWUP_INDICATORS)

        except Exception as e:
            logger.error(f"❌ Error in is_conversational_followup: {e}")
            return False

    @staticmethod
    def contains_ambiguous_references(text: str) -> bool:
        """
        Check if text contains references that need context resolution.

        Args:
            text: Text to analyze

        Returns:
            True if text contains ambiguous references
        """
        try:
            # ALL business logic here
            text_lower = text.lower()
            return any(ref in text_lower.split() for ref in AMBIGUOUS_REFS)

        except Exception as e:
            logger.error(f"❌ Error in contains_ambiguous_references: {e}")
            return False

    @staticmethod
    def is_helper_command(command: str) -> bool:
        """
        Check if a command is a helper system command.

        Args:
            command: The command to check

        Returns:
            True if it's a helper command, False otherwise
        """
        try:
            # ALL business logic here
            # Helper system is now proactive - no command-driven interactions
            return False

        except Exception as e:
            logger.error(f"❌ Error in is_helper_command: {e}")
            return False
