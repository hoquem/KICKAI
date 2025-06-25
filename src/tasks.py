from crewai import Task
from src.tools.supabase_tools import PlayerTools

# Instantiate the tools your tasks will use
player_tool = PlayerTools()

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
            description="Retrieve and list all active players currently in the team's database.",
            expected_output="A formatted string containing the ID, name, and phone number of every active player.",
            agent=agent,
            tools=[player_tool]
        )

# Note: We are defining the tasks within a class. This is a good practice for organization,
# allowing us to group related tasks. For example, we could later add a `FixtureTasks` class.
