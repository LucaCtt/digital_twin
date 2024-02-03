#!/usr/bin/env python3

import os
from fastapi import FastAPI
import uvicorn

from api import create_api
from data import RepositoryFactory
from config import Config


if os.environ.get("CONFIG_FILE") is None:
    raise ValueError("CONFIG_FILE environment variable is not set")

config = Config.from_toml(os.environ["CONFIG_FILE"])
repository = RepositoryFactory.create(config.database_config)
api=create_api(repository, config.energy_config)


if __name__ == "__main__":
    uvicorn.run("dt.__main__:api", reload=True)
