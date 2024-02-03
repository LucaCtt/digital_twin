#!/usr/bin/env python3

import os
import uvicorn

from api import create_api
from data import RepositoryFactory
from config import Config

def start_api():
    if os.environ.get("CONFIG_FILE") is None:
        raise ValueError("CONFIG_FILE environment variable is not set")

    config = Config.from_toml(os.environ["CONFIG_FILE"])

    repository = RepositoryFactory.create(config.database_config)

    uvicorn.run(create_api(repository, config.energy_config))


if __name__ == "__main__":
    start_api()
