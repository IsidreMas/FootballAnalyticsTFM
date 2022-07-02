import random
import numpy as np
from numba import jit


@jit(nopython=True)
def Monte_Carlo(matrix, E, M, mida_matriu_row, mida_matriu_column, steps, h, J, T):
	for j in range(steps):
		a = random.randint(0, mida_matriu_row-1)
		b = random.randint(0, mida_matriu_column-1)
		matrix[a,b] *= -1
		DeltaH = -2*matrix[a,b]*h[a,b]
		DeltaJ = -4*J_E(matrix,a,b,mida_matriu_row,mida_matriu_column,J)
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
		# energy.append(E)

	return matrix, E, M


@jit(nopython=True)
def J_E(matrix, a, b, mida_matriu_row, mida_matriu_column, J):

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


def Compute_Energy_Magn(matrix, h, mida_matriu_row, mida_matriu_column, J):

	E = 0
	M = 0

	for i in range(mida_matriu_row):
		for j in range(mida_matriu_column):
			E += (-h[i,j]*matrix[i,j] - J_E(matrix, i, j, mida_matriu_row, mida_matriu_column, J))
			M += (1.0/(mida_matriu_row*mida_matriu_column))*matrix[i,j]

	return E, M

def Compute_Energy(matrix, h, mida_matriu_row, mida_matriu_column, J):

	E = 0

	for i in range(mida_matriu_row):
		for j in range(mida_matriu_column):
			E += (-h[i,j]*matrix[i,j] - J_E(matrix, i, j, mida_matriu_row, mida_matriu_column, J))

	return E