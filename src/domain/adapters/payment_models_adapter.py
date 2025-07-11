from domain.interfaces.payment_models import PaymentModel, ExpenseModel, PaymentStatus, ExpenseCategory
from database.models_improved import Payment, Expense


class PaymentModelAdapter(PaymentModel):
    """Adapter to convert infrastructure Payment model to domain interface."""
    
    def __init__(self, payment: Payment):
        self._payment = payment
    
    @property
    def id(self) -> str:
        return self._payment.id
    
    @property
    def amount(self) -> float:
        return self._payment.amount
    
    @property
    def payment_type(self) -> str:
        return self._payment.payment_type
    
    @property
    def status(self) -> PaymentStatus:
        return PaymentStatus(self._payment.status.value)
    
    @property
    def description(self):
        return self._payment.description
    
    @property
    def due_date(self):
        return self._payment.due_date
    
    @property
    def paid_date(self):
        return self._payment.paid_date


class ExpenseModelAdapter(ExpenseModel):
    """Adapter to convert infrastructure Expense model to domain interface."""
    
    def __init__(self, expense: Expense):
        self._expense = expense
    
    @property
    def id(self) -> str:
        return self._expense.id
    
    @property
    def amount(self) -> float:
        return self._expense.amount
    
    @property
    def category(self) -> ExpenseCategory:
        return ExpenseCategory(self._expense.category.value)
    
    @property
    def description(self):
        return self._expense.description 