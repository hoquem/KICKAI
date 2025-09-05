# Data Authority Pattern for CrewAI Agents

## Problem Statement
Agents were hallucinating and adding fabricated data instead of relying solely on tool outputs.

## Solution: Strict Data Authority Protocol

### Core Pattern (Applied to All Agents)

```yaml
🚨 DATA AUTHORITY PROTOCOL (ABSOLUTE - ZERO TOLERANCE):
1) TOOLS ARE YOUR ONLY SOURCE OF TRUTH - Never create data not explicitly returned by tools
2) IF A TOOL RETURNS EMPTY/ERROR → State "No data found" or the exact error
3) IF NO TOOL EXISTS FOR DATA → State "I cannot access that information"
4) NEVER ASSUME, INFER, OR FABRICATE ANY DATA POINT

✅ WHAT YOU CAN DO:
- Call tools and relay their EXACT output
- Format tool responses for clarity (but preserve ALL data)
- Provide usage instructions and guidance
- Explain what tools are available
- Suggest appropriate commands or actions

❌ WHAT YOU MUST NEVER DO:
- Add players, matches, or teams not in tool output
- "Fill in" missing data with assumptions
- Create example data or placeholders
- Extend partial data with fabricated details
- Make up statistics, dates, or any information

RESPONSE PATTERN:
1) Call the appropriate tool(s)
2) Present ONLY the data returned by tools
3) If helpful, add usage guidance (clearly separated from data)
4) If data is incomplete, state exactly what's missing
```

## Implementation Details

### 1. Shared Template Update
Located in `kickai/config/agents.yaml` under `shared_templates.shared_backstory`
- Applies baseline data authority rules to all agents
- Ensures consistent behavior across the system

### 2. Agent-Specific Reinforcement
Each agent's backstory includes a condensed DATA AUTHORITY section:
- **MESSAGE_PROCESSOR**: Tools return data → Present EXACTLY what they return
- **HELP_ASSISTANT**: Your tools provide help text → Present it exactly
- **PLAYER_COORDINATOR**: Tools are your ONLY data source. Present their output exactly
- **TEAM_ADMINISTRATOR**: Tools are your ONLY data source. Present their output exactly  
- **SQUAD_SELECTOR**: If a tool returns 3 matches, show exactly 3. Never fabricate additional data

### 3. Task Routing Update
In `kickai/agents/crew_agents.py`, the manager LLM routing includes:
- DATA AUTHORITY reminder in routing guidelines
- Emphasizes that agents ONLY report what tools return
- Clarifies behavior for empty results ("No data found")

## Key Principles

### 1. Tools as Single Source of Truth
- Tools are the ONLY authoritative data source
- No data exists outside of what tools return
- Empty results are valid and should be reported as such

### 2. Clear Boundary Between Data and Guidance
- Data: What tools return (exact, unmodified)
- Guidance: How to use the system (helpful, but separate)
- Never mix or confuse the two

### 3. Transparent Communication
- If data doesn't exist, say so clearly
- If a tool isn't available, explain the limitation
- Never hide missing data with fabricated content

## Testing the Pattern

To verify agents follow data authority:
1. Request data that doesn't exist
2. Check agent responds with "No data found" not fabricated data
3. Request information without appropriate tools
4. Verify agent states "Cannot access that information"

## Benefits

1. **Reliability**: Users can trust all data is real
2. **Consistency**: Predictable behavior across all agents
3. **Debugging**: Clear distinction between tool issues and agent behavior
4. **Transparency**: Users know when data is unavailable

## Example Correct Behaviors

### When Tool Returns Data
```
User: "Show me active players"
Agent: [Calls list_players_active tool]
Tool returns: ["Player A", "Player B"]  
Agent: "Here are the active players: Player A, Player B"
```

### When Tool Returns Empty
```
User: "Show me matches next month"
Agent: [Calls list_matches_upcoming tool]
Tool returns: []
Agent: "No matches found for the requested period"
```

### When No Tool Exists
```
User: "Show me the weather forecast"
Agent: "I cannot access weather information. I can only help with team management tasks."
```

## Maintenance Notes

- This pattern must be maintained in any agent updates
- New agents must include DATA AUTHORITY sections
- Tool descriptions should be clear about what data they provide
- Regular testing should verify no hallucination occurs