
from enum import Enum, auto

class RegistrationState(Enum):
    START = auto()
    AWAITING_CONFIRMATION = auto()
    REGISTERED = auto()

class RegistrationStateMachine:
    def __init__(self):
        self.state = RegistrationState.START

    def transition(self, new_state: RegistrationState):
        self.state = new_state
