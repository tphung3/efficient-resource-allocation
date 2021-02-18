def get_mem(file_name):
	all_mem = []
	all_vir_mem = []
	with open(file_name, 'r') as f:
		Lines = f.readlines()
		for line in Lines[1:]:
			resource = line.split(" -- ")
			mem = int(resource[2])
			vir_mem = int(resource[3])
			all_mem.append(mem)
			all_vir_mem.append(vir_mem)
	return [all_mem, all_vir_mem]

def declare_resources(all_mem):
	def_mem = 4000
	all_waste = sum([def_mem-x for x in all_mem])
	return [all_waste, all_waste/len(all_mem)]

def use_vir_mem(all_mem, vir_mem):
	all_waste = 0
	for i in range(len(all_mem)):
		all_waste += vir_mem[i] - all_mem[i]
	return [all_waste, all_waste/len(all_mem)]

def slow_increase(all_mem):
	seed = max(all_mem[:20])
	rate = 1.1
	all_waste = 0
	for i in range(len(all_mem[20:])):
		if all_mem[i] > seed:
			seed = all_mem[i]*rate
		else:
			all_waste += seed - all_mem[i]
	return [all_waste, all_waste/len(all_mem)]

file_name = "resources_all.txt"
all_mem, all_vir_mem = get_mem(file_name)
w1, aw1 = declare_resources(all_mem)
print("Initial resources declaration wastes in total {} MB, on average {} MB".format(w1, aw1))
w2, aw2 = use_vir_mem(all_mem, all_vir_mem)
print("Using virtual memory wastes in total {} MB, on average {} MB".format(w2, aw2))
w3, aw3 = slow_increase(all_mem)
print("Slow increase wastes in total {} MB, on average {} MB".format(w3, aw3))
print(len(all_mem))
