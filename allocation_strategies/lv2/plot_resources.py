#This file generates plots of resources consumption of tasks
import sys
import numpy as np
print("Start plotting")
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 15})
mem_big_datasets = ["colmena", "bimodal_small_std", "trimodal", "exponential_small", "normal_small", "uniform_large"]

#generate figure that shows resource usage over time
def gen_chronos(chrono_resource_use, xlabel, ylabel, title, fig_name):
	if dataset in mem_big_datasets:
		chrono_resource_use = [i/1000 for i in chrono_resource_use]
		ylabel = "Memory (GBs)"
	plt.figure()
	plt.scatter([i for i in range(len(chrono_resource_use))], chrono_resource_use, marker='o', s=[10]*len(chrono_resource_use))
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.ylim(ymin=0)
	if dataset == "normal_small":
		plt.yticks([int(i) for i in range(0, int(np.ceil(max(chrono_resource_use))), 2)], [int(i) for i in range(0, int(np.ceil(max(chrono_resource_use))), 2)])
	plt.tick_params(axis='x', which='both', bottom=False, top=False)
	plt.savefig(plots_dir+fig_name)
	plt.close()

#generate figure that shows efficiency in resource usage of all tasks if we simply apply upper bound
def gen_upper_bound(chrono_resource_use, xlabel, ylabel, title, fig_name):
	if dataset in mem_big_datasets:
		chrono_resource_use = [i/1000 for i in chrono_resource_use]
		ylabel = "Memory (GBs)"

	ratio_guess = 2
	plt.figure()
	if dataset == "colmena":
		max_mem = 64
		#max_mem = max(chrono_resource_use)*1.05
	elif dataset == "coffea":
		max_mem = 4000
	else:
		plt.close()
		exit()
	chrono_resource_use.sort()
	print(max_mem)
	consume = round(sum(chrono_resource_use)/(max_mem*len(chrono_resource_use)), 3)
	print(consume)
	waste = 1 - consume
	plt.stackplot([i for i in range(len(chrono_resource_use))], chrono_resource_use, [max_mem - a for a in chrono_resource_use], colors=['papayawhip', 'cyan'], labels=["Actual Consumption", "Resource Waste"])
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	if dataset == "colmena":
		plt.text(80, 32, "{}%".format(round(waste*100, 3)))
		plt.text(160, 5, "{}%".format(round(consume*100, 3)))
	elif dataset == "coffea":
		plt.text(900, 2300, "{}%".format(round(waste*100, 3)))
		plt.text(1100, 200, "{}%".format(round(consume*100, 3)))	
	plt.title(title)
	plt.ylim(ymin=0)
	plt.xlim(xmin=0)
	plt.legend(loc="upper right")
	plt.savefig(plots_dir+fig_name)
	plt.close()
	

#generate figure that shows resource distribution
def gen_dists(chrono_resource_use, xlabel, ylabel, title, fig_name):
	if dataset in mem_big_datasets:
		chrono_resource_use = [i/1000 for i in chrono_resource_use]
		ylabel = "Memory (GBs)"
	chrono_resource_use.sort()
	plt.figure()
	plt.scatter([i for i in range(len(chrono_resource_use))], chrono_resource_use, marker='o', s=[10]*len(chrono_resource_use))
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.ylim(ymin=0)
	if dataset == "normal_small":
		plt.yticks([int(i) for i in range(0, int(np.ceil(max(chrono_resource_use))), 2)], [int(i) for i in range(0, int(np.ceil(max(chrono_resource_use))), 2)])
	plt.tick_params(axis='x', which='both', bottom=False, top=False)
	plt.savefig(plots_dir+fig_name)
	plt.close()

#generate figure showing cores vs memory consumption
def gen_mem_cores(mem_cores_use):
	plt.figure()
	plt.scatter([x[0] for x in mem_cores_use], [x[1] for x in mem_cores_use])
	plt.xlabel("Memory")
	plt.ylabel("Cores")
	plt.title("Memory-Core consumption")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"{}_mem_cores_use.png".format(dataset))
	plt.close()

#generate figure showing average cores vs memory consumption
def gen_mem_average_cores(mem_average_cores_use):
	plt.figure()
	plt.scatter([x[0] for x in mem_average_cores_use], [x[1] for x in mem_average_cores_use])
	plt.xlabel("Memory")
	plt.ylabel("load average cores")
	plt.title("Memory-average-core consumption")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"{}_mem_average_cores_use.png".format(dataset))
	plt.close()

chrono_cores_use = []
chrono_disk_use = []
chrono_mem_use = []
chrono_time_use = []
mem_cores_use = []
mem_average_cores_use = []
print("Reading..")

dataset=sys.argv[1]

level = 'lv2'

plots_dir = "resources_analysis/{}/{}/plots/".format(level, dataset)

data_dir = "resources_data/{}/{}/data/".format(level, dataset)

typ = {}
#read in data
with open(data_dir+"resources_all.txt", "r") as f:
	Lines = f.readlines()
	for line in Lines[1:]:
		resource = line.split(" -- ")
		resource[6] = resource[6].split("\n")[0]
		task_id = int(resource[0])
		core = int(resource[1])
		mem = int(resource[2])
		virt_mem = int(resource[3])
		disk = int(resource[4])
		time = round(float(resource[5]), 5)
		average_cores = round(float(resource[6]), 2)
		task_type = resource[7]
		chrono_cores_use.append(core)
		chrono_mem_use.append(mem)
		chrono_disk_use.append(disk)
		chrono_time_use.append(time)
		mem_cores_use.append([mem, core])
		mem_average_cores_use.append([mem, average_cores])
		if task_type not in typ:
			typ[task_type] = 1
		else:
			typ[task_type] += 1

print(typ)
#generate figures	
gen_chronos(chrono_cores_use, "time flow", "cores", "Cores consumption over time", "{}_chrono_cores.png".format(dataset))
gen_chronos(chrono_mem_use, "time flow", "memory (MBs)", "Memory consumption over time", "{}_chrono_mem.png".format(dataset))
gen_chronos(chrono_disk_use, "time flow", "disk (MBs)", "Disk consumption over time", "{}_chrono_disk.png".format(dataset))
gen_chronos(chrono_time_use, "time flow", "execution time (s)", "Execution time over time", "{}_chrono_time.png".format(dataset))
gen_dists(chrono_cores_use, "tasks in sorted order", "cores", "Cores consumption distribution", "{}_dist_cores.png".format(dataset))
gen_dists(chrono_mem_use, "tasks in sorted order", "memory (MBs)", "Memory consumption distribution", "{}_dist_mem.png".format(dataset))
gen_dists(chrono_disk_use, "tasks in sorted order", "disk (MBs)", "Disk consumption distribution", "{}_dist_disk.png".format(dataset))
gen_dists(chrono_time_use, "tasks in sorted order", "execution time (s)", "Execution time distribution", "{}_dist_time.png".format(dataset))
gen_mem_cores(mem_cores_use)
gen_mem_average_cores(mem_average_cores_use)
gen_upper_bound(chrono_mem_use, "tasks in sorted order", "memory (MBs)", "Workflow Efficiency", "{}_upper_bound_mem_whole_machine.png".format(dataset))
