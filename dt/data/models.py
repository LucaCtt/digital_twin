"""Models for the data layer of the digital twin.

This module contains the models for the data layer of the digital twin.
They are meant to be independent from the data layer implementation, e.g. JSON files or a database.

All IDs are integers, and they should be unique for each entity type (appliance, operation mode, routine, etc.).
Integers were chosen as they are more efficient in memory, easy to assign as they can be incremented,
easy to compare, and they allow more than enough IDs for the scope of this project.
"""

from __future__ import annotations
from datetime import datetime, timedelta


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
        manufacturer (str): The manufacturer of the appliance.
        model (str): The model of the appliance.
        location (str): The location of the appliance (e.g. kitchen, bedroom, etc.)
        modes (list[OperationMode]): The operation modes of the appliance.
        An "off" mode is required, and it's a good practice to have it as the first one in the list.
    """

    def __init__(self, id: int, device: str, manufacturer: str, model: str, location: str, modes: list[OperationMode]):
        self.id = id
        self.device = device
        self.manufacturer = manufacturer
        self.model = model
        self.location = location
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

    def conflicts_with(self, other: RoutineAction):
        """Check if the action conflicts with another action.

        Args:
            other (RoutineAction): The other action to check.

        Returns:
            bool: True if the actions conflict, False otherwise.
        """
        return self.appliance == other.appliance and self.mode != other.mode


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

    def conflicting_actions(self, other: Routine) -> tuple[RoutineAction, RoutineAction] | None:
        """Check if any action in the routine conflicts with any action in another routine.

        Args:
            other (Routine): The other routine to check.

        Returns:
            bool: True if the routines conflict, False otherwise.
        """

        if not self.enabled or not other.enabled:
            return None

        def actions_overlap(self_action: RoutineAction, other_action: RoutineAction) -> bool:
            if self_action.appliance.id != other_action.appliance.id:
                return False

            if self_action.mode.id == other_action.mode.id:
                return False

            if self_action.duration is None and other_action.duration is None:
                return True

            if self_action.duration is None and other_action.duration is not None and other.when + timedelta(minutes=other_action.duration) > self.when:
                return True

            if self_action.duration is not None and other_action.duration is None and self.when + timedelta(minutes=self_action.duration) > other.when:
                return True

            assert self_action.duration is not None and other_action.duration is not None
            return self.when < other.when + timedelta(minutes=other_action.duration) and other.when < self.when + timedelta(minutes=self_action.duration)

        for action in self.actions:
            for other_action in other.actions:
                if actions_overlap(action, other_action):
                    return action, other_action

        return None

    def power_consumption_at(self, when: datetime) -> float:
        """Calculate the power consumption of the routine at a given time.

        Args:
            when (datetime): The time to calculate the power consumption.

        Returns:
            float: The power consumption of the routine at the given time.
        """
        return sum(action.mode.power_consumption for action in self.actions
                   if (not action.duration and self.when <= when) or
                   (action.duration and self.when <= when <= self.when + timedelta(minutes=action.duration)))
