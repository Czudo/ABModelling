import matplotlib.pyplot as plt
from mesa.batchrunner import BatchRunner
from ForestFireModel import ForestFireModel, compute_p
import numpy as np

# Perlocation threshold

fixed_params = {"L": 25}

variable_params = {"p": np.arange(0.05, 0.95, 0.1)}

batch_run = BatchRunner(
    ForestFireModel,
    variable_params,
    fixed_params,
    iterations=10,
    model_reporters={"p*": compute_p}
)

batch_run.run_all()

run_data = batch_run.get_model_vars_dataframe()

data = run_data.groupby('p').mean()
plt.plot(data['p*'], '-o')
plt.show()
