from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any
import numpy as np

from dt.config import HomeConfig
from dt.data import Appliance, Routine, RoutineAction
from dt import const


class ConflictError(Exception):
    """Error raised when there is a conflict in the routines.
    """

    def __init__(self, message: str, context: dict[str, Any]) -> None:
        super().__init__(message)
        self.context = context


class InconsistentRoutinesError(ConflictError):
    """Error raised when there are two routines with conflicting actions.
    """

    def __init__(self, routines: list[Routine], appliance: Appliance):
        super().__init__(
            f"\"{appliance.device}\" is set to conflicting modes.",
            {"routines": routines, "appliance": appliance})

        self.routines = routines
        self.appliance = appliance


class MaxPowerExceededError(ConflictError):
    """Error raised when the power consumption of the house is greater than the maximum power consumption.
    """

    def __init__(self, max_power: float, when: datetime):
        super().__init__(
            f"Power consumption of the house is greater than {max_power/1000}kW at {when.strftime('%H:%M')}. This can cause a power cut-off.",
            {"max_power": max_power, "when": when})
        self.max_power = max_power
        self.when = when


class StateMatrix():
    """A matrix that represents the operation mode of each appliance in each minute of the day.
    A row is created for each minute of the day, and a column for each appliance.
    So if there are 10 appliances, the matrix will have 1440 rows and 10 columns.
    Currently the matrix is implemented as a numpy array of integers.

    Methods are provided to calculate the total consumption of the house at a given time,
    the consumption of a specific appliance at a given time, and to simulate a new matrix
    with a new set of routines.
    """

    def __init__(self, appliances: list[Appliance], routines: list[Routine], config: HomeConfig):
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

                conflicting_actions = routine.conflicting_actions(
                    other_routine)
                if conflicting_actions is None:
                    continue

                raise InconsistentRoutinesError(
                    [routine, other_routine], conflicting_actions[0].appliance)

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
            sum = 0
            for appliance_id, mode_id in enumerate(self.matrix[minute_of_day]):
                appliance = next(
                    a for a in self.appliances if a.id == appliance_id)
                mode = next(m for m in appliance.modes if m.id == mode_id)
                sum += mode.power_consumption

            if sum > config.max_power:
                time = datetime.today().replace(hour=minute_of_day//60, minute=minute_of_day % 60)
                raise MaxPowerExceededError(config.max_power, time)

    def add_routine(self, routine: Routine) -> StateMatrix:
        """Creates a new matrix with a new routine added.

        Args:
            routine (Routine): The routine to add.

        Returns:
            StateMatrix: The new matrix with the new routine added.
        """
        return StateMatrix(self.appliances, self.routines + [routine], self.config)

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

            appliance = next(a for a in self.appliances if a.id == i)
            mode = next(m for m in appliance.modes if m.id == mode_id)
            total_consumption += mode.power_consumption

        return total_consumption

    def consumptions(self, when: datetime) -> dict[Appliance, float]:
        """Calculate the consumption of the appliances at a given time.

        Args:
            when (datetime): The time to calculate the consumption.

        Returns:
            dict[Appliance, float]: The consumption of the appliances at the given time.
        """

        minute_of_day = when.hour * 60 + when.minute
        modes_ids = self.matrix[minute_of_day]

        consumptions_dict = {}
        for appliance_id, mode_id in enumerate(modes_ids):
            appliance = next(
                a for a in self.appliances if a.id == appliance_id)
            mode = next(m for m in appliance.modes if m.id == mode_id)
            consumptions_dict[appliance] = mode.power_consumption

        return consumptions_dict

    def appliance_consumption(self, appliance: Appliance, when: datetime) -> float:
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

    def __init__(self, config: HomeConfig) -> None:
        self.config = config
        self.matrix = np.zeros(
            (const.DAYS_IN_WEEK, const.HOURS_IN_DAY), dtype=float)

        for day_of_week in list(range(const.DAYS_IN_WEEK)):
            if config.energy_rates_number == 1:
                # Set everything to F1
                self.matrix[day_of_week, :] = config.energy_rates_prices[0]

            elif config.energy_rates_number == 2:
                # Set everything to F23
                self.matrix[day_of_week, :] = config.energy_rates_prices[1]

                # Set monday to friday from 8:00 to 18:00 to F1
                if const.DAY_OF_WEEK_MONDAY <= day_of_week <= const.DAY_OF_WEEK_FRIDAY:
                    self.matrix[day_of_week,
                                8:18+1] = config.energy_rates_prices[0]

            elif config.energy_rates_number == 3:
                # Set everything to F3
                self.matrix[day_of_week, :] = config.energy_rates_prices[2]

                if day_of_week <= const.DAY_OF_WEEK_SATURDAY:
                    if day_of_week <= const.DAY_OF_WEEK_FRIDAY:
                        self.matrix[day_of_week,
                                    7] = config.energy_rates_prices[1]
                        self.matrix[day_of_week,
                                    8:18+1] = config.energy_rates_prices[0]
                        self.matrix[day_of_week, 19:22 +
                                    1] = config.energy_rates_prices[1]
                    else:
                        # Set monday to friday from 8:00 to 18:00 to F1
                        self.matrix[day_of_week,
                                    7:22+1] = config.energy_rates_prices[1]

    def get_cost(self, when: datetime) -> float:
        """Calculate the eletricity cost at a given time.

        Args:
            when (datetime): The time to calculate the cost.

        Returns:
            float: The cost of the electricity at the given time.
        """
        return self.matrix[when.weekday(), when.hour]

    def get_duration_cost(self, when: datetime, duration: timedelta) -> float:
        """Calculate the eletricity cost of a sequence of time,
        starting from a given time and lasting for a given duration.

        Args:
            when (datetime): The start time of the sequence.
            duration (timedelta): The duration of the sequence.

        Returns:
            float: The cost of the electricity for the sequence.
        """
        return self.matrix[when.weekday(), when.hour:(
            when + duration).hour + 1].sum()

    def raw_matrix(self) -> np.ndarray:
        """Return the raw matrix.

        Returns:
            np.ndarray: The raw matrix.
        """
        return self.matrix


class RoutineOptimizer:
    def __init__(self, state_matrix: StateMatrix, costs_matrix: CostsMatrix) -> None:
        self.state_matrix = state_matrix
        self.costs_matrix = costs_matrix
        self.config = state_matrix.config

    def find_best_start_time(self, routine: Routine) -> tuple[datetime, float] | None:
        if self.config.activity_hours is not None:
            start = self.config.activity_hours[0].hour * \
                60 + self.config.activity_hours[0].minute
            end = self.config.activity_hours[1].hour * \
                60 + self.config.activity_hours[1].minute
        else:
            start = 0
            end = const.MINUTES_IN_DAY

        print(start)

        # Calculate the latest end time of the routine so that
        # the longest running action is completed before the end of the day.
        latest_end_time = min(
            end - action.duration for action in routine.actions if action.duration is not None)

        # Calculate the cost of starting the routine at each minute of the day
        routine_costs_per_minute = np.array([self.__routine_cost(routine, routine.when.replace(
            hour=minute//60, minute=minute % 60)) for minute in range(0, latest_end_time+1)])

        # Calculate the cost of the original routine
        original_routine_cost = routine_costs_per_minute[routine.when.hour *
                                                         60 + routine.when.minute]

        # Get the list of indices of the routine costs ordered by cost
        sorted_minutes = np.argsort(routine_costs_per_minute)

        # Iterate the ordered indices of the routine costs
        for m in sorted_minutes:
            if m < start:
                continue

            # If the cost of the routine at the current iteration is greater than the original cost, return
            if routine_costs_per_minute[m] >= original_routine_cost:
                return None

            old_when = routine.when
            new_when = routine.when.replace(
                hour=m//60, minute=m % 60)

            # Try to add the routine to the matrix at the new time.
            # If it fails, continue to the next iteration.
            try:
                routine.when = new_when
                self.state_matrix.add_routine(routine)
                return new_when, original_routine_cost - routine_costs_per_minute[m]
            except ConflictError:
                routine.when = old_when
                continue

        return None

    def __routine_cost(self, routine: Routine, when: datetime) -> float:
        costs = [self.costs_matrix.get_duration_cost(when, timedelta(minutes=action.duration))*action.mode.power_consumption
                 for action in routine.actions if action.duration is not None]

        return np.sum(costs)
