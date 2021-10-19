# Efficient Resource Allocation for Scheduling Tasks in Distributed Systems

## Purpose: 
We are experimenting scheduling strategies to allocate resources to workloads with widely different resource consumption between tasks. A side product of the work storing in this repository is a paper accepted to the WORKS workshop 2021 (to be updated later).

## Data:
You can find all synthetic and real datasets under the resources_data directory.

## Usage:
Running `make {dataset}` where dataset is in {colmena, hypersweep, exponential, normal_large, normal_small, bimodal, trimodal, uniform_large, uniform_small} will generate respective results in `resources_analysis/{dataset}/`.

## Note:
4 levels of information: nothing -> number of classes -> tag for each task -> everything

