from crewai import Task
from src.tools.supabase_tools import PlayerTools, FixtureTools, AvailabilityTools

# Instantiate the tools your tasks will use
player_tool = PlayerTools()
fixture_tool = FixtureTools()
availability_tool = AvailabilityTools()

# --- Player Management Tasks ---

class PlayerTasks:
    """
    A class to encapsulate all tasks related to player management.
    """
    
    def add_player_task(self, agent):
        """
        Defines the task for adding a new player.
        The description uses placeholders like {name} and {phone_number}
        which will be filled in when the task is executed.
        """
        return Task(
            description="Add a new player to the team's database. The player's name is '{name}' and their phone number is '{phone_number}'.",
            expected_output="A confirmation message indicating that the player '{name}' was successfully added to the database.",
            agent=agent,
            tools=[player_tool]
        )

    def list_players_task(self, agent):
        """
        Defines the task for retrieving a list of all players.
        """
        return Task(
            description="Retrieve and list all players currently in the team's database, including their status (active/inactive).",
            expected_output="A formatted string containing the ID, name, phone number, and status of every player.",
            agent=agent,
            tools=[player_tool]
        )

    def get_player_task(self, agent):
        """
        Defines the task for retrieving a specific player's information.
        """
        return Task(
            description="Retrieve information for a specific player. Use either player_id '{player_id}' or phone_number '{phone_number}' to find the player.",
            expected_output="Detailed information about the player including their ID, name, phone number, and active status.",
            agent=agent,
            tools=[player_tool]
        )

    def update_player_task(self, agent):
        """
        Defines the task for updating a player's information.
        """
        return Task(
            description="Update a player's information. Player ID is '{player_id}'. Update fields: {update_fields}.",
            expected_output="A confirmation message indicating that the player was successfully updated.",
            agent=agent,
            tools=[player_tool]
        )

# --- Fixture Management Tasks ---

class FixtureTasks:
    """
    A class to encapsulate all tasks related to fixture management.
    """
    
    def add_fixture_task(self, agent):
        """
        Defines the task for adding a new fixture.
        """
        return Task(
            description="Add a new fixture to the team's schedule. Opponent: '{opponent}', Date: '{match_date}', Location: '{location}', Home Game: {is_home_game}.",
            expected_output="A confirmation message indicating that the fixture was successfully added to the database.",
            agent=agent,
            tools=[fixture_tool]
        )

    def list_fixtures_task(self, agent):
        """
        Defines the task for retrieving a list of all fixtures.
        """
        return Task(
            description="Retrieve and list all fixtures. Show upcoming fixtures only: {upcoming_only}.",
            expected_output="A formatted string containing all fixtures with their opponent, date, location, and home/away status.",
            agent=agent,
            tools=[fixture_tool]
        )

    def get_fixture_task(self, agent):
        """
        Defines the task for retrieving a specific fixture's information.
        """
        return Task(
            description="Retrieve detailed information for fixture ID '{fixture_id}'.",
            expected_output="Detailed information about the fixture including opponent, date, location, and any recorded result.",
            agent=agent,
            tools=[fixture_tool]
        )

    def update_fixture_task(self, agent):
        """
        Defines the task for updating a fixture's information.
        """
        return Task(
            description="Update fixture information. Fixture ID is '{fixture_id}'. Update fields: {update_fields}.",
            expected_output="A confirmation message indicating that the fixture was successfully updated.",
            agent=agent,
            tools=[fixture_tool]
        )

# --- Availability Management Tasks ---

class AvailabilityTasks:
    """
    A class to encapsulate all tasks related to availability management.
    """
    
    def set_availability_task(self, agent):
        """
        Defines the task for setting a player's availability for a fixture.
        """
        return Task(
            description="Set a player's availability for a fixture. Player ID: '{player_id}', Fixture ID: '{fixture_id}', Status: '{status}' (Available/Unavailable/Maybe).",
            expected_output="A confirmation message indicating that the availability was successfully set.",
            agent=agent,
            tools=[availability_tool]
        )

    def get_availability_task(self, agent):
        """
        Defines the task for retrieving availability for a fixture.
        """
        return Task(
            description="Retrieve availability information for fixture ID '{fixture_id}'.",
            expected_output="A formatted string showing all players' availability, squad status, and payment status for the fixture.",
            agent=agent,
            tools=[availability_tool]
        )

    def get_squad_task(self, agent):
        """
        Defines the task for retrieving the squad for a fixture.
        """
        return Task(
            description="Retrieve the squad selection for fixture ID '{fixture_id}'.",
            expected_output="A formatted string showing the starting XI and substitutes for the fixture.",
            agent=agent,
            tools=[availability_tool]
        )

    def set_squad_status_task(self, agent):
        """
        Defines the task for setting a player's squad status.
        """
        return Task(
            description="Set a player's squad status for a fixture. Player ID: '{player_id}', Fixture ID: '{fixture_id}', Squad Status: '{squad_status}' (Starter/Substitute/Not Selected).",
            expected_output="A confirmation message indicating that the squad status was successfully set.",
            agent=agent,
            tools=[availability_tool]
        )

    def mark_payment_task(self, agent):
        """
        Defines the task for marking a player's payment status.
        """
        return Task(
            description="Mark a player's payment status for a fixture. Player ID: '{player_id}', Fixture ID: '{fixture_id}', Has Paid: {has_paid}.",
            expected_output="A confirmation message indicating that the payment status was successfully updated.",
            agent=agent,
            tools=[availability_tool]
        )

# --- Team Management Tasks ---

class TeamManagementTasks:
    """
    A class to encapsulate high-level team management tasks.
    """
    
    def analyze_availability_task(self, agent):
        """
        Defines the task for analyzing player availability for a fixture.
        """
        return Task(
            description="Analyze player availability for fixture ID '{fixture_id}'. Provide insights on available players, potential squad selection, and any concerns.",
            expected_output="A comprehensive analysis of player availability including recommendations for squad selection and any issues to address.",
            agent=agent,
            tools=[availability_tool, player_tool, fixture_tool]
        )

    def squad_selection_task(self, agent):
        """
        Defines the task for selecting the squad for a fixture.
        """
        return Task(
            description="Select the squad for fixture ID '{fixture_id}'. Choose 11 starters and 3 substitutes from available players. Consider player positions and form.",
            expected_output="A detailed squad selection with 11 starters and 3 substitutes, including reasoning for each selection.",
            agent=agent,
            tools=[availability_tool, player_tool, fixture_tool]
        )

    def payment_report_task(self, agent):
        """
        Defines the task for generating a payment report for a fixture.
        """
        return Task(
            description="Generate a payment report for fixture ID '{fixture_id}'. Show which players have paid and which haven't.",
            expected_output="A detailed payment report showing payment status for all players in the fixture.",
            agent=agent,
            tools=[availability_tool, player_tool, fixture_tool]
        )

    def team_status_report_task(self, agent):
        """
        Defines the task for generating a comprehensive team status report.
        """
        return Task(
            description="Generate a comprehensive team status report. Include player count, upcoming fixtures, recent results, and overall team health.",
            expected_output="A comprehensive team status report covering all aspects of team management.",
            agent=agent,
            tools=[player_tool, fixture_tool, availability_tool]
        )

# --- Communication Tasks ---

class CommunicationTasks:
    """
    A class to encapsulate all communication-related tasks.
    """
    
    def availability_request_task(self, agent):
        """
        Defines the task for creating an availability request message.
        """
        return Task(
            description="Create an availability request message for fixture ID '{fixture_id}'. The message should be clear, friendly, and encourage responses.",
            expected_output="A well-crafted availability request message ready to be sent to the team.",
            agent=agent,
            tools=[fixture_tool, player_tool]
        )

    def squad_announcement_task(self, agent):
        """
        Defines the task for creating a squad announcement message.
        """
        return Task(
            description="Create a squad announcement message for fixture ID '{fixture_id}'. Include starters, substitutes, and match details.",
            expected_output="A professional squad announcement message ready to be sent to the team.",
            agent=agent,
            tools=[fixture_tool, availability_tool]
        )

    def fixture_reminder_task(self, agent):
        """
        Defines the task for creating a fixture reminder message.
        """
        return Task(
            description="Create a fixture reminder message for fixture ID '{fixture_id}'. Include match details, location, and any important information.",
            expected_output="A clear and informative fixture reminder message.",
            agent=agent,
            tools=[fixture_tool]
        )

    def payment_reminder_task(self, agent):
        """
        Defines the task for creating a payment reminder message.
        """
        return Task(
            description="Create a payment reminder message for fixture ID '{fixture_id}'. List players who haven't paid and include payment instructions.",
            expected_output="A polite but firm payment reminder message.",
            agent=agent,
            tools=[availability_tool, fixture_tool]
        )


def create_tasks(agents):
    """Create tasks for the new agent structure."""
    team_manager, player_coordinator, match_analyst, communication_specialist = agents
    
    # Create a simple task to test the system
    test_task = Task(
        description="Provide a brief overview of the KICKAI football team management system and its capabilities.",
        expected_output="A comprehensive overview of the KICKAI system including its main features and benefits.",
        agent=team_manager
    )
    
    return [test_task]
