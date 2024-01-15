from datetime import datetime


class OperationMode:
    def __init__(self, id: int, name: str, power_consumption: float, default_duration: int | None = None):
        self.id = id
        self.name = name
        self.power_consumption = power_consumption
        self.default_duration = default_duration


class Appliance:
    def __init__(self, id: str, device: str, modes: list[OperationMode]):
        self.id = id
        self.device = device
        self.modes = modes


class RoutineAction:
    def __init__(self, id: int, appliance: Appliance, mode: OperationMode, duration: int | None = None):
        self.id = id
        self.appliance = appliance
        self.mode = mode
        self.duration = duration


class Routine:
    def __init__(self, id: int, name: str, when: datetime, actions: list[RoutineAction], enabled: bool = True):
        self.id = id
        self.name = name
        self.enabled = enabled
        self.when = when
        self.actions = actions
