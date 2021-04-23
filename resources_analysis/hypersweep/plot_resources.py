#This file generates plots of resources consumption of hypersweep tasks

print("Start")
import matplotlib.pyplot as plt

#generate figure with x and y values as arguments
def gen_fig(plot_sth, resource_type, hyp):
	print(hyp+resource_type)
	x_axis = []
	y_axis = []
	plot_sth.sort(key=lambda x : x[0])
	for point in plot_sth:
		x_axis.append(point[0])
		y_axis.append(point[1])
	plt.figure()
	plt.scatter(x_axis, y_axis)
	plt.xlabel(hyp)
	plt.ylabel(resource_type)
	plt.ylim(ymin=0)
	plt.savefig(hyp+"_"+resource_type+".png")
	plt.close()

#generate figure that shows distribution of cores consumption
def gen_cpu(cpu_count):
	cpu_x = []
	cpu_y = []
	for item in cpu_count.items():
		cpu_x.append(item[0])
		cpu_y.append(item[1])
	plt.figure()
	plt.scatter(cpu_x, cpu_y)
	plt.xlabel("cores")
	plt.ylabel("count")
	plt.title("Cores count")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"cpu_count.png")
	plt.close()

#generate figure that shows disk consumption over time
def gen_disk(disk_use):
	plt.figure()
	plt.scatter([i for i in range(len(disk_use))], disk_use)
	plt.xlabel("Time")
	plt.ylabel("Disk consumption (MB)")
	plt.title("Disk consumption over time")
	plt.ylim(ymin=0)
	plt.tick_params(axis='x', which='both', bottom=False, top=False)
	plt.savefig(plots_dir+"disk_use.png")
	plt.close()

#generate figure showing memory consumption in sorted order
def gen_mem(mem_use):
	mem_use.sort()
	plt.figure()
	plt.plot([x for x in range(len(mem_use))], mem_use)
	plt.xlabel("Task")
	plt.ylabel("Memory")
	plt.title("Memory usage")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"mem_use.png")
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

#generate figure showing memory consumption over time as tasks complete
def gen_chrono_mem(mem_use):
	plt.figure()
	plt.scatter([x for x in range(len(mem_use))], mem_use)
	plt.xlabel("Task complete in time")
	plt.ylabel("Memory")
	plt.title("Chronological Memory Usage")
	plt.ylim(ymin=0)
	plt.tick_params(axis='x', which='both', bottom=False, top=False)
	plt.savefig(plots_dir+"chrono_mem_use.png")
	plt.close()

#generate figure showing cores consumption over time as tasks complete
def gen_chrono_cores(chrono_cores_use):
	plt.figure()
	plt.scatter([x for x in range(len(chrono_cores_use))], chrono_cores_use)
	plt.xlabel("Task complete in time")
	plt.ylabel("Cores")
	plt.title("Chronological Core Usage")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"chrono_cores_use.png")
	plt.close()

#generate figure showing average cores consumption over time as tasks complete
def gen_chrono_average_cores(chrono_average_cores_use):
	plt.figure()
	plt.scatter([x for x in range(len(chrono_average_cores_use))], chrono_average_cores_use)
	plt.xlabel("Task complete in time")
	plt.ylabel("Average cores")
	plt.title("Chronological load average core usage")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"chrono_average_cores_use.png")
	plt.close()

cpu_count = {}
disk_use = []
mem_use = []
mem_cores_use = []
mem_average_cores_use = []
chrono_cores_use = []
chrono_average_cores_use = []
print("Reading..")

plots_dir = "resources_analysis/hypersweep/plots/"

#read in data
with open("resources_analysis/hypersweep/resources_all.txt", "r") as f:
	Lines = f.readlines()
	for line in Lines[1:]:
		resource = line.split(" -- ")
		resource[5] = resource[5].split("\n")[0]
		task_id = int(resource[0])
		core = int(resource[1])
		if core in cpu_count:
			cpu_count[core] += 1
		else:
			cpu_count[core] = 1
		mem = int(resource[2])
		mem_use.append(mem)
		virt_mem = int(resource[3])
		disk = int(resource[4])
		average_cores = round(float(resource[6]), 2)
		disk_use.append(disk)
		time = round(float(resource[5]), 2)
		mem_cores_use.append([mem, core])
		mem_average_cores_use.append([mem, average_cores])
		chrono_cores_use.append(core)
		chrono_average_cores_use.append(average_cores)

#generate figures	
gen_cpu(cpu_count)
gen_disk(disk_use)
gen_mem(mem_use)
gen_mem_cores(mem_cores_use)
gen_chrono_mem(mem_use)
gen_chrono_cores(chrono_cores_use)
gen_chrono_average_cores(chrono_average_cores_use)
gen_mem_average_cores(mem_average_cores_use)
