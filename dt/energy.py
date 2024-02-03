from __future__ import annotations
from abc import ABC
from datetime import datetime
import numpy as np

from config import EnergyConfig
from data import Appliance, Routine, RoutineAction
from ortools.linear_solver import pywraplp
import const


class Recommendation(ABC):
    """A recommendation to solve a conflict or to improve the energy consumption.
    """

    def __init__(self, message: str) -> None:
        self.message = message


class DisableRoutineRecommendation(Recommendation):
    """A recommendation to disable a routine.
    """

    def __init__(self, routine: Routine) -> None:
        super().__init__(f"Disable routine {routine.name}.")
        self.routine = routine


class ConflictError(Exception):
    """Error raised when there is a conflict in the routines.
    """

    def __init__(self, message: str, recommendations: list[Recommendation] | None = None) -> None:
        super().__init__(message)
        self.recommendations = recommendations


class InconsistentRoutinesError(ConflictError):
    """Error raised when there are two routines with conflicting actions.
    """

    def __init__(self, first_routine: Routine, second_routine: Routine, first_action: RoutineAction, second_action: RoutineAction):
        recommendations: list[Recommendation] = [DisableRoutineRecommendation(
            first_routine), DisableRoutineRecommendation(second_routine)]

        super().__init__(
            f"Appliance {first_action.appliance.device} has conflicting modes.", recommendations)

        self.first_routine = first_routine
        self.second_routine = second_routine
        self.first_action = first_action
        self.second_action = second_action


class MaxPowerExceededError(ConflictError):
    """Error raised when the power consumption of the house is greater than the maximum power consumption.
    """

    def __init__(self, max_power: float, when: datetime, routines_to_disable: list[Routine]):
        recommendations: list[Recommendation] = [DisableRoutineRecommendation(
            r) for r in routines_to_disable]

        super().__init__(
            f"Power consumption of the house is greater than {max_power} at {when}.", recommendations)
        self.max_power = max_power
        self.when = when


class ConsumptionsMatrix():
    """A matrix that represents the power consumption of each appliance in each minute of the day.
    A row is created for each minute of the day, and a column for each appliance.
    So if there are 10 appliances, the matrix will have 1440 rows and 10 columns.
    Currently the matrix is implemented as a numpy array of integers.

    Methods are provided to calculate the total consumption of the house at a given time,
    the consumption of a specific appliance at a given time, and to simulate a new matrix
    with a new set of routines.
    """

    def __init__(self, appliances: list[Appliance], routines: list[Routine], config: EnergyConfig):
        """Constructor.

        Args:
            appliances (list[Appliance]): The list of appliances.
            routines (list[Routine]): The list of routines.
        """

        self.appliances = appliances
        self.routines = routines
        self.config = config
        self.matrix = np.zeros(
            (const.MINUTES_IN_DAY, len(appliances)), dtype=np.float16)

        for routine in routines:
            for other_routine in routines:
                if routine == other_routine:
                    continue

                conflicting_actions = routine.actions_conflict_with(
                    other_routine)
                if conflicting_actions is None:
                    continue

                raise InconsistentRoutinesError(
                    routine, other_routine, conflicting_actions[0], conflicting_actions[1])

        for routine in routines:
            if not routine.enabled:
                continue

            for action in routine.actions:
                # Convert start and end time to minutes of the day
                start = routine.when.hour * 60 + routine.when.minute
                end = min(action.duration + start,
                          const.MINUTES_IN_DAY) if action.duration else const.MINUTES_IN_DAY - start

                for minute in range(start, end+1):
                    self.matrix[minute-1][action.appliance.id] = action.mode.id

        # Check that the power consumption of each appliance is not greater than the maximum power consumption of the house
        for minute_of_day in range(const.MINUTES_IN_DAY):
            if float(np.sum(self.matrix[minute_of_day, :])) > config.max_power:
                time = datetime.today().replace(hour=minute_of_day//60, minute=minute_of_day % 60)
                most_consuming = sorted(
                    routines, key=lambda r: r.power_consumption_at(time), reverse=True)

                # Convert minute of day to datetime
                raise MaxPowerExceededError(
                    config.max_power, time, most_consuming[:2])

    def add_routine(self, routine: Routine) -> ConsumptionsMatrix:
        """Creates a new matrix with a new routine added.

        Args:
            routine (Routine): The routine to add.

        Returns:
            ConsumptionsMatrix: The new matrix with the new routine added.
        """
        return ConsumptionsMatrix(self.appliances, self.routines + [routine], self.config)

    def total_consumption(self, when: datetime) -> float:
        """Calculate the total consumption of the house at a given time.

        Args:
            when (datetime): The time to calculate the total consumption.

        Returns:
            float: The total consumption of the house at the given time.
        """
        minute_of_day = when.hour * 60 + when.minute
        row_now = self.matrix[minute_of_day]

        total_consumption = 0

        for i, mode_id in enumerate(row_now):
            if mode_id == 0:
                continue
            else:
                appliance = next(a for a in self.appliances if a.id == i)
                mode = next(m for m in appliance.modes if m.id == mode_id)
                total_consumption += mode.power_consumption

        return total_consumption

    def consumption(self, appliance: Appliance, when: datetime) -> float:
        """Calculate the consumption of a specific appliance at a given time.

        Args:
            appliance (Appliance): The appliance to calculate the consumption.
            when (datetime): The time to calculate the consumption.

        Returns:
            float: The consumption of the appliance at the given time.
        """

        minute_of_day = when.hour * 60 + when.minute
        mode_id = self.matrix[minute_of_day][appliance.id]
        return appliance.modes[mode_id].power_consumption

    def raw_matrix(self) -> np.ndarray:
        """Return the raw matrix.

        Returns:
            np.ndarray: The raw matrix.
        """
        return self.matrix


class CostsMatrix:
    """A matrix that represents the cost of the house at each time of the week.

    The consumption at each time depends on the number of energy rates,
    according to the italian energy market:
    https://www.arera.it/bolletta/glossario-dei-termini/dettaglio/fasce-orarie
    """

    def __init__(self, config: EnergyConfig) -> None:
        self.config = config
        self.matrix = np.zeros(
            (const.DAYS_IN_WEEK, const.MINUTES_IN_DAY), dtype=np.int8)

        for day_of_week in list(range(const.DAYS_IN_WEEK)):
            if config.energy_rates_number == 1:
                # Set everything to F1
                self.matrix[day_of_week, :] = config.energy_rates_prices[0]
            elif config.energy_rates_number == 2:
                # Set everything to F23
                self.matrix[day_of_week, :] = config.energy_rates_prices[1]

                # Set monday to friday from 8:00 to 18:00 to F1
                if day_of_week >= 0 and day_of_week <= 4:
                    self.matrix[day_of_week, 8*60:18 *
                                60] = config.energy_rates_prices[0]
            elif config.energy_rates_number == 3:
                # Set everything to F3
                self.matrix[day_of_week, :] = config.energy_rates_prices[2]

                if day_of_week >= 0 and day_of_week <= 5:
                    if day_of_week >= 0 and day_of_week <= 4:
                        # Set monday to saturday from 7:00 to 22:00 to F2
                        self.matrix[day_of_week, 8*60:18 *
                                    60] = config.energy_rates_prices[0]
                    else:
                        # Set monday to friday from 8:00 to 18:00 to F1
                        self.matrix[day_of_week, 7*60:22 *
                                    60] = config.energy_rates_prices[1]

    def get_cost(self, when: datetime) -> float:
        """Calculate the eletrcity cost at a given time.

        Args:
            when (datetime): The time to calculate the cost.

        Returns:
            float: The cost of the house at the given time.
        """
        minute_of_day = when.hour * 60 + when.minute
        day_of_week = when.weekday()

        return self.matrix[day_of_week, minute_of_day]


class RoutineSimulator:
    def __init__(self, consumptions_matrix: ConsumptionsMatrix, costs_matrix: CostsMatrix, max_power: float) -> None:
        self.consumptions_matrix = consumptions_matrix
        self.costs_matrix = costs_matrix
        self.max_power = max_power

    def simulate(self, routine: Routine) -> list[Recommendation]:
        self.simulated_consumption_matrix = self.consumptions_matrix.add_routine(routine)
        return []
    

    """
    def find_best_start_time(self, routine: Routine) -> datetime:
        existing_matrix = self.consumptions_matrix.raw_matrix()
        simulated_matrix = ConsumptionsMatrix(self.consumptions_matrix.appliances, [
                                              routine], self.consumptions_matrix.config).raw_matrix()

        e = np.zeros(existing_matrix.shape, dtype=np.int8)

        for minute in range(const.MINUTES_IN_DAY):
            for appliance in self.consumptions_matrix.appliances:
                e[minute, appliance.id] = self.solver.NumVar(
                    0, self.max_power, f"e_{minute}_{appliance.id}")

                appliance = next(
                    a for a in self.consumptions_matrix.appliances if a.id == appliance.id)
                mode = next(m for m in appliance.modes if m.id ==
                            existing_matrix[minute, appliance.id])
                self.solver.Add(e[minute, appliance.id]
                                == mode.power_consumption)

        x = np.zeros((const.MINUTES_IN_DAY, len(
            routine.actions)), dtype=np.int8)
        y = np.zeros((const.MINUTES_IN_DAY, len(
            routine.actions)), dtype=np.int8)

        for minute in range(const.MINUTES_IN_DAY):
            for action in routine.actions:
                x[minute, action.id] = self.solver.IntVar(
                    0, 1, f"x_{minute}_{action.id}")
                y[minute, action.id] = self.solver.IntVar(
                    0, 1, f"x_{minute}_{action.id}")

                start = routine.when.hour * 60 + routine.when.minute
                duration = action.duration if action.duration else const.MINUTES_IN_DAY - start
                self.solver.Add([y[i, action.id] == 1 for i in range(
                    minute + duration) if x[minute, action.id] == 1])
                self.solver.Add(sum(x[:, action.id]) == 1)
                self.solver.Add(sum(y[:, action.id]) == minute + duration)

        return 0
    """
