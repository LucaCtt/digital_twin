from .appliance import Appliance
from .operation_mode import OperationMode

class RoutineAction:
    def __init__(self, id: int, appliance: Appliance, mode: OperationMode, duration: int | None):
        self.id = id
        self.appliance = appliance
        self.mode = mode
        self.duration = duration