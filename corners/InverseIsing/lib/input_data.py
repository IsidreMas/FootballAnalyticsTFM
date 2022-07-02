from params import *


def Compute_CellM_Av():

	for i in range(systems):
		exec("matrix_{} = pickle.load(open(matrix_dir+\"/corner_{}.bin\", \"rb\"))".format(i+1,i+1), globals())
		exec("matrix_{} = matrix_{}.to_numpy()".format(i+1,i+1), globals())
	M_matrix = np.zeros((mida_matriu_row, mida_matriu_column))
	corr_matrix = np.zeros((mida_matriu_row*mida_matriu_column, mida_matriu_row*mida_matriu_column))

	for i in range(systems):
		if i%100==0: print(f"Processing system {i+1}")
		exec("matrix = matrix_{}".format(i+1), globals())

		M_matrix += matrix/systems
		
		mat = matrix.tolist()
		matrix_list = [item for sublist in mat for item in sublist]
		
		for j in range(mida_matriu_row*mida_matriu_column):
			for k in range(mida_matriu_row*mida_matriu_column):
		 		corr_matrix[j,k] += matrix_list[j]*matrix_list[k]/systems
		 		if j==k:
		 			corr_matrix[j,k] = 0

	return M_matrix, corr_matrix



def M_and_Corr(matrix_in):

	corr_matrix = np.zeros((mida_matriu_row*mida_matriu_column, mida_matriu_row*mida_matriu_column))
	mat = matrix_in.tolist()
	matrix_list = [item for sublist in mat for item in sublist]
	
	for j in range(mida_matriu_row*mida_matriu_column):
		for k in range(mida_matriu_row*mida_matriu_column):
	 		corr_matrix[j,k] += matrix_list[j]*matrix_list[k]/MCsystems
	 		if j==k:
	 			corr_matrix[j,k] = 0


	return matrix_in/MCsystems, corr_matrix


