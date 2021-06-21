#This file defines the strategies to allocate resources to tasks and evaluates them on different metrics.

import math
import csv
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import copy
from textwrap import wrap

#dictionary to store statistics of each strategy
stats = {"num_tasks": 0, 
		 "total_cores_t": 0, "avg_total_cores_t": 0, "no_cold_total_cores_t": 0,
		 "wcores_t": 0, "no_cold_wcores_t": 0, "avg_wcores_t": 0, "wfail_alloc_core_t": 0,
		 "avg_wfail_alloc_core_t": 0, "int_frag_core_t": 0, "avg_int_frag_core_t": 0, 
		 "cores_t_efficiency": 0, "no_cold_cores_t_effi": 0, "avg_cores_t_efficiency": 0,
		 "total_mem_t": 0, "avg_total_mem_t": 0, "no_cold_total_mem_t": 0,
		 "wmem_t": 0, "no_cold_wmem_t": 0, "avg_wmem_t": 0, "wfail_alloc_mem_t": 0,
		 "avg_wfail_alloc_mem_t": 0, "int_frag_mem_t": 0, "avg_int_frag_mem_t": 0, 
		 "mem_t_efficiency": 0, "no_cold_mem_t_effi": 0, "avg_mem_t_efficiency": 0,
		 "total_disk_t": 0, "avg_total_disk_t": 0, "no_cold_total_disk_t": 0,
		 "wdisk_t": 0, "no_cold_wdisk_t": 0, "avg_wdisk_t": 0, "wfail_alloc_disk_t": 0,
		 "avg_wfail_alloc_disk_t": 0, "int_frag_disk_t": 0, "avg_int_frag_disk_t": 0, 
		 "disk_t_efficiency": 0, "no_cold_disk_t_effi": 0, "avg_disk_t_efficiency": 0,
		 "num_retries": 0, "num_retries_bucket": 0, "num_retries_machine": 0,
		 "total_run_time": 0, "avg_run_time": 0}

#array of statistics that is convertible to spreadsheets
csv_arr = []

#each machine is assumed to have 16 cores, 128GB of RAM and disk. This is not always true but used still for the purpose of evaluation
mach_capa = [16, 128000, 128000]

#This is used in the declared_resources strategy, and this is a pretty good guess (for colmena dataset only) that has no fails due to under-allocation.
def_res = [4, 40000, 10]

#get name of dataset
dataset = sys.argv[1]

#level of information
level = 'lv2'

#input file of resources_consumption
res_file = "resources_data/{}/{}/data/resources_all.txt".format(level, dataset)

#output csv file
csv_file = "resources_analysis/{}/{}/results/strategies_evaluation.csv".format(level, dataset)

#plots go here
plot_dir = "resources_analysis/{}/{}/plots/".format(level, dataset)

#maximum number of tasks to process
max_num_tasks = -1

#initialize the list to store results in a spreadsheet
def init_csv_arr(csv_arr):
	csv_arr = [[''], ['#buckets'], ['# cold starts'], ['diagonal?']]
	for key in stats:
		csv_arr.append([key])
	return csv_arr

#reset the dictionary of statistics at the beginning of each strategy
def reset_stats(stats):
	for key in stats:
		stats[key] = 0

#read in tasks' resources consumption
def get_tasks_resources(file_name):
	all_res = []
	global max_num_tasks
	if dataset == 'hypersweep':
		max_num_tasks = 2000
	with open(file_name, 'r') as f:
		Lines = f.readlines()
		for line in Lines[1:max_num_tasks]:
			resource = line.split(" -- ")
			tid = int(resource[0])
			core = int(resource[1])
			mem = int(resource[2])
			disk = int(resource[4])
			time = round(float(resource[5]), 5)
			tag = int(resource[7])
			all_res.append([core, mem, disk, time, tag])
	return all_res

def update_aver_res_effi(resource_name, all_tasks_resource_t_allocated, all_tasks_resource_t_used):
	all_effi = [all_tasks_resource_t_used[i]/all_tasks_resource_t_allocated[i] for i in range(len(all_tasks_resource_t_allocated))]
	stats['avg_{}_t_efficiency'] = np.average(all_effi)	

def plot_effi_dists(strat_name, resource_name, all_tasks_resource_t_allocated, all_tasks_resource_t_used):
	all_effi = [all_tasks_resource_t_used[i]/all_tasks_resource_t_allocated[i] for i in range(len(all_tasks_resource_t_allocated))]
	avg_effi = np.average(all_effi)
	std_effi = np.std(all_effi)
	max_effi = np.amax(all_effi)
	min_effi = np.amin(all_effi)
	plt.plot([i for i in range(len(all_tasks_resource_t_allocated))], all_effi)
	plt.xlabel("Tasks' completion over time")
	plt.ylabel("Level of efficiency")
	plt.title('\n'.join(wrap("Chronological efficiency - {} - {} - average effi.: {} - stan. dev.: {} - max effi.: {} - min effi. : {}".format(resource_name, strat_name, round(avg_effi, 3), round(std_effi, 3), round(max_effi, 3), round(min_effi, 3)), 50)))
	plt.ylim(bottom=0, top=1)
	plt.savefig(plot_dir+"effi_dist_chrono_{}_{}".format(resource_name, strat_name))
	plt.close()
	all_effi.sort()
	plt.plot([i for i in range(len(all_tasks_resource_t_allocated))], all_effi)
	plt.xlabel("Tasks' sorted by efficiency level")
	plt.ylabel("Efficiency level")
	plt.title('\n'.join(wrap("Efficiency - {} - {} - average effi.: {} - stan. dev.: {} - max effi.: {} - min effi. : {}".format(resource_name, strat_name, round(avg_effi, 3), round(std_effi, 3), round(max_effi, 3), round(min_effi, 3)), 50)))
	plt.ylim(bottom=0, top=1)
	plt.savefig(plot_dir+"effi_dist_{}_{}".format(resource_name, strat_name))
	plt.close()

#Whole machine strategy: each task is allocated a whole machine with capacity defined above
def whole_machine(all_resources, machine, bool_plot_effi):
	reset_stats(stats)
	mcore = machine[0]
	mmem = machine[1]
	mdisk = machine[2]
	all_tasks_cores_t_allocated = []
	all_tasks_mem_t_allocated = []
	all_tasks_disk_t_allocated = []
	all_tasks_cores_t_used = []
	all_tasks_mem_t_used = []
	all_tasks_disk_t_used = []
	for task_res in all_resources:
		tcore = task_res[0]
		tmem = task_res[1]
		tdisk = task_res[2]
		ttime = task_res[3]
		stats["wcores_t"] += (mcore - tcore)*ttime
		stats["wmem_t"] += (mmem - tmem)*ttime
		stats["wdisk_t"] += (mdisk - tdisk)*ttime
		stats["num_tasks"] += 1
		stats["total_run_time"] += ttime
		stats["int_frag_core_t"] += (mcore - tcore)*ttime
		stats["int_frag_mem_t"] += (mmem - tmem)*ttime
		stats["int_frag_disk_t"] += (mdisk - tdisk)*ttime
		stats["total_cores_t"] += mcore*ttime
		stats["total_mem_t"] += mmem*ttime
		stats["total_disk_t"] += mdisk*ttime
		all_tasks_cores_t_allocated.append(mcore*ttime)
		all_tasks_mem_t_allocated.append(mmem*ttime)
		all_tasks_disk_t_allocated.append(mdisk*ttime)
		all_tasks_cores_t_used.append(tcore*ttime)
		all_tasks_mem_t_used.append(tmem*ttime)
		all_tasks_disk_t_used.append(tdisk*ttime)
	stats["avg_total_cores_t"] = stats["total_cores_t"]/stats["num_tasks"]
	stats["avg_total_mem_t"] = stats["total_mem_t"]/stats["num_tasks"]
	stats["avg_total_disk_t"] = stats["total_disk_t"]/stats["num_tasks"]
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]
	stats["cores_t_efficiency"] = 1 - stats["wcores_t"]/stats["total_cores_t"]
	stats["mem_t_efficiency"] = 1 - stats["wmem_t"]/stats["total_mem_t"]
	stats["disk_t_efficiency"] = 1 - stats["wdisk_t"]/stats["total_disk_t"]
	all_effi_cores = [all_tasks_cores_t_used[i]/all_tasks_cores_t_allocated[i] for i in range(len(all_tasks_cores_t_allocated))]
	stats['avg_cores_t_efficiency'] = np.average(all_effi_cores)
	all_effi_mem = [all_tasks_mem_t_used[i]/all_tasks_mem_t_allocated[i] for i in range(len(all_tasks_mem_t_allocated))]
	stats['avg_mem_t_efficiency'] = np.average(all_effi_mem)
	all_effi_disk = [all_tasks_disk_t_used[i]/all_tasks_disk_t_allocated[i] for i in range(len(all_tasks_disk_t_allocated))]
	stats['avg_disk_t_efficiency'] = np.average(all_effi_disk)
	if bool_plot_effi == 1:
		plot_effi_dists("whole_machine", "cores", all_tasks_cores_t_allocated, all_tasks_cores_t_used)
		plot_effi_dists("whole_machine", "mem", all_tasks_mem_t_allocated, all_tasks_mem_t_used)
		plot_effi_dists("whole_machine", "disk", all_tasks_disk_t_allocated, all_tasks_disk_t_used)
	
	"""#print out results/statistics of this strategy
	rept = "Report for whole machine strat:\n"
	for stat, value in stats.items():
		rept += " {}: {}\n".format(stat, value)
	print(rept)"""

#Boxing machine strategy: each task is allocated with boxes of machines in increasing order (e.g, [1/8, 1/4, 1/2, 1])
def boxing_machine(all_resources, machine, list_portions, bool_plot_effi):
	reset_stats(stats)
	mcore = machine[0]
	mmem = machine[1]
	mdisk = machine[2]
	all_tasks_cores_t_allocated = []
	all_tasks_mem_t_allocated = []
	all_tasks_disk_t_allocated = []
	all_tasks_cores_t_used = []
	all_tasks_mem_t_used = []
	all_tasks_disk_t_used = []
	for task_res in all_resources:
		tcore = task_res[0]
		tmem = task_res[1]
		tdisk = task_res[2]
		ttime = task_res[3]
		task_cores_t_allocated = 0
		task_mem_t_allocated = 0
		task_disk_t_allocated = 0
		task_cores_t_used = 0
		task_mem_t_used = 0
		task_disk_t_used = 0
		for i in range(len(list_portions)):
			portion = list_portions[i]
			pcore = portion*mcore
			pmem = portion*mmem
			pdisk = portion*mdisk
			task_cores_t_allocated += pcore*ttime
			task_mem_t_allocated += pmem*ttime
			task_disk_t_allocated += pdisk*ttime
			if (pcore < tcore or pmem < tmem or pdisk < tdisk):
				stats["total_cores_t"] += pcore*ttime		
				stats["total_mem_t"] += pmem*ttime		
				stats["total_disk_t"] += pdisk*ttime
				stats["wcores_t"] += pcore*ttime		
				stats["wmem_t"] += pmem*ttime		
				stats["wdisk_t"] += pdisk*ttime	
				stats["wfail_alloc_core_t"] += pcore*ttime	
				stats["wfail_alloc_mem_t"] += pmem*ttime	
				stats["wfail_alloc_disk_t"] += pdisk*ttime	
				stats["num_retries"] += 1
				if i == len(list_portions) - 2:
					stats["num_retries_machine"] += 1
				else:
					stats["num_retries_bucket"] += 1
				stats["total_run_time"] += ttime
			else:
				stats["total_cores_t"] += pcore*ttime		
				stats["total_mem_t"] += pmem*ttime		
				stats["total_disk_t"] += pdisk*ttime
				stats["wcores_t"] += (pcore-tcore)*ttime		
				stats["wmem_t"] += (pmem-tmem)*ttime		
				stats["wdisk_t"] += (pdisk-tdisk)*ttime	
				stats["int_frag_core_t"] += (pcore-tcore)*ttime	
				stats["int_frag_mem_t"] += (pmem-tmem)*ttime	
				stats["int_frag_disk_t"] += (pdisk-tdisk)*ttime	
				stats["total_run_time"] += ttime
				task_cores_t_used = tcore*ttime
				task_mem_t_used = tmem*ttime
				task_disk_t_used = tdisk*ttime
				break
		all_tasks_cores_t_allocated.append(task_cores_t_allocated)
		all_tasks_mem_t_allocated.append(task_mem_t_allocated)
		all_tasks_disk_t_allocated.append(task_disk_t_allocated)
		all_tasks_cores_t_used.append(task_cores_t_used)
		all_tasks_mem_t_used.append(task_mem_t_used)
		all_tasks_disk_t_used.append(task_disk_t_used)
		stats["num_tasks"] += 1	
	stats["avg_total_cores_t"] = stats["total_cores_t"]/stats["num_tasks"]
	stats["avg_total_mem_t"] = stats["total_mem_t"]/stats["num_tasks"]
	stats["avg_total_disk_t"] = stats["total_disk_t"]/stats["num_tasks"]
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_core_t"] = stats["wfail_alloc_core_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_mem_t"] = stats["wfail_alloc_mem_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_disk_t"] = stats["wfail_alloc_disk_t"]/stats["num_tasks"]
	stats["cores_t_efficiency"] = 1 - stats["wcores_t"]/stats["total_cores_t"]
	stats["mem_t_efficiency"] = 1 - stats["wmem_t"]/stats["total_mem_t"]
	stats["disk_t_efficiency"] = 1 - stats["wdisk_t"]/stats["total_disk_t"]
	all_effi_cores = [all_tasks_cores_t_used[i]/all_tasks_cores_t_allocated[i] for i in range(len(all_tasks_cores_t_allocated))]
	stats['avg_cores_t_efficiency'] = np.average(all_effi_cores)
	all_effi_mem = [all_tasks_mem_t_used[i]/all_tasks_mem_t_allocated[i] for i in range(len(all_tasks_mem_t_allocated))]
	stats['avg_mem_t_efficiency'] = np.average(all_effi_mem)
	all_effi_disk = [all_tasks_disk_t_used[i]/all_tasks_disk_t_allocated[i] for i in range(len(all_tasks_disk_t_allocated))]
	stats['avg_disk_t_efficiency'] = np.average(all_effi_disk)
	if bool_plot_effi == 1:
		plot_effi_dists("boxing_machine", "cores", all_tasks_cores_t_allocated, all_tasks_cores_t_used)
		plot_effi_dists("boxing_machine", "mem", all_tasks_mem_t_allocated, all_tasks_mem_t_used)
		plot_effi_dists("boxing_machine", "disk", all_tasks_disk_t_allocated, all_tasks_disk_t_used)

	
#declare resources strategy: each task is allocated by a manually declared amount of resources. This amount is also defined above.
def declare_resources(all_resources, default_resources, machine_resources, bool_plot_effi):
	reset_stats(stats)
	dcore = default_resources[0]
	dmem = default_resources[1]
	ddisk = default_resources[2]
	mcore = machine_resources[0]
	mmem = machine_resources[1]
	mdisk = machine_resources[2]	
	
	all_tasks_cores_t_allocated = []
	all_tasks_mem_t_allocated = []
	all_tasks_disk_t_allocated = []
	all_tasks_cores_t_used = []
	all_tasks_mem_t_used = []
	all_tasks_disk_t_used = []

	for task_res in all_resources:
		tcore, tmem, tdisk, ttime, ttag = task_res
		fail = tcore > dcore or tmem > dmem or tdisk > ddisk
		task_cores_t_allocated = 0
		task_mem_t_allocated = 0
		task_disk_t_allocated = 0
		task_cores_t_used = 0
		task_mem_t_used = 0
		task_disk_t_used = 0
		stats["wcores_t"] += (dcore+fail*mcore-tcore)*ttime
		stats["wmem_t"] += (dmem+fail*mmem-tmem)*ttime
		stats["wdisk_t"] += (ddisk+fail*mdisk-tdisk)*ttime
		stats["num_retries"] += fail*1
		stats["num_tasks"] += 1
		stats["total_run_time"] += ttime
		stats["int_frag_core_t"] += (dcore + fail*mcore - tcore)*ttime
		stats["int_frag_mem_t"] += (dmem + fail*mmem - tmem)*ttime
		stats["int_frag_disk_t"] += (ddisk + fail*mdisk - tdisk)*ttime
		stats["total_cores_t"] += (dcore+fail*mcore)*ttime
		stats["total_mem_t"] += (dmem+fail*mmem)*ttime
		stats["total_disk_t"] += (ddisk+fail*mdisk)*ttime
		task_cores_t_allocated = (dcore+fail*mcore)*ttime
		task_mem_t_allocated = (dmem+fail*mmem)*ttime
		task_disk_t_allocated = (ddisk+fail*mdisk)*ttime
		task_cores_t_used = tcore*ttime
		task_mem_t_used = tmem*ttime
		task_disk_t_used = tdisk*ttime
		all_tasks_cores_t_allocated.append(task_cores_t_allocated)
		all_tasks_mem_t_allocated.append(task_mem_t_allocated)
		all_tasks_disk_t_allocated.append(task_disk_t_allocated)
		all_tasks_cores_t_used.append(task_cores_t_used)
		all_tasks_mem_t_used.append(task_mem_t_used)
		all_tasks_disk_t_used.append(task_disk_t_used)
	stats["avg_total_cores_t"] = stats["total_cores_t"]/stats["num_tasks"]
	stats["avg_total_mem_t"] = stats["total_mem_t"]/stats["num_tasks"]
	stats["avg_total_disk_t"] = stats["total_disk_t"]/stats["num_tasks"]
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]
	stats["cores_t_efficiency"] = 1 - stats["wcores_t"]/stats["total_cores_t"]
	stats["mem_t_efficiency"] = 1 - stats["wmem_t"]/stats["total_mem_t"]
	stats["disk_t_efficiency"] = 1 - stats["wdisk_t"]/stats["total_disk_t"]	
	all_effi_cores = [all_tasks_cores_t_used[i]/all_tasks_cores_t_allocated[i] for i in range(len(all_tasks_cores_t_allocated))]
	stats['avg_cores_t_efficiency'] = np.average(all_effi_cores)
	all_effi_mem = [all_tasks_mem_t_used[i]/all_tasks_mem_t_allocated[i] for i in range(len(all_tasks_mem_t_allocated))]
	stats['avg_mem_t_efficiency'] = np.average(all_effi_mem)
	all_effi_disk = [all_tasks_disk_t_used[i]/all_tasks_disk_t_allocated[i] for i in range(len(all_tasks_disk_t_allocated))]
	stats['avg_disk_t_efficiency'] = np.average(all_effi_disk)
	if bool_plot_effi == 1:
		plot_effi_dists("declare_resources", "cores", all_tasks_cores_t_allocated, all_tasks_cores_t_used)
		plot_effi_dists("declare_resources", "mem", all_tasks_mem_t_allocated, all_tasks_mem_t_used)
		plot_effi_dists("declare_resources", "disk", all_tasks_disk_t_allocated, all_tasks_disk_t_used)

#slow increase strategy: Not implemented after a deep and careful thought about the potential of this strategy
def slow_increase(all_res, mach_capa):
	seed = max(all_mem[:10])
	all_waste = 0
	for i in range(len(all_mem[10:])):
		if all_mem[i] > seed:
			seed = all_mem[i]*rate
		else:
			all_waste += seed - all_mem[i]
	return [all_waste, all_waste/len(all_mem)]


#bucketing strategy: This strategy divides tasks into buckets and allocates tasks based on these buckets. Note: don't use this as it is not realistic and also buggy. Use cold_bucketing instead.
def bucketing(all_res, num_buckets):
	reset_stats(stats)
	all_cores = []
	all_mem = []
	all_disk = []
	all_time = []
	#sort resources to get buckets
	for task_res in all_res:
		all_cores.append(task_res[0])
		all_mem.append(task_res[1])
		all_disk.append(task_res[2])
		all_time.append(task_res[3])
	all_cores.sort()
	all_mem.sort()
	all_disk.sort()
	bucket_cores = [0]*(num_buckets)
	bucket_mem = [0]*(num_buckets)
	bucket_disk = [0]*(num_buckets)
	
	#forming buckets/delimiters
	for i in range(num_buckets):
		bucket_cores[i] = all_cores[(i+1)*(len(all_cores)-1)//num_buckets]
		bucket_mem[i] = all_mem[(i+1)*(len(all_mem)-1)//num_buckets]
		bucket_disk[i] = all_disk[(i+1)*(len(all_disk)-1)//num_buckets]
	print(bucket_cores)
	print(bucket_mem)
	print(bucket_disk)
	#get waste of each task
	for task_res in all_res:
		num_retries_task = 0
		task_waste_cores, task_waste_mem, task_waste_disk = 0, 0, 0
		task_wfail_alloc_core, task_wfail_alloc_mem, task_wfail_alloc_disk = 0, 0, 0
		task_int_frag_core, task_int_frag_mem, task_int_frag_disk = 0, 0, 0
		tcore, tmem, tdisk, ttime = task_res
		num_retries_task_core = 0
		cores_used = 0
		for mark in bucket_cores:
			if tcore > mark:
				num_retries_task_core += 1
				task_waste_cores += mark
			else:
				task_waste_cores += mark - tcore
				cores_used = mark
				break
		num_retries_task_mem = 0
		mem_used = 0
		for mark in bucket_mem:
			if tmem > mark:
				num_retries_task_mem += 1
				task_waste_mem += mark
			else:
				task_waste_mem += mark - tmem
				mem_used = mark
				break
		num_retries_task_disk = 0
		disk_used = 0
		for mark in bucket_disk:
			if tdisk > mark:
				num_retries_task_disk += 1
				task_waste_disk += mark
			else:
				task_waste_disk += mark - tdisk
				disk_used = mark
				break
		num_retries_task = max(num_retries_task_core, num_retries_task_mem, num_retries_task_disk)
		task_waste_cores += (num_retries_task - num_retries_task_core) * cores_used
		task_waste_mem += (num_retries_task - num_retries_task_mem) * mem_used
		task_waste_disk += (num_retries_task - num_retries_task_disk) * disk_us
		
		#update stats
		stats["wcores"] += task_waste_cores
		stats["wcores_t"] += task_waste_cores*num_retries_task*ttime
		stats["wmem"] += task_waste_mem
		stats["wmem_t"] += task_waste_mem*num_retries_task*ttime
		stats["wdisk"] += task_waste_disk
		stats["wdisk_t"] += task_waste_disk*num_retries_task*ttime
		stats["num_retries"] += num_retries_task
		stats["num_tasks"] += 1
		stats["total_run_time"] += ttime
	stats["avg_wcores"] = stats["wcores"]/stats["num_tasks"]
	stats["avg_wmem"] = stats["wmem"]/stats["num_tasks"]
	stats["avg_wdisk"] = stats["wdisk"]/stats["num_tasks"]
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	rept = "Report for bucketing with {} buckets strat:\n".format(num_buckets)
	for stat, value in stats.items():
	    rept += " {}: {}\n".format(stat, value)
	print(rept)

#plot buckets over time
def plot_buckets_over_time(strat_name, all_cores, all_mem, all_disk, all_tag, all_bucket_cores, all_bucket_mem, all_bucket_disk, num_buckets, plot_dir, num_cold_start):
	#plot memory
	plt.figure(figsize=(30,10))
	plt.scatter([i for i in range(len(all_mem))], all_mem, c=all_tag, label="Actual memory consumption")
	for j in range(num_buckets):
		plt.plot([i+num_cold_start for i in range(len(all_bucket_mem))], [all_bucket_mem[i][j] for i in range(len(all_bucket_mem))], label="Bucket {}".format(j+1))
	plt.legend(bbox_to_anchor=(1.02, 1))
	plt.title("Memory buckets over time - {}".format(strat_name))
	plt.savefig(plot_dir+"{}_mem_{}_buckets_over_time_{}_cold_starts.png".format(strat_name, num_buckets, num_cold_start))
	plt.close()
	
	#plot cores
	plt.figure(figsize=(30,10))
	plt.scatter([i for i in range(len(all_cores))], all_cores, c=all_tag, label="Actual memory consumption")
	for j in range(num_buckets):
		plt.plot([i+num_cold_start for i in range(len(all_bucket_cores))], [all_bucket_cores[i][j] for i in range(len(all_bucket_cores))], label="Bucket {}".format(j+1))
	plt.legend(bbox_to_anchor=(1.02, 1))
	plt.title("Cores buckets over time - {}".format(strat_name))
	plt.savefig(plot_dir+"{}_cores_{}_buckets_over_time_{}_cold_starts.png".format(strat_name, num_buckets, num_cold_start))
	plt.close()

	#plot disk
	plt.figure(figsize=(30,10))
	plt.scatter([i for i in range(len(all_disk))], all_disk, c=all_tag, label="Actual memory consumption")
	for j in range(num_buckets):
		plt.plot([i+num_cold_start for i in range(len(all_bucket_disk))], [all_bucket_disk[i][j] for i in range(len(all_bucket_disk))], label="Bucket {}".format(j+1))
	plt.legend(bbox_to_anchor=(1.02, 1))
	plt.title("Disk buckets over time - {}".format(strat_name))
	plt.savefig(plot_dir+"{}_disk_{}_buckets_over_time_{}_cold_starts.png".format(strat_name, num_buckets, num_cold_start))
	plt.close()

#generate plots to make movies
def plot_for_movies(strat_name, chro_cores, chro_mem, chro_disk, all_tag, all_bucket_cores, all_bucket_mem, all_bucket_disk, num_buckets, plot_dir, num_cold_start, num_movie, num_all_tasks, top):
	plt.figure(figsize=(30,10))
	plt.scatter([k for k in range(len(chro_mem))], chro_mem, c=all_tag, label="Actual memory consumption")
	plt.xlim(left=0, right=num_all_tasks)
	plt.ylim(top=top*1.05, bottom=0)
	if num_movie < num_cold_start:
		plt.savefig(plot_dir+"movie_000{}.png".format(num_movie))
		plt.close()
	else:	
		for j in range(num_buckets):
			plt.plot([k+num_cold_start for k in range(len(all_bucket_mem))], [all_bucket_mem[k][j] for k in range(len(all_bucket_mem))], label="Bucket {}".format(j+1))
			plt.legend(bbox_to_anchor=(1.02, 1))
			plt.title("Memory buckets over time - {}".format(strat_name))
			if num_movie < 10:
				plt.savefig(plot_dir+"movie_000{}.png".format(num_movie))
			elif num_movie < 100:	
				plt.savefig(plot_dir+"movie_00{}.png".format(num_movie))
			elif num_movie < 1000:
				plt.savefig(plot_dir+"movie_0{}.png".format(num_movie))
			else:	
				plt.savefig(plot_dir+"movie_{}.png".format(num_movie))
		plt.close()

#cold bucketing strategy: This strategy assumes that we have a resources log of completed tasks and allocates the remaining tasks based on this log. It divides the completed tasks into a number of equal-sized buckets (this number must be predefined) from 1 to n (assuming n buckets), with elements in bucket i always smaller than elements in bucket i+1. Then each task is allocated by the maximum element in each bucket in the increasing order (only retried if allocation fails). As we need a log of completed tasks (no completed tasks in the beginning/cold start problem), this log is achieved by running a number of tasks using whole machines. Finally, two ways of choosing buckets are implemented. Either we increase only the exceeded resources (diagonal=0) or we increase all resources/move to next buckets of all resources (diagonal=1).
def cold_bucketing(all_res, num_buckets, num_cold_start, mach_capa, diagonal, bool_plot, bool_plot_effi):
	
	#resetting stats
	reset_stats(stats)
	
	#list of records of completed tasks' resources over time
	chro_cores = []
	chro_mem = []
	chro_disk = []
	chro_time = []
	
	#list of records of completed tasks' resources
	all_cores = []
	all_mem = []
	all_disk = []
	all_time = []
	all_tag = []
	
	#list of buckets' upperbounds of completed tasks
	bucket_cores = [[0] for i in range(num_buckets)]
	bucket_mem = [[0] for i in range(num_buckets)]
	bucket_disk = [[0] for i in range(num_buckets)]	

	#list of all buckets over time
	all_bucket_cores = []
	all_bucket_mem = []
	all_bucket_disk = []

	#get machine specs
	mcore, mmem, mdisk = mach_capa

	#store individual task util level
	all_tasks_cores_t_allocated = []
	all_tasks_mem_t_allocated = []
	all_tasks_disk_t_allocated = []
	all_tasks_cores_t_used = []
	all_tasks_mem_t_used = []
	all_tasks_disk_t_used = []

	#loop for each task
	for i in range(len(all_res)):
		
		#get tasks' actual resources consumption
		task_res = all_res[i]
		
		#initialize variables tracking waste and number of retries
		num_retries_task = 0
		task_waste_cores, task_waste_mem, task_waste_disk = 0, 0, 0
		task_wfail_alloc_core, task_wfail_alloc_mem, task_wfail_alloc_disk = 0, 0, 0
		task_int_frag_core, task_int_frag_mem, task_int_frag_disk = 0, 0, 0
		task_num_retries_bucket, task_num_retries_machine = 0, 0		

		#get tasks' actual peak resources consumption
		tcore, tmem, tdisk, ttime, ttag = task_res
		chro_cores.append(tcore)
		chro_mem.append(tmem)
		chro_disk.append(tdisk)
		chro_time.append(ttime)
		
		task_cores_t_allocated = 0
		task_mem_t_allocated = 0
		task_disk_t_allocated = 0
		task_cores_t_used = 0
		task_mem_t_used = 0
		task_disk_t_used = 0
		
		#for cold start tasks
		if i < num_cold_start:

			#update with task using whole machine
			stats["wcores_t"] += (mcore - tcore)*ttime
			stats["wmem_t"] += (mmem - tmem)*ttime
			stats["wdisk_t"] += (mdisk-tdisk)*ttime
			stats["num_tasks"] += 1
			stats["total_run_time"] += ttime
			stats["num_retries"] += num_retries_task
			stats["int_frag_core_t"] += (mcore - tcore)*ttime		
			stats["int_frag_mem_t"] += (mmem - tmem)*ttime		
			stats["int_frag_disk_t"] += (mdisk - tdisk)*ttime		
			stats["total_cores_t"] += mcore*ttime			
			stats["total_mem_t"] += mmem*ttime			
			stats["total_disk_t"] += mdisk*ttime	
			task_cores_t_allocated = mcore*ttime		
			task_mem_t_allocated = mmem*ttime		
			task_disk_t_allocated = mdisk*ttime	
			task_cores_t_used = tcore*ttime	
			task_mem_t_used = tmem*ttime	
			task_disk_t_used = tdisk*ttime	
	
			#add to lists of records
			all_cores.append(tcore)
			all_mem.append(tmem)
			all_disk.append(tdisk)
			all_time.append(ttime)
			all_tag.append(ttag)
		else:
			
			#sort all lists of records
			all_cores.sort()				
			all_mem.sort()
			all_disk.sort()
			
			#forming buckets/delimiters
			for j in range(num_buckets):
				bucket_cores[j] = all_cores[math.floor((j+1)*(len(all_cores)-1)/num_buckets)]
				bucket_mem[j] = all_mem[math.floor((j+1)*(len(all_mem)-1)/num_buckets)]
				bucket_disk[j] = all_disk[math.floor((j+1)*(len(all_disk)-1)/num_buckets)]
			
			#add current bucket to chronological list of buckets
			all_bucket_cores.append(copy.deepcopy(bucket_cores))
			all_bucket_mem.append(copy.deepcopy(bucket_mem))
			all_bucket_disk.append(copy.deepcopy(bucket_disk))

			#get waste of this task
			#declare variables to track number of retries, etc.
			num_retries_task_core = 0
			num_retries_task_mem = 0
			num_retries_task_disk = 0
			cores_used = 0
			mem_used = 0
			disk_used = 0
					
			#loop for trying buckets in an increasing order
			if diagonal==1:
				for j in range(len(bucket_cores)):

					#get the upper bound of buckets
					mark_core = bucket_cores[j]
					mark_mem = bucket_mem[j]
					mark_disk = bucket_disk[j]

					#if upper bound is exceeded
					if tcore > mark_core or tmem > mark_mem or tdisk > mark_disk:
						num_retries_task += 1
						task_waste_cores += mark_core
						task_waste_mem += mark_mem
						task_waste_disk += mark_disk
						task_wfail_alloc_core += mark_core
						task_wfail_alloc_mem += mark_mem
						task_wfail_alloc_disk += mark_disk
						task_num_retries_bucket += 1
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core*ttime
						stats["no_cold_total_mem_t"] += mark_mem*ttime
						stats["no_cold_total_disk_t"] += mark_disk*ttime
						task_cores_t_allocated += mark_core*ttime 
						task_mem_t_allocated += mark_mem*ttime 
						task_disk_t_allocated += mark_disk*ttime 

						#if we are at the last bucket, must use whole machine
						if j == len(bucket_cores)-1:
							task_waste_cores += mcore-tcore
							task_waste_mem += mmem-tmem
							task_waste_disk += mdisk-tdisk
							cores_used = mcore
							mem_used = mmem
							disk_used = mdisk
							task_int_frag_core = mcore-tcore
							task_int_frag_mem = mmem-tmem
							task_int_frag_disk = mdisk-tdisk
							task_num_retries_machine += 1
							num_retries_task += 1
							stats["total_cores_t"] += mcore*ttime
							stats["total_mem_t"] += mmem*ttime
							stats["total_disk_t"] += mdisk*ttime	
							stats["no_cold_total_cores_t"] += mcore*ttime
							stats["no_cold_total_mem_t"] += mmem*ttime
							stats["no_cold_total_disk_t"] += mdisk*ttime
							task_cores_t_allocated += mcore*ttime 
							task_mem_t_allocated += mmem*ttime 
							task_disk_t_allocated += mdisk*ttime
							task_cores_t_used = tcore*ttime
							task_mem_t_used = tmem*ttime
							task_disk_t_used = tdisk*ttime

					#otherwise, successful resources allocation
					else:
						task_waste_cores += mark_core-tcore
						task_waste_mem += mark_mem-tmem
						task_waste_disk += mark_disk-tdisk
						cores_used = mark_core
						mem_used = mark_mem
						disk_used = mark_disk
						task_int_frag_core = mark_core-tcore
						task_int_frag_mem = mark_mem-tmem
						task_int_frag_disk = mark_disk-tdisk
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core * ttime
						stats["no_cold_total_mem_t"] += mark_mem * ttime
						stats["no_cold_total_disk_t"] += mark_disk * ttime
						task_cores_t_allocated += mark_core*ttime 
						task_mem_t_allocated += mark_mem*ttime 
						task_disk_t_allocated += mark_disk*ttime
						task_cores_t_used = tcore*ttime
						task_mem_t_used = tmem*ttime
						task_disk_t_used = tdisk*ttime
						break
			else:
				allocate_task_success = 0
				#index for cores, memory, and disk buckets to increment
				ci, mi, di = 0, 0, 0
				j = 0
				while allocate_task_success != 1:
		
					#get the upper bound of buckets
					mark_core = bucket_cores[ci]
					mark_mem = bucket_mem[mi]
					mark_disk = bucket_disk[di]

					#if upper bound is exceeded
					if tcore > mark_core or tmem > mark_mem or tdisk > mark_disk:
						#only increment index of whichever resource is exceeded
						if tcore > mark_core:
							ci += 1
						elif tmem > mark_mem:
							mi += 1
						elif tdisk > mark_disk:
							di += 1
						else:
							print("Error in cold bucketing strategy. Exiting...")
							exit(10)
						num_retries_task += 1
						task_waste_cores += mark_core
						task_waste_mem += mark_mem
						task_waste_disk += mark_disk
						task_wfail_alloc_core += mark_core
						task_wfail_alloc_mem += mark_mem
						task_wfail_alloc_disk += mark_disk
						task_num_retries_bucket += 1
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core*ttime				
						stats["no_cold_total_mem_t"] += mark_mem*ttime				
						stats["no_cold_total_disk_t"] += mark_disk*ttime				
						task_cores_t_allocated += mark_core*ttime 
						task_mem_t_allocated += mark_mem*ttime 
						task_disk_t_allocated += mark_disk*ttime

						#if we are at the last bucket of any type of resources, must use whole machine
						if ci == len(bucket_cores) or mi == len(bucket_mem) or di == len(bucket_disk):
							task_waste_cores += mcore-tcore
							task_waste_mem += mmem-tmem
							task_waste_disk += mdisk-tdisk
							cores_used = mcore
							mem_used = mmem
							disk_used = mdisk
							allocate_task_success = 1
							task_int_frag_core = mcore-tcore
							task_int_frag_mem = mmem-tmem
							task_int_frag_disk = mdisk-tdisk
							task_num_retries_machine += 1
							num_retries_task += 1
							stats["total_cores_t"] += mcore*ttime
							stats["total_mem_t"] += mmem*ttime
							stats["total_disk_t"] += mdisk*ttime
							stats["no_cold_total_cores_t"] += mcore*ttime
							stats["no_cold_total_mem_t"] += mmem*ttime
							stats["no_cold_total_disk_t"] += mdisk*ttime
							task_cores_t_allocated += mcore*ttime 
							task_mem_t_allocated += mmem*ttime 
							task_disk_t_allocated += mdisk*ttime
							task_cores_t_used = tcore*ttime
							task_mem_t_used = tmem*ttime
							task_disk_t_used = tdisk*ttime

					#otherwise
					else:
						task_waste_cores += mark_core-tcore
						task_waste_mem += mark_mem-tmem
						task_waste_disk += mark_disk-tdisk
						cores_used = mark_core
						mem_used = mark_mem
						disk_used = mark_disk
						allocate_task_success = 1
						task_int_frag_core = mark_core - tcore
						task_int_frag_mem = mark_mem - tmem
						task_int_frag_disk = mark_disk - tdisk
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core*ttime
						stats["no_cold_total_mem_t"] += mark_mem*ttime
						stats["no_cold_total_disk_t"] += mark_disk*ttime
						task_cores_t_allocated += mark_core*ttime 
						task_mem_t_allocated += mark_mem*ttime 
						task_disk_t_allocated += mark_disk*ttime
						task_cores_t_used = tcore*ttime
						task_mem_t_used = tmem*ttime
						task_disk_t_used = tdisk*ttime

			#update stats, assuming tasks fail at the end of their executions.
			stats["num_retries"] += num_retries_task
			stats["num_tasks"] += 1
			stats["total_run_time"] += (num_retries_task+1)*ttime			
			stats["wfail_alloc_core_t"] += task_wfail_alloc_core*ttime
			stats["wfail_alloc_mem_t"] += task_wfail_alloc_mem*ttime
			stats["wfail_alloc_disk_t"] += task_wfail_alloc_disk*ttime
			stats["int_frag_core_t"] += task_int_frag_core*ttime
			stats["int_frag_mem_t"] += task_int_frag_mem*ttime
			stats["int_frag_disk_t"] += task_int_frag_disk*ttime
			stats["num_retries_bucket"] += task_num_retries_bucket			
			stats["num_retries_machine"] += task_num_retries_machine
			stats["wcores_t"] += task_wfail_alloc_core*ttime + task_int_frag_core*ttime
			stats["wmem_t"] += task_wfail_alloc_mem*ttime + task_int_frag_mem*ttime
			stats["wdisk_t"] += task_wfail_alloc_disk*ttime + task_int_frag_disk*ttime
			stats["no_cold_wcores_t"] += task_wfail_alloc_core*ttime + task_int_frag_core*ttime
			stats["no_cold_wmem_t"] += task_wfail_alloc_mem*ttime + task_int_frag_mem*ttime
			stats["no_cold_wdisk_t"] += task_wfail_alloc_disk*ttime + task_int_frag_disk*ttime

			#add to list of records
			all_cores.append(tcore)
			all_mem.append(tmem)
			all_disk.append(tdisk)
			all_time.append(ttime)
			all_tag.append(ttag)
	
		all_tasks_cores_t_allocated.append(task_cores_t_allocated)
		all_tasks_mem_t_allocated.append(task_mem_t_allocated)
		all_tasks_disk_t_allocated.append(task_disk_t_allocated)
		all_tasks_cores_t_used.append(task_cores_t_used)
		all_tasks_mem_t_used.append(task_mem_t_used)
		all_tasks_disk_t_used.append(task_disk_t_used)

	stats["avg_total_cores_t"] = stats["total_cores_t"]/stats["num_tasks"]
	stats["avg_total_mem_t"] = stats["total_mem_t"]/stats["num_tasks"]
	stats["avg_total_disk_t"] = stats["total_disk_t"]/stats["num_tasks"]	
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_wfail_alloc_core_t"] = stats["wfail_alloc_core_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_mem_t"] = stats["wfail_alloc_mem_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_disk_t"] = stats["wfail_alloc_disk_t"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]
	stats["cores_t_efficiency"] = 1 - stats["wcores_t"]/stats["total_cores_t"]
	stats["mem_t_efficiency"] = 1 - stats["wmem_t"]/stats["total_mem_t"]
	stats["disk_t_efficiency"] = 1 - stats["wdisk_t"]/stats["total_disk_t"]
	stats["no_cold_cores_t_effi"] = 1 - stats["no_cold_wcores_t"]/stats["no_cold_total_cores_t"]
	stats["no_cold_mem_t_effi"] = 1 - stats["no_cold_wmem_t"]/stats["no_cold_total_mem_t"]
	stats["no_cold_disk_t_effi"] = 1 - stats["no_cold_wdisk_t"]/stats["no_cold_total_disk_t"]
	all_effi_cores = [all_tasks_cores_t_used[i]/all_tasks_cores_t_allocated[i] for i in range(len(all_tasks_cores_t_allocated))]
	stats['avg_cores_t_efficiency'] = np.average(all_effi_cores)
	all_effi_mem = [all_tasks_mem_t_used[i]/all_tasks_mem_t_allocated[i] for i in range(len(all_tasks_mem_t_allocated))]
	stats['avg_mem_t_efficiency'] = np.average(all_effi_mem)
	all_effi_disk = [all_tasks_disk_t_used[i]/all_tasks_disk_t_allocated[i] for i in range(len(all_tasks_disk_t_allocated))]
	stats['avg_disk_t_efficiency'] = np.average(all_effi_disk)	

	#plot the dynamics of buckets
	if bool_plot == 1:
		plot_buckets_over_time("cold_bucketing", chro_cores, chro_mem, chro_disk, all_tag, all_bucket_cores, all_bucket_mem, all_bucket_disk, num_buckets, plot_dir, num_cold_start)
	if bool_plot_effi == 1:
		plot_effi_dists("cold_bucketing_{}_{}_{}".format(num_buckets, num_cold_start, diagonal), "cores", all_tasks_cores_t_allocated, all_tasks_cores_t_used)
		plot_effi_dists("cold_bucketing_{}_{}_{}".format(num_buckets, num_cold_start, diagonal), "mem", all_tasks_mem_t_allocated, all_tasks_mem_t_used)
		plot_effi_dists("cold_bucketing_{}_{}_{}".format(num_buckets, num_cold_start, diagonal), "disk", all_tasks_disk_t_allocated, all_tasks_disk_t_used)

#k-means bucketing strategy: In this strategy, we will classify incoming tasks into buckets based on the means of elements of buckets, then we will recompute means of buckets for next iteration.
def k_means_bucketing(all_res, num_buckets, num_cold_start, mach_capa, diagonal, bool_plot, bool_movie, bool_plot_effi):

	#resetting stats
	reset_stats(stats)
	
	#list of records of completed tasks' resources over time
	chro_cores = []
	chro_mem = []
	chro_disk = []
	chro_time = []

	#list of records of completed tasks' resources
	all_cores = []
	all_mem = []
	all_disk = []
	all_time = []
	all_tag = []
	
	#list of buckets with all completed tasks
	bucket_cores = [[0] for i in range(num_buckets)]
	bucket_mem = [[0] for i in range(num_buckets)]
	bucket_disk = [[0] for i in range(num_buckets)]
	
	#list of all buckets over time
	all_bucket_cores = []
	all_bucket_mem = []
	all_bucket_disk = []

	#get machine specs
	mcore, mmem, mdisk = mach_capa
	
	#counter for movie
	num_movie = 0
	num_all_tasks = len(all_res)
	max_tmem = 0
	for i in range(len(all_res)):
		task_res = all_res[i]
		tmem = task_res[1]
		if max_tmem < tmem:
			max_tmem = tmem
	all_tasks_cores_t_allocated = []
	all_tasks_mem_t_allocated = []
	all_tasks_disk_t_allocated = []
	all_tasks_cores_t_used = []
	all_tasks_mem_t_used = []
	all_tasks_disk_t_used = []
	
	#loop for each task
	for i in range(len(all_res)):
		#get tasks' actual resources consumption
		task_res = all_res[i]
		
		#initialize variables tracking waste and number of retries
		num_retries_task = 0
		task_waste_cores, task_waste_mem, task_waste_disk = 0, 0, 0
		task_wfail_alloc_core, task_wfail_alloc_mem, task_wfail_alloc_disk = 0, 0, 0
		task_int_frag_core, task_int_frag_mem, task_int_frag_disk = 0, 0, 0
		task_num_retries_bucket, task_num_retries_machine = 0, 0		

		#get tasks' actual peak resources consumption
		tcore, tmem, tdisk, ttime, ttag = task_res

		chro_cores.append(tcore)
		chro_mem.append(tmem)
		chro_disk.append(tdisk)
		chro_time.append(ttime)		
	
		task_cores_t_allocated = 0
		task_mem_t_allocated = 0
		task_disk_t_allocated = 0
		task_cores_t_used = 0
		task_mem_t_used = 0
		task_disk_t_used = 0

		#for cold start tasks
		if i < num_cold_start:

			#update with task using whole machine
			stats["wcores_t"] += (mcore - tcore)*ttime
			stats["wmem_t"] += (mmem - tmem)*ttime
			stats["wdisk_t"] += (mdisk-tdisk)*ttime
			stats["num_tasks"] += 1
			stats["total_run_time"] += ttime
			stats["num_retries"] += num_retries_task
			stats["int_frag_core_t"] += (mcore - tcore)*ttime		
			stats["int_frag_mem_t"] += (mmem - tmem)*ttime		
			stats["int_frag_disk_t"] += (mdisk - tdisk)*ttime		
			stats["total_cores_t"] += mcore*ttime			
			stats["total_mem_t"] += mmem*ttime			
			stats["total_disk_t"] += mdisk*ttime			
			
			#add to lists of records
			all_cores.append(tcore)
			all_mem.append(tmem)
			all_disk.append(tdisk)
			all_time.append(ttime)
			all_tag.append(ttag)
	
			task_cores_t_allocated = mcore*ttime
			task_mem_t_allocated = mmem*ttime
			task_disk_t_allocated = mdisk*ttime
			task_cores_t_used = tcore*ttime
			task_mem_t_used = tmem*ttime
			task_disk_t_used = tdisk*ttime
			
			#if we are at last iteration of cold starts, initialize buckets
			if i == num_cold_start - 1:
				all_cores.sort()
				all_mem.sort()
				all_disk.sort()
				index = 0
				for j in range(num_buckets):
					bucket_cores[j] = all_cores[index:math.floor((j+1)*(len(all_cores)-1)/num_buckets) + 1]
					bucket_mem[j] = all_mem[index:math.floor((j+1)*(len(all_mem)-1)/num_buckets)+1]
					bucket_disk[j] = all_disk[index:math.floor((j+1)*(len(all_disk)-1)/num_buckets)+1]
					index = math.floor((j+1)*(len(all_cores)-1)/num_buckets) + 1
							
		else:

			#forming buckets
			bucket_cores_means = []
			bucket_mem_means = []
			bucket_disk_means = []	
			for j in range(num_buckets):
				bucket_cores_means.append(np.mean(bucket_cores[j]))
				bucket_mem_means.append(np.mean(bucket_mem[j]))
				bucket_disk_means.append(np.mean(bucket_disk[j]))	
		
			#reassign tasks' consumption to buckets
			bucket_cores = [[0] for i in range(num_buckets)]	
			bucket_mem = [[0] for i in range(num_buckets)]	
			bucket_disk = [[0] for i in range(num_buckets)]	
			for j in range(len(all_cores)):
				core = all_cores[j]
				mem = all_mem[j]
				disk = all_disk[j]
				#add core
				for k in range(num_buckets):
					if k == 0:
						if core <= bucket_cores_means[k]:
							bucket_cores[k].append(core)
							break
					if k == num_buckets-1:
						bucket_cores[k].append(core)
					elif abs(core-bucket_cores_means[k]) <= abs(core-bucket_cores_means[k+1]):
						bucket_cores[k].append(core)
						break

				#add mem
				for k in range(num_buckets):
					if k == 0:
						if mem <= bucket_mem_means[k]:
							bucket_mem[k].append(mem)
							break
					if k == num_buckets-1:
						bucket_mem[k].append(mem)
					elif abs(mem-bucket_mem_means[k]) <= abs(mem-bucket_mem_means[k+1]):
						bucket_mem[k].append(mem)
						break

					"""if k == num_buckets-1:
						bucket_mem[k].append(mem)
					elif abs(mem-bucket_mem_means[k]) < abs(mem-bucket_mem_means[k+1]):
						bucket_mem[k].append(mem)
						break
					elif abs(mem-bucket_mem_means[k]) == abs(mem-bucket_mem_means[k+1]):
						if len(bucket_mem[k]) == 1:
							bucket_mem[k].append(mem)
							break
						else:
							bucket_mem[k+1].append(mem)
							break"""
				#add disk
				for k in range(num_buckets):
					if k == 0:
						if disk <= bucket_disk_means[k]:
							bucket_disk[k].append(disk)
							break
					if k == num_buckets-1:
						bucket_disk[k].append(disk)
					elif abs(disk-bucket_disk_means[k]) <= abs(disk-bucket_disk_means[k+1]):
						bucket_disk[k].append(disk)
						break

			for j in range(num_buckets):
				bucket_cores[j] = bucket_cores[j][1:]
				bucket_mem[j] = bucket_mem[j][1:]
				bucket_disk[j] = bucket_disk[j][1:]
				
			#ensure no buckets are empty
			for j in range(num_buckets):			
				if len(bucket_cores[j]) == 0:
					if j == 0:
						bucket_cores[j].append(min(all_cores))
					else:
						bucket_cores[j].append(max(bucket_cores[j-1]))
				if len(bucket_mem[j]) == 0:
					if j == 0:
						bucket_mem[j].append(min(all_mem))
					else:
						bucket_mem[j].append(max(bucket_mem[j-1]))
				if len(bucket_disk[j]) == 0:
					if j == 0:
						bucket_disk[j].append(min(all_disk))
					else:
						bucket_disk[j].append(max(bucket_disk[j-1]))

			#add records for buckets over time
			temp_buckets = []
			for j in range(num_buckets):
				temp_buckets.append(max(bucket_cores[j]))
			all_bucket_cores.append(temp_buckets)
			temp_buckets = []
			for j in range(num_buckets):
				temp_buckets.append(max(bucket_mem[j]))
			all_bucket_mem.append(temp_buckets)
			temp_buckets = []
			for j in range(num_buckets):
				temp_buckets.append(max(bucket_disk[j]))
			all_bucket_disk.append(temp_buckets)

			#get waste of this task
			#declare variables to track number of retries, etc.
			num_retries_task_core = 0
			num_retries_task_mem = 0
			num_retries_task_disk = 0
			cores_used = 0
			mem_used = 0
			disk_used = 0
					
			#loop for trying buckets in an increasing order
			if diagonal==1:
				for j in range(len(bucket_cores)):

					#get the upper bound of buckets
					mark_core = max(bucket_cores[j])
					mark_mem = max(bucket_mem[j])
					mark_disk = max(bucket_disk[j])

					#if upper bound is exceeded
					if tcore > mark_core or tmem > mark_mem or tdisk > mark_disk:
						num_retries_task += 1
						task_waste_cores += mark_core
						task_waste_mem += mark_mem
						task_waste_disk += mark_disk
						task_wfail_alloc_core += mark_core
						task_wfail_alloc_mem += mark_mem
						task_wfail_alloc_disk += mark_disk
						task_num_retries_bucket += 1
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core*ttime
						stats["no_cold_total_mem_t"] += mark_mem*ttime
						stats["no_cold_total_disk_t"] += mark_disk*ttime
						task_cores_t_allocated += mark_core*ttime
						task_mem_t_allocated += mark_mem*ttime
						task_disk_t_allocated += mark_disk*ttime

						#if we are at the last bucket, must use whole machine
						if j == len(bucket_cores)-1:
							task_waste_cores += mcore-tcore
							task_waste_mem += mmem-tmem
							task_waste_disk += mdisk-tdisk
							cores_used = mcore
							mem_used = mmem
							disk_used = mdisk
							task_int_frag_core = mcore-tcore
							task_int_frag_mem = mmem-tmem
							task_int_frag_disk = mdisk-tdisk
							task_num_retries_machine += 1
							num_retries_task += 1
							stats["total_cores_t"] += mcore*ttime
							stats["total_mem_t"] += mmem*ttime
							stats["total_disk_t"] += mdisk*ttime	
							stats["no_cold_total_cores_t"] += mcore*ttime
							stats["no_cold_total_mem_t"] += mmem*ttime
							stats["no_cold_total_disk_t"] += mdisk*ttime
							task_cores_t_allocated += mcore*ttime
							task_mem_t_allocated += mmem*ttime
							task_disk_t_allocated += mdisk*ttime
							task_cores_t_used = tcore*ttime
							task_mem_t_used = tmem*ttime
							task_disk_t_used = tdisk*ttime


					#otherwise, successful resources allocation
					else:
						task_waste_cores += mark_core-tcore
						task_waste_mem += mark_mem-tmem
						task_waste_disk += mark_disk-tdisk
						cores_used = mark_core
						mem_used = mark_mem
						disk_used = mark_disk
						task_int_frag_core = mark_core-tcore
						task_int_frag_mem = mark_mem-tmem
						task_int_frag_disk = mark_disk-tdisk
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core*ttime
						stats["no_cold_total_mem_t"] += mark_mem*ttime
						stats["no_cold_total_disk_t"] += mark_disk*ttime
						task_cores_t_allocated += mark_core*ttime
						task_mem_t_allocated += mark_mem*ttime
						task_disk_t_allocated += mark_disk*ttime
						task_cores_t_used = tcore*ttime
						task_mem_t_used = tmem*ttime
						task_disk_t_used = tdisk*ttime
						break
			else:
				allocate_task_success = 0
				#index for cores, memory, and disk buckets to increment
				ci, mi, di = 0, 0, 0
				j = 0
				while allocate_task_success != 1:
		
					#get the upper bound of buckets
					mark_core = max(bucket_cores[ci])
					mark_mem = max(bucket_mem[mi])
					mark_disk = max(bucket_disk[di])

					#if upper bound is exceeded
					if tcore > mark_core or tmem > mark_mem or tdisk > mark_disk:
						#only increment index of whichever resource is exceeded
						if tcore > mark_core:
							ci += 1
						elif tmem > mark_mem:
							mi += 1
						elif tdisk > mark_disk:
							di += 1
						else:
							print("Error in cold bucketing strategy. Exiting...")
							exit(10)
						num_retries_task += 1
						task_waste_cores += mark_core
						task_waste_mem += mark_mem
						task_waste_disk += mark_disk
						task_wfail_alloc_core += mark_core
						task_wfail_alloc_mem += mark_mem
						task_wfail_alloc_disk += mark_disk
						task_num_retries_bucket += 1
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime	
						stats["no_cold_total_cores_t"] += mark_core*ttime			
						stats["no_cold_total_mem_t"] += mark_mem*ttime			
						stats["no_cold_total_disk_t"] += mark_disk*ttime			
						task_cores_t_allocated += mark_core*ttime
						task_mem_t_allocated += mark_mem*ttime
						task_disk_t_allocated += mark_disk*ttime

						#if we are at the last bucket of any type of resources, must use whole machine
						if ci == len(bucket_cores) or mi == len(bucket_mem) or di == len(bucket_disk):
							task_waste_cores += mcore-tcore
							task_waste_mem += mmem-tmem
							task_waste_disk += mdisk-tdisk
							cores_used = mcore
							mem_used = mmem
							disk_used = mdisk
							allocate_task_success = 1
							task_int_frag_core = mcore-tcore
							task_int_frag_mem = mmem-tmem
							task_int_frag_disk = mdisk-tdisk
							task_num_retries_machine += 1
							num_retries_task += 1
							stats["total_cores_t"] += mcore*ttime
							stats["total_mem_t"] += mmem*ttime
							stats["total_disk_t"] += mdisk*ttime
							stats["no_cold_total_cores_t"] += mcore*ttime
							stats["no_cold_total_mem_t"] += mmem*ttime
							stats["no_cold_total_disk_t"] += mdisk*ttime
							task_cores_t_allocated += mcore*ttime
							task_mem_t_allocated += mmem*ttime
							task_disk_t_allocated += mdisk*ttime
							task_cores_t_used = tcore*ttime
							task_mem_t_used = tmem*ttime
							task_disk_t_used = tdisk*ttime

					#otherwise, successful allocation
					else:
						task_waste_cores += mark_core-tcore
						task_waste_mem += mark_mem-tmem
						task_waste_disk += mark_disk-tdisk
						cores_used = mark_core
						mem_used = mark_mem
						disk_used = mark_disk
						allocate_task_success = 1
						task_int_frag_core = mark_core - tcore
						task_int_frag_mem = mark_mem - tmem
						task_int_frag_disk = mark_disk - tdisk
						stats["total_cores_t"] += mark_core*ttime
						stats["total_mem_t"] += mark_mem*ttime
						stats["total_disk_t"] += mark_disk*ttime
						stats["no_cold_total_cores_t"] += mark_core*ttime
						stats["no_cold_total_mem_t"] += mark_mem*ttime
						stats["no_cold_total_disk_t"] += mark_disk*ttime
						task_cores_t_allocated += mark_core*ttime
						task_mem_t_allocated += mark_mem*ttime
						task_disk_t_allocated += mark_disk*ttime
						task_cores_t_used = tcore*ttime
						task_mem_t_used = tmem*ttime
						task_disk_t_used = tdisk*ttime

			#update stats, assuming tasks fail at the end of their executions.
			stats["num_retries"] += num_retries_task
			stats["num_tasks"] += 1
			stats["total_run_time"] += (num_retries_task+1)*ttime			
			stats["wfail_alloc_core_t"] += task_wfail_alloc_core*ttime
			stats["wfail_alloc_mem_t"] += task_wfail_alloc_mem*ttime
			stats["wfail_alloc_disk_t"] += task_wfail_alloc_disk*ttime
			stats["int_frag_core_t"] += task_int_frag_core*ttime
			stats["int_frag_mem_t"] += task_int_frag_mem*ttime
			stats["int_frag_disk_t"] += task_int_frag_disk*ttime
			stats["num_retries_bucket"] += task_num_retries_bucket			
			stats["num_retries_machine"] += task_num_retries_machine
			stats["wcores_t"] += task_wfail_alloc_core*ttime + task_int_frag_core*ttime
			stats["wmem_t"] += task_wfail_alloc_mem*ttime + task_int_frag_mem*ttime
			stats["wdisk_t"] += task_wfail_alloc_disk*ttime + task_int_frag_disk*ttime
			stats["no_cold_wcores_t"] += task_wfail_alloc_core*ttime + task_int_frag_core*ttime
			stats["no_cold_wmem_t"] += task_wfail_alloc_mem*ttime + task_int_frag_mem*ttime
			stats["no_cold_wdisk_t"] += task_wfail_alloc_disk*ttime + task_int_frag_disk*ttime

			#add to list of records
			all_cores.append(tcore)
			all_mem.append(tmem)
			all_disk.append(tdisk)
			all_time.append(ttime)
			all_tag.append(ttag)	

		all_tasks_cores_t_allocated.append(task_cores_t_allocated)	
		all_tasks_mem_t_allocated.append(task_mem_t_allocated)	
		all_tasks_disk_t_allocated.append(task_disk_t_allocated)
		all_tasks_cores_t_used.append(task_cores_t_used)	
		all_tasks_mem_t_used.append(task_mem_t_used)	
		all_tasks_disk_t_used.append(task_disk_t_used)	
		#movies or not		
		if bool_movie > 0:
			plot_for_movies("k-means bucketing", chro_cores, chro_mem, chro_disk, all_tag, all_bucket_cores, all_bucket_mem, all_bucket_disk, num_buckets, plot_dir, num_cold_start, num_movie, num_all_tasks, max_tmem)
			num_movie += 1
		
		
	stats["avg_total_cores_t"] = stats["total_cores_t"]/stats["num_tasks"]
	stats["avg_total_mem_t"] = stats["total_mem_t"]/stats["num_tasks"]
	stats["avg_total_disk_t"] = stats["total_disk_t"]/stats["num_tasks"]	
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_wfail_alloc_core_t"] = stats["wfail_alloc_core_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_mem_t"] = stats["wfail_alloc_mem_t"]/stats["num_tasks"]
	stats["avg_wfail_alloc_disk_t"] = stats["wfail_alloc_disk_t"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]
	stats["cores_t_efficiency"] = 1 - stats["wcores_t"]/stats["total_cores_t"]
	stats["mem_t_efficiency"] = 1 - stats["wmem_t"]/stats["total_mem_t"]
	stats["disk_t_efficiency"] = 1 - stats["wdisk_t"]/stats["total_disk_t"]
	stats["no_cold_cores_t_effi"] = 1 - stats["no_cold_wcores_t"]/stats["no_cold_total_cores_t"]
	stats["no_cold_mem_t_effi"] = 1 - stats["no_cold_wmem_t"]/stats["no_cold_total_mem_t"]
	stats["no_cold_disk_t_effi"] = 1 - stats["no_cold_wdisk_t"]/stats["no_cold_total_disk_t"]
	all_effi_cores = [all_tasks_cores_t_used[i]/all_tasks_cores_t_allocated[i] for i in range(len(all_tasks_cores_t_allocated))]
	stats['avg_cores_t_efficiency'] = np.average(all_effi_cores)
	all_effi_mem = [all_tasks_mem_t_used[i]/all_tasks_mem_t_allocated[i] for i in range(len(all_tasks_mem_t_allocated))]
	stats['avg_mem_t_efficiency'] = np.average(all_effi_mem)
	all_effi_disk = [all_tasks_disk_t_used[i]/all_tasks_disk_t_allocated[i] for i in range(len(all_tasks_disk_t_allocated))]
	stats['avg_disk_t_efficiency'] = np.average(all_effi_disk)
	
	#plot the dynamics of buckets
	if bool_plot == 1:
		plot_buckets_over_time("k_means_bucketing", chro_cores, chro_mem, chro_disk, all_tag, all_bucket_cores, all_bucket_mem, all_bucket_disk, num_buckets, plot_dir, num_cold_start)	
	if bool_plot_effi == 1:
		plot_effi_dists("k_means_bucketing_{}_{}_{}".format(num_buckets, num_cold_start, diagonal), "cores", all_tasks_cores_t_allocated, all_tasks_cores_t_used)
		plot_effi_dists("k_means_bucketing_{}_{}_{}".format(num_buckets, num_cold_start, diagonal), "mem", all_tasks_mem_t_allocated, all_tasks_mem_t_used)
		plot_effi_dists("k_means_bucketing_{}_{}_{}".format(num_buckets, num_cold_start, diagonal), "disk", all_tasks_disk_t_allocated, all_tasks_disk_t_used)


#wrapper to record results of strategies to create spreadsheet of statistics
def wrapper_csv(type_sim, params):
	csv_arr[0].append(type_sim)
	if type_sim == "whole_machine":
		whole_machine(params[0], params[1], params[2])
		csv_arr[1].append('x')
		csv_arr[2].append('x')
		csv_arr[3].append('x')
	elif type_sim == "declare_resources":
		declare_resources(params[0], params[1], params[2], params[3])
		csv_arr[1].append('x')
		csv_arr[2].append('x')
		csv_arr[3].append('x')
	elif type_sim == "boxing_machine":
		boxing_machine(params[0], params[1], params[2], params[3])
		csv_arr[1].append('x')
		csv_arr[2].append('x')
		csv_arr[3].append(params[2])
	elif type_sim == "cold_bucketing":
		cold_bucketing(params[0], params[1], params[2], params[3], params[4], params[5], params[6])
		csv_arr[1].append(params[1])
		csv_arr[2].append(params[2])
		csv_arr[3].append(params[4])
	elif type_sim == "k_means_bucketing":
		k_means_bucketing(params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7])
		csv_arr[1].append(params[1])
		csv_arr[2].append(params[2])
		csv_arr[3].append(params[4])
	for i in range(4, len(csv_arr)):
		csv_arr[i].append(stats[csv_arr[i][0]])

#write out results to a csv file, can be opened on google docs (tested on Apr 19 2021)
def write_csv(csv_arr, file_name):
	with open(file_name, 'w', newline='') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(csv_arr)

#get tasks' resources consumption
all_res = get_tasks_resources(res_file)
csv_arr = init_csv_arr(csv_arr)

#testing

#def k_means_bucketing(all_res, num_buckets, num_cold_start, mach_capa, diagonal, bool_plot, bool_movie):
#def cold_bucketing(all_res, num_buckets, num_cold_start, mach_capa, diagonal, bool_plot):
#evaluate methods
wrapper_csv("whole_machine", [all_res, mach_capa, 1])
wrapper_csv("boxing_machine", [all_res, mach_capa, [1/8, 1/4, 1/2, 1], 0])
wrapper_csv("boxing_machine", [all_res, mach_capa, [1/4, 1/2, 1], 1])
wrapper_csv("boxing_machine", [all_res, mach_capa, [1/4, 1/2, 3/4, 1], 0])
wrapper_csv("declare_resources", [all_res, def_res, mach_capa, 1]) 
wrapper_csv("k_means_bucketing", [all_res, 1, 10, mach_capa, 1, 0, 0, 0])
wrapper_csv("k_means_bucketing", [all_res, 2, 10, mach_capa, 0, 0, 0, 0])
wrapper_csv("k_means_bucketing", [all_res, 2, 10, mach_capa, 1, 1, 0, 1])
wrapper_csv("k_means_bucketing", [all_res, 3, 10, mach_capa, 1, 1, 0, 0])
wrapper_csv("k_means_bucketing", [all_res, 4, 10, mach_capa, 1, 1, 0, 0])
wrapper_csv("cold_bucketing", [all_res, 1, 10, mach_capa, 1, 0, 0])
wrapper_csv("cold_bucketing", [all_res, 2, 10, mach_capa, 0, 0, 0])
wrapper_csv("cold_bucketing", [all_res, 2, 10, mach_capa, 1, 1, 1])
wrapper_csv("cold_bucketing", [all_res, 3, 10, mach_capa, 1, 1, 0])
wrapper_csv("cold_bucketing", [all_res, 4, 10, mach_capa, 1, 1, 0])

#write results to csv file
write_csv(csv_arr, csv_file)

"""#plotting effects of hyperparameters of cold_bucketing strategy
#fix number of buckets, change cold starts
plot_wmem_t = []
plot_wcores_t = []

#20 cold starts
cold_starts = [i for i in range(2, 21)]
for i in range(2, 21):
	cold_bucketing(all_res, 2, i, mach_capa, 1, 0)
	plot_wmem_t.append(stats['wmem_t'])
	plot_wcores_t.append(stats['wcores_t'])
fig, ax = plt.subplots()
ax.plot(cold_starts, plot_wcores_t, color="red", marker="o")
ax.set_xlabel("number of cold starts")
ax.set_ylabel("wcores_t - Waste in core over time")
ax.set_ylim(ymin=0)
ax2 = ax.twinx()
ax2.plot(cold_starts, plot_wmem_t, color='blue', marker='o')
ax2.set_ylabel("wmem_t - Waste in memory over time")
ax2.set_ylim(ymin=0)
plt.savefig(plot_dir + "2_buckets_change_cold_starts.png")

#fix number of cold strats, change number of buckets
plot_wmem_t = []
plot_wcores_t = []
num_buckets = [i for i in range(1, 21)]
for i in range(1, 21):
	cold_bucketing(all_res, i, 20, mach_capa, 1, 0)
	plot_wmem_t.append(stats['wmem_t'])
	plot_wcores_t.append(stats['wcores_t'])
fig, ax = plt.subplots()
ax.plot(num_buckets, plot_wcores_t, color="red", marker="o")
ax.set_xlabel("number of buckets")
ax.set_ylabel("wcores_t - Waste in core over time")
ax.set_ylim(ymin=0)
ax2 = ax.twinx()
ax2.plot(num_buckets, plot_wmem_t, color='blue', marker='o')
ax2.set_ylabel("wmem_t - Waste in memory over time")
ax2.set_ylim(ymin=0)
plt.savefig(plot_dir + "20_cold_starts_change_num_buckets.png")"""

#plot core efficiency
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
effi_level = csv_arr[15][1:]
ax.bar(strats, effi_level)
plt.xticks(rotation=90)
plt.ylim(top=1)
plt.title('Core efficiency for all strats')
plt.ylabel('Efficiency level')
rects = ax.patches
labels = [round(i, 2) for i in effi_level]
for rect, label in zip(rects, labels):
	height = rect.get_height()
	ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
plt.savefig(plot_dir + 'effi_all_strats_cores.png', bbox_inches='tight')
plt.close()

#plot memory efficiency
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
util_level = csv_arr[28][1:]
ax.bar(strats, util_level)
plt.xticks(rotation=90)
plt.ylim(top=1)
plt.title('Memory efficiency for all strats')
plt.ylabel('Effi level')
rects = ax.patches
labels = [round(i, 2) for i in effi_level]
for rect, label in zip(rects, labels):
	height = rect.get_height()
	ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
plt.savefig(plot_dir + 'effi_all_strats_memory.png', bbox_inches='tight')
plt.close()

#plot disk efficiency
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
effi_level = csv_arr[41][1:]
ax.bar(strats, effi_level)
plt.xticks(rotation=90)
plt.ylim(top=1)
plt.title('Disk efficiency for all strats')
plt.ylabel('Effi level')
rects = ax.patches
labels = [round(i, 2) for i in effi_level]
for rect, label in zip(rects, labels):
	height = rect.get_height()
	ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
plt.savefig(plot_dir + 'effi_all_strats_disk.png', bbox_inches='tight')
plt.close()

#plot cores efficiency with no cold
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
effi_level = csv_arr[16][1:]
ax.bar(strats, effi_level)
plt.xticks(rotation=90)
plt.ylim(top=1)
plt.title('Cores efficiency for all strats - no cold')
plt.ylabel('Effi level')
rects = ax.patches
labels = [round(i, 2) for i in effi_level]
for rect, label in zip(rects, labels):
	height = rect.get_height()
	ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
plt.savefig(plot_dir + 'effi_all_strats_cores_no_cold.png', bbox_inches='tight')
plt.close()

#plot memory efficiency with no cold
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
effi_level = csv_arr[29][1:]
ax.bar(strats, effi_level)
plt.xticks(rotation=90)
plt.ylim(top=1)
plt.title('Memory efficiency for all strats - no cold')
plt.ylabel('Effi level')
rects = ax.patches
labels = [round(i, 2) for i in effi_level]
for rect, label in zip(rects, labels):
	height = rect.get_height()
	ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
plt.savefig(plot_dir + 'effi_all_strats_memory_no_cold.png', bbox_inches='tight')
plt.close()

#plot disk efficiency with no cold
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
effi_level = csv_arr[42][1:]
ax.bar(strats, effi_level)
plt.xticks(rotation=90)
plt.ylim(top=1)
plt.title('Disk efficiency for all strats - no cold')
plt.ylabel('Effi level')
rects = ax.patches
labels = [round(i, 2) for i in effi_level]
for rect, label in zip(rects, labels):
	height = rect.get_height()
	ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
plt.savefig(plot_dir + 'effi_all_strats_disk_no_cold.png', bbox_inches='tight')
plt.close()

def plot_aver_effi(row_num, resource_name):
	fig = plt.figure()
	ax = fig.add_axes([0,0,1,1])
	strats=['whole', 'boxing8-4-2-1', 'boxing4-2-1', 'boxing4-2-4/3-1', 'declare', 'k-means1-10-1', 'k-means2-10-0', 'k-means2-10-1','k-means3-10-1','k-means4-10-1','cold1-10-1','cold2-10-0','cold2-10-1','cold3-10-1','cold4-10-1']
	effi_level = csv_arr[row_num][1:]
	ax.bar(strats, effi_level)
	plt.xticks(rotation=90)
	plt.ylim(top=1)
	plt.title('Average {} efficiency for all strats'.format(resource_name))
	plt.ylabel('Effi level')
	rects = ax.patches
	labels = [round(i, 2) for i in effi_level]
	for rect, label in zip(rects, labels):
		height = rect.get_height()
		ax.text(rect.get_x()+0.3, height+0.01, label, ha='center', va='bottom')
	plt.savefig(plot_dir + 'average_effi_all_strats_{}.png'.format(resource_name), bbox_inches='tight')
	plt.close()

plot_aver_effi(17, "cores")
plot_aver_effi(30, "mem")
plot_aver_effi(43, "disk")
