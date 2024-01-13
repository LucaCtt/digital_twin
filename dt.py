import typer
from consumptions import plot_simulated_matrix, total_consumption_now, plot_consumptions_matrix
from read_data import read_data

app = typer.Typer()

appliances, routines, tests = read_data()


@app.command()
def plot_matrix():
    plot_consumptions_matrix(appliances, routines)


@app.command()
def now():
    print(f"Consumption now: {total_consumption_now(appliances, routines)}W")


@app.command()
def simulate():
    plot_simulated_matrix(appliances, routines, tests)


if __name__ == "__main__":
    app()
