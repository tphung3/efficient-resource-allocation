all: colmena hypersweep normal_large normal_small uniform_large uniform_small exponential bimodal trimodal bimodal_small_std trimodal_small_std bioblast lobsterCMSsimulation lobsterCMSanalysis 

colmena: colmena_lv2 colmena_lv3 

hypersweep: hypersweep_lv2 hypersweep_lv3 

normal_large: normal_large_lv2 normal_large_lv3 

normal_small: normal_small_lv2 normal_small_lv3 

uniform_large: uniform_large_lv2 uniform_large_lv3 

uniform_small: uniform_small_lv2 uniform_small_lv3 

exponential: exponential_lv2 exponential_lv3 

bimodal: bimodal_lv2 bimodal_lv3 

trimodal: trimodal_lv2 trimodal_lv3 

bimodal_small_std: bimodal_small_std_lv2 bimodal_small_std_lv3 

trimodal_small_std: trimodal_small_std_lv2 trimodal_small_std_lv3 

bioblast: bioblast_lv2 bioblast_lv3 

lobsterCMSsimulation: lobsterCMSsimulation_lv2 lobsterCMSsimulation_lv3 

lobsterCMSanalysis: lobsterCMSanalysis_lv2 lobsterCMSanalysis_lv3 

colmena_lv2: colmena_lv2_get_resources colmena_lv2_get_results colmena_lv2_get_plots

colmena_lv2_get_resources: 
	python allocation_strategies/lv2/read_summary_log.py colmena

colmena_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py colmena

colmena_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py colmena

colmena_lv3: colmena_lv3_get_resources colmena_lv3_get_results colmena_lv3_get_plots

colmena_lv3_get_resources: 
	python allocation_strategies/lv3/read_summary_log.py colmena

colmena_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py colmena

colmena_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py colmena

hypersweep_lv2: hypersweep_lv2_get_resources hypersweep_lv2_get_results hypersweep_lv2_get_plots

hypersweep_lv2_get_resources: 
	python allocation_strategies/lv2/read_summary_log.py hypersweep

hypersweep_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py hypersweep

hypersweep_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py hypersweep

hypersweep_lv3: hypersweep_lv3_get_resources hypersweep_lv3_get_results hypersweep_lv3_get_plots

hypersweep_lv3_get_resources: 
	python allocation_strategies/lv3/read_summary_log.py hypersweep

hypersweep_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py hypersweep

hypersweep_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py hypersweep

normal_large_lv2: normal_large_lv2_get_results normal_large_lv2_get_plots

normal_large_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py normal_large

normal_large_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py normal_large

normal_large_lv3: normal_large_lv3_get_results normal_large_lv3_get_plots

normal_large_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py normal_large

normal_large_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py normal_large

normal_small_lv2: normal_small_lv2_get_results normal_small_lv2_get_plots

normal_small_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py normal_small

normal_small_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py normal_small

normal_small_lv3: normal_small_lv3_get_results normal_small_lv3_get_plots

normal_small_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py normal_small

normal_small_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py normal_small

uniform_large_lv2: uniform_large_lv2_get_results uniform_large_lv2_get_plots

uniform_large_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py uniform_large

uniform_large_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py uniform_large

uniform_large_lv3: uniform_large_lv3_get_results uniform_large_lv3_get_plots

uniform_large_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py uniform_large

uniform_large_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py uniform_large

uniform_small_lv2: uniform_small_lv2_get_results uniform_small_lv2_get_plots

uniform_small_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py uniform_small

uniform_small_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py uniform_small

uniform_small_lv3: uniform_small_lv3_get_results uniform_small_lv3_get_plots

uniform_small_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py uniform_small

uniform_small_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py uniform_small

exponential_lv2: exponential_lv2_get_results exponential_lv2_get_plots

exponential_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py exponential

exponential_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py exponential

exponential_lv3: exponential_lv3_get_results exponential_lv3_get_plots

exponential_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py exponential

exponential_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py exponential

bimodal_lv2: bimodal_lv2_get_results bimodal_lv2_get_plots

bimodal_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py bimodal

bimodal_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py bimodal

bimodal_lv3: bimodal_lv3_get_results bimodal_lv3_get_plots

bimodal_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py bimodal

bimodal_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py bimodal

trimodal_lv2: trimodal_lv2_get_results trimodal_lv2_get_plots

trimodal_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py trimodal

trimodal_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py trimodal

trimodal_lv3: trimodal_lv3_get_results trimodal_lv3_get_plots

trimodal_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py trimodal

trimodal_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py trimodal

bimodal_small_std_lv2: bimodal_small_std_lv2_get_results bimodal_small_std_lv2_get_plots

bimodal_small_std_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py bimodal_small_std

bimodal_small_std_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py bimodal_small_std

bimodal_small_std_lv3: bimodal_small_std_lv3_get_results bimodal_small_std_lv3_get_plots

bimodal_small_std_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py bimodal_small_std

bimodal_small_std_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py bimodal_small_std

trimodal_small_std_lv2: trimodal_small_std_lv2_get_results trimodal_small_std_lv2_get_plots

trimodal_small_std_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py trimodal_small_std

trimodal_small_std_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py trimodal_small_std

trimodal_small_std_lv3: trimodal_small_std_lv3_get_results trimodal_small_std_lv3_get_plots

trimodal_small_std_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py trimodal_small_std

trimodal_small_std_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py trimodal_small_std

bioblast_lv2: bioblast_lv2_get_results bioblast_lv2_get_plots

bioblast_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py bioblast

bioblast_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py bioblast

bioblast_lv3: bioblast_lv3_get_results bioblast_lv3_get_plots

bioblast_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py bioblast

bioblast_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py bioblast

lobsterCMSsimulation_lv2: lobsterCMSsimulation_lv2_get_results lobsterCMSsimulation_lv2_get_plots

lobsterCMSsimulation_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py lobsterCMSsimulation

lobsterCMSsimulation_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py lobsterCMSsimulation

lobsterCMSsimulation_lv3: lobsterCMSsimulation_lv3_get_results lobsterCMSsimulation_lv3_get_plots

lobsterCMSsimulation_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py lobsterCMSsimulation

lobsterCMSsimulation_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py lobsterCMSsimulation

lobsterCMSanalysis_lv2: lobsterCMSanalysis_lv2_get_results lobsterCMSanalysis_lv2_get_plots

lobsterCMSanalysis_lv2_get_results: 
	python allocation_strategies/lv2/eval_alloc_strats.py lobsterCMSanalysis

lobsterCMSanalysis_lv2_get_plots: 
	python allocation_strategies/lv2/plot_resources.py lobsterCMSanalysis

lobsterCMSanalysis_lv3: lobsterCMSanalysis_lv3_get_results lobsterCMSanalysis_lv3_get_plots

lobsterCMSanalysis_lv3_get_results: 
	python allocation_strategies/lv3/eval_alloc_strats.py lobsterCMSanalysis

lobsterCMSanalysis_lv3_get_plots: 
	python allocation_strategies/lv3/plot_resources.py lobsterCMSanalysis

clean:
	rm resource_analysis/*/plots/*; rm resource_analysis/*/results/*