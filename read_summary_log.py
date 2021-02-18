import re

resources_all = [["taskid", "core", "memory", "disk", "time","drate","rblock","batch","epoch"]]
num = 0
with open("full_sweep_resources_summary/wq-22156.summaries", "r") as f:
	Lines = f.readlines()
	#Lines[0] = Lines[0].split("140722965902.032,\"procs\"]}")[1]
	for line in Lines:
		resource = []
			#find task id
		if len(line.split('{"task_id":"')) == 1:
			continue
		task_id = line.split('{"task_id":"')[1].split('","category"')[0]
		if len(line.split('"cores_avg":[')) == 1:
			continue
		core = line.split('"cores_avg":[')[1].split(',"cores"],')[0]
		memory = line.split('"procs"],"memory":[')[1].split(",\"MB\"],\"virtual_memory")[0]
		if len(line.split('les"],"disk":[')) == 1:
			continue
		disk = line.split('les"],"disk":[')[1].split(",\"MB\"],\"machine")[0]
		time = line.split("\"wall_time\":[")[1].split(",\"s\"],\"cpu_time\":")[0]
		vir_mem = line.split('"virtual_memory":[')[1].split(',"MB"]')[0]
		hparams = line.split("bash script.sh results")[1].split(".csv")[0]
		hparams = hparams.split("_")
		drate = hparams[0]
		rblock = hparams[1]
		batch = hparams[2]
		epoch = hparams[3]
		resource = [task_id, core, memory, vir_mem, disk, time, drate, rblock, batch, epoch]
		resources_all.append(resource)
		print("task " + task_id + " processed successfully!") 
		num += 1
with open("resources_all.txt", "w") as f:
	for resource in resources_all:
		try:
			line = resource[0]+" -- "+resource[1]+" -- "+resource[2]+" -- "+resource[3]+" -- "+resource[4] + " -- "+resource[5]+" -- "+resource[6]+" -- "+resource[7]+" -- "+resource[8]+" -- "+resource[9]
		except:
			continue
		f.write(str(line) + "\n")
print("Total lines processed: " + str(num))
