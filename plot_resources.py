import matplotlib.pyplot as plt

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

resources_all = []
plot_rate_and_core = []
plot_rate_and_mem = []
plot_rate_and_disk = []
plot_rate_and_time = []
plot_block_and_core = []
plot_block_and_mem = []
plot_block_and_disk = []
plot_block_and_time = []
plot_batch_and_core = []
plot_batch_and_mem = []
plot_batch_and_disk = []
plot_batch_and_time = []
plot_epoch_and_core = []
plot_epoch_and_mem = []
plot_epoch_and_disk = []
plot_epoch_and_time = []
plot_block_and_mem_one = []
plot_block_and_mem_two = []
plot_block_and_mem_three = []
plot_block_and_mem_four = []
plot_rate_and_mem_one = []
plot_rate_and_mem_two = []
plot_rate_and_mem_three = []
plot_rate_and_mem_four = []
plot_batch_and_mem_one = []
plot_batch_and_mem_two = []
plot_batch_and_mem_three = []
plot_batch_and_mem_four = []
plot_epoch_and_mem_one = []
plot_epoch_and_mem_two = []
plot_epoch_and_mem_three = []
plot_epoch_and_mem_four = []
plot_block_and_core_one = []
plot_block_and_core_two = []
plot_block_and_core_three = []
plot_block_and_core_four = []
plot_rate_and_core_one = []
plot_rate_and_core_two = []
plot_rate_and_core_three = []
plot_rate_and_core_four = []
plot_batch_and_core_one = []
plot_batch_and_core_two = []
plot_batch_and_core_three = []
plot_batch_and_core_four = []
plot_epoch_and_core_one = []
plot_epoch_and_core_two = []
plot_epoch_and_core_three = []
plot_epoch_and_core_four = []

conf = [[0.30, 15, 100, 36], [0.50, 18, 108, 30], [0.40, 16, 92, 34], [0.60, 10, 84, 24]]


print("Checkpoint 1")
with open("resources_all.txt", "r") as f:
	Lines = f.readlines()
	for line in Lines[1:]:
		resource = line.split(" -- ")
		resource[8] = resource[8].split("\n")[0]
		resources_all.append(resource)
		core = round(float(resource[1]), 3)
		mem = int(resource[2])
		disk = int(resource[3])
		time = round(float(resource[4]), 2)
		rate = round(float(resource[5]), 2)
		block = int(resource[6])
		batch = int(resource[7])
		epoch = int(resource[8])
		plot_rate_and_core.append([rate, core])
		plot_rate_and_mem.append([rate, mem])
		plot_rate_and_disk.append([rate, disk])
		plot_rate_and_time.append([rate, time])
		plot_block_and_core.append([block, core])
		plot_block_and_mem.append([block, mem])
		plot_block_and_disk.append([block, disk])
		plot_block_and_time.append([block, time])
		plot_batch_and_core.append([batch, core])
		plot_batch_and_mem.append([batch, mem])
		plot_batch_and_disk.append([batch, disk])
		plot_batch_and_time.append([batch, time])
		plot_epoch_and_core.append([epoch, core])
		plot_epoch_and_mem.append([epoch, mem])
		plot_epoch_and_disk.append([epoch, disk])
		plot_epoch_and_time.append([epoch, time])
		#change block
		if rate == conf[0][0] and batch == conf[0][2] and epoch == conf[0][3]:
			plot_block_and_mem_one.append([block, mem])
			plot_block_and_core_one.append([block, core])
		if rate == conf[1][0] and batch == conf[1][2] and epoch == conf[1][3]:
			plot_block_and_mem_two.append([block, mem])
			plot_block_and_core_two.append([block, core])
		if rate == conf[2][0] and batch == conf[2][2] and epoch == conf[2][3]:
			plot_block_and_mem_three.append([block, mem])
			plot_block_and_core_three.append([block, core])
		if rate == conf[3][0] and batch == conf[3][2] and epoch == conf[3][3]:
			plot_block_and_mem_four.append([block, mem])
			plot_block_and_core_four.append([block, core])
		#change rate
		if block == conf[0][1] and batch == conf[0][2] and epoch == conf[0][3]:
			plot_rate_and_mem_one.append([rate, mem])
			plot_rate_and_core_one.append([rate, core])
		if block == conf[1][1] and batch == conf[1][2] and epoch == conf[1][3]:
			plot_rate_and_mem_two.append([rate, mem])
			plot_rate_and_core_two.append([rate, core])
		if block == conf[2][1] and batch == conf[2][2] and epoch == conf[2][3]:
			plot_rate_and_mem_three.append([rate, mem])
			plot_rate_and_core_three.append([rate, core])
		if block == conf[3][1] and batch == conf[3][2] and epoch == conf[3][3]:
			plot_rate_and_mem_four.append([rate, mem])
			plot_rate_and_core_four.append([rate, core])
		#change batch
		if block == conf[0][1] and rate == conf[0][0] and epoch == conf[0][3]:
			plot_batch_and_mem_one.append([batch, mem])
			plot_batch_and_core_one.append([batch, core])
		if block == conf[1][1] and rate == conf[1][0] and epoch == conf[1][3]:
			plot_batch_and_mem_two.append([batch, mem])
			plot_batch_and_core_two.append([batch, core])
		if block == conf[2][1] and rate == conf[2][0] and epoch == conf[2][3]:
			plot_batch_and_mem_three.append([batch, mem])
			plot_batch_and_core_three.append([batch, core])
		if block == conf[3][1] and rate == conf[3][0] and epoch == conf[3][3]:
			plot_batch_and_mem_four.append([batch, mem])
			plot_batch_and_core_four.append([batch, core])
		#change epoch
		if block == conf[0][1] and rate == conf[0][0] and batch == conf[0][2]:
			plot_epoch_and_mem_one.append([epoch, mem])
			plot_epoch_and_core_one.append([epoch, core])
		if block == conf[1][1] and rate == conf[1][0] and batch == conf[1][2]:
			plot_epoch_and_mem_two.append([epoch, mem])
			plot_epoch_and_core_two.append([epoch, core])
		if block == conf[2][1] and rate == conf[2][0] and batch == conf[2][2]:
			plot_epoch_and_mem_three.append([epoch, mem])
			plot_epoch_and_core_three.append([epoch, core])
		if block == conf[3][1] and rate == conf[3][0] and batch == conf[3][2]:
			plot_epoch_and_mem_four.append([epoch, mem])
			plot_epoch_and_core_four.append([epoch, core])

print("Checkpoint 2")
gen_fig(plot_rate_and_core, "core", "drop_out_rate")
gen_fig(plot_rate_and_mem, "memory", "drop_out_rate")
gen_fig(plot_rate_and_disk, "disk", "drop_out_rate")
gen_fig(plot_rate_and_time, "time", "drop_out_rate")
gen_fig(plot_block_and_core, "core", "number_of_residual_blocks")
gen_fig(plot_block_and_mem, "memory", "number_of_residual_blocks")
gen_fig(plot_block_and_disk, "disk", "number_of_residual_blocks")
gen_fig(plot_block_and_time, "time", "number_of_residual_blocks")
gen_fig(plot_batch_and_core, "core", "number of data points per batch")
gen_fig(plot_batch_and_mem, "mem", "number of data points per batch")
gen_fig(plot_batch_and_disk, "disk", "number of data points per batch")
gen_fig(plot_batch_and_time, "time", "number of data points per batch")
gen_fig(plot_epoch_and_core, "core", "number of epochs")
gen_fig(plot_epoch_and_mem, "mem", "number of epochs")
gen_fig(plot_epoch_and_disk, "disk", "number of epochs")
gen_fig(plot_epoch_and_time, "time", "number of epochs")
gen_fig(plot_block_and_mem_one, "memory", "number_of_residual_blocks_one")
gen_fig(plot_block_and_mem_two, "memory", "number_of_residual_blocks_two")
gen_fig(plot_block_and_mem_three, "memory", "number_of_residual_blocks_three")
gen_fig(plot_block_and_mem_four, "memory", "number_of_residual_blocks_four")
gen_fig(plot_rate_and_mem_one, "memory", "drop_out_rate_one")
gen_fig(plot_rate_and_mem_two, "memory", "drop_out_rate_two")
gen_fig(plot_rate_and_mem_three, "memory", "drop_out_rate_three")
gen_fig(plot_rate_and_mem_four, "memory", "drop_out_rate_four")
gen_fig(plot_batch_and_mem_one, "memory", "number_of_data_points_per_batch_one")
gen_fig(plot_batch_and_mem_two, "memory", "number_of_data_points_per_batch_two")
gen_fig(plot_batch_and_mem_three, "memory", "number_of_data_points_per_batch_three")
gen_fig(plot_batch_and_mem_four, "memory", "number_of_data_points_per_batch_four")
gen_fig(plot_epoch_and_mem_one, "memory", "number_of_epochs_one")
gen_fig(plot_epoch_and_mem_two, "memory", "number_of_epochs_two")
gen_fig(plot_epoch_and_mem_three, "memory", "number_of_epochs_three")
gen_fig(plot_epoch_and_mem_four, "memory", "number_of_epochs_four")
gen_fig(plot_block_and_core_one, "core", "number_of_residual_blocks_one")
gen_fig(plot_block_and_core_two, "core", "number_of_residual_blocks_two")
gen_fig(plot_block_and_core_three, "core", "number_of_residual_blocks_three")
gen_fig(plot_block_and_core_four, "core", "number_of_residual_blocks_four")
gen_fig(plot_rate_and_core_one, "core", "drop_out_rate_one")
gen_fig(plot_rate_and_core_two, "core", "drop_out_rate_two")
gen_fig(plot_rate_and_core_three, "core", "drop_out_rate_three")
gen_fig(plot_rate_and_core_four, "core", "drop_out_rate_four")
gen_fig(plot_batch_and_core_one, "core", "number_of_data_points_per_batch_one")
gen_fig(plot_batch_and_core_two, "core", "number_of_data_points_per_batch_two")
gen_fig(plot_batch_and_core_three, "core", "number_of_data_points_per_batch_three")
gen_fig(plot_batch_and_core_four, "core", "number_of_data_points_per_batch_four")
gen_fig(plot_epoch_and_core_one, "core", "number_of_epochs_one")
gen_fig(plot_epoch_and_core_two, "core", "number_of_epochs_two")
gen_fig(plot_epoch_and_core_three, "core", "number_of_epochs_three")
gen_fig(plot_epoch_and_core_four, "core", "number_of_epochs_four")

	

 
