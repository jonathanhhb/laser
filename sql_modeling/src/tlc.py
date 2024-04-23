import pdb
# Import a model
#import laser_numpy_mode.sir_numpy as model
import sir_numpy_c as model
from copy import deepcopy
import time

import settings
#from laser_numpy_model import report
import report

report.write_report = True # sometimes we want to turn this off to check for non-reporting bottlenecks
# fractions = {}
report_births = {}
#report_deaths = {}
transmission_time = 0
pre_transmission_time = 0
prog_infs_time = 0
new_infs_time = 0
post_transmission_time = 0
report_time = 0
vd_time = 0
mig_time = 0
vd_time = 0
iv_time = 0
ani_time = 0
import_time = 0
wtr_time = 0

new_infections_empty = {}
for i in range(settings.num_nodes):
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
    #print( fractions["S"][10] )
    #print( counts["S"][10] )
    start_time = time.time()
    try:
        #report.write_timestep_report( csvwriter, timestep, counts["I"], counts["S"], counts["R"], new_births=report_births, new_deaths={} )
        report.write_timestep_report( csvwriter, timestep, counts["I"], counts["S"], counts["R"], new_births=report_births, new_deaths={} )
    except Exception as ex:
        raise ValueError( f"Exception {ex} at timestep {timestep} and counts {counts['I']}, {counts['S']}, {counts['R']}" )
    end_time = time.time()
    global wtr_time
    wtr_time += (end_time-start_time)
    return counts, fractions, totals

def run_simulation(ctx, csvwriter, num_timesteps, sm=1.0, bi=100, mf=0.01):
    counts, fractions, totals = collect_and_report(csvwriter,0, ctx)
    global transmission_time, pre_transmission_time, post_transmission_time, prog_infs_time, new_infs_time, report_time, vd_time, mig_time, vd_time, iv_time, ani_time, import_time

    for timestep in range(1, num_timesteps + 1):
        if timestep==1000:
            transmission_time = 0
            pre_transmission_time = 0
            prog_infs_time = 0
            new_infs_time = 0
            post_transmission_time = 0
            report_time = 0
            vd_time = 0
            mig_time = 0
            vd_time = 0
            iv_time = 0
            ani_time = 0
            import_time = 0
            wtr_time = 0

        start_time = time.time()
        # We should always be in a low prev setting so this should only really ever operate
        # on ~1% of the active population
        ctx = model.progress_infections( ctx, timestep, sum(counts["I"].values()) )
        end_time = time.time()
        prog_infs_time += (end_time-start_time)
        start_time = end_time

        # The perma-immune should not consume cycles but there could be lots of waning immune
        ctx = model.progress_immunities( ctx )

        # The core transmission part begins
        if timestep>settings.burnin_delay:
            new_infections = list()
            if sum( fractions["I"].values() ) > 0:
                new_infections = model.calculate_new_infections( ctx, fractions["I"], fractions["S"], totals, timestep, seasonal_mutiplier=sm, base_infectivity=bi )
                report.new_infections = new_infections 
            #print( f"new_infections=\n{new_infections}" )

            # TBD: for loop should probably be implementation-specific
            end_time = time.time()
            new_infs_time += (end_time-start_time)
            start_time = end_time
            if sum( new_infections ) > 0:
                ctx = model.handle_transmission( ctx, new_infections, counts["S"] )
                end_time = time.time()
                transmission_time += (end_time-start_time)
                start_time = end_time

                ctx = model.add_new_infections( ctx )
                end_time = time.time()
                ani_time += (end_time-start_time)
                start_time = end_time

            ctx = model.distribute_interventions( ctx, timestep )
            end_time = time.time()
            iv_time += (end_time-start_time)
            start_time = end_time

        # Transmission is done, now migrate some. Only infected?
        if timestep>settings.burnin_delay and settings.num_nodes>1:
            ctx = model.migrate( ctx, timestep, migration_fraction=mf )
        end_time = time.time()
        mig_time += (end_time-start_time)
        start_time = end_time

        # if we have had total fade-out, inject imports
        if timestep>settings.burnin_delay and sum(counts["I"].values()) == 0 and settings.import_cases > 0:
            print( f"Injecting {settings.import_cases} new cases into node {settings.num_nodes-1}." )
            #model.inject_cases( ctx, timestep=timestep, import_cases=settings.import_cases, import_node=507 )
            for node in range(settings.num_nodes):
                model.inject_cases( ctx, sus=counts["S"], import_cases=settings.import_cases, import_node=node )
        end_time = time.time()
        import_time += (end_time-start_time)
        start_time = end_time

        # We almost certainly won't waste time updating everyone's ages every timestep but this is 
        # here as a placeholder for "what if we have to do simple math on all the rows?"
        global report_births, report_deaths 
        ( report_births, report_deaths ) = model.update_ages( ctx, totals, timestep )
        #model.update_ages( ctx, totals, timestep )
        end_time = time.time()
        vd_time += (end_time-start_time)
        start_time = end_time

        # Report
        counts, fractions, totals = collect_and_report(csvwriter,timestep,ctx)
        end_time = time.time()
        post_transmission_time += (end_time-start_time)
        end_time = time.time()
        report_time += (end_time-start_time)
        start_time = end_time
        

    print(f"Simulation completed. Report saved to '{settings.report_filename}'.")
    print(f"transmission_time = {transmission_time}" )
    #print(f"pre_transmission_time = {pre_transmission_time}" )
    print(f"prog_infs_time = {prog_infs_time}" )
    print(f"new_infs_time = {new_infs_time}" )
    print(f"report_time = {report_time}" )
    #print(f"vd_time = {vd_time}" )
    #print(f"mig_time = {mig_time}" )
    #print(f"vd_time = {vd_time}" )
    #print(f"iv_time = {iv_time}" )
    #print(f"ani_time = {ani_time}" )
    #print(f"import_time = {import_time}" )
    print(f"wtr_time = {wtr_time}" )
    print(f"s_to_i_swap_time = {model.s_to_i_swap_time}" )
    print(f"i_to_r_swap_time = {model.i_to_r_swap_time}" )
    print(f"Total infecteds = {model.infecteds}, total recovereds = {model.recovereds}" )

    #print(f"post_transmission_time = {post_transmission_time}" )

# Main simulation
if __name__ == "__main__":
    # Initialize the 'database' (or load the dataframe/csv)
    # ctx might be db cursor or dataframe or dict of numpy vectors
    ctx = model.initialize_database()
    #ctx = model.init_db_from_csv( settings )
    ctx = model.eula_init( ctx, settings.eula_age )

    csv_writer = report.init()

    # Run the simulation for 1000 timesteps
    from functools import partial
    runsim = partial( run_simulation, ctx=ctx, csvwriter=csv_writer, num_timesteps=settings.duration )
    from timeit import timeit
    runtime = timeit( runsim, number=1 )
    print( f"Execution time = {runtime}." )

    import post_proc
    post_proc.analyze()

