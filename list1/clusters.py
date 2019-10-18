import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner
from ForestFireModel import ForestFireModel, compute_cluster

import numpy as np
#
fixed_params = {"L": 10}

variable_params = {"p": np.arange(0.05, 0.95, 0.1)}

batch_run = BatchRunner(
    ForestFireModel,
    variable_params,
    fixed_params,
    iterations=1000,
    model_reporters={"cluster": compute_cluster}
)
batch_run.run_all()

run_data = batch_run.get_model_vars_dataframe()
data = run_data.groupby('p').mean()
plt.plot(data['cluster'], '-o')
plt.show()
