import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner
from ForestFireModel import ForestFireModel, compute_p
import numpy as np

L = [25, 50, 100]
for i in L:
    fixed_params = {"L": i}

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
    plt.plot(data['p*'], '-o', label='L = ' + str(i))

plt.title(r'Percolation threshold $p^*$')
plt.xlabel(r'$p$')
plt.ylabel(r'$p^*$')
plt.legend()
plt.show()
