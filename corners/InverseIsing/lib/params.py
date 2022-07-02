import numpy as np
import pickle
import time
import os


mida_matriu_row = 7
mida_matriu_column = 6
systems = 45
MCsystems = 5000
gaussians = 6
Frame = 25
T = 1.5
steps = 8000

eps1 = 1e-2
eps2 = (mida_matriu_row*mida_matriu_column)*eps1
max_steps = 3000

h = np.zeros((mida_matriu_row, mida_matriu_column))
J = np.zeros((mida_matriu_row*mida_matriu_column, mida_matriu_row*mida_matriu_column))
matriuspins = np.zeros((mida_matriu_row, mida_matriu_column))

working_dir = os.getcwd()
matrix_dir = "../sampled"+f"/pj{Frame}_ball{Frame}_{gaussians}_{gaussians}_{gaussians}"
spins=[-1,1]

def create_dir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir