from datetime import datetime
import numpy as np
from config import EnergyConfig
import const


class CostsMatrix:
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
        """Calculate the cost of the house at a given time.

        Args:
            when (datetime): The time to calculate the cost.

        Returns:
            float: The cost of the house at the given time.
        """
        minute_of_day = when.hour * 60 + when.minute
        day_of_week = when.weekday()

        return self.matrix[day_of_week, minute_of_day]
