import numpy as np
import os
import math
import sys

#fix seed for consistent datasets
seed=20210602
np.random.seed(seed)

level = 'lv2'
data_dir = "resources_data/{}/".format(level)
num_tasks = 200
analysis_dir = "resources_analysis/{}/".format(level)

def generate_data_dir(name, mem):
	cores = [4]*num_tasks
	virtual_memory = [0]*num_tasks
	disk = [4000]*num_tasks
	time = [500]*num_tasks
	average_cores = [0]*num_tasks
	if not os.path.isdir(data_dir+name):
		mem_tag = [[math.floor(val), math.floor(tag)] for val, tag in mem]
		os.mkdir("{}{}".format(data_dir, name))
		os.mkdir("{}{}/data/".format(data_dir, name))
		with open("{}{}/data/resources_all.txt".format(data_dir, name), 'w') as f:
			f.write("taskid -- core -- memory -- virtual_memory -- disk -- time -- average_cores -- tag\n")
			for i in range(num_tasks):
				line = "{} -- {} -- {} -- {} -- {} -- {} -- {} -- {}\n".format(i+1, cores[i], mem_tag[i][0], virtual_memory[i], disk[i], time[i], average_cores[i], mem_tag[i][1])
				f.write(line)
	if not os.path.isdir(analysis_dir+name):
		os.mkdir("{}{}".format(analysis_dir, name))
		os.mkdir("{}{}/plots/".format(analysis_dir, name))
		os.mkdir("{}{}/results/".format(analysis_dir, name))

def normal(mean, std, num_tasks):
	mem = np.random.normal(mean, std, num_tasks)
	mem_tag = [[i, 1] for i in mem]
	return mem_tag

def uniform(low, high, num_tasks):
	mem = np.random.uniform(low, high, num_tasks)
	mem_tag = [[i, 1] for i in mem]
	return mem_tag

def exponential(scale, size):
	mem = np.random.exponential(scale, size)
	mem_tag = [[i, 1] for i in mem]
	return mem_tag

def bimodal(mean1, mean2, std1, std2, num_tasks):
	mem1 = np.random.normal(mean1, std1, num_tasks//2)
	mem2 = np.random.normal(mean2, std2, num_tasks//2)
	mem1_tag = [[i, 1] for i in mem1]
	mem2_tag = [[i, 2] for i in mem2]
	mem_tag = np.concatenate((mem1_tag, mem2_tag))
	np.random.shuffle(mem_tag)
	return mem_tag

def trimodal(mean1, mean2, std1, std2, mean3, std3, num_tasks):
	mem1 = np.random.normal(mean1, std1, num_tasks//3)
	mem2 = np.random.normal(mean2, std2, num_tasks//3)
	mem3 = np.random.normal(mean3, std3, num_tasks - 2*(num_tasks//3))
	mem1_tag = [[i, 1] for i in mem1]
	mem2_tag = [[i, 2] for i in mem2]
	mem3_tag = [[i, 3] for i in mem3]
	mem_tag = np.concatenate((mem1_tag, mem2_tag, mem3_tag))
	np.random.shuffle(mem_tag)
	return mem_tag

generate_data_dir("normal_large", normal(32000, 11000, 200))
generate_data_dir("normal_small", normal(8000, 2000, 200))
generate_data_dir("uniform_large", uniform(10000, 40000, 200))
generate_data_dir("uniform_small", uniform(1000, 4000, 200))
generate_data_dir("exponential", exponential(20000, (200)))
generate_data_dir("bimodal", bimodal(32000, 11000, 8000, 2000, 200))
generate_data_dir("trimodal", trimodal(32000, 11000, 4000, 1000, 16000, 4000, 200))
generate_data_dir("bimodal_small_std", bimodal(32000, 8000, 500, 200, 200))
generate_data_dir("trimodal_small_std", trimodal(32000, 11000, 500, 500, 16000, 500, 200))
