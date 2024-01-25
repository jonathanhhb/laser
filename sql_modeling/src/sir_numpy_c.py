import random
import csv
import numpy as np
import concurrent.futures
from functools import partial
import numba
import ctypes
import pdb

import settings
import report

# Load the shared library
update_ages_lib = ctypes.CDLL('./update_ages.so')
# Define the function signature
update_ages_lib.update_ages.argtypes = [
    ctypes.c_size_t,  # n
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS')
]
update_ages_lib.progress_infections.argtypes = [
    ctypes.c_size_t,  # n
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # infection_timer
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # incubation_timer
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # infected
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # immunity_timer
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # immunity
]
update_ages_lib.progress_immunities.argtypes = [
    ctypes.c_size_t,  # n
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # immunity_timer
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # immunity
]
update_ages_lib.calculate_new_infections.argtypes = [
    ctypes.c_size_t,  # n
    ctypes.c_size_t,  # n
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'),  # nodes
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # incubation_timer
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # inf_counts
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # sus_counts
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # tot_counts
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'),  # new_infections
    ctypes.c_float, # base_inf
]
update_ages_lib.handle_new_infections.argtypes = [
    ctypes.c_uint32, # num_agents
    ctypes.c_uint32, # node
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # nodes
    np.ctypeslib.ndpointer(dtype=np.bool_, flags='C_CONTIGUOUS'),  # infected
    np.ctypeslib.ndpointer(dtype=np.bool_, flags='C_CONTIGUOUS'),  # immunity
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'), # incubation_timer
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'), # infection_timer
    ctypes.c_int # num_new_infections
]
update_ages_lib.migrate.argtypes = [
    ctypes.c_uint32, # num_agents
    np.ctypeslib.ndpointer(dtype=np.bool_, flags='C_CONTIGUOUS'),  # infected
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # nodes
]
update_ages_lib.collect_report.argtypes = [
    ctypes.c_uint32, # num_agents
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # nodes
    np.ctypeslib.ndpointer(dtype=np.bool_, flags='C_CONTIGUOUS'),  # infected
    np.ctypeslib.ndpointer(dtype=np.bool_, flags='C_CONTIGUOUS'),  # immunity
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # mcw
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # infection_count_out
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # susceptible_count_out
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # recovered_count_out
]

def load( pop_file ):
    """
    Load population from csv file as np arrays. Each property column is an np array.
    """
    # Load the entire CSV file into a NumPy array
    header_row = np.genfromtxt(pop_file, delimiter=',', dtype=str, max_rows=1)

    # Load the remaining data as numerical values, skipping the header row
    data = np.genfromtxt(pop_file, delimiter=',', dtype=float, skip_header=1)

    # Extract headers from the header row
    headers = header_row

    # Load each column into a separate NumPy array
    columns = {header: data[:, i] for i, header in enumerate(headers)}
    columns['infected'] = columns['infected'].astype(bool)
    columns['immunity'] = columns['immunity'].astype(bool)
    columns['node'] = columns['node'].astype(np.uint32)
    columns['infection_timer'] = columns['infection_timer'].astype(np.float32) # int better?
    columns['incubation_timer'] = columns['incubation_timer'].astype(np.float32) # int better?
    columns['immunity_timer'] = columns['immunity_timer'].astype(np.float32) # int better?
    columns['age'] = columns['age'].astype(np.float32)
    columns['mcw'] = columns['mcw'].astype(np.uint32)

    settings.pop = len(columns['infected'])
    print( f"Population={settings.pop}" )
    settings.nodes = [ node for node in np.unique(columns['node']) ]
    settings.num_nodes = len(settings.nodes)
    print( f"Nodes={settings.num_nodes}" )
    # Now 'columns' is a dictionary where keys are column headers and values are NumPy arrays
    import sir_numpy
    sir_numpy.add_expansion_slots( columns, num_slots=settings.expansion_slots )
    return columns

def initialize_database():
    return load( settings.pop_file )

def eula( ctx, age_threshold_yrs = 5, eula_strategy=None ):
    # For now just use numpy version
    import sir_numpy
    return sir_numpy.eula( ctx, age_threshold_yrs, eula_strategy )

def collect_report( data ):
    """
    Report data to file for a given timestep.
    """
    #print( "Start timestep report." )
    def collect_report_c():
        infected_counts_raw = np.zeros( settings.num_nodes ).astype( np.uint32 )
        susceptible_counts_raw = np.zeros( settings.num_nodes ).astype( np.uint32 )
        recovered_counts_raw = np.zeros( settings.num_nodes ).astype( np.uint32 )

        update_ages_lib.collect_report(
                len( data['node'] ),
                data['node'],
                data['infected'],
                data['immunity'],
                data['mcw'],
                infected_counts_raw,
                susceptible_counts_raw,
                recovered_counts_raw
        )

        susceptible_counts = dict(zip(settings.nodes, susceptible_counts_raw))
        infected_counts = dict(zip(settings.nodes, infected_counts_raw))
        recovered_counts = dict(zip(settings.nodes, recovered_counts_raw))
        #print( f"Reporting back SIR counts of\n{susceptible_counts},\n{infected_counts}, and\n{recovered_counts}." )
        return infected_counts, susceptible_counts, recovered_counts
    return collect_report_c()

def update_ages( data, totals ):
    def update_ages_c( ages ):
        update_ages_lib.update_ages(len(ages), ages)
        return ages

    #data['age'] = update_ages_c( data['age'] )
    import sir_numpy
    data = sir_numpy.births( data, totals )
    data = sir_numpy.deaths( data )
    return data
    #return update_births_deaths( data )

def update_births_deaths( data ):
    # Births
    # Calculate number of women of child-bearing age: constant across nodes
    # Add new babies as percentage of that.
    # TBD NOT IMPLEMENTED YET
    update_ages_lib.update_ages(len(ages), ages)
    # Non-disease deaths
    return data

def progress_infections( data ):
    # Update infected agents
    # infection timer: decrement for each infected person
    def progress_infections_c( data ):
        update_ages_lib.progress_infections(len(data['age']), data['infection_timer'], data['incubation_timer'], data['infected'], data['immunity_timer'], data['immunity'])
        return

    progress_infections_c( data )
    return data

# Update immune agents
def progress_immunities( data ):
    def progress_immunities_c( data ):
        update_ages_lib.progress_immunities(len(data['age']), data['immunity_timer'], data['immunity'])
        return

    progress_immunities_c( data )
    return data

def calculate_new_infections( data, inf, sus, totals ):
    def calculate_new_infections_c( data, inf, sus ):
        new_infections = np.zeros( len( inf ) ).astype( np.uint32 ) # return variable
        sorted_items = sorted(inf.items())
        #inf_np = np.array([value for _, value in sorted_items]).astype(np.uint32)
        inf_np = np.array([np.float32(value) for _, value in sorted_items])
        sus_np = np.array([np.float32(value) for value in sus.values()])
        tot_np = np.array([np.float32(value) for value in totals.values()])
        update_ages_lib.calculate_new_infections(
                len(data['age']),
                len( inf ),
                data['node'],
                data['incubation_timer'],
                inf_np,
                sus_np,
                tot_np,
                new_infections,
                settings.base_infectivity
            )
        return new_infections 
    return calculate_new_infections_c( data, inf, sus )

def handle_transmission_by_node( data, new_infections, node=0 ):
    # Step 5: Update the infected flag for NEW infectees
    def handle_new_infections_c(new_infections):
        update_ages_lib.handle_new_infections(
                len(data['age']),
                node,
                data['node'],
                data['infected'],
                data['immunity'],
                data['incubation_timer'],
                data['infection_timer'],
                new_infections
            )

    #print( new_infections[node] )
    if new_infections[node]>0:
        handle_new_infections_c(new_infections[node])

    #print( f"{new_infections} new infections in node {node}." )
    return data

def handle_transmission( data_in, new_infections_in ):
    # We want to do this in parallel;
    #print( f"DEBUG: New Infections: {new_infections_in}" )
    htbn = partial( handle_transmission_by_node, data_in, new_infections_in )
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(htbn, settings.nodes))
    return data_in

def add_new_infections( data ):
    # Actually this just sets the new infection timers (globally) for all the new infections
    # New infections themselves are set node-wise
    def add_new_infections_c( data ):
        return data # already done
    data = add_new_infections_c( data )
    return data

def migrate( data, timestep, num_infected=None ):
    # Migrate 1% of infecteds "downstream" every week; coz
    if timestep % 7 == 0: # every week
        def migrate_c():
            update_ages_lib.migrate(
                len(data['age']),
                data['infected'],
                data['node'])
        migrate_c()
    return data

def distribute_interventions( ctx, timestep ):
    import sir_numpy
    return sir_numpy.distribute_interventions( ctx, timestep )

# Function to run the simulation for a given number of timesteps
def run_simulation(data, csvwriter, num_timesteps):
    currently_infectious, currently_sus, cur_reco  = collect_report( data )
    report.write_timestep_report( csvwriter, 0, currently_infectious, currently_sus, cur_reco )

    for timestep in range(1, num_timesteps + 1):
        data = update_ages( data )

        data = progress_infections( data )

        data = progress_immunities( data )

        new_infections = calculate_new_infections( data, currently_infectious, currently_sus )

        data = handle_transmission( data_in=data, new_infections_in=new_infections )

        data = add_new_infections( data )

        data = migrate( data, timestep )

        currently_infectious, currently_sus, cur_reco = collect_report( data )
        report.write_timestep_report( csvwriter, timestep, currently_infectious, currently_sus, cur_reco )


    print("Simulation completed. Report saved to 'simulation_report.csv'.")

# Main simulation
if __name__ == "__main__":
    data = initialize_database()

    # Create a CSV file for reporting
    csvfile = open('simulation_report.csv', 'w', newline='') 
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Timestep', 'Node', 'Susceptible', 'Infected', 'Recovered'])

    # Run the simulation for 1000 timesteps
    run_simulation(data, csvwriter, num_timesteps=settings.duration )

