#!/usr/bin/env python3

import os
import tomllib
import uvicorn

from api import create_api
from data import JSONRepository
from plots import plot_consumptions_matrix, plot_simulated_matrix

def start_api():
    with open(os.environ["CONFIG_FILE"], "rb") as f:
        config = tomllib.load(f)

    if config["database"]["type"] != "json":
        raise ValueError("Database type not supported")

    repository = JSONRepository(config["database"]["appliances_dir"], config["database"]
                                ["routines_dir"], config["database"]["test_routines_dir"])

    uvicorn.run(create_api(repository))

if __name__ == "__main__":
    start_api()
