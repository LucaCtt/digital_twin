#!/usr/bin/env python3

import os
import uvicorn

from api import create_api
from data import RepositoryFactory
from config import Config
from energy import ConsumptionsMatrix, CostsMatrix


def start_api():
    config = Config.from_toml(os.environ["CONFIG_FILE"])

    repository = RepositoryFactory.create(config.database_config)
    costs_matrix = CostsMatrix(config.energy_config)
    consumptions_matrix = ConsumptionsMatrix(
        repository.get_appliances(), repository.get_routines(), costs_matrix)

    uvicorn.run(create_api(repository, consumptions_matrix))


if __name__ == "__main__":
    start_api()
