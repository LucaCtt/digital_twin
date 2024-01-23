#!/usr/bin/env python3

import os
import argparse
import subprocess
import tomllib
import typer
import uvicorn

from api import create_api
from data import JSONRepository
from plots import plot_consumptions_matrix, plot_simulated_matrix

with open(os.environ["CONFIG_FILE"], "rb") as f:
    config = tomllib.load(f)

if config["database"]["type"] != "json":
    raise ValueError("Database type not supported")

repository = JSONRepository(config["database"]["appliances_dir"], config["database"]
                            ["routines_dir"], config["database"]["test_routines_dir"])

# Read command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--frontend', action='store_true')
args = parser.parse_args()

if __name__ == "__main__":
    if (args.frontend):
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
        frontend_dist = os.path.join(frontend_dir, "dist")
        print(frontend_dir)

        subprocess.check_call("npm run build", cwd=frontend_dir, shell=True)
        api = create_api(repository, serve_static=True, serve_dir=frontend_dist)

        uvicorn.run(api)
    else:
        uvicorn.run(create_api(repository))
