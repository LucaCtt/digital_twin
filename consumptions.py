from datetime import datetime
from matplotlib import patheffects
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from const import MINUTES_IN_DAY
from models.appliance import Appliance
from models.routine import Routine

plt.rcParams['axes.labelsize'] = "medium"
plt.rcParams['font.size'] = 11
plt.rcParams['font.family'] = "serif"
plt.rcParams['savefig.bbox'] = "tight"


def __consumptions_matrix(appliances: list[Appliance], routines: list[Routine]):
    matrix = np.zeros((MINUTES_IN_DAY, len(appliances)), dtype=np.int8)

    for routine in routines:
        if not routine.enabled:
            continue

        for action in routine.actions:
            start = routine.when
            end = min(action.duration + start,
                      MINUTES_IN_DAY) if action.duration else MINUTES_IN_DAY - start

            for minute in range(start, end+1):
                matrix[minute-1][action.appliance.id] = action.mode.id

    return matrix


def __prepare_matrix_figure(appliances: list[Appliance], routines: list[Routine], title: str = "Consumptions"):
    sorted_appliances = [a for a in sorted(appliances, key=lambda a: a.id)]
    appliances_names = [a.device.title() for a in sorted_appliances]
    hours_in_day = [f"{h:02d}:00" for h in range(0, 24)]

    matrix = __consumptions_matrix(appliances, routines)
    matrix_masked = np.ma.masked_where(matrix == 0, matrix)

    c_map = cm.get_cmap('tab10')
    c_map.set_bad('whitesmoke')

    plt.figure(title, figsize=(10, 10))
    plt.matshow(matrix_masked, fignum=plt.gcf().number, aspect="auto", cmap=c_map) # type: ignore

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
            mode = next(mode for mode in appliance_modes if mode.id == column[m])
            plt.text(appliance_id, m, mode.name.title(), ha="center", va="center", color="w").set_path_effects([patheffects.withStroke(linewidth=2, foreground='k')])

        
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


def total_consumption_now(appliances: list[Appliance], routines: list[Routine]):
    now = datetime.now()
    minute_of_day = now.hour * 60 + now.minute

    matrix = __consumptions_matrix(appliances, routines)
    row_now = matrix[minute_of_day]

    total_consumption = 0

    for i, mode_id in enumerate(row_now):
        if mode_id == 0:
            continue
        else:
            appliance = next(a for a in appliances if a.id == i)
            mode = next(m for m in appliance.modes if m.id == mode_id)
            total_consumption += mode.power_consumption

    return total_consumption


def plot_simulated_matrix(appliances: list[Appliance], routines: list[Routine], test_routines: list[Routine]):

    __prepare_matrix_figure(appliances, routines, "Real")
    __prepare_matrix_figure(appliances, routines + test_routines, "Simulated")

    plt.show()
