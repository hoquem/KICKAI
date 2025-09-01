from crewai.tools import tool

@tool("mock_list_team_members_and_players")
def mock_list_team_members_and_players(team_id: str) -> str:
    """
    A mock tool that returns a canned response for team members and players.
    """
    return """
    Team Overview for KTI

    Team Members:
    - Coach Wilson - Coach

    Players:
    - Jane Doe - Midfielder Active (ID: 01JD)
    - John Smith - Forward Active (ID: JS001)
    """
