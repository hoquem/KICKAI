from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


class TaskParameterType(Enum):
    STRING = auto()
    INTEGER = auto()


class TaskParameterValidationError(ValueError):
    pass


@dataclass
class TaskParameter:
    name: str
    type: TaskParameterType
    description: str
    required: bool = True


@dataclass
class TaskTemplate:
    id: str
    name: str
    description: str
    parameters: list[TaskParameter]
    agent_type: str

    def instantiate(self, params: dict[str, Any]) -> Task:
        for p in self.parameters:
            if p.required and p.name not in params:
                raise TaskParameterValidationError(f"Missing required parameter: {p.name}")
            if p.name in params:
                if p.type == TaskParameterType.STRING and not isinstance(params[p.name], str):
                    raise TaskParameterValidationError(f"Parameter '{p.name}' must be a string")
                if p.type == TaskParameterType.INTEGER and not isinstance(params[p.name], int):
                    raise TaskParameterValidationError(f"Parameter '{p.name}' must be an integer")

        return Task(
            id=f"{self.id}_{int(datetime.utcnow().timestamp()*1000)}",
            name=self.name,
            description=self.description,
            status=TaskStatus.PENDING,
            parameters=params,
            template_name=self.id,
        )


@dataclass
class Task:
    id: str
    name: str
    description: str
    status: TaskStatus
    parameters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    template_name: str | None = None


class TaskRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, TaskTemplate] = {}
        # Seed a minimal set used by tests
        self.register_template(
            TaskTemplate(
                id="message_processing",
                name="Message Processing",
                description="Process a user message",
                parameters=[
                    TaskParameter("message", TaskParameterType.STRING, "Message text", True),
                    TaskParameter("user_id", TaskParameterType.STRING, "User ID", True),
                ],
                agent_type="message_processor",
            )
        )
        self.register_template(
            TaskTemplate(
                id="player_registration",
                name="Player Registration",
                description="Register a player",
                parameters=[TaskParameter("player", TaskParameterType.STRING, "Player info", True)],
                agent_type="player_coordinator",
            )
        )
        self.register_template(
            TaskTemplate(
                id="payment_processing",
                name="Payment Processing",
                description="Process a payment",
                parameters=[
                    TaskParameter("payment", TaskParameterType.STRING, "Payment info", True)
                ],
                agent_type="finance_manager",
            )
        )
        self.register_template(
            TaskTemplate(
                id="team_creation",
                name="Team Creation",
                description="Create a team",
                parameters=[TaskParameter("team", TaskParameterType.STRING, "Team entity", True)],
                agent_type="team_administrator",
            )
        )

    def register_template(self, template: TaskTemplate) -> None:
        self._templates[template.id] = template

    def get_template(self, template_id: str) -> TaskTemplate | None:
        return self._templates.get(template_id)

    def list_templates(self) -> list[TaskTemplate]:
        return list(self._templates.values())

    def get_templates_by_agent_type(self, agent_type: str) -> list[TaskTemplate]:
        return [t for t in self._templates.values() if t.agent_type == agent_type]

    def create_task(
        self, template_id: str, params: dict[str, Any], task_id: str | None = None
    ) -> Task:
        template = self.get_template(template_id)
        if not template:
            raise ValueError("Template not found")
        task = template.instantiate(params)
        if task_id:
            task.id = task_id
        return task

    # Convenience constructors used by tests
    def create_message_processing_task(self, message: str, user_id: str) -> Task:
        return self.create_task("message_processing", {"message": message, "user_id": user_id})

    def create_player_registration_task(self, player: Any) -> Task:
        return self.create_task("player_registration", {"player": player})

    def create_payment_processing_task(self, payment: Any) -> Task:
        return self.create_task("payment_processing", {"payment": payment})

    def create_team_creation_task(self, team: Any) -> Task:
        return self.create_task("team_creation", {"team": team})
