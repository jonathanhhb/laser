import csv
import sir_sql as model
import settings

def init_report():
    # Create a CSV file for reporting
    csvfile = open( settings.report_filename, 'w', newline='') 
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Timestep', 'Node', 'Susceptible', 'Infected', 'Recovered'])
    return csvwriter

def run_simulation(ctx, csvwriter, num_timesteps):
    currently_infectious, currently_sus = model.report( ctx, 0, csvwriter )

    for timestep in range(1, num_timesteps + 1):
        model.update_ages( ctx )

        model.progress_infections( ctx )

        model.progress_immunities( ctx )

        new_infections = model.calculate_new_infections( ctx, currently_infectious, currently_sus )

        for node in settings.nodes:
            model.handle_transmission( ctx, new_infections[node], node )

        model.add_new_infections( ctx )
        model.migrate( ctx, timestep )
        #conn.commit() # deb-specific
        currently_infectious, currently_sus = model.report( ctx, timestep, csvwriter )

    print("Simulation completed. Report saved to 'simulation_report.csv'.")

# Main simulation
if __name__ == "__main__":
    # Initialize the database
    ctx = model.initialize_database()

    csv_writer = init_report()

    # Run the simulation for 1000 timesteps
    run_simulation(ctx, csv_writer, num_timesteps=settings.duration )
