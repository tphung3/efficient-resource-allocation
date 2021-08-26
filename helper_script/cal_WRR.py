import numpy as np
import csv

datasets = ["colmena", "coffea", "normal_small", "uniform_large", "exponential_small", "bimodal_small_std", "trimodal"]

dire = "../resources_analysis/lv2/"

#for WRR
for dataset in datasets:
	print(dataset)
	with open(dire+dataset+"/results/strategies_evaluation.csv") as f:
		csv_f = csv.reader(f, delimiter=',')
		data = [data for data in csv_f]
		data_array = np.asarray(data)
		for i in range(1, len(data_array[0])):
			print(data_array[0][i] + data_array[1][i] + data_array[2][i])
			print(np.float(data_array[21][i])/np.float(data_array[21][1]))


"""
#for ATE
for dataset in datasets:
	print(dataset)
	with open(dire+dataset+"/results/strategies_evaluation.csv") as f:
		csv_f = csv.reader(f, delimiter=',')
		data = [data for data in csv_f]
		data_array = np.asarray(data)
		for i in range(1, len(data_array[0])):
			print(data_array[0][i] + data_array[1][i] + data_array[2][i])
			print(round(np.float(data_array[30][i]), 3))

"""
"""
#for TWE
for dataset in datasets:
	print(dataset)
	with open(dire+dataset+"/results/strategies_evaluation.csv") as f:
		csv_f = csv.reader(f, delimiter=',')
		data = [data for data in csv_f]
		data_array = np.asarray(data)
		for i in range(1, len(data_array[0])):
			print(data_array[0][i] + data_array[1][i] + data_array[2][i])
			print(round(np.float(data_array[28][i]), 3))

"""
