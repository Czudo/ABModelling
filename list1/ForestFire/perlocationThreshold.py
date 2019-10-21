import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner
from ForestFireModel import ForestFireModel, compute_p
import numpy as np
import multiprocessing


def perlocation(L):

    fixed_params = {"L": L}

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
    L = [25, 50]
    p = np.arange(0, 1.1, 0.1)

    multiprocess = multiprocessing.Pool()
    a = multiprocess.map(perlocation, L)

    for i in range(len(L)):
        plt.plot(p, a[i], '-o', label='L = ' + str(L[i]))
    plt.title(r'Percolation threshold $p^*$')
    plt.xlabel(r'$p$')
    plt.ylabel(r'$p^*$')
    plt.legend()
    plt.show()
