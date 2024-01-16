"""Models for the data layer of the digital twin.

This module contains the models for the data layer of the digital twin.
They are meant to be independent from the data layer implementation, e.g. JSON files or a database.

All IDs are integers, and they should be unique for each entity type (appliance, operation mode, routine, etc.).
Integers were chosen as they are more efficient in memory, easy to assign as they can be incremented,
easy to compare, and they allow more than enough IDs for the scope of this project.
"""

from datetime import datetime


class OperationMode:
    """An operation mode of an appliance.

    Attributes:
        id (int): The id of the operation mode.
        name (str): The name of the operation mode.
        power_consumption (float): The power consumption of the operation mode, in watts.
        default_duration (int | None): The default duration of the operation mode, in minutes.
        If None, the duration is unlimited by default.
    """

    def __init__(self, id: int, name: str, power_consumption: float, default_duration: int | None = None):
        self.id = id
        self.name = name
        self.power_consumption = power_consumption
        self.default_duration = default_duration


class Appliance:
    """An appliance.

    Attributes:
        id (int): The id of the appliance.
        device (str): The type of device of the appliance (e.g. fridge, microwave, etc.)
        modes (list[OperationMode]): The operation modes of the appliance.
        An "off" mode is required, and it's a good practice to have it as the first one in the list.
    """

    def __init__(self, id: int, device: str, modes: list[OperationMode]):
        self.id = id
        self.device = device
        self.modes = modes

    def get_mode(self, mode_id: int) -> OperationMode | None:
        """Get an operation mode of the appliance by ID.

        Args:
            mode_id (int): The ID of the operation mode.

        Returns:
            OperationMode | None: The operation mode if found, None otherwise.
        """
        return next((mode for mode in self.modes if mode.id == mode_id), None)


class RoutineAction:
    """An action of a routine.

    Attributes:
        id (int): The id of the action.
        appliance (Appliance): The appliance affected by the action.
        mode (OperationMode): The operation mode to assign to the appliance.
        duration (int | None): The duration of the operation mode, in minutes.
        If None, the duration of the operation mode is used instead.
        If that is None as well, the duration is unlimited,
        and an explicit action to change the mode of the appliance is required.
    """

    def __init__(self, id: int, appliance: Appliance, mode: OperationMode, duration: int | None = None):
        self.id = id
        self.appliance = appliance
        self.mode = mode
        self.duration = duration


class Routine:
    """A routine.

    Attributes:
        id (int): The id of the routine.
        name (str): The name of the routine.
        when (datetime): The date and time when the routine should be executed.
        actions (list[RoutineAction]): The actions of the routine.
        enabled (bool): Whether the routine is enabled. If False, the routine is not executed.
    """

    def __init__(self, id: int, name: str, when: datetime, actions: list[RoutineAction], enabled: bool = True):
        self.id = id
        self.name = name
        self.enabled = enabled
        self.when = when
        self.actions = actions
