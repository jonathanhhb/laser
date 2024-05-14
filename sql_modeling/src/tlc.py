import sys
import os

# Append the current working directory to the beginning of sys.path
sys.path.insert(0, os.getcwd())

import pdb
# Import a model
#import laser_numpy_mode.sir_numpy as model
import sir_numpy_c as model
from copy import deepcopy

import settings
import demographics_settings
import report

report.write_report = True # sometimes we want to turn this off to check for non-reporting bottlenecks
# fractions = {}
report_births = {}
#report_deaths = {}

new_infections_empty = {}
for i in range(demographics_settings.num_nodes):
    new_infections_empty[ i ] = 0

def collect_and_report(csvwriter, timestep, ctx):
    currently_infectious, currently_sus, cur_reco = model.collect_report( ctx )
    counts = {
            "S": deepcopy( currently_sus ),
            "I": deepcopy( currently_infectious ),
            "R": deepcopy( cur_reco ) 
        }
    #print( f"Counts =\nS:{counts['S']}\nI:{counts['I']}\nR:{counts['R']}" )
    def normalize( sus, inf, rec ):
        totals = {}
        for idx in currently_sus.keys():
            totals[ idx ] = sus[ idx ] + inf[ idx ] + rec[ idx ]
            if totals[ idx ] > 0:
                sus[ idx ] /= totals[ idx ] 
                inf[ idx ] /= totals[ idx ] 
                rec[ idx ] /= totals[ idx ] 
            else:
                sus[ idx ] = 0
                inf[ idx ] = 0
                rec[ idx ] = 0
        return totals
    totals = normalize( currently_sus, currently_infectious, cur_reco )
    fractions = {
            "S": currently_sus,
            "I": currently_infectious,
            "R": cur_reco 
        }
    try:
        #report.write_timestep_report( csvwriter, timestep, counts["I"], counts["S"], counts["R"], new_births=report_births, new_deaths={} )
        report.write_timestep_report( csvwriter, timestep, counts["I"], counts["S"], counts["R"], new_births=report_births, new_deaths={} )
    except Exception as ex:
        raise ValueError( f"Exception {ex} at timestep {timestep} and counts {counts['I']}, {counts['S']}, {counts['R']}" )
    return counts, fractions, totals

def run_simulation(ctx, csvwriter, num_timesteps, sm=-1, bi=-1, mf=-1):
    counts, fractions, totals = collect_and_report(csvwriter,0, ctx)
    if sm==-1:
        sm = settings.seasonal_multiplier
    if bi==-1:
        bi = settings.base_infectivity
    if mf==-1:
        mf = settings.migration_fraction

    for timestep in range(1, num_timesteps + 1):
        # We should always be in a low prev setting so this should only really ever operate
        # on ~1% of the active population
        ctx = model.progress_infections( ctx, timestep, sum(counts["I"].values()) )

        # The perma-immune should not consume cycles but there could be lots of waning immune
        ctx = model.progress_immunities( ctx )

        # The core transmission part begins
        if timestep>settings.burnin_delay:
            new_infections = list()
            #if sum( fractions["I"].values() ) > 0:
            if sum( counts["I"].values() ) > 0:
                #new_infections = model.calculate_new_infections( ctx, fractions["I"], fractions["S"], totals, timestep, seasonal_multiplier=sm, base_infectivity=bi )
                new_infections = model.calculate_new_infections( ctx, counts["I"], counts["S"], totals, timestep, seasonal_multiplier=sm, base_infectivity=bi )
                report.new_infections = new_infections 
            #print( f"new_infections=\n{new_infections}" )

            # TBD: for loop should probably be implementation-specific
            if sum( new_infections ) > 0:
                ctx = model.handle_transmission( ctx, new_infections, counts["S"] )
                ctx = model.add_new_infections( ctx )

            ctx = model.distribute_interventions( ctx, timestep )

        # Transmission is done, now migrate some. Only infected?
        if timestep>settings.burnin_delay and settings.num_nodes>1:
            ctx = model.migrate( ctx, timestep, migration_fraction=mf )

        # if we have had total fade-out, inject imports
        big_cities=[99,507,492,472,537]
        if timestep>settings.burnin_delay and sum(counts["I"].values()) == 0 and settings.import_cases > 0:
            for node in range(settings.num_nodes):
                #import_cases = int(0.1*counts["S"][node])
                import_cases = int(counts["S"][node]/80.)
                print( f"ELIMINATION Detected: Reeseding: Injecting {import_cases} new cases into node {node}." )
                model.inject_cases( ctx, sus=counts["S"], import_cases=import_cases, import_node=node )
            #model.inject_cases( ctx, sus=counts["S"], import_cases=settings.import_cases, import_node=507 )

        # We almost certainly won't waste time updating everyone's ages every timestep but this is 
        # here as a placeholder for "what if we have to do simple math on all the rows?"
        global report_births, report_deaths 
        ( report_births, report_deaths ) = model.update_ages( ctx, totals, timestep )

        # Report
        counts, fractions, totals = collect_and_report(csvwriter,timestep,ctx)

    print(f"Simulation completed. Report saved to '{settings.report_filename}'.")
    print(f"Total infecteds = {model.infecteds}, total recovereds = {model.recovereds}" )

# Main simulation
if __name__ == "__main__":
    # Initialize the 'database' (or load the dataframe/csv)
    # ctx might be db cursor or dataframe or dict of numpy vectors
    ctx = model.initialize_database()
    ctx = model.eula_init( ctx, demographics_settings.eula_age )

    csv_writer = report.init()

    # Run the simulation for 1000 timesteps
    from functools import partial
    runsim = partial( run_simulation, ctx=ctx, csvwriter=csv_writer, num_timesteps=settings.duration )
    from timeit import timeit
    runtime = timeit( runsim, number=1 )
    print( f"Execution time = {runtime}." )

    #import post_proc
    #post_proc.analyze()

