import pandas as pd

burnin = 1000
def analyze():
    # Read the CSV file into a DataFrame
    raw_df = pd.read_csv("simulation_output.csv")

    df = raw_df[raw_df["Timestep"] > burnin]

    # Measure some things based on simulation_output.csv
    # 1) Total new infections per year...

    # Calculate the total number of new infections
    total_new_infections = df["New Infections"].sum()

    # Calculate the number of years
    num_years = ( df["Timestep"].max()-burnin) / 365  # Assuming 365 timesteps per year

    # Calculate the average number of new infections per year
    average_new_infections_per_year = total_new_infections / num_years


    # Filter the DataFrame to include only rows where Node is 507 (London)
    df_london = df[df["Node"] == 507]

    # Calculate the total number of new infections in London
    total_new_infections_london = df_london["New Infections"].sum()

    # Calculate the average number of new infections in London per year
    average_new_infections_per_year_london = total_new_infections_london / num_years


    # Create a DataFrame with the metric and its value
    data = {
        "metric": ["mean_new_infs_per_year", "mean_new_infs_per_year_london"],
        "value": [average_new_infections_per_year, average_new_infections_per_year_london]
    }
    report_df = pd.DataFrame(data)

    # Write the DataFrame to a CSV file
    report_df.to_csv("metrics.csv", index=False)
