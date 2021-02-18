import matplotlib.pyplot as plt
import os

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

plot_acc_and_batch = []
plot_acc_and_rblock = []
plot_acc_and_drate = []
plot_acc_and_epoch = []

directory = "full_sweep_results/"
print("Checkpoint 1")

all_files = os.listdir(directory)
for f in all_files:
	with open(directory+f, 'r') as fi:
		stats = fi.readlines()[1].split(', ')
		acc = round(float(stats[1]), 3)
		batch = int(stats[2])
		rblock = int(stats[3])
		drate = round(float(stats[4]), 2)
		epoch = int(stats[5])
		plot_acc_and_rblock.append([rblock, acc])
		plot_acc_and_drate.append([drate, acc])
		plot_acc_and_batch.append([batch, acc])
		plot_acc_and_epoch.append([epoch, acc]) 

print("Checkpoint 2")
gen_fig(plot_acc_and_rblock, "accuracy", "number_of_residual_blocks")
gen_fig(plot_acc_and_drate, "accuracy", "drop_out_rate")
gen_fig(plot_acc_and_batch, "accuracy", "batch_size")
gen_fig(plot_acc_and_epoch, "accuracy", "number_of_epochs")
		

 
