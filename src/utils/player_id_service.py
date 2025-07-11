"""
Player ID Service (thin wrapper around id_manager in id_generator.py)
"""

from utils.id_generator import id_manager
from database.interfaces import DataStoreInterface
from typing import Optional, Set, Tuple

# Thin wrapper for backward compatibility

def parse_player_name(full_name: str) -> Tuple[str, str]:
    if not full_name or not full_name.strip():
        return "", ""
    parts = [part.strip() for part in full_name.strip().split() if part.strip()]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[-1]


def generate_player_id_from_name(full_name: str, existing_ids: Optional[Set[str]] = None) -> str:
    first_name, last_name = parse_player_name(full_name)
    return id_manager.generate_player_id(first_name, last_name, existing_ids)


def validate_player_id_format(player_id: str) -> bool:
    return id_manager.player_generator.validate_player_id(player_id)


def extract_player_id_from_text(text: str) -> Optional[str]:
    return id_manager.player_generator.extract_player_id_from_text(text)


# Async uniqueness helper (moved from player_id_service)
async def generate_unique_player_id(full_name: str, team_id: str, data_store: DataStoreInterface) -> str:
    first_name, last_name = parse_player_name(full_name)
    base_id = f"{first_name[0].upper()}{last_name[0].upper()}"
    all_players_with_base = await data_store.query_documents('players', [
        {'field': 'player_id', 'operator': '>=', 'value': base_id},
        {'field': 'player_id', 'operator': '<', 'value': base_id + 'Z'}
    ])
    existing_ids = set(p.get('player_id') for p in all_players_with_base if p.get('player_id'))
    return id_manager.player_generator.find_next_available_id(base_id, existing_ids) 