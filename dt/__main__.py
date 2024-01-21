#!/usr/bin/env python3

import os
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

app = typer.Typer()


@app.command()
def map(simulate: bool = False):
    if simulate:
        plot_simulated_matrix(repository)
    else:
        plot_consumptions_matrix(repository)


@app.command()
def start_api():
    api = create_api(repository)
    uvicorn.run(api)


if __name__ == "__main__":
    app()
