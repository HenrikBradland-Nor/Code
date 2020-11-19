import pandas as pd
import os
import random
import numpy as np

X_BOUNDS = np.array([-0.5, 0.5], dtype=np.float64)
Y_BOUNDS = np.array([-0.2, np.inf], dtype=np.float64)
Z_BOUNDS = np.array([-0.1, 0.5], dtype=np.float64)

print(np.concatenate((X_BOUNDS, Y_BOUNDS, Z_BOUNDS), axis=None))