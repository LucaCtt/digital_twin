class OperationMode:
    def __init__(self, id: int, name: str, power_consumption: float, default_duration: int | None):
        self.id = id
        self.name = name
        self.power_consumption = power_consumption
        self.default_duration = default_duration

