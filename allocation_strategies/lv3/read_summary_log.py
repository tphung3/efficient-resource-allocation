#This file reads in the raw resources log and writes out formatted summary of resources consumption of tasks.

import re
import sys

resources_all = [["taskid", "core", "memory", "virtual_memory", "disk", "time", "average_cores"]]
num = -1
dataset = sys.argv[1]
level = "lv3"
resources_log = "resources_data/{}/{}/raw_data/{}.summaries".format(level, dataset, dataset)
#open resources log and read in data to resources_all list.
with open(resources_log, "r") as f:
	Lines = f.readlines()
	#skip the first line containing irrelevant metadata
	for line in Lines[1:]:
		resource = []
		#parse the resources line to get data
		try:
			task_id = line.split('{"task_id":"')[1].split('","category"')[0]
		except:
			continue
		core = line.split('"cores":[')[1].split(',"cores"]')[0]
		average_cores = line.split('"cores_avg":[')[1].split(',"cores"]')[0]
		memory = line.split('"procs"],"memory":[')[1].split(",\"MB\"],\"virtual_memory")[0]
		disk = line.split('les"],"disk":[')[1].split(",\"MB\"],\"machine")[0]
		time = line.split("\"wall_time\":[")[1].split(",\"s\"],\"cpu_time\":")[0]
		vir_mem = line.split('"virtual_memory":[')[1].split(',"MB"]')[0]
		resource = [task_id, core, memory, vir_mem, disk, time, average_cores]
		resources_all.append(resource)
		print("task " + task_id + " processed successfully!") 

#write to file the formatted summary of consumption
summaries = 'resources_data/{}/{}/data/'.format(level, dataset)
with open(summaries+"resources_all.txt", "w") as f:
	tag = "1"
	for resource in resources_all:
		try:
			line = resource[0]+" -- "+resource[1]+" -- "+resource[2]+" -- "+resource[3]+" -- "+resource[4] + " -- "+resource[5]+" -- "+resource[6] + " -- {}".format(tag)
		except:
			continue
		f.write(str(line) + "\n")
		num += 1
print("Total lines processed: " + str(num))
