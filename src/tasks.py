from crewai import Task
from src.tools.supabase_tools import PlayerTools, FixtureTools, AvailabilityTools

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
            tools=agent.tools
        )

    def list_players_task(self, agent):
        """
        Defines the task for retrieving a list of all players.
        """
        return Task(
            description="Retrieve and list all players currently in the team's database, including their status (active/inactive).",
            expected_output="A formatted string containing the ID, name, phone number, and status of every player.",
            agent=agent,
            tools=agent.tools
        )

    def get_player_task(self, agent):
        """
        Defines the task for retrieving a specific player's information.
        """
        return Task(
            description="Retrieve information for a specific player. Use either player_id '{player_id}' or phone_number '{phone_number}' to find the player.",
            expected_output="Detailed information about the player including their ID, name, phone number, and active status.",
            agent=agent,
            tools=agent.tools
        )

    def update_player_task(self, agent):
        """
        Defines the task for updating a player's information.
        """
        return Task(
            description="Update a player's information. Player ID is '{player_id}'. Update fields: {update_fields}.",
            expected_output="A confirmation message indicating that the player was successfully updated.",
            agent=agent,
            tools=agent.tools
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
            tools=agent.tools
        )

    def list_fixtures_task(self, agent):
        """
        Defines the task for retrieving a list of all fixtures.
        """
        return Task(
            description="Retrieve and list all fixtures. Show upcoming fixtures only: {upcoming_only}.",
            expected_output="A formatted string containing all fixtures with their opponent, date, location, and home/away status.",
            agent=agent,
            tools=agent.tools
        )

    def get_fixture_task(self, agent):
        """
        Defines the task for retrieving a specific fixture's information.
        """
        return Task(
            description="Retrieve detailed information for fixture ID '{fixture_id}'.",
            expected_output="Detailed information about the fixture including opponent, date, location, and any recorded result.",
            agent=agent,
            tools=agent.tools
        )

    def update_fixture_task(self, agent):
        """
        Defines the task for updating a fixture's information.
        """
        return Task(
            description="Update fixture information. Fixture ID is '{fixture_id}'. Update fields: {update_fields}.",
            expected_output="A confirmation message indicating that the fixture was successfully updated.",
            agent=agent,
            tools=agent.tools
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
            tools=agent.tools
        )

    def get_availability_task(self, agent):
        """
        Defines the task for retrieving availability for a fixture.
        """
        return Task(
            description="Retrieve availability information for fixture ID '{fixture_id}'.",
            expected_output="A formatted string showing all players' availability, squad status, and payment status for the fixture.",
            agent=agent,
            tools=agent.tools
        )

    def get_squad_task(self, agent):
        """
        Defines the task for retrieving the squad for a fixture.
        """
        return Task(
            description="Retrieve the squad selection for fixture ID '{fixture_id}'.",
            expected_output="A formatted string showing the starting XI and substitutes for the fixture.",
            agent=agent,
            tools=agent.tools
        )

    def set_squad_status_task(self, agent):
        """
        Defines the task for setting a player's squad status.
        """
        return Task(
            description="Set a player's squad status for a fixture. Player ID: '{player_id}', Fixture ID: '{fixture_id}', Squad Status: '{squad_status}' (Starter/Substitute/Not Selected).",
            expected_output="A confirmation message indicating that the squad status was successfully set.",
            agent=agent,
            tools=agent.tools
        )

    def mark_payment_task(self, agent):
        """
        Defines the task for marking a player's payment status.
        """
        return Task(
            description="Mark a player's payment status for a fixture. Player ID: '{player_id}', Fixture ID: '{fixture_id}', Has Paid: {has_paid}.",
            expected_output="A confirmation message indicating that the payment status was successfully updated.",
            agent=agent,
            tools=agent.tools
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
            tools=agent.tools
        )

    def squad_selection_task(self, agent):
        """
        Defines the task for selecting the squad for a fixture.
        """
        return Task(
            description="Select the squad for fixture ID '{fixture_id}'. Choose 11 starters and 3 substitutes from available players. Consider player positions and form.",
            expected_output="A detailed squad selection with 11 starters and 3 substitutes, including reasoning for each selection.",
            agent=agent,
            tools=agent.tools
        )

    def payment_report_task(self, agent):
        """
        Defines the task for generating a payment report for a fixture.
        """
        return Task(
            description="Generate a payment report for fixture ID '{fixture_id}'. Show who has paid and who still owes money.",
            expected_output="A detailed payment report showing paid and unpaid players with amounts owed.",
            agent=agent,
            tools=agent.tools
        )

    def team_status_report_task(self, agent):
        """
        Defines the task for generating a comprehensive team status report.
        """
        return Task(
            description="Generate a comprehensive team status report including player counts, upcoming fixtures, and any issues that need attention.",
            expected_output="A detailed team status report covering all aspects of team management.",
            agent=agent,
            tools=agent.tools
        )

# --- Communication Tasks ---

class CommunicationTasks:
    """
    A class to encapsulate all tasks related to team communication.
    """
    
    def availability_request_task(self, agent):
        """
        Defines the task for requesting player availability for an upcoming fixture.
        """
        return Task(
            description="Request availability from all players for fixture ID '{fixture_id}'. Send a clear message asking players to confirm their availability.",
            expected_output="A confirmation that the availability request was sent to all players.",
            agent=agent,
            tools=agent.tools
        )

    def squad_announcement_task(self, agent):
        """
        Defines the task for announcing the selected squad for a fixture.
        """
        return Task(
            description="Announce the selected squad for fixture ID '{fixture_id}'. Include starters and substitutes with clear instructions.",
            expected_output="A confirmation that the squad announcement was sent to all players.",
            agent=agent,
            tools=agent.tools
        )

    def fixture_reminder_task(self, agent):
        """
        Defines the task for sending fixture reminders to players.
        """
        return Task(
            description="Send a reminder about fixture ID '{fixture_id}' to all players. Include match details and important information.",
            expected_output="A confirmation that the fixture reminder was sent to all players.",
            agent=agent,
            tools=agent.tools
        )

    def payment_reminder_task(self, agent):
        """
        Defines the task for sending payment reminders to players.
        """
        return Task(
            description="Send payment reminders to players who haven't paid for fixture ID '{fixture_id}'. Include amount owed and payment instructions.",
            expected_output="A confirmation that payment reminders were sent to unpaid players.",
            agent=agent,
            tools=agent.tools
        )

def create_tasks(agents):
    """
    Create a list of tasks for the agents to work on.
    This function creates tasks that the agents can execute to manage the team.
    """
    team_manager, player_coordinator, match_analyst, communication_specialist = agents
    
    # Create task instances
    player_tasks = PlayerTasks()
    fixture_tasks = FixtureTasks()
    availability_tasks = AvailabilityTasks()
    team_management_tasks = TeamManagementTasks()
    communication_tasks = CommunicationTasks()
    
    # Define the tasks
    tasks = [
        # Team Manager tasks
        team_management_tasks.team_status_report_task(team_manager),
        
        # Player Coordinator tasks
        player_tasks.list_players_task(player_coordinator),
        
        # Match Analyst tasks
        fixture_tasks.list_fixtures_task(match_analyst),
        
        # Communication Specialist tasks
        communication_tasks.fixture_reminder_task(communication_specialist)
    ]
    
    return tasks
