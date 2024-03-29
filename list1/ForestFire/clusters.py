import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner
from ForestFireModel import ForestFireModel, compute_cluster
import numpy as np

if __name__ == '__main__':
    fixed_params = {"L": 100}

    variable_params = {"p": np.arange(0, 1.05, 0.05)}

    batch_run = BatchRunner(
        ForestFireModel,
        variable_params,
        fixed_params,
        iterations=3,
        model_reporters={"cluster": compute_cluster}
    )
    batch_run.run_all()

    run_data = batch_run.get_model_vars_dataframe()
    data = run_data.groupby('p').mean()
    plt.plot(data['cluster'], '-o')
    plt.title(r'The biggest cluster dependent of $p$')
    plt.xlabel(r'$p$')
    plt.ylabel('average size of the biggest cluster')
    plt.show()
