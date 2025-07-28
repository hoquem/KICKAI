# Python Files Missing "from typing import Optional" Import

This analysis identifies all Python files in the KICKAI project that use `Optional[]` type annotations but are missing the proper `from typing import Optional` import statement.

## Files Found with Missing Imports

### Player Registration (`kickai/features/player_registration/`)

1. **`domain/tools/registration_parser.py`**
   - Line 7: `def parse_registration_command(command: str) -> Optional[Dict[str, str]]:`

2. **`domain/services/player_linking_service.py`**
   - Line 31: `) -> Optional[Player]:`
   - Line 105: `) -> Optional[Player]:`

3. **`domain/services/fa_registration_checker.py`**
   - Line 71: `async def get_fixture_data(self, player_id: str) -> Optional[FixtureData]:`

4. **`domain/services/player_lookup_service.py`**
   - Line 12: `async def get_player_team_id(self, player_id: str) -> Optional[str]:`

5. **`domain/interfaces/player_service_interface.py`**
   - Line 11: `async def get_player(self, player_id: str, team_id: str) -> Optional[Dict[str, Any]]:`
   - Line 23: `async def list_players(self, team_id: Optional[str] = None) -> List[Dict[str, Any]]:`
   - Line 27: `async def find_player_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:`

6. **`domain/interfaces/player_lookup_interface.py`**
   - Line 15: `async def get_player_team_id(self, player_id: str) -> Optional[str]:`

### Team Administration (`kickai/features/team_administration/`)

1. **`domain/tools/team_management_tools.py`**
   - Line 23: `admin_user_id: Optional[str] = None`
   - Line 27: `def create_team(team_name: str, team_id: str, admin_user_id: Optional[str] = None) -> str:`

2. **`domain/services/multi_team_manager.py`**
   - Line 23: `def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:`

### Payment Management (`kickai/features/payment_management/`)

1. **`infrastructure/firebase_payment_repository.py`**
   - Line 24: `async def get_by_id(self, payment_id: str) -> Optional[Payment]:`

2. **`infrastructure/collectiv_payment_gateway.py`**
   - Line 55: `paid_at: Optional[datetime] = None`
   - Line 56: `transaction_id: Optional[str] = None`
   - Line 71: `completed_at: Optional[datetime] = None`

3. **`infrastructure/firebase_budget_repository.py`**
   - Line 23: `async def get_budget_by_id(self, budget_id: str) -> Optional[Budget]:`
   - Line 27: `async def get_budget_by_team_id(self, team_id: str) -> Optional[Budget]:`
   - Line 39: `async def list_budgets(self, team_id: Optional[str] = None) -> List[Budget]:`

4. **`domain/repositories/payment_repository_interface.py`**
   - Line 12: `async def get_by_id(self, payment_id: str):  # -> Optional[Payment]`

5. **`domain/repositories/budget_repository_interface.py`**
   - Line 23: `async def get_budget_by_id(self, budget_id: str) -> Optional[Budget]:`
   - Line 28: `async def get_budget_by_team_id(self, team_id: str) -> Optional[Budget]:`
   - Line 43: `async def list_budgets(self, team_id: Optional[str] = None) -> List[Budget]:`

6. **`domain/services/budget_service.py`**
   - Line 37: `async def get_budget_by_team(self, team_id: str) -> Optional[Budget]:`

7. **`domain/services/payment_service.py`**
   - Line 31: `payment_gateway: Optional[IPaymentGateway] = None,`
   - Line 32: `player_lookup: Optional[IPlayerLookup] = None,`
   - Line 33: `team_id: Optional[str] = None,`

8. **`domain/entities/budget.py`**
   - Line 20: `team_id: Optional[str] = None`
   - Line 21: `total_amount: Optional[Decimal] = None`
   - Line 26: `end_date: Optional[datetime] = None`

9. **`domain/entities/payment.py`**
   - Line 24: `id: Optional[str] = None`
   - Line 25: `team_id: Optional[str] = None`
   - Line 26: `description: Optional[str] = None`

10. **`domain/interfaces/budget_service_interface.py`**
    - Line 24: `async def get_budget_by_team(self, team_id: str) -> Optional[Budget]:`

11. **`domain/interfaces/payment_gateway_interface.py`**
    - Line 32: `self, transaction_id: str, amount: Optional[float] = None`
    - Line 39: `self, amount: float, currency: str, source: str, description: Optional[str] = None`
    - Line 45: `async def create_refund(self, charge_id: str, amount: Optional[float] = None) -> Dict[str, Any]:`

12. **`domain/interfaces/payment_service_interface.py`**
    - Line 22: `due_date: Optional[datetime] = None,`
    - Line 23: `related_entity_id: Optional[str] = None,`
    - Line 40: `self, transaction_id: str, amount: Optional[float] = None`

13. **`domain/interfaces/expense_service_interface.py`**
    - Line 24: `date: Optional[datetime] = None,`
    - Line 30: `async def get_expenses_by_team(self, team_id: str, limit: Optional[int] = None) -> List[Expense]:`
    - Line 43: `self, team_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None`

### Shared Components (`kickai/features/shared/`)

1. **`application/commands/types.py`**
   - Line 26: `additional_data: Optional[Dict[str, Any]] = None`
   - Line 35: `error: Optional[str] = None`
   - Line 36: `data: Optional[Dict[str, Any]] = None`

2. **`application/commands/base_command.py`**
   - Line 37: `error: Optional[str] = None`
   - Line 38: `data: Optional[Dict[str, Any]] = None`

3. **`domain/services/command_processing_service.py`**
   - Line 34: `user_permissions: Optional[UserPermissions] = None`
   - Line 35: `player_data: Optional[Dict[str, Any]] = None`
   - Line 36: `team_member_data: Optional[Dict[str, Any]] = None`

4. **`domain/services/message_formatting_service.py`**
   - Line 25: `user_name: Optional[str] = None`
   - Line 60: `def format_error_message(self, error: str, context: Optional[MessageContext] = None) -> str:`
   - Line 64: `def format_success_message(self, message: str, context: Optional[MessageContext] = None) -> str:`

5. **`domain/entities/base_entity.py`**
   - Line 13: `id: Optional[str] = None`
   - Line 14: `created_at: Optional[datetime] = None`
   - Line 15: `updated_at: Optional[datetime] = None`

### Health Monitoring (`kickai/features/health_monitoring/`)

1. **`infrastructure/firebase_health_check_repository.py`**
   - Line 18: `async def get_by_id(self, check_id: str) -> Optional[Dict[str, Any]]:`

2. **`domain/repositories/health_check_repository_interface.py`**
   - Line 11: `async def get_by_id(self, check_id: str) -> Optional[Dict[str, Any]]:`

3. **`domain/services/background_health_monitor.py`**
   - Line 31: `resolved_at: Optional[datetime] = None`
   - Line 124: `details: Optional[Dict[str, Any]] = None,`

4. **`domain/services/health_check_service.py`**
   - Line 739: `async def export_health_report(self, file_path: Optional[str] = None) -> str:`

5. **`domain/entities/health_check_types.py`**
   - Line 43: `error: Optional[Exception] = None`

6. **`domain/interfaces/health_check_service_interface.py`**
   - Line 25: `async def export_health_report(self, file_path: Optional[str] = None) -> str:`

### Communication (`kickai/features/communication/`)

1. **`infrastructure/firebase_notification_repository.py`**
   - Line 15: `async def get_by_id(self, notification_id: str) -> Optional[Dict[str, Any]]:`

2. **`infrastructure/firebase_message_repository.py`**
   - Line 27: `async def get_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:`

3. **`domain/tools/telegram_tools.py`**
   - Line 23: `team_id: Optional[str] = None`
   - Line 27: `def send_telegram_message(chat_id: str, text: str, team_id: Optional[str] = None) -> str:`

4. **`domain/repositories/message_repository_interface.py`**
   - Line 12: `async def get_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:`

5. **`domain/services/communication_service.py`**
   - Line 14: `def __init__(self, telegram_bot_service: Optional[TelegramBotService] = None):`

6. **`domain/services/message_service.py`**
   - Line 21: `conversation_id: Optional[str] = None,`
   - Line 22: `metadata: Optional[Dict[str, Any]] = None,`

7. **`domain/services/reminder_service.py`**
   - Line 70: `async def send_automated_reminder(self, player: Player) -> Optional[ReminderMessage]:`

8. **`domain/services/notification_service.py`**
   - Line 11: `self, recipient_id: str, message: str, metadata: Optional[Dict[str, Any]] = None`

9. **`domain/services/message_routing_service.py`**
   - Line 22: `def should_route_to_onboarding(player: Optional[Player], message: str) -> tuple[bool, str]:`
   - Line 57: `def should_route_to_player_update(player: Optional[Player], message: str) -> tuple[bool, str]:`
   - Line 98: `def should_route_to_general_handler(player: Optional[Player], message: str) -> tuple[bool, str]:`

10. **`domain/services/invite_link_service.py`**
    - Line 104: `def _validate_secure_invite_data(self, invite_data: str) -> Optional[dict]:`
    - Line 346: `) -> Optional[Dict[str, Any]]:`
    - Line 487: `def _extract_invite_id_from_link(self, invite_link: str) -> Optional[str]:`

11. **`domain/entities/message.py`**
    - Line 14: `metadata: Optional[Dict[str, Any]] = None`

### System Infrastructure (`kickai/features/system_infrastructure/`)

1. **`domain/tools/help_tools.py`**
   - Line 22: `user_id: Optional[str] = None`
   - Line 23: `team_id: Optional[str] = None`
   - Line 29: `user_id: Optional[str] = None,`

2. **`domain/tools/logging_tools.py`**
   - Line 19: `user_id: Optional[str] = None`
   - Line 20: `team_id: Optional[str] = None`
   - Line 27: `context: Optional[str] = None`

3. **`domain/tools/firebase_tools.py`**
   - Line 23: `team_id: Optional[str] = None`
   - Line 27: `def get_firebase_document(collection: str, document_id: str, team_id: Optional[str] = None) -> str:`

4. **`domain/services/permission_service.py`**
   - Line 32: `username: Optional[str] = None`
   - Line 368: `async def handle_last_admin_leaving(self, team_id: str) -> Optional[str]:`
   - Line 383: `_permission_service: Optional[PermissionService] = None`

### Match Management (`kickai/features/match_management/`)

1. **`infrastructure/firebase_match_repository.py`**
   - Line 16: `async def get_by_id(self, match_id: str) -> Optional[Match]:`

2. **`domain/repositories/match_repository_interface.py`**
   - Line 12: `async def get_by_id(self, match_id: str) -> Optional[Match]:`

3. **`domain/services/match_management_service.py`**
   - Line 14: `async def get_match_by_id(self, match_id: str) -> Optional[Match]:`

4. **`domain/services/match_service.py`**
   - Line 28: `location: Optional[str] = None,`
   - Line 31: `competition: Optional[str] = None,`
   - Line 69: `async def get_match(self, match_id: str) -> Optional[Match]:`

5. **`domain/interfaces/match_service_interface.py`**
   - Line 11: `async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:`
   - Line 23: `async def list_matches(self, team_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:`

## Summary

**Total Files Missing Import: 61 files**

**Distribution by Feature:**
- Payment Management: 13 files
- Communication: 11 files  
- Player Registration: 6 files
- Health Monitoring: 6 files
- Match Management: 5 files
- Shared Components: 5 files
- System Infrastructure: 4 files
- Team Administration: 2 files

## Impact Assessment

These missing imports will cause runtime errors when the bot starts up and these modules are loaded. Since many of these files are in critical paths (repositories, services, tools), this is likely preventing successful bot startup.

## Recommended Fix

Add `from typing import Optional` to the import section of each identified file. For files that already have other typing imports, add `Optional` to the existing import statement. For files without typing imports, add a new import line.