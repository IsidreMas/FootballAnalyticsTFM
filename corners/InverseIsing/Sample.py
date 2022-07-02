import numpy as np
import os
import random
import time
import pickle
import matplotlib.pyplot as plt
from numba import jit

mida_matriu_row = 7
mida_matriu_column = 6
spins=[-1,1]

working_dir = os.getcwd()
matriuspins = np.zeros((mida_matriu_row, mida_matriu_column))


def create_dir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir


J = pickle.load(open(working_dir+f"/gaussians/{mida_matriu_row}x{mida_matriu_column}/inverse/J.bin", "rb"))
hs = pickle.load(open(working_dir+f"/gaussians/{mida_matriu_row}x{mida_matriu_column}/inverse/h.bin", "rb"))



def E_M_averaged(energy, magn):

	return sum(energy)/len(energy), sum(magn)/len(magn)


def E_M_squared(energy, magn):
	E = 0
	M = 0

	for i in range(len(energy)):
		E += energy[i]*energy[i]
		M += magn[i]*magn[i]

	return E/len(energy), M/len(magn)

@jit(nopython=True)
def Compute_Energy_Magn(matrix, J):

	E = 0 
	M = 0

	for i in range(mida_matriu_row):
		for j in range(mida_matriu_column):
			E += (-hs[i,j]*matrix[i,j] - J_E(matrix, i, j, J))
			M += (1.0/(mida_matriu_row*mida_matriu_column))*matrix[i,j]

	return E, M


@jit(nopython=True)
def J_E(matrix, a, b, J):

	energy = 0
	pos = 0

	for i in range(mida_matriu_row):
		for j in range(mida_matriu_column):
			if a==i and b==j:
				row=pos
				break
			pos+=1

	pos = 0
	for i in range(mida_matriu_row):
		for j in range(mida_matriu_column):
			energy += J[row,pos]*matrix[i,j]
			pos+=1
	return matrix[a,b]*energy/2


def Boltzmann_Statistics(matrixs, energies):
	E_hist = []
	times_E = []

	while (len(matrixs)!=0):
		print(f"next with len(): {len(matrixs)}")
		indexes = []
		mat = np.copy(matrixs[np.argmin(energies)])
		e = np.copy(energies[np.argmin(energies)])
		for j in range(len(matrixs)):
			if np.allclose(mat, matrixs[j]):
				indexes.append(j)
		E_hist.append(e)
		times_E.append(len(indexes))
		matrixs = np.delete(matrixs, indexes, 0)
		energies = np.delete(energies, indexes, 0)

	print(matrixs)
	plt.scatter(E_hist, times_E)
	plt.yscale("log")
	plt.show()


@jit(nopython=True)
def Monte_Carlo(matrix, E, M, steps, h, J, T):

	for j in range(steps):
		a = random.randint(0, mida_matriu_row-1)
		b = random.randint(0, mida_matriu_column-1)

		matrix[a,b] *= -1
		DeltaH = -2*matrix[a,b]*h[a,b]
		DeltaJ = -4*J_E(matrix,a,b,J)
		DeltaE = DeltaH+DeltaJ

		if DeltaE<0:
			E += DeltaE

			if matrix[a,b] == -1:
				M -= 2.0/(mida_matriu_row*mida_matriu_column)

			else:
				M += 2.0/(mida_matriu_row*mida_matriu_column)

		else:
			boltzmann = np.exp(-(DeltaE)/T)
			c = random.random()

			if c<boltzmann:
				E += DeltaE

				if matrix[a,b] == -1:
					M -= 2.0/(mida_matriu_row*mida_matriu_column)

				else:
					M += 2.0/(mida_matriu_row*mida_matriu_column)

			else:
				matrix[a,b] *= -1

	return matrix, E, M


steps = 300000

energy = open(create_dir(working_dir + f"/new_corners/{mida_matriu_row}x{mida_matriu_column}/")+f"matrix_energies.txt", "w")
ener = open(create_dir(working_dir + f"/new_corners/{mida_matriu_row}x{mida_matriu_column}/")+f"matrix_energies_fin.txt", "w")
t0 = time.time()
e = []
en = []

for i in range(0,5000):
	T = 1.5
	if i%1==0: print(f"Evolution till equilibrium of system {i+1} at T={T}")
	for p in range(mida_matriu_row):
		for q in range(mida_matriu_column):
			matriuspins[p,q] = random.choice(spins)

	E, M = Compute_Energy_Magn(matriuspins, J)
	while T > 0.1:
		if T == 0.6:
			steps = 800000
			matriuspins, E, M = Monte_Carlo(matriuspins, E, M, steps, hs, J, T)
		else:
			matriuspins, E, M = Monte_Carlo(matriuspins, E, M, steps, hs, J, T)
		T -= 0.1

	ee, mm = Compute_Energy_Magn(matriuspins, J)
	en.append(ee)
	e.append(E)
	pickle.dump(matriuspins, open(create_dir(working_dir+f"/new_corners/{mida_matriu_row}x{mida_matriu_column}/")+f"new_corner_{i+1}.bin", "wb"))

np.savetxt(ener, en)
np.savetxt(energy, e)
energy.close()
print(f"CPU time elapsed: {time.time()-t0} seconds")















