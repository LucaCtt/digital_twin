#!/usr/bin/env python3

import typer
import uvicorn

from api import create_api
from data import JSONRepository
from plots import plot_consumptions_matrix, plot_simulated_matrix
import const

app = typer.Typer()
repository = JSONRepository(
    const.APPLIANCES_DIR, const.ROUTINES_DIR, const.TEST_ROUTINES_DIR)


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
