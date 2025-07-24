#!/usr/bin/env python3
"""
Firebase Expense Repository Implementation

This module provides the Firebase implementation of the expense repository interface.
"""


from kickai.core.firestore_constants import COLLECTION_PAYMENTS
from kickai.database.interfaces import DataStoreInterface
from kickai.features.payment_management.domain.repositories.expense_repository_interface import (
    Expense,
    ExpenseRepositoryInterface,
)


class FirebaseExpenseRepository(ExpenseRepositoryInterface):
    """Firebase implementation of the expense repository."""

    def __init__(self, database: DataStoreInterface):
        self.database = database
        self.collection_name = COLLECTION_PAYMENTS

    async def create_expense(self, expense: Expense) -> Expense:
        """Create a new expense."""
        expense_data = {
            "id": expense.id,
            "team_id": expense.team_id,
            "description": expense.description,
            "amount": expense.amount,
            "category": expense.category,
            "created_by": expense.created_by,
            "created_at": expense.created_at,
            "updated_at": expense.updated_at
        }

        await self.database.create_document(
            collection_name=self.collection_name,
            document_id=expense.id,
            data=expense_data
        )

        return expense

    async def get_expense_by_id(self, expense_id: str, team_id: str) -> Expense | None:
        """Get an expense by ID."""
        try:
            doc = await self.database.get_document(
                collection_name=self.collection_name,
                document_id=expense_id
            )

            if doc and doc.get("team_id") == team_id:
                return self._doc_to_expense(doc)
            return None
        except Exception:
            return None

    async def get_all_expenses(self, team_id: str) -> list[Expense]:
        """Get all expenses for a team."""
        try:
            docs = await self.database.query_documents(
                collection_name=self.collection_name,
                filters=[("team_id", "==", team_id)]
            )

            return [self._doc_to_expense(doc) for doc in docs]
        except Exception:
            return []

    async def update_expense(self, expense: Expense) -> Expense:
        """Update an expense."""
        expense_data = {
            "id": expense.id,
            "team_id": expense.team_id,
            "description": expense.description,
            "amount": expense.amount,
            "category": expense.category,
            "created_by": expense.created_by,
            "created_at": expense.created_at,
            "updated_at": expense.updated_at
        }

        await self.database.update_document(
            collection_name=self.collection_name,
            document_id=expense.id,
            data=expense_data
        )

        return expense

    async def delete_expense(self, expense_id: str, team_id: str) -> bool:
        """Delete an expense."""
        try:
            # Verify the expense exists and belongs to the team
            expense = await self.get_expense_by_id(expense_id, team_id)
            if not expense:
                return False

            await self.database.delete_document(
                collection_name=self.collection_name,
                document_id=expense_id
            )

            return True
        except Exception:
            return False

    async def get_expenses_by_category(self, team_id: str, category: str) -> list[Expense]:
        """Get expenses by category."""
        try:
            docs = await self.database.query_documents(
                collection_name=self.collection_name,
                filters=[
                    ("team_id", "==", team_id),
                    ("category", "==", category)
                ]
            )

            return [self._doc_to_expense(doc) for doc in docs]
        except Exception:
            return []

    def _doc_to_expense(self, doc: dict) -> Expense:
        """Convert a Firestore document to an Expense entity."""
        return Expense(
            id=doc.get("id"),
            team_id=doc.get("team_id"),
            description=doc.get("description"),
            amount=doc.get("amount", 0.0),
            category=doc.get("category"),
            created_by=doc.get("created_by"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at")
        )
