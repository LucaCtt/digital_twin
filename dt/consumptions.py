from __future__ import annotations
from datetime import datetime
import numpy as np

from const import MINUTES_IN_DAY
from data import Appliance, Routine


class ConsumptionsMatrix():
    """A matrix that represents the power consumption of each appliance in each minute of the day.
    A row is created for each minute of the day, and a column for each appliance.
    So if there are 10 appliances, the matrix will have 1440 rows and 10 columns.
    Currently the matrix is implemented as a numpy array of integers.

    Methods are provided to calculate the total consumption of the house at a given time,
    the consumption of a specific appliance at a given time, and to simulate a new matrix
    with a new set of routines.
    """

    def __init__(self, appliances: list[Appliance], routines: list[Routine]):
        """Constructor.

        Args:
            appliances (list[Appliance]): The list of appliances.
            routines (list[Routine]): The list of routines.
        """

        self.appliances = appliances
        self.routines = routines
        self.matrix = np.zeros(
            (MINUTES_IN_DAY, len(appliances)), dtype=np.int8)

        for routine in routines:
            if not routine.enabled:
                continue

            for action in routine.actions:
                # Convert start and end time to minutes of the day
                start = routine.when.hour * 60 + routine.when.minute
                end = min(action.duration + start,
                          MINUTES_IN_DAY) if action.duration else MINUTES_IN_DAY - start

                for minute in range(start, end+1):
                    self.matrix[minute-1][action.appliance.id] = action.mode.id

    def simulate(self, new_routine: Routine) -> ConsumptionsMatrix:
        """Simulate a new matrix with a new set of routines to be added to the existing ones.

        Args:
            new_routines (list[Routine]): The new set of routines.

        Returns:
            ConsumptionsMatrix: The new matrix, with the new routines added to the existing ones.
        """
        return ConsumptionsMatrix(self.appliances, self.routines + [new_routine])

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
