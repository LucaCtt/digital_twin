from abc import ABC, abstractmethod
from datetime import datetime
import json
import os

from .models import Appliance, OperationMode, Routine, RoutineAction


class DataRepository(ABC):
    """Abstract tepository for the data of the digital twin.
    Do not instantiantiate this class directly. Use a concrete implementation instead.
    Only `get` methods are defined because the app is not meant to create or modify data.
    """
    @abstractmethod
    def get_appliances() -> list[Appliance]:
        """Get the list of appliances.

        Returns:
            list[Appliance]: The list of appliances.
        """
        pass

    @abstractmethod
    def get_routines() -> list[Routine]:
        """Get the list of routines.

        Returns:
            list[Routine]: The list of routines.
        """
        pass

    @abstractmethod
    def get_test_routines() -> list[Routine]:
        """Get the list of test routines.

        Returns:
            list[Routine]: The list of test routines.
        """
        pass


class JSONRepository(DataRepository):
    """Repository for the data of the digital twin, stored in JSON files.
    """

    def __init__(self, appliances_dir: str, routines_dir: str, test_routines_dir: str):
        """Constructor.

        Args:
            appliances_dir (str): The path to the directory containing the appliances JSON files.
            routines_dir (str): The path to the directory containing the routines JSON files.
            test_routines_dir (str): The path to the directory containing the test routines JSON files.
        """
        self.appliances_dir = appliances_dir
        self.routines_dir = routines_dir
        self.test_routines_dir = test_routines_dir

    def get_appliances(self) -> list[Appliance]:
        """Get the list of appliances.

        Returns:
            list[Appliance]: The list of appliances.
        """
        return __read_appliances_json(self.appliances_dir)

    def get_routines(self) -> list[Routine]:
        """Get the list of routines.

        Returns:
            list[Routine]: The list of routines.
        """
        appliances = self.get_appliances()
        routines = __read_routines_json(self.routines_dir, appliances)
        return routines

    def get_test_routines(self) -> list[Routine]:
        """Get the list of test routines.

        Returns:
            list[Routine]: The list of test routines.
        """
        appliances = self.get_appliances()
        test_routines = __read_routines_json(
            self.test_routines_dir, appliances)
        return test_routines


def __read_appliance_json(filepath: str) -> Appliance:
    """Read an appliance from a JSON file.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        Appliance: The appliance.
    """
    with open(filepath) as file:
        data = json.load(file)

        id = data["id"]
        device = data["device"]
        modes = []

        for mode_data in data["modes"]:
            mode_id = mode_data["id"]
            mode_name = mode_data["name"]
            power_consumption = mode_data["power_consumption"]
            default_duration = mode_data["default_duration"] // 60 if "default_duration" in mode_data else None

            mode = OperationMode(
                mode_id, mode_name, power_consumption, default_duration)
            modes.append(mode)

        return Appliance(id, device, modes)


def __read_appliances_json(dir_path: str) -> list[Appliance]:
    """Read the appliances from a directory containing JSON files.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        list[Appliance]: The list of appliances.
    """
    appliances = []

    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            appliance = __read_appliance_json(
                os.path.join(dir_path, filename))
            appliances.append(appliance)

    return appliances


def __read_routine_json(filepath: str, appliances: list[Appliance]) -> Routine:
    """Read a routine from a JSON file.

    Args:
        filepath (str): The path to the JSON file.
        appliances (list[Appliance]): The list of appliances.

    Returns:
        Routine: The routine.
    """

    with open(filepath) as file:
        data = json.load(file)

        id = data["id"]
        name = data["name"]
        enabled = data["enabled"]
        when = data["when"][1]
        when = datetime.strptime(when, "%H:%M")

        actions = []

        for action_data in data["actions"]:
            action_id = action_data["id"]
            action_appliance_id = action_data["appliance_id"]
            action_mode_id = action_data["mode_id"]
            action_duration = action_data["duration"] // 60 if "duration" in action_data else None

            appliance = next(a for a in appliances if a.id ==
                             action_appliance_id)
            mode = next(m for m in appliance.modes if m.id == action_mode_id)
            duration = action_duration if action_duration else mode.default_duration

            action = RoutineAction(action_id, appliance, mode, duration)
            actions.append(action)

        routine = Routine(id, name, when, actions, enabled)

        return routine


def __read_routines_json(dir_path: str, appliances: list[Appliance]) -> list[Routine]:
    """Read the routines from a directory containing JSON files.

    Args:
        dir_path (str): The path to the directory.
        appliances (list[Appliance]): The list of appliances.

    Returns:
        list[Routine]: The list of routines.
    """

    routines = []

    for filename in os.listdir(dir_path):
        routine = __read_routine_json(
            os.path.join(dir_path, filename), appliances)
        routines.append(routine)

    return routines
