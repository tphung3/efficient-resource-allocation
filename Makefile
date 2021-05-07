all: colmena hypersweep normal_large normal_small uniform_large uniform_small exponential bimodal trimodal bimodal_small_std 

colmena: colmena_get_resources colmena_get_results colmena_get_plots

colmena_get_resources: 
	python allocation_strategies/read_summary_log.py colmena

colmena_get_results: 
	python allocation_strategies/eval_alloc_strats.py colmena

colmena_get_plots: 
	python allocation_strategies/plot_resources.py colmena

hypersweep: hypersweep_get_resources hypersweep_get_results hypersweep_get_plots

hypersweep_get_resources: 
	python allocation_strategies/read_summary_log.py hypersweep

hypersweep_get_results: 
	python allocation_strategies/eval_alloc_strats.py hypersweep

hypersweep_get_plots: 
	python allocation_strategies/plot_resources.py hypersweep

normal_large: normal_large_get_results normal_large_get_plots

normal_large_get_results: 
	python allocation_strategies/eval_alloc_strats.py normal_large

normal_large_get_plots: 
	python allocation_strategies/plot_resources.py normal_large

normal_small: normal_small_get_results normal_small_get_plots

normal_small_get_results: 
	python allocation_strategies/eval_alloc_strats.py normal_small

normal_small_get_plots: 
	python allocation_strategies/plot_resources.py normal_small

uniform_large: uniform_large_get_results uniform_large_get_plots

uniform_large_get_results: 
	python allocation_strategies/eval_alloc_strats.py uniform_large

uniform_large_get_plots: 
	python allocation_strategies/plot_resources.py uniform_large

uniform_small: uniform_small_get_results uniform_small_get_plots

uniform_small_get_results: 
	python allocation_strategies/eval_alloc_strats.py uniform_small

uniform_small_get_plots: 
	python allocation_strategies/plot_resources.py uniform_small

exponential: exponential_get_results exponential_get_plots

exponential_get_results: 
	python allocation_strategies/eval_alloc_strats.py exponential

exponential_get_plots: 
	python allocation_strategies/plot_resources.py exponential

bimodal: bimodal_get_results bimodal_get_plots

bimodal_get_results: 
	python allocation_strategies/eval_alloc_strats.py bimodal

bimodal_get_plots: 
	python allocation_strategies/plot_resources.py bimodal

trimodal: trimodal_get_results trimodal_get_plots

trimodal_get_results: 
	python allocation_strategies/eval_alloc_strats.py trimodal

trimodal_get_plots: 
	python allocation_strategies/plot_resources.py trimodal

bimodal_small_std: bimodal_small_std_get_results bimodal_small_std_get_plots

bimodal_small_std_get_results: 
	python allocation_strategies/eval_alloc_strats.py bimodal_small_std

bimodal_small_std_get_plots: 
	python allocation_strategies/plot_resources.py bimodal_small_std

