import numpy as np

resources_all = []

with open("resources_all.txt", 'r') as f:
	Lines = f.readlines()
	for line in Lines[1:]:
		resource = line.split(" -- ")
		resource[8] = resource[8].split("\n")[0]
		resources_all.append(resource)

mem_all = [int(resource[2]) for resource in resources_all]
mem_all = np.asarray(mem_all)
print("Average memory usage: {}".format(np.average(mem_all)))
print("Maximum memory usage: {}".format(np.max(mem_all)))
print("Minimum memory usage: {}".format(np.min(mem_all)))
print("Standard deviation of memory usage: {}".format(np.std(mem_all)))

