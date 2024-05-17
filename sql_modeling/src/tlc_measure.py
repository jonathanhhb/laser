import pdb
# Import a model
#import laser_numpy_mode.sir_numpy as model
import sir_numpy_c as model
import numpy as np
from copy import deepcopy
import time

import settings
import demographics_settings
#from laser_numpy_model import report
import report

#report.write_report = True # sometimes we want to turn this off to check for non-reporting bottlenecks
# fractions = {}
report_births = {}
#report_deaths = {}
transmission_time = 0
pre_transmission_time = 0
prog_infs_time = 0
prog_imms_time = 0
new_infs_time = 0
post_transmission_time = 0
report_time = 0
vd_time = 0
mig_time = 0
iv_time = 0
ani_time = 0
import_time = 0
wtr_time = 0

new_infections_empty = {}
for i in range(demographics_settings.num_nodes):
    new_infections_empty[ i ] = 0

def collect_and_report(csvwriter, timestep, ctx):
    #currently_infectious, currently_exposed, currently_sus, cur_reco = model.collect_report( ctx )
    currently_infectious, currently_sus, cur_reco = model.collect_report( ctx )
    counts = {
            #"S": deepcopy( currently_sus ),
            "S": currently_sus,
            #"E": deepcopy( currently_exposed ),
            #"I": deepcopy( currently_infectious ),
            "I": currently_infectious,
            #"R": deepcopy( cur_reco ) 
            "R": cur_reco 
        }
    #print( f"Counts =\nS:{counts['S']}\nI:{counts['I']}\nR:{counts['R']}" )
    def calculate_totals(sus, inf, rec):
        #return {idx: sus[idx] + inf[idx] + rec[idx] for idx in sus}
        totals = {}
        for idx in sus.keys():  # Assuming all dictionaries have the same keys
            totals[idx] = sus[idx] + inf[idx] + rec[idx]
        return totals
    totals = calculate_totals( currently_sus, currently_infectious, cur_reco )

    #print( counts["S"][10] )
    start_time = time.time()
    try:
        report.write_timestep_report( csvwriter, timestep, counts["I"], counts["S"], counts["R"], new_births=report_births, new_deaths={} )
        #report.write_timestep_report( csvwriter, timestep, counts["I"], counts["E"], counts["S"], counts["R"], new_births=report_births, new_deaths={} )
    except Exception as ex:
        raise ValueError( f"Exception {ex} at timestep {timestep} and counts {counts['I']}, {counts['S']}, {counts['R']}" )
    end_time = time.time()
    global wtr_time
    wtr_time += (end_time-start_time)
    return counts, totals

def run_simulation(ctx, csvwriter, num_timesteps, sm=-1, bi=-1, mf=-1):
    counts, totals = collect_and_report(csvwriter,0, ctx)
    global transmission_time, pre_transmission_time, post_transmission_time, prog_infs_time, prog_imms_time, new_infs_time, report_time, vd_time, mig_time, iv_time, ani_time, import_time

    if sm==-1:
        sm = settings.seasonal_multiplier
    if bi==-1:
        bi = settings.base_infectivity
    if mf==-1:
        mf = settings.migration_fraction

    for timestep in range(1, num_timesteps + 1):
        if timestep==settings.burnin_delay:
            transmission_time = 0
            pre_transmission_time = 0
            prog_infs_time = 0
            prog_imms_time = 0
            new_infs_time = 0
            post_transmission_time = 0
            report_time = 0
            vd_time = 0
            mig_time = 0
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
        end_time = time.time()
        prog_imms_time += (end_time-start_time)
        start_time = end_time

        # The core transmission part begins
        if timestep>settings.burnin_delay:
            new_infections = list()
            if sum( counts["I"].values() ) > 0:
                #new_infections = model.calculate_new_infections( ctx, fractions["I"], fractions["S"], totals, timestep, seasonal_multiplier=sm, base_infectivity=bi )
                new_infections = model.calculate_new_infections( ctx, counts["I"], counts["S"], totals, timestep, seasonal_multiplier=sm, base_infectivity=bi )
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
        if timestep>settings.burnin_delay and demographics_settings.num_nodes>1:
            ctx = model.migrate( ctx, timestep, migration_fraction=mf )
        end_time = time.time()
        mig_time += (end_time-start_time)
        start_time = end_time

        # if we have had total fade-out, inject imports
        #if timestep>settings.burnin_delay and (sum(counts["I"].values()) == 0+sum(counts["E"].values()) == 0) and settings.import_cases > 0:
        if timestep>settings.burnin_delay and (sum(counts["I"].values()) == 0) and settings.import_cases > 0:
            print( f"Injecting {settings.import_cases} new cases into node {settings.num_nodes-1}." )
            #model.inject_cases( ctx, timestep=timestep, import_cases=settings.import_cases, import_node=507 )
            def divide_and_round(susceptibles):
                for node, count in susceptibles.items():
                    susceptibles[node] = round(count / 80)
                return list(susceptibles.values())
            import_cases = np.array(divide_and_round( counts["S"] ), dtype=np.uint32)
            model.handle_transmission( ctx, import_cases, counts["S"] )
            #for node in range(demographics_settings.num_nodes):
            #    import_cases = int(counts["S"][node]/80)
            #    model.inject_cases( ctx, sus=counts["S"], import_cases=import_cases, import_node=node )
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
        counts, totals = collect_and_report(csvwriter,timestep,ctx)
        end_time = time.time()
        #post_transmission_time += (end_time-start_time)
        #end_time = time.time()
        report_time += (end_time-start_time)
        start_time = end_time
        

    print(f"Simulation completed. Report saved to '{settings.report_filename}'.")
    print(f"transmission_time = {transmission_time}" )
    #print(f"pre_transmission_time = {pre_transmission_time}" )
    print(f"prog_infs_time = {prog_infs_time}" )
    print(f"prog_imms_time = {prog_imms_time}" )
    print(f"new_infs_time = {new_infs_time}" )
    print(f"report_time = {report_time}" )
    print(f"vd_time = {vd_time}" )
    print(f"mig_time (include garg collect) = {mig_time}" )
    print(f"iv_time = {iv_time}" )
    print(f"ani_time = {ani_time}" )
    print(f"import_time = {import_time}" )
    print(f"wtr_time = {wtr_time}" )
    print(f"s_to_i_swap_time = {model.s_to_i_swap_time}" )
    print(f"i_to_r_swap_time = {model.i_to_r_swap_time}" )
    print(f"cr_time = {model.cr_time}" )
    print(f"eula_reco_time = {model.eula_reco_time}" )
    print(f"Total infecteds = {model.infecteds}, total recovereds = {model.recovereds}" )

    #print(f"post_transmission_time = {post_transmission_time}" )

# Main simulation
if __name__ == "__main__":
    # Initialize the 'database' (or load the dataframe/csv)
    # ctx might be db cursor or dataframe or dict of numpy vectors
    ctx = model.initialize_database()
    #ctx = model.init_db_from_csv( settings )
    ctx = model.eula_init( ctx, demographics_settings.eula_age )

    csv_writer = report.init()

    # Run the simulation for 1000 timesteps
    from functools import partial
    runsim = partial( run_simulation, ctx=ctx, csvwriter=csv_writer, num_timesteps=settings.duration )
    from timeit import timeit
    runtime = timeit( runsim, number=1 )
    print( f"Execution time = {runtime}." )

    import post_proc
    post_proc.analyze()

