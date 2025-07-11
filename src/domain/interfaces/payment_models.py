from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from datetime import datetime


class PaymentStatus(Enum):
    """Domain enum for payment status."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ExpenseCategory(Enum):
    """Domain enum for expense categories."""
    EQUIPMENT = "equipment"
    FACILITY = "facility"
    TRAVEL = "travel"
    ADMINISTRATION = "administration"
    OTHER = "other"


class PaymentModel(ABC):
    """Domain interface for payment model."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        pass
    
    @property
    @abstractmethod
    def amount(self) -> float:
        pass
    
    @property
    @abstractmethod
    def payment_type(self) -> str:
        pass
    
    @property
    @abstractmethod
    def status(self) -> PaymentStatus:
        pass
    
    @property
    @abstractmethod
    def description(self) -> Optional[str]:
        pass
    
    @property
    @abstractmethod
    def due_date(self) -> Optional[datetime]:
        pass
    
    @property
    @abstractmethod
    def paid_date(self) -> Optional[datetime]:
        pass


class ExpenseModel(ABC):
    """Domain interface for expense model."""
    
    @property
    @abstractmethod
    def id(self) -> str:
        pass
    
    @property
    @abstractmethod
    def amount(self) -> float:
        pass
    
    @property
    @abstractmethod
    def category(self) -> ExpenseCategory:
        pass
    
    @property
    @abstractmethod
    def description(self) -> Optional[str]:
        pass 