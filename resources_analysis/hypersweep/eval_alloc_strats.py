#This file defines the strategies to allocate resources to tasks and evaluates them on different metrics.

import math
import csv
import matplotlib.pyplot as plt
import os

#dictionary to store statistics of each strategy
stats = {"num_tasks": 0, "wcores_t": 0, "avg_wcores_t": 0, "wfail_alloc_core_t": 0,
		 "avg_wfail_alloc_core_t": 0, "int_frag_core_t": 0, "avg_int_frag_core_t": 0, 
		 "wmem_t": 0, "avg_wmem_t": 0, "wfail_alloc_mem_t": 0,
		 "avg_wfail_alloc_mem_t": 0, "int_frag_mem_t": 0, "avg_int_frag_mem_t": 0, 
		 "wdisk_t": 0, "avg_wdisk_t": 0, "wfail_alloc_disk_t": 0,
		 "avg_wfail_alloc_disk_t": 0, "int_frag_disk_t": 0, "avg_int_frag_disk_t": 0, 
		 "num_retries": 0, "num_retries_bucket": 0, "num_retries_machine": 0,
		 "total_run_time": 0, "avg_run_time": 0}

#array of statistics that is convertible to spreadsheets
csv_arr = []

#each machine is assumed to have 16 cores, 128GB of RAM and disk. This is not always true but used for the purpose of evaluation
mach_capa = [16, 128000, 128000]

#This is used in the declared_resources strategy, and this is a pretty good guess that has no fails due to under-allocation.
def_res = [4, 40000, 40000]

#input file of resources_consumption
res_file = "resources_analysis/hypersweep/resources_all.txt"

#number of buckets of the cold_bucketing strategy
num_buckets = 2

csv_file = "results/strategies_evaluation.csv"

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
	with open(file_name, 'r') as f:
		Lines = f.readlines()
		for line in Lines[1:]:
			resource = line.split(" -- ")
			core = int(resource[1])
			mem = int(resource[2])
			disk = int(resource[4])
			time = round(float(resource[5]), 2)
			all_res.append([core, mem, disk, time])
	return all_res

#Whole machine strategy: each task is allocated a whole machine with capacity defined above
def whole_machine(all_resources, machine):
	reset_stats(stats)
	mcore = machine[0]
	mmem = machine[1]
	mdisk = machine[2]
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
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]
	
	#print out results/statistics of this strategy
	rept = "Report for whole machine strat:\n"
	for stat, value in stats.items():
		rept += " {}: {}\n".format(stat, value)
	print(rept)	

#declare resources strategy: each task is allocated by a manually declared amount of resources. This amount is also defined above.
def declare_resources(all_resources, default_resources, machine_resources):
	reset_stats(stats)
	dcore = default_resources[0]
	dmem = default_resources[1]
	ddisk = default_resources[2]
	mcore = machine_resources[0]
	mmem = machine_resources[1]
	mdisk = machine_resources[2]	

	for task_res in all_resources:
		tcore, tmem, tdisk, ttime = task_res
		fail = tcore > dcore or tmem > dmem or tdisk > ddisk
		stats["wcores_t"] += (dcore+fail*mcore-tcore)*ttime
		stats["wmem_t"] += (dmem+fail*mmem-tmem)*ttime
		stats["wdisk_t"] += (ddisk+fail*mdisk-tdisk)*ttime
		stats["num_retries"] += fail*1
		stats["num_tasks"] += 1
		stats["total_run_time"] += ttime
		stats["int_frag_core_t"] += (dcore + fail*mcore - tcore)*ttime
		stats["int_frag_mem_t"] += (dmem + fail*mmem - tmem)*ttime
		stats["int_frag_disk_t"] += (ddisk + fail*mdisk - tdisk)*ttime
	stats["avg_wcores_t"] = stats["wcores_t"]/stats["num_tasks"]
	stats["avg_wmem_t"] = stats["wmem_t"]/stats["num_tasks"]
	stats["avg_wdisk_t"] = stats["wdisk_t"]/stats["num_tasks"]
	stats["avg_run_time"] = stats["total_run_time"]/stats["num_tasks"]
	stats["avg_int_frag_core_t"] = stats["int_frag_core_t"]/stats["num_tasks"]
	stats["avg_int_frag_mem_t"] = stats["int_frag_mem_t"]/stats["num_tasks"]
	stats["avg_int_frag_disk_t"] = stats["int_frag_disk_t"]/stats["num_tasks"]

	#print out results/statistics of this strategy
	rept = "Report for declare_resources strat:\n"
	for stat, value in stats.items():
		rept += " {}: {}\n".format(stat, value)
	print(rept)						

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

#cold bucketing strategy: This strategy assumes that we have a resources log of completed tasks and allocates the remaining tasks based on this log. It divides the completed tasks into a number of equal-sized buckets (this number must be predefined) from 1 to n (assuming n buckets), with elements in bucket i always smaller than elements in bucket i+1. Then each task is allocated by the maximum element in each bucket in the increasing order (only retried if allocation fails). As we need a log of completed tasks (no completed tasks in the beginning/cold start problem), this log is achieved by running a number of tasks using whole machines. Finally, two ways of choosing buckets are implemented. Either we increase only the exceeded resources (diagonal=0) or we increase all resources/move to next buckets of all resources (diagonal=1).
def cold_bucketing(all_res, num_buckets, num_cold_start, mach_capa, diagonal):
	
	#resetting stats
	reset_stats(stats)
	
	#list of records of completed tasks' resources
	all_cores = []
	all_mem = []
	all_disk = []
	all_time = []
	
	#list of buckets' upperbounds of completed tasks
	bucket_cores = [0]*(num_buckets)
	bucket_mem = [0]*(num_buckets)
	bucket_disk = [0]*(num_buckets)	

	#get machine specs
	mcore, mmem, mdisk = mach_capa

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
		tcore, tmem, tdisk, ttime = task_res

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
		
			#add to lists of records
			all_cores.append(tcore)
			all_mem.append(tmem)
			all_disk.append(tdisk)
			all_time.append(ttime)
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

			#print out the lists of buckets for sanity check
			if i == len(all_res)-1:
				print(bucket_cores)
				print(bucket_mem)
				print(bucket_disk)

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

			#add to list of records
			all_cores.append(tcore)
			all_mem.append(tmem)
			all_disk.append(tdisk)
			all_time.append(ttime)
	
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
	
	#print out results/statistics of this strategy
	rept = "Report for cold-start bucketing with {} buckets and {} cold tasks and {} diagonal strat:\n".format(num_buckets, num_cold_start, diagonal)
	for stat, value in stats.items():
	    rept += " {}: {}\n".format(stat, value)
	print(rept)

#wrapper to record results of strategies to create spreadsheet of statistics
def wrapper_csv(type_sim, params):
	csv_arr[0].append(type_sim)
	if len(params) == 2:
		whole_machine(params[0], params[1])
		csv_arr[1].append('x')
		csv_arr[2].append('x')
		csv_arr[3].append('x')
	elif len(params) == 3:
		declare_resources(params[0], params[1], params[2])
		csv_arr[1].append('x')
		csv_arr[2].append('x')
		csv_arr[3].append('x')
	else:
		cold_bucketing(params[0], params[1], params[2], params[3], params[4])
		csv_arr[1].append(params[1])
		csv_arr[2].append(params[2])
		csv_arr[3].append(params[4])
	for i in range(4, len(csv_arr)):
		csv_arr[i].append(stats[csv_arr[i][0]])

#write out results to a csv file, can be opened on google docs (tested on Apr 19 2021)
def write_csv(csv_arr, file_name):
	cwd = os.getcwd()
	with open("resources_analysis/hypersweep/"+file_name, 'w', newline='') as f:
		writer = csv.writer(f, delimiter=',')
		writer.writerows(csv_arr)

#get tasks' resources consumption
all_res = get_tasks_resources(res_file)
csv_arr = init_csv_arr(csv_arr)
#evaluate methods
wrapper_csv("whole_machine", [all_res, mach_capa])
wrapper_csv("declare_resources", [all_res, def_res, mach_capa])
wrapper_csv("cold_bucketing", [all_res, 1, 10, mach_capa, 1]) 
wrapper_csv("cold_bucketing", [all_res, 2, 10, mach_capa, 1])
wrapper_csv("cold_bucketing", [all_res, 2, 10, mach_capa, 0])
wrapper_csv("cold_bucketing", [all_res, 2, 5, mach_capa, 1])
wrapper_csv("cold_bucketing", [all_res, 3, 10, mach_capa, 1])
wrapper_csv("cold_bucketing", [all_res, 3, 5, mach_capa, 1])
wrapper_csv("cold_bucketing", [all_res, 4, 10, mach_capa, 1])
wrapper_csv("cold_bucketing", [all_res, 7, 20, mach_capa, 1])

#write results to csv file
write_csv(csv_arr, csv_file)

#plots go here
plot_dir = "resources_analysis/hypersweep/plots/"

#plotting effects of hyperparameters of cold_bucketing strategy
#fix number of buckets, change cold starts
plot_wmem_t = []
plot_wcores_t = []

#20 cold starts
cold_starts = [i for i in range(2, 21)]
for i in range(2, 21):
	cold_bucketing(all_res, 2, i, mach_capa, 1)
	plot_wmem_t.append(stats['wmem_t'])
	plot_wcores_t.append(stats['wcores_t'])
fig, ax = plt.subplots()
ax.plot(cold_starts, plot_wcores_t, color="red", marker="o")
ax.set_xlabel("number of cold starts")
ax.set_ylabel("wcores_t - Waste in core over time")
ax2 = ax.twinx()
ax2.plot(cold_starts, plot_wmem_t, color='blue', marker='o')
ax2.set_ylabel("wmem_t - Waste in memory over time")
plt.savefig(plot_dir + "2_buckets_change_cold_starts.png")

#fix number of cold strats, change number of buckets
plot_wmem_t = []
plot_wcores_t = []
num_buckets = [i for i in range(1, 21)]
for i in range(1, 21):
	cold_bucketing(all_res, i, 20, mach_capa, 1)
	plot_wmem_t.append(stats['wmem_t'])
	plot_wcores_t.append(stats['wcores_t'])
fig, ax = plt.subplots()
ax.plot(num_buckets, plot_wcores_t, color="red", marker="o")
ax.set_xlabel("number of buckets")
ax.set_ylabel("wcores_t - Waste in core over time")
ax2 = ax.twinx()
ax2.plot(num_buckets, plot_wmem_t, color='blue', marker='o')
ax2.set_ylabel("wmem_t - Waste in memory over time")
plt.savefig(plot_dir + "20_cold_starts_change_num_buckets.png")



print('####TESTING PURPOSES')
cold_bucketing(all_res, 2, 5, mach_capa, 0)
