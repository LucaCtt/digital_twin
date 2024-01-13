from .operation_mode import OperationMode

class Appliance:
    def __init__(self, id: str, device: str, modes: list[OperationMode]):
        self.id = id
        self.device = device
        self.modes = modes