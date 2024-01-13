from .routine_action import RoutineAction

class Routine:
    def __init__(self, id: int, name: str, when: int, enabled: bool, actions: list[RoutineAction]):
        self.id = id
        self.name = name
        self.enabled = enabled
        self.when = when
        self.actions = actions