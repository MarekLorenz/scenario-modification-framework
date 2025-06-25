# Scenario Modification Framework

## An LLM-based approach to improve the Safety Criticality of Driving Scenarios

This is the practical implementation accompanying the work described in my Bachelor's thesis **Risk-Aware Scenario Analysis Based on LLMs
in Autonomous Driving (2025).** 

## What is it used for?

Since safety-critical scenarios are rare, recorded data from the CommonRoad simulation platform can be used to synthesize more safety-critical scenario data, to enable more thorough testing of Motion Planners. For this purpose, we can conduct a safety-critical analysis, which serves as the basis for anb iterative scenario modification.

## Prerequisites

Make sure to have all needed packages listed in the `requirements.txt` installed in your environment.

Fill in the `.env` with the environment variables from the `.env.sample`

## How to use it for one scenario?
### Step 1:
Download a CommonRoad Scenario XML at https://commonroad.in.tum.de/scenarios/.
Then use the [Frenetix Motion Planner](https://github.com/TUM-AVS/Frenetix-Motion-Planner) to generate a planned ego trajectory.

### Step 2:
To analyse and modify a scenario, the file that should be used is `main.py`. The scenario XML from CommonRoad should be stores as follows: `data/scenarios/{scenario_name}.xml` and the corresponding pre-computed ego-trajectory should be stored under `data/ego_trajectories/ego_trajectory_{scenario_name}.csv`.

Now the modification can be run with the following configuration (s ... Scenario name without XML, n ... maximum number of iterations, v ... Visualization true/false?)

For example it can look like this:
`python3 main.py -s BEL_Antwerp-1_9_T-1 -n 3 -v False`

## How to use the framework for multiple scenarios?
### Step 1:
Create a folder with all CommonRoad XML scenarios that you want to modify. Then input them in the Frenetix Motion Planner and extract the newly generated logs folder from Frenetix Motion Planner. 

### Step 2:
Then store the XML scenarios in `data/scenarios` and the logs folder as `data/logs`.

### Step 3:
Run the modification with `python scripts/simulation/run_evaluation.py`. In this file the output directory for the modified scenarios and number of iterations can be specified in the main method.

## Implementation

The implemenation is built on top of [Yuan Gao's Risk-Aware Scenario Analysis](https://github.com/yuangao-tum/Riskaware-Scenario-analyse), especially reusing calculations for safety-critical metrics.

The framework is divided in Scenario Analysis and Scenario Modification, as you can see below.

![image](https://github.com/user-attachments/assets/ae92da7b-2b13-4563-88e9-08666ece567e)


The ouput modifies the scenario to make it more safety-critical, as in the following example producing a collision using the same Motion Planner.
![image](https://github.com/user-attachments/assets/24836eab-c6ac-4806-87d6-24303ba092e5)


## Thesis Abstract

 Safety-critical scenario generation is an important step in testing edge cases of motion planners
for autonomous driving. However, it involves two non-trivial challenges: evaluating the
scenario and, in this case, modifying a recorded one. This work aims to solve both problems
in a time-efficient yet precise way.
This thesis proposes a novel end-to-end framework that leverages Large Language Models
for scenario evaluation and ego-adversarial generation, using a compressed, formalized
scenario description based on Metric Temporal Logic (MTL).
Our findings show that scenario evaluation can be done with 79% accuracy and a median
runtime of less than 7 seconds, demonstrating both effectiveness and efficiency. On the
other hand, scenario generation still struggles with realism, with only few correctly updated
scenarios produced.
This work marks an initial step, and further improvements are needed, especially in
extending the MTL definitions to better capture all aspects of a scenario.

## Experiment Data

The analysis and modification results referenced in the thesis can be found in the folder `data_thesis`, the modified scenarios are in the `data_thesis/analysis_modification` folder and the analysis evaluation can be found in the folder `data_thesis/analysis_evaluation` alongside the ablation study results. 

There are scripts for automatically running a batch of scenarios and analyzing the results of runtime, token count and accuracy in the folder `scripts`.

