#This file generates plots of resources consumption of colmena tasks

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
	plt.figure()
	plt.scatter([1,2,3], cpu_count)
	plt.xlabel("cores")
	plt.ylabel("count")
	plt.title("Cores count")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"cpu_count.png")
	plt.close()

#generate figure that shows distribution of disk consumption
def gen_disk(disk_use):
	plt.figure()
	disk_use = disk_use.items()
	plt.scatter([pair[0] for pair in disk_use], [pair[1] for pair in disk_use])
	plt.xlabel("disk")
	plt.ylabel("count")
	plt.title("Disk usage")
	plt.ylim(ymin=0)
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
def gen_chrono_mem(task_id_list, chrono_mem_use):
	plt.figure()
	plt.scatter([str(x) for x in task_id_list], [chrono_mem_use[x-1] for x in task_id_list])
	plt.xlabel("Task complete in time")
	plt.ylabel("Memory")
	plt.title("Chronological Memory Usage over time")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"chrono_mem_use.png")
	plt.close()

#generate figure showing cores consumption over time as tasks complete
def gen_chrono_cores(task_id_list, chrono_cores_use):
	plt.figure()
	plt.scatter([str(x) for x in task_id_list], [chrono_cores_use[x-1] for x in task_id_list])
	plt.xlabel("Task complete in time")
	plt.ylabel("Cores")
	plt.title("Chronological Core Usage over time")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"chrono_cores_use.png")
	plt.close()

#generate figure showing average cores consumption over time as tasks complete
def gen_chrono_average_cores(task_id_list, chrono_average_cores_use):
	plt.figure()
	plt.scatter([str(x) for x in task_id_list], [chrono_average_cores_use[x-1] for x in task_id_list])
	plt.xlabel("Task complete in time")
	plt.ylabel("Average cores")
	plt.title("Chronological load average core usage")
	plt.ylim(ymin=0)
	plt.savefig(plots_dir+"chrono_average_cores_use.png")
	plt.close()

cpu_count = [0,0,0]
disk_use = {}
mem_use = []
mem_cores_use = []
mem_average_cores_use = []
chrono_mem_use = [0]*228
chrono_cores_use = [0]*228
chrono_average_cores_use = [0]*228
print("Reading..")
task_id_list = []

plots_dir = "resources_analysis/colmena/plots/"

#read in data
with open("resources_all.txt", "r") as f:
	Lines = f.readlines()
	for line in Lines[1:]:
		resource = line.split(" -- ")
		resource[5] = resource[5].split("\n")[0]
		task_id = int(resource[0])
		core = int(resource[1])
		cpu_count[core-1] += 1
		mem = int(resource[2])
		mem_use.append(mem)
		virt_mem = int(resource[3])
		disk = int(resource[4])
		average_cores = round(float(resource[6]), 2)
		if disk in disk_use:
			disk_use[disk] += 1
		else:
			disk_use[disk] = 1
		time = round(float(resource[5]), 2)
		mem_cores_use.append([mem, core])
		mem_average_cores_use.append([mem, average_cores])
		try:
			chrono_mem_use[task_id-1] = mem
		except:
			print(task_id)
		chrono_cores_use[task_id-1] = core
		chrono_average_cores_use[task_id-1] = average_cores
		task_id_list.append(task_id)

#generate figures	
gen_cpu(cpu_count)
gen_disk(disk_use)
gen_mem(mem_use)
gen_mem_cores(mem_cores_use)
gen_chrono_mem(task_id_list, chrono_mem_use)
gen_chrono_cores(task_id_list, chrono_cores_use)
gen_chrono_average_cores(task_id_list, chrono_average_cores_use)
gen_mem_average_cores(mem_average_cores_use)
