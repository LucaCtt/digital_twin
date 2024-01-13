from datetime import datetime
import json
import os
import const
from models import Appliance, OperationMode, Routine, RoutineAction


def __read_appliance(filepath: str) -> Appliance:
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


def __read_appliances(dir_path: str) -> list[Appliance]:
    appliances = []

    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            appliance = __read_appliance(
                os.path.join(dir_path, filename))
            appliances.append(appliance)

    return appliances


def __read_routine(filepath: str, appliances: list[Appliance]) -> Routine:
    with open(filepath) as file:
        data = json.load(file)

        id = data["id"]
        name = data["name"]
        enabled = data["enabled"]
        when = data["when"][1]
        when = datetime.strptime(when, "%H:%M")
        when = when.hour * 60 + when.minute

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

        routine = Routine(id, name, when, enabled, actions)

        return routine


def __read_routines(dir_path: str, appliances: list[Appliance]) -> list[Routine]:
    routines = []

    for filename in os.listdir(dir_path):
        routine = __read_routine(os.path.join(dir_path, filename), appliances)
        routines.append(routine)

    return routines


def read_data() -> tuple[list[Appliance], list[Routine], list[Routine]]:
    appliances = __read_appliances(const.APPLIANCES_DIR)
    routines = __read_routines(const.ROUTINES_DIR, appliances)
    tests = __read_routines(const.TESTS_DIR, appliances)

    return appliances, routines, tests
