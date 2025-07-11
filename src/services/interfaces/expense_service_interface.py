from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from database.models_improved import Expense, ExpenseCategory

class IExpenseService(ABC):
    @abstractmethod
    async def record_expense(self, team_id: str, amount: float, category: ExpenseCategory, description: Optional[str] = None, date: Optional[datetime] = None, receipt_url: Optional[str] = None) -> Expense:
        pass

    @abstractmethod
    async def get_team_expenses(self, team_id: str, category: Optional[ExpenseCategory] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Expense]:
        pass

    @abstractmethod
    async def get_team_financial_summary(self, team_id: str, period: str) -> Dict[str, Any]:
        pass
