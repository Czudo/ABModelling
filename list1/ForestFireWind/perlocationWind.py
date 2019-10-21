import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner
from ForestFireWind import ForestFireModel, compute_p
import numpy as np
import multiprocessing


def perlocationDirection(direction):

    fixed_params = {"L": 25, "strength": 0.5, "direction": direction}

    variable_params = {"p": np.arange(0, 1.1, 0.1)}

    batch_run = BatchRunner(
        ForestFireModel,
        variable_params,
        fixed_params,
        iterations=100,
        model_reporters={"p*": compute_p}
    )

    batch_run.run_all()

    run_data = batch_run.get_model_vars_dataframe()

    data = run_data.groupby('p').mean()
    return data["p*"]


def perlocationStrength(strength):

    fixed_params = {"L": 25, "strength": strength, "direction": (1, 1)}

    variable_params = {"p": np.arange(0, 1.1, 0.1)}

    batch_run = BatchRunner(
        ForestFireModel,
        variable_params,
        fixed_params,
        iterations=100,
        model_reporters={"p*": compute_p}
    )

    batch_run.run_all()

    run_data = batch_run.get_model_vars_dataframe()

    data = run_data.groupby('p').mean()
    return data["p*"]


if __name__ == '__main__':

    p = np.arange(0, 1.1, 0.1)
    direction = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    directionText = ['no wind', 'North', 'South', 'East', 'West', 'North-East', 'North-West',
                     'South-East', 'South-West']
    strength = np.arange(0, 1.1, 0.25)

    multiprocess = multiprocessing.Pool()
    a = multiprocess.map(perlocationDirection, direction)

    for i in range(len(direction)):
        plt.plot(p, a[i], '-o', label=str(directionText[i]))
    plt.title(r'Percolation threshold $p^*$')
    plt.xlabel(r'$p$')
    plt.ylabel(r'$p^*$')
    plt.legend()
    plt.show()

    a = multiprocess.map(perlocationStrength, strength)

    for i in range(len(strength)):
        plt.plot(p, a[i], '-o', label='strength = ' + str(strength[i]))
    plt.title(r'Percolation threshold $p^*$')
    plt.xlabel(r'$p$')
    plt.ylabel(r'$p^*$')
    plt.legend()
    plt.show()