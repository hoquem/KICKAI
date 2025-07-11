import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.firebase_client import get_firebase_client
from database.models_improved import Expense, ExpenseCategory
from core.exceptions import ExpenseError, create_error_context

logger = logging.getLogger(__name__)

class ExpenseService:
    """Service for managing team expenses."""

    def __init__(self, data_store=None):
        if data_store is None:
            self._data_store = get_firebase_client()
        else:
            self._data_store = data_store
        # Local import to break circular dependency
        from services.team_service import get_team_service
        self.team_service = get_team_service()

    async def record_expense(self, team_id: str, amount: float, category: ExpenseCategory, description: Optional[str] = None, receipt_url: Optional[str] = None) -> Expense:
        """Records a new expense for a team."""
        try:
            # Check against budget limits
            can_afford, remaining_budget = await self.team_service.check_expense_against_budget(team_id, category, amount)
            if not can_afford:
                raise ExpenseError(f"Expense of £{amount:.2f} for {category.value} exceeds budget limit. Remaining budget: £{remaining_budget:.2f}")

            expense = Expense(
                team_id=team_id,
                amount=amount,
                category=category,
                description=description,
                receipt_url=receipt_url
            )

            expense_id = await self._data_store.create_document('expenses', expense.to_dict(), expense.id)
            expense.id = expense_id
            logger.info(f"Expense recorded: {expense.id} for team {team_id}")
            return expense
        except ExpenseError:
            raise
        except Exception as e:
            logger.error(f"Failed to record expense for team {team_id}: {e}")
            raise ExpenseError(f"Failed to record expense: {str(e)}", create_error_context("record_expense"))

    async def get_expense(self, expense_id: str) -> Optional[Expense]:
        """Retrieves an expense by its ID."""
        try:
            data = await self._data_store.get_document('expenses', expense_id)
            if data:
                return Expense.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get expense {expense_id}: {e}")
            raise ExpenseError(f"Failed to get expense: {str(e)}", create_error_context("get_expense"))

    async def list_expenses(self, team_id: str, category: Optional[ExpenseCategory] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Expense]:
        """Lists expenses for a team, with optional filters."""
        try:
            filters = [{'field': 'team_id', 'operator': '==', 'value': team_id}]
            if category:
                filters.append({'field': 'category', 'operator': '==', 'value': category.value})
            if start_date:
                filters.append({'field': 'date', 'operator': '>=', 'value': start_date})
            if end_date:
                filters.append({'field': 'date', 'operator': '<=', 'value': end_date})

            data_list = await self._data_store.query_documents('expenses', filters)
            return [Expense.from_dict(data) for data in data_list]
        except Exception as e:
            logger.error(f"Failed to list expenses for team {team_id}: {e}")
            raise ExpenseError(f"Failed to list expenses: {str(e)}", create_error_context("list_expenses"))

    async def get_total_expenses_by_category(self, team_id: str, category: ExpenseCategory) -> float:
        """Calculates the total expenses for a given category for a team."""
        try:
            expenses = await self.list_expenses(team_id, category=category)
            return sum(e.amount for e in expenses)
        except Exception as e:
            logger.error(f"Failed to get total expenses for category {category.value} for team {team_id}: {e}")
            raise ExpenseError(f"Failed to get total expenses by category: {str(e)}", create_error_context("get_total_expenses_by_category"))

    async def get_total_expenses(self, team_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """Calculates the total expenses for a team within a given period."""
        try:
            expenses = await self.list_expenses(team_id, start_date=start_date, end_date=end_date)
            return sum(e.amount for e in expenses)
        except Exception as e:
            logger.error(f"Failed to get total expenses for team {team_id}: {e}")
            raise ExpenseError(f"Failed to get total expenses: {str(e)}", create_error_context("get_total_expenses"))

    async def categorize_expense_ai(self, description: str) -> ExpenseCategory:
        """Placeholder for AI-assisted expense categorization."""
        # In a real implementation, this would call an LLM or a dedicated AI model
        # For now, it's a simple keyword-based categorization
        description_lower = description.lower()
        if "pitch" in description_lower or "field" in description_lower:
            return ExpenseCategory.PITCH_FEES
        elif "referee" in description_lower or "umpire" in description_lower:
            return ExpenseCategory.REFEREE_FEES
        elif "kit" in description_lower or "ball" in description_lower or "cone" in description_lower:
            return ExpenseCategory.EQUIPMENT
        elif "food" in description_lower or "drink" in description_lower or "meal" in description_lower:
            return ExpenseCategory.TEAM_MEAL
        elif "fa fee" in description_lower or "registration" in description_lower:
            return ExpenseCategory.FA_FEES
        return ExpenseCategory.OTHER


_expense_service: Optional[ExpenseService] = None

def get_expense_service() -> ExpenseService:
    global _expense_service
    if _expense_service is None:
        _expense_service = ExpenseService()
    return _expense_service

def initialize_expense_service() -> ExpenseService:
    global _expense_service
    _expense_service = ExpenseService()
    return _expense_service
