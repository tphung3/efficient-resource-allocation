colmena: colmena_get_resources colmena_get_results colmena_get_plots

colmena_get_resources:
	python resources_analysis/colmena/read_summary_log.py

colmena_get_results: colmena_get_resources
	python resources_analysis/colmena/eval_alloc_strats.py

colmena_get_plots: colmena_get_resources
	python resources_analysis/colmena/plot_resources.py

hypersweep: hypersweep_get_resources hypersweep_get_results hypersweep_get_plots

hypersweep_get_resources:
	python resources_analysis/hypersweep/read_summary_log.py

hypersweep_get_results: hypersweep_get_resources
	python resources_analysis/hypersweep/eval_alloc_strats.py

hypersweep_get_plots: hypersweep_get_resources
	python resources_analysis/hypersweep/plot_resources.py

clean:
	rm resources_analysis/colmena/plots/*
	rm resources_analysis/colmena/results/*
	rm resources_analysis/colmena/resources_all.txt	
	rm resources_analysis/hypersweep/plots/*
	rm resources_analysis/hypersweep/results/*
	rm resources_analysis/hypersweep/resources_all.txt
