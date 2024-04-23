import pandas as pd
import pdb

burnin = 1000
def analyze_ccs():
    from scipy.stats import binom
    import pandas as pd

    # Load the CSV file
    cases_df = pd.read_csv('simulation_output.csv')

    # Set the parameters for the binomial distribution
    num_trials = cases_df['New Infections']  # Number of trials (events)
    prob_success = 0.5  # Probability of success (observation)

    cases_df['Observed Infections'] = binom.rvs(num_trials, prob_success)
   
    # Load the cities.csv file into a DataFrame
    cities_df = pd.read_csv('cities.csv')

    # Merge the cases_df with cities_df based on the 'node' column
    merged_df = pd.merge(cases_df, cities_df, left_on='Node', right_on='ID')

    # Load the pops.csv file into a DataFrame
    pops_df = pd.read_csv('pops.csv')
    pops_df = pops_df[pops_df['Timestep'] == 1954]
    pops_df['ID'] = pops_df.reset_index().index

    # Merge the merged_df with pops_df based on the 'name' column
    #merged_df = pd.merge(merged_df, pops_df, on=['Timestep', 'Name'])

    # Filter the merged DataFrame based on the condition
    filtered_df = merged_df[(merged_df['Timestep'] == 1954)]

    # Group by 'ID' and calculate the fraction of time Observed Infections is 0
    #fraction_nonzero = filtered_df.groupby('ID')['Observed Infections'].apply(lambda x: (x == 0).mean()).reset_index()
    fraction_nonzero = merged_df.groupby('ID').apply(lambda group: (group['Observed Infections'] == 0).mean()).reset_index()

    # Rename the column to 'Fraction_NonZero_New_Infections'
    fraction_nonzero.columns = ['ID', 'Fraction_NonZero_New_Infections']

    # Sort the DataFrame by 'Fraction_NonZero_New_Infections'
    sorted_df = fraction_nonzero.sort_values(by='Fraction_NonZero_New_Infections')
    sorted_df = pd.merge(sorted_df, pops_df, on='ID')
    #print( sorted_df )

    # Select the rows corresponding to the specified cities
    cities = ['London', 'Birmingham', 'Liverpool', 'Manchester', 'Leeds']
    city_rows = sorted_df.loc[sorted_df['Name'].isin(cities)]

    # Calculate the mean of 'Fraction_NonZero_New_Infections' for the selected cities
    mean_fraction = city_rows['Fraction_NonZero_New_Infections'].mean()
    return mean_fraction 



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

    ccs_mean = analyze_ccs()

    # Create a DataFrame with the metric and its value
    data = {
        "metric": ["mean_new_infs_per_year", "mean_new_infs_per_year_london", "mean_ccs_fraction_big_cities"],
        "value": [average_new_infections_per_year, average_new_infections_per_year_london, ccs_mean ]
    }
    report_df = pd.DataFrame(data)

    # Write the DataFrame to a CSV file
    report_df.to_csv("metrics.csv", index=False)

