from telegram import Update
from telegram.ext import ContextTypes
from src.services.player_service import PlayerService
from src.core.logger import BotLogger
from src.core.exceptions import PlayerRegistrationError
from src.utils.id_generator import IdGenerator
from typing import Optional

logger = BotLogger.get_logger(__name__)

async def handle_add_player(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    player_name: str,
    phone: str,
    position: str,
    fa_eligible: bool = False,
    player_id: Optional[str] = None
) -> None:
    """
    Handles the /addplayer command to register a new player.
    Parameters are expected to be parsed by LLMIntentExtractor.
    """
    if not update.message:
        logger.warning("Add player command received without a message.")
        return

    player_service = PlayerService()

    try:
        if player_id:
            # If player_id is provided, use it
            new_player = await player_service.create_player(player_name=player_name, phone=phone, position=position, added_by=str(update.effective_user.id), fa_eligible=fa_eligible, player_id=player_id)
            await update.message.reply_text(
                f"Player '{new_player.player_name}' registered with ID '{new_player.player_id}'."
            )
            logger.info(f"Player '{new_player.player_name}' registered with provided ID '{new_player.player_id}'.")
        else:
            # If player_id is not provided, generate one
            generated_player_id = IdGenerator.generate_player_id(player_name)
            new_player = await player_service.create_player(player_name=player_name, phone=phone, position=position, added_by=str(update.effective_user.id), fa_eligible=fa_eligible, player_id=generated_player_id)
            await update.message.reply_text(
                f"Player '{new_player.player_name}' registered with generated ID '{new_player.player_id}'."
            )
            logger.info(f"Player '{new_player.player_name}' registered with generated ID '{new_player.player_id}'.")

    except PlayerRegistrationError as e:
        await update.message.reply_text(f"Error registering player: {e}")
        logger.error(f"Error registering player '{player_name}' (ID: {player_id}): {e}")
    except Exception as e:
        await update.message.reply_text("An unexpected error occurred during player registration.")
        logger.critical(f"Unexpected error in handle_add_player for '{player_name}' (ID: {player_id}): {e}", exc_info=True)