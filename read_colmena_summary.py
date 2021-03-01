import sys
resources_all = [["taskid", "core", "memory", "disk", "time","drate","rblock","batch","epoch"]]
num = 0
line_num = 0
with open("resource_data/hypersweep.summaries", "r") as f:
	Lines = f.readlines()
	for line in Lines:
		line_num += 1
		if len(line.split("was not available")) > 1:
			continue
		if line == "\n":
			continue
		resource = []
		task_id = line.split('{"task_id":"')[1].split('","category"')[0]
		core = line.split(',"cores":[')[1].split(',"cores"],"wall_time"')[0]
		memory = line.split('"memory":[')[1].split(',"MB"],"virtual_memory"')[0]
		disk = line.split('"disk":[')[1].split(',"MB"],"machine_cpus"')[0]
		time = line.split('"wall_time":[')[1].split(',"s"],"cpu_time"')[0]
		vir_mem = line.split('"virtual_memory":[')[1].split(',"MB"],"swap_memory"')[0]
		hparams = line.split("bash script.sh results")[1].split(".csv")[0]
		hparams = hparams.split("_")
		drate = hparams[0]
		rblock = hparams[1]
		batch = hparams[2]
		epoch = hparams[3]
		resource = [task_id, core, memory, vir_mem, disk, time, drate, rblock, batch, epoch]
		resources_all.append(resource)
with open("resource_data/hypersweep.dat", "w") as f:
	f.write("taskid -- cores -- memory -- virtual_memory -- disk -- time -- drate -- rblock -- batch -- epoch\n")
	for resource in resources_all:
		try:
			line = resource[0]+" -- "+resource[1]+" -- "+resource[2]+" -- "+resource[3]+" -- "+resource[4] + " -- "+resource[5]+" -- "+resource[6]+" -- "+resource[7]+" -- "+resource[8]+" -- "+resource[9]
		except:
			continue
		num += 1
		f.write(str(line) + "\n")
