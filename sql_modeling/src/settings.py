# Pop & Nodes if building pop from params
pop = int(1e7)+1
#num_nodes = 1
#num_nodes = 60
num_nodes = 954
nodes = [ x for x in range(num_nodes) ]
# Epidemiologically Useless Light Agents
eula_age=5

# Filenames if loading pop from file
#pop_file="modeled_pop.csv.gz"
pop_file="engwal_modeled.csv.gz"
#pop_file="pop_1M_1nodes_seeded.csv.gz"
eula_file="ew_eula_binned.csv"
#pop_file_out=f"pop_seeded.csv"
eula_pop_fits="fits.npy"
attraction_probs_file="attraction_probabilities.csv"
report_filename="simulation_output.csv"

# numerical runtime config params
# simulation duration
#duration = 10*365
duration = 20*365
#duration = 2000
#base_infectivity = 0.9e7 # ccs = 55-140k
#base_infectivity = 2e7 # ccs = 55-140k
#base_infectivity = 1e7 # ccs = 30-55k
base_infectivity = 240
# cbr=crude bith rate
cbr=17.5
cbr_file="cbrs.csv"
births_file="births.csv"
# total E&W babies = 12638423
# number of babies we expect to be born
expansion_slots=2e7
#expansion_slots=3e5
campaign_day=6000000
campaign_coverage=0.75

campaign_node=15
migration_fraction=0.2
migration_interval=7
mortality_interval=1 # 30
fertility_interval=1 # 7
ria_interval=700000
burnin_delay=730
import_cases=10

#import numpy as np
#infectivity_multiplier = np.concatenate( (np.linspace( 1,2,366//2), np.linspace( 2,1,366//2)) )
seasonal_multiplier = 0.93
infectivity_multiplier = [0.0, 0.0, 0.06, 0.12, 0.18, 0.24, 0.3, 0.2, 0.1, 0.05, 0.0, 0.05, 0.1, 0.05, 0.0, -0.05000000000000002, -0.1, -0.05, 0.0, 0.05000000000000002, 0.1, 0.05, 0.0, -0.05000000000000002, -0.1, -0.1, -0.15714285714285714, -0.2142857142857143, -0.27142857142857146, -0.3285714285714286, -0.3857142857142857, -0.44285714285714295, -0.5, -0.40625, -0.3125, -0.21875, -0.125, -0.03125, 0.0625, 0.15625, 0.25, 0.225, 0.2, 0.175, 0.15, 0.175, 0.2, 0.1, 0.0, 0.06666666666666667, 0.13333333333333333, 0.20000000000000004]


