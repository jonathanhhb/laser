attraction_probs_file="attraction_probabilities.csv"
report_filename="simulation_output.csv"

# numerical runtime config params
# simulation duration
#duration = 5*365
duration = 20*365
#duration = 2000
#base_infectivity = 0.9e7 # ccs = 55-140k
#base_infectivity = 2e7 # ccs = 55-140k
#base_infectivity = 1e7 # ccs = 30-55k base_infectivity = 0.2 # 372 # cbr=crude bith rate
#base_infectivity = 13.52
base_infectivity = 3.0 # 8.74
cbr=17.5
births_file="births.csv"
# total E&W babies = 12638423
# number of babies we expect to be born
expansion_slots=2e7
#expansion_slots=3e5
campaign_day=6000000
campaign_coverage=0.75

campaign_node=15
migration_fraction=0.098 # 0.10 # 0.013
migration_interval=700000
mortality_interval=1 # 30
fertility_interval=1 # 7
ria_interval=700000
burnin_delay=30 # 365*3
import_cases=3000

#import numpy as np
#infectivity_multiplier = np.concatenate( (np.linspace( 1,2,366//2), np.linspace( 2,1,366//2)) )
seasonal_multiplier = 1 # 2.32 # 1.62
infectivity_multiplier = [0.0, 0.0, 0.06, 0.12, 0.18, 0.24, 0.3, 0.2, 0.1, 0.05, 0.0, 0.05, 0.1, 0.05, 0.0, -0.05000000000000002, -0.1, -0.05, 0.0, 0.05000000000000002, 0.1, 0.05, 0.0, -0.05000000000000002, -0.1, -0.1, -0.15714285714285714, -0.2142857142857143, -0.27142857142857146, -0.3285714285714286, -0.3857142857142857, -0.44285714285714295, -0.5, -0.40625, -0.3125, -0.21875, -0.125, -0.03125, 0.0625, 0.15625, 0.25, 0.225, 0.2, 0.175, 0.15, 0.175, 0.2, 0.1, 0.0, 0.06666666666666667, 0.13333333333333333, 0.20000000000000004]


