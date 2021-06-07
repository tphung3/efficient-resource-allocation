datasets = ["colmena", "hypersweep", "normal_large", "normal_small", "uniform_large", "uniform_small", "exponential", "bimodal", "trimodal", "bimodal_small_std", "trimodal_small_std", "bioblast", "lobsterCMSsimulation", "lobsterCMSanalysis"]

real_datasets = ["colmena", "hypersweep"]
levels = ['lv2', 'lv3']

with open("Makefile", 'w') as f:
	line='all: '
	for dataset in datasets:
		line+=dataset+" "
	line += '\n\n'
	f.write(line)
	for dataset in datasets:
		line = '{}: '.format(dataset)
		for level in levels:
			line += '{}_{} '.format(dataset, level) 		
		line += '\n\n'
		f.write(line)	

	for dataset in datasets:
		for level in levels:
			block = ""
			if dataset in real_datasets:
				block += "{}_{}: {}_{}_get_resources {}_{}_get_results {}_{}_get_plots\n\n".format(dataset, level, dataset, level, dataset, level, dataset, level)
				block += "{}_{}_get_resources: \n".format(dataset, level)
				block += "\tpython allocation_strategies/{}/read_summary_log.py {}\n\n".format(level, dataset)
			else:
				block += "{}_{}: {}_{}_get_results {}_{}_get_plots\n\n".format(dataset, level, dataset, level, dataset, level)	
			block += "{}_{}_get_results: \n".format(dataset, level)
			block += "\tpython allocation_strategies/{}/eval_alloc_strats.py {}\n\n".format(level, dataset)
			block += "{}_{}_get_plots: \n".format(dataset, level)
			block += "\tpython allocation_strategies/{}/plot_resources.py {}\n\n".format(level, dataset)
			f.write(block)
	clean = "clean:\n\trm resource_analysis/*/plots/*; rm resource_analysis/*/results/*"
	f.write(clean)
	
	
