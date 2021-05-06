datasets = ["colmena", "hypersweep", "normal_large", "normal_small", "uniform_large", "uniform_small", "exponential", "bimodal", "trimodal"]

real_datasets = ["colmena", "hypersweep"]

with open("Makefile_test", 'w') as f:
	line='all: '
	for dataset in datasets:
		line+=dataset+" "
	line += '\n\n'
	f.write(line)
	for dataset in datasets:
		block = ""
		if dataset in real_datasets:
			block += "{}: {}_get_resources {}_get_results {}_get_plots\n\n".format(dataset, dataset, dataset, dataset)
			block += "{}_get_resources: \n".format(dataset)
			block += "\tpython allocation_strategies/read_summary_log.py {}\n\n".format(dataset)
		else:
			block += "{}: {}_get_results {}_get_plots\n\n".format(dataset, dataset, dataset)	
		block += "{}_get_results: \n".format(dataset)
		block += "\tpython allocation_strategies/eval_alloc_strats.py {}\n\n".format(dataset)
		block += "{}_get_plots: \n".format(dataset)
		block += "\tpython allocation_strategies/plot_resources.py {}\n\n".format(dataset)
		f.write(block)

	
	
