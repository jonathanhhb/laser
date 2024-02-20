# Pop & Nodes if building pop from params
pop = int(5e5)+1
num_nodes = 60 
nodes = [ x for x in range(num_nodes) ]
# Epidemiologically Useless Light Agents
eula_age=5

# Filenames if loading pop from file
#pop_file="pop_1M_25nodes_seeded.csv"
#pop_file="age_lt_5.csv"
pop_file="sorted_by_age.csv"
eula_file="eula_pop.csv"
#pop_file_out=f"pop_{int(pop/1e6)}M_{num_nodes}nodes_seeded.csv"
#pop_file_out=f"pop_{int(pop/1e6)}M_seeded.csv"
pop_file_out=f"pop_seeded.csv"

report_filename="simulation_output.csv"

# numerical runtime config params
# simulation duration
duration = 20*365 # 900
base_infectivity = 1.5e4
# cbr=crude bith rate
cbr=26
# number of babies we expect to be born
expansion_slots=3e6
campaign_day=60
campaign_coverage=0.25
campaign_node=15
migration_interval=7
mortality_interval=30
fertility_interval=14
ria_interval=7
