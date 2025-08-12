"""
Utilities for capturing tool outputs and validating agent responses against tool data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ToolExecution:
    tool_name: str
    input_parameters: dict[str, Any]
    output_result: Any
    execution_time: datetime
    duration_ms: float
    success: bool
    error_message: str | None = None


@dataclass
class ToolOutputCapture:
    executions: list[ToolExecution] = field(default_factory=list)

    def add_execution(self, execution: ToolExecution) -> None:
        logger.debug(f"[TOOL CAPTURE] Added execution for {execution.tool_name}")
        self.executions.append(execution)

    def get_latest_output(self, tool_name: str) -> Any | None:
        for execution in reversed(self.executions):
            if execution.tool_name == tool_name and execution.success:
                return execution.output_result
        return None

    def get_all_outputs(self, tool_name: str) -> list[Any]:
        return [e.output_result for e in self.executions if e.tool_name == tool_name and e.success]

    def get_tool_names(self) -> list[str]:
        return list({e.tool_name for e in self.executions})

    def get_execution_summary(self) -> dict[str, Any]:
        total = len(self.executions)
        successful = sum(1 for e in self.executions if e.success)
        failed = total - successful
        tools: set[str] = {e.tool_name for e in self.executions}

        latest_outputs: dict[str, Any | None] = {}
        for tool in tools:
            latest_outputs[tool] = self.get_latest_output(tool)

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "tools_used": list(tools),
            "latest_outputs": latest_outputs,
        }


class ToolOutputCaptureMixin:
    def __init__(self) -> None:
        self.tool_capture = ToolOutputCapture()

    def clear_captured_outputs(self) -> None:
        self.tool_capture.executions.clear()
        logger.debug("🧹 [TOOL CAPTURE] Cleared all captured outputs")


def extract_tool_outputs_from_context(context: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}

    direct = context.get("tool_outputs")
    if isinstance(direct, dict):
        result.update(direct)

    agent_result = context.get("agent_result")
    if isinstance(agent_result, dict):
        tool_results = agent_result.get("tool_results")
        if isinstance(tool_results, dict):
            # merge, agent_result can add more keys
            for k, v in tool_results.items():
                result[k] = v

    return result


def _parse_player_names_from_text(text: str) -> dict[str, list[str]]:
    lines = text.splitlines()
    active: list[str] = []
    pending: list[str] = []
    other: list[str] = []

    current_section = "active"
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()
        if "PENDING APPROVAL" in upper:
            current_section = "pending"
            continue
        if line.startswith("• "):
            # Extract name before first occurrence of " - " or " ("
            name_part = line[2:]
            idx_dash = name_part.find(" - ")
            idx_paren = name_part.find(" (")
            candidates = [i for i in [idx_dash, idx_paren] if i != -1]
            if candidates:
                cut = min(candidates)
                name_part = name_part[:cut]
            name = name_part.strip()
            if current_section == "active":
                active.append(name)
            elif current_section == "pending":
                pending.append(name)
            else:
                other.append(name)

    # Deduplicate preserving order
    def dedupe(seq: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    active = dedupe(active)
    pending = dedupe(pending)
    other = dedupe(other)
    all_players = dedupe(active + pending + other)

    return {
        "active_players": active,
        "pending_players": pending,
        "other_players": other,
        "all_players": all_players,
    }


def extract_players_from_text(text: str) -> dict[str, list[str]]:
    if not isinstance(text, str) or not text.strip():
        return {
            "active_players": [],
            "pending_players": [],
            "other_players": [],
            "all_players": [],
        }
    return _parse_player_names_from_text(text)


def extract_structured_data_from_tool_outputs(tool_outputs: dict[str, Any]) -> dict[str, Any]:
    players_agg: dict[str, set[str]] = {
        "active_players": set(),
        "pending_players": set(),
        "other_players": set(),
        "all_players": set(),
    }

    tools_used: list[str] = list(tool_outputs.keys())

    for _, value in tool_outputs.items():
        if isinstance(value, str):
            parsed = extract_players_from_text(value)
            for k in players_agg:
                players_agg[k].update(parsed.get(k, []))

    players_dict = {k: sorted(v) for k, v in players_agg.items()}
    return {
        "player_count": len(players_dict["all_players"]),
        "tools_used": tools_used,
        "players": players_dict,
    }


def extract_structured_data_from_agent_result(agent_result: Any) -> dict[str, Any]:
    if not isinstance(agent_result, str) or not agent_result.strip():
        return {
            "player_count": 0,
            "mentions_players": False,
            "players": {"all_players": []},
        }
    parsed = extract_players_from_text(agent_result)
    mentions_players = "player" in agent_result.lower()
    return {
        "player_count": len(parsed["all_players"]),
        "mentions_players": mentions_players,
        "players": parsed,
    }


def compare_data_consistency(actual_data: dict[str, Any], agent_data: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    actual_players = set(actual_data.get("players", {}).get("all_players", []))
    agent_players = set(agent_data.get("players", {}).get("all_players", []))

    # Fabricated names
    fabricated = agent_players - actual_players
    if fabricated:
        issues.append(
            f"Agent mentioned players not in tool outputs: {', '.join(sorted(fabricated))}"
        )

    # Data inflation
    if len(agent_players) > len(actual_players) and actual_players:
        issues.append(
            f"Agent listed {len(agent_players)} players but tools returned {len(actual_players)}"
        )

    # Mentions without tools
    player_tools_used = any("player" in t for t in actual_data.get("tools_used", []))
    if agent_data.get("mentions_players") and not player_tools_used:
        issues.append("Agent mentioned players but no player-related tools were used")

    # Status distribution mismatch
    a_dist = actual_data.get("status_distribution") or {}
    g_dist = agent_data.get("status_distribution") or {}
    for key in set(a_dist.keys()).union(g_dist.keys()):
        if key in a_dist and key in g_dist and a_dist[key] != g_dist[key]:
            issues.append(
                f"Agent listed {g_dist[key]} {key} players but tools returned {a_dist[key]}"
            )

    return issues


def validate_tool_output_consistency(agent_result: Any, tool_outputs: dict[str, Any] | None) -> dict[str, Any]:
    if not tool_outputs:
        return {"consistent": True, "issues": [], "tool_outputs_used": []}

    structured = extract_structured_data_from_tool_outputs(tool_outputs)
    agent_structured = extract_structured_data_from_agent_result(agent_result)
    issues = compare_data_consistency(structured, agent_structured)

    response: dict[str, Any] = {
        "consistent": len(issues) == 0,
        "issues": issues,
        "tool_outputs_used": structured.get("tools_used", []),
    }

    if issues:
        response["recommendations"] = [
            "Use only data returned by tools",
        ]

    return response


