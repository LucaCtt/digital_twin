#!/usr/bin/env python3

"""Plot consumptions matrix

This script plots the consumptions matrix of the appliances in the database.
"""

import datetime
import os
import matplotlib
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import patheffects
import matplotlib.patches as mpatches
import numpy as np

from dt.config import Config, HomeConfig
from dt.data import RepositoryFactory, Appliance, Routine, DataRepository
from dt.energy import StateMatrix, CostsMatrix
from dt.const import MINUTES_IN_DAY

matplotlib.use("GTK4Agg")

SAVE = True

plt.rcParams['axes.labelsize'] = "medium"
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = "serif"
plt.rcParams['savefig.bbox'] = "tight"


def __get_appliance_name(appliance: Appliance):
    if appliance.device in ["lamp", "television"]:
        return f"{appliance.device.title()} ({appliance.location})"

    return f"{appliance.device.title()}"


def __prepare_matrix_figure(appliances: list[Appliance], routines: list[Routine], config: HomeConfig, title: str = "Consumptions"):
    sorted_appliances = list(sorted(appliances, key=lambda a: a.id))
    appliances_names = [__get_appliance_name(a) for a in sorted_appliances]
    hours_in_day = [f"{h:02d}:00" for h in range(0, 24)]

    matrix_raw = StateMatrix(appliances, routines, config).raw_matrix()
    matrix_masked = np.ma.masked_where(matrix_raw == 0, matrix_raw)

    c_map = cm.get_cmap('tab10')
    c_map.set_bad('whitesmoke')

    plt.figure(title, figsize=(10, 10))
    plt.matshow(matrix_masked, fignum=plt.gcf().number,  # type: ignore
                aspect="auto", cmap=c_map)

    for appliance_id, column in enumerate(matrix_raw.T):
        sequences = []
        start = -1
        end = -1

        for j, value in enumerate(column):
            if value != 0:
                if start == -1:
                    start = j
                end = j
            elif start != -1:
                sequences.append((start, end))
                start = -1
                end = -1

        if start != -1:
            sequences.append((start, end))

        # Compute middle points of sequences
        middle_points = [(start + end) // 2 for start, end in sequences]
        appliance_modes = sorted_appliances[appliance_id].modes

        for m in middle_points:
            mode = next(
                mode for mode in appliance_modes if mode.id == column[m])
            plt.text(appliance_id, m, mode.name.title(), ha="center", va="center", color="w").set_path_effects(
                [patheffects.withStroke(linewidth=2, foreground='k')])

    plt.xticks(range(len(appliances)), appliances_names,
               rotation=45, ha="left", rotation_mode="anchor")
    plt.yticks(range(0, MINUTES_IN_DAY, 60), hours_in_day)

    # Gridlines
    plt.xticks(np.arange(len(appliances))-0.5, minor=True)
    plt.yticks(np.arange(0, MINUTES_IN_DAY, 60)-0.5, minor=True)
    plt.grid(which="minor", color="k", linestyle="--", linewidth=1, alpha=0.4)
    plt.tick_params(which="minor", top=False, bottom=False, left=False)
    plt.tick_params(bottom=False)

    plt.tight_layout()
    if SAVE:
        plt.savefig(f"{title}.png", dpi=300)


def plot_state_matrix(repository: DataRepository, config: HomeConfig):
    __prepare_matrix_figure(repository.get_appliances(),
                            repository.get_routines(), config)

    plt.show()


def plot_simulated_matrix(repository: DataRepository, config: HomeConfig):
    __prepare_matrix_figure(repository.get_appliances(),
                            repository.get_routines(), config, "Real")
    __prepare_matrix_figure(
        repository.get_appliances(), repository.get_routines() + repository.get_test_routines(), config, "Simulated")

    plt.show()


def run_plots():
    config = Config.from_toml(os.environ["DT_CONFIG_FILE"])
    repository = RepositoryFactory.create(config.database_config)

    plot_simulated_matrix(repository, config.home_config)


def plot_costs_matrix():
    values: list[float] = [1, 2, 3]
    costs_matrix = CostsMatrix(HomeConfig(3000, 3, values))
    days_of_week = ["Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"]
    hours_in_day = [f"{h:02d}:00" for h in range(0, 24)]
    cell_labels = ["F1", "F2", "F3"]

    matrix_raw = costs_matrix.raw_matrix().transpose()
    # matrix_masked = np.ma.masked_where(matrix_raw == 0, matrix_raw)

    c_map = ListedColormap(["#aaaaaa", "#dddddd", "#ffffff"])

    plt.figure("Electricity time slots", figsize=(12, 10))
    m = plt.matshow(matrix_raw,  fignum=plt.gcf().number,  # type: ignore
                    aspect="auto", cmap=c_map)

    for (i, j), z in np.ndenumerate(matrix_raw):
        plt.text(j, i, cell_labels[int(z)-1], ha='center', va='center')

    plt.xticks(np.arange(len(days_of_week)), labels=days_of_week)
    plt.yticks(np.arange(0, len(hours_in_day)), labels=hours_in_day)

    plt.grid(which="minor", color="k", linestyle="--", linewidth=1, alpha=0.4)
    plt.tick_params(which="minor", top=False, bottom=False, left=False)
    plt.tick_params(bottom=False)
    plt.xticks(np.arange(len(days_of_week))-0.5, minor=True)
    plt.yticks(np.arange(0, len(hours_in_day))-0.5, minor=True)

    plt.tight_layout()
    plt.savefig(f"costs.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    plot_costs_matrix()
