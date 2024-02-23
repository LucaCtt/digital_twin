#!/usr/bin/env python3

import os
import uvicorn

from dt.api import create_api
from dt.data import RepositoryFactory
from dt.config import Config


def main():
    if os.environ.get("DT_CONFIG_FILE") is None:
        raise ValueError("DT_CONFIG_FILE environment variable is not set")

    config = Config.from_toml(os.environ["DT_CONFIG_FILE"])
    repository = RepositoryFactory.create(config.database_config)
    api = create_api(repository, config.home_config)

    if os.environ.get("DT_BACKEND_URL") is None:
        port = 8000
    else:
        port = int(os.environ["DT_BACKEND_URL"].split(":")[2])

    uvicorn.run(api, port=port)

if __name__ == "__main__":
    main()
