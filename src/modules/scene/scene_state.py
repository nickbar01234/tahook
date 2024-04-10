from enum import Enum, auto


class SceneState(Enum):
    ENTRY = auto()  # Setup server IP address

    ROLE_SELECTION = auto()

    PLAYER_WAIT = auto()  # Player's waiting room
    PLAYER_NAME = auto()  # Player's entering name
    PLAYER_QUESTION = auto()  # Quiz in progress
    PLAYER_END = auto()  # Final result

    REFEREE_ADD_QUESTION = auto()  # Referee adds questions to question bank
    REFEREE_MONITOR = auto()  # Referee's view

    QUIT = auto()
