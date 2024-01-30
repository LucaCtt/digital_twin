import tomllib
from typing import Any

class EnergyConfig:
    def __init__(self, max_power: float, energy_rates_number: int, energy_rates_prices: list[float]):
        self.max_power = max_power
        self.energy_rates_number = energy_rates_number
        self.energy_rates_prices = energy_rates_prices

        if len(self.energy_rates_prices) != self.energy_rates_number:
            raise ValueError(
                "Energy rates prices must match the number of energy rates")


class DatabaseConfig:
    def __init__(self, type: str, appliances_dir: str, routines_dir: str, test_routines_dir: str):
        self.type = type
        self.appliances_dir = appliances_dir
        self.routines_dir = routines_dir
        self.test_routines_dir = test_routines_dir


class Config:
    def __init__(self, config: dict[str, Any]) -> None:
        self.energy_config = EnergyConfig(
            config["home"]["max_power"], config["home"]["energy_rates_number"], config["home"]["energy_rates_prices"])

        self.database_config = DatabaseConfig(
            config["database"]["type"], config["database"]["appliances_dir"], config["database"]["routines_dir"], config["database"]["test_routines_dir"])

    @staticmethod
    def from_toml(config_path: str):
        with open(config_path, "rb") as f:
            dict = tomllib.load(f)

        return Config(dict)