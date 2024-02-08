# Pop & Nodes if building pop from params
pop = int(5e6)+1
num_nodes = 60
nodes = [ x for x in range(num_nodes) ]

# Filenames if loading pop from file
#pop_file="pop_1M_25nodes_seeded.csv"
#pop_file_out=f"pop_{int(pop/1e6)}M_{num_nodes}nodes_seeded.csv"
#pop_file_out=f"pop_{int(pop/1e6)}M_seeded.csv"
pop_file_out=f"full_pop_seeded.csv"
pop_file="modeled_pop.csv"
eula_file="eula_pop.csv"

report_filename="simulation_output.csv"

# numerical runtime config params
duration = 20*365 # 900
base_infectivity = 1e7
cbr=17
expansion_slots=2e6
campaign_day=6000
migration_interval=7
campaign_coverage=0
campaign_node=1
eula_age=5

