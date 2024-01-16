import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import patheffects
import numpy as np

from .consumptions import ConsumptionsMatrix
from .data import Appliance, Routine
from .const import MINUTES_IN_DAY

plt.rcParams['axes.labelsize'] = "medium"
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = "serif"
plt.rcParams['savefig.bbox'] = "tight"


def __prepare_matrix_figure(appliances: list[Appliance], routines: list[Routine], title: str = "Consumptions"):
    sorted_appliances = [a for a in sorted(appliances, key=lambda a: a.id)]
    appliances_names = [a.device.title() for a in sorted_appliances]
    hours_in_day = [f"{h:02d}:00" for h in range(0, 24)]

    matrix = ConsumptionsMatrix(appliances, routines).raw_matrix()
    matrix_masked = np.ma.masked_where(matrix == 0, matrix)

    c_map = cm.get_cmap('tab10')
    c_map.set_bad('whitesmoke')

    plt.figure(title, figsize=(10, 10))
    plt.matshow(matrix_masked, fignum=plt.gcf().number,  # type: ignore
                aspect="auto", cmap=c_map)

    for appliance_id, column in enumerate(matrix.T):
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


def plot_consumptions_matrix(appliances: list[Appliance], routines: list[Routine]):
    __prepare_matrix_figure(appliances, routines)

    plt.show()


def plot_simulated_matrix(appliances: list[Appliance], routines: list[Routine], test_routines: list[Routine]):
    __prepare_matrix_figure(appliances, routines, "Real")
    __prepare_matrix_figure(appliances, routines + test_routines, "Simulated")

    plt.show()
