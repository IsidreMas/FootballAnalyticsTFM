import sys
sys.path.append("./lib")
from params import *
from input_data import *
from MC import *


t0 = time.time()

M_matrix, corr_matrix = Compute_CellM_Av()
print(M_matrix)

M_matrix = np.where(np.isclose(M_matrix, 1, rtol=1e-05),0.999, M_matrix)
M_matrix = np.where(np.isclose(M_matrix, -1, rtol=1e-05),-0.999, M_matrix)

print(M_matrix)

h = 0.5*np.log((1+M_matrix)/(1-M_matrix))
print(h)

for i in range(MCsystems):
	if i%500==0: print(f"Generating system {i+1}")
	for p in range(mida_matriu_row):
		for q in range(mida_matriu_column):
			matriuspins[p,q] = random.choice(spins)

	E, M = Compute_Energy_Magn(matriuspins, h, mida_matriu_row, mida_matriu_column, J)
	matriuspins, E, M = Monte_Carlo(matriuspins, E, M, mida_matriu_row, mida_matriu_column, steps, h, J, T)

	if i==0:
		M_sampled, Corr_sampled = M_and_Corr(matriuspins)
	else:
		a, b = M_and_Corr(matriuspins)
		M_sampled += a
		Corr_sampled += b


tol1 = 0
tol2 = 0

for i in range(mida_matriu_row):
	for j in range(mida_matriu_column):
		tol1 += abs(M_sampled[i,j]-M_matrix[i,j])

for i in range(mida_matriu_row*mida_matriu_column):
	for j in range(mida_matriu_row*mida_matriu_column):
		tol2 += abs(Corr_sampled[i,j]-corr_matrix[i,j])/2

count = 1

file = open(create_dir(working_dir+"/results/")+f"convergence.txt", "w")
file.write("step \t\t\t tol1 \t\t\t tol2\n")
data = np.column_stack([count, tol1, tol2])
np.savetxt(file, data)

while (True):
	eta = 1/np.sqrt(count)
	print(f"step: {count}, tol1: {tol1} with eps: {eps1}, tol2: {tol2} with eps: {eps2}")

	h = h + eta*(M_matrix-M_sampled)
	J = J + eta*(corr_matrix-Corr_sampled)

	for i in range(MCsystems):
		if i%500==0: print(f"Generating system {i+1}")
		for p in range(mida_matriu_row):
			for q in range(mida_matriu_column):
				matriuspins[p,q] = random.choice(spins)

		E, M = Compute_Energy_Magn(matriuspins, h, mida_matriu_row, mida_matriu_column, J)
		matriuspins, E, M = Monte_Carlo(matriuspins, E, M, mida_matriu_row, mida_matriu_column, steps, h, J, T)

		if i==0:
			M_sampled, Corr_sampled = M_and_Corr(matriuspins)
		else:
			a, b = M_and_Corr(matriuspins)
			M_sampled += a
			Corr_sampled += b

	tol1 = 0
	tol2 = 0

	for i in range(mida_matriu_row):
		for j in range(mida_matriu_column):
			tol1 += abs(M_sampled[i,j]-M_matrix[i,j])

	for i in range(mida_matriu_row*mida_matriu_column):
		for j in range(mida_matriu_row*mida_matriu_column):
			tol2 += abs(Corr_sampled[i,j]-corr_matrix[i,j])/2

	count+=1
	data = np.column_stack([count, tol1, tol2])
	np.savetxt(file, data)
	
	if (((tol1<eps1) & (tol2<eps2)) | (count>max_steps)):
		break

	
file.close()

pickle.dump(M_sampled, open(create_dir(working_dir+f"/sampled/{mida_matriu_row}x{mida_matriu_column}/")+f"M_{systems}.bin", "wb"))
pickle.dump(Corr_sampled, open(create_dir(working_dir+f"/sampled/{mida_matriu_row}x{mida_matriu_column}/")+f"Corr_{systems}.bin", "wb"))
pickle.dump(M_matrix, open(create_dir(working_dir+f"/sampled/{mida_matriu_row}x{mida_matriu_column}/")+f"M_{systems}_initial.bin", "wb"))
pickle.dump(corr_matrix, open(create_dir(working_dir+f"/sampled/{mida_matriu_row}x{mida_matriu_column}/")+f"Corr_{systems}_initial.bin", "wb"))
pickle.dump(J, open(create_dir(working_dir+f"/gaussians/{mida_matriu_row}x{mida_matriu_column}/inverse/")+"J.bin", "wb"))
pickle.dump(h, open(create_dir(working_dir+f"/gaussians/{mida_matriu_row}x{mida_matriu_column}/inverse/")+"h.bin", "wb"))

print(f"CPU time elapsed: {(time.time()-t0)/60} minutes")




