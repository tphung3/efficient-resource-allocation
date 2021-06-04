#This file generates plots of resources consumption of tasks
import sys

print("Start plotting")
import matplotlib.pyplot as plt

#generate figure that shows resource usage over time
def gen_chronos(chrono_resource_use, xlabel, ylabel, title, fig_name):
	plt.figure()
	plt.scatter([i for i in range(len(chrono_resource_use))], chrono_resource_use)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.ylim(ymin=0)
	plt.tick_params(axis='x', which='both', bottom=False, top=False)
	plt.savefig(plots_dir+fig_name)
	plt.close()

#generate figure that shows resource distribution
def gen_dists(chrono_resource_use, xlabel, ylabel, title, fig_name):
	chrono_resource_use.sort()
	plt.figure()
	plt.scatter([i for i in range(len(chrono_resource_use))], chrono_resource_use)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)
	plt.ylim(ymin=0)
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
	plt.savefig(plots_dir+"mem_cores_use.png")
	plt.close()

#generate figure showing average cores vs memory consumption
def gen_mem_average_cores(mem_average_cores_use):
	plt.figure()
	plt.scatter([x[0] for x in mem_average_cores_use], [x[1] for x in mem_average_cores_use])
	plt.xlabel("Memory")
	plt.ylabel("load average cores")
	plt.title("Memory-average-core consumption")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"mem_average_cores_use.png")
	plt.close()

chrono_cores_use = []
chrono_disk_use = []
chrono_mem_use = []
mem_cores_use = []
mem_average_cores_use = []
print("Reading..")

dataset=sys.argv[1]

level = 'lv2'

plots_dir = "resources_analysis/{}/{}/plots/".format(level, dataset)

data_dir = "resources_data/{}/{}/data/".format(level, dataset)

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
		time = round(float(resource[5]), 2)
		average_cores = round(float(resource[6]), 2)
		chrono_cores_use.append(core)
		chrono_mem_use.append(mem)
		chrono_disk_use.append(disk)
		mem_cores_use.append([mem, core])
		mem_average_cores_use.append([mem, average_cores])
		

#generate figures	
gen_chronos(chrono_cores_use, "time", "cores", "Cores usage over time", "chrono_cores.png")
gen_chronos(chrono_mem_use, "time", "mem", "Mem usage over time", "chrono_mem.png")
gen_chronos(chrono_disk_use, "time", "disk", "Disk usage over time", "chrono_disk.png")
gen_dists(chrono_cores_use, "tasks in sorted order", "cores", "Cores usage distribution", "dist_cores.png")
gen_dists(chrono_mem_use, "tasks in sorted order", "mem", "Mem usage distribution", "dist_mem.png")
gen_dists(chrono_disk_use, "tasks in sorted order", "disk", "Disk usage distribution", "dist_disk.png")
gen_mem_cores(mem_cores_use)
gen_mem_average_cores(mem_average_cores_use)
