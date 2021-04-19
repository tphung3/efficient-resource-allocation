colmena: colmena_get_resources colmena_get_results colmena_get_plots

colmena_get_resources:
	python resources_analysis/colmena/read_summary_log.py

colmena_get_results: colmena_get_resources
	python resources_analysis/colmena/eval_alloc_strats.py

colmena_get_plots: colmena_get_resources
	python resources_analysis/colmena/plot_resources.py

clean:
	rm resources_analysis/colmena/plots/*
	rm resources_analysis/colmena/results/*
	rm resources_analysis/colmena/resources_all.txt	
