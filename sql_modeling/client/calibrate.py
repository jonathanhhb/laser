#from optuna.trial.Trial import suggest_float
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import optuna
import requests
import pdb

url = 'http://10.24.14.21:5000/submit'
#url = 'http://172.19.0.2:5000/submit'

# Load reference/target values from metrics_ref.csv
reference_values = pd.read_csv('metrics_ref.csv', index_col='metric').to_dict()['value']

# Define the objective function to minimize the difference between simulated and reference values
def objective(trial):
    # Define the ranges for the parameters A, B, and C
    base_infectivity = trial.suggest_float('base_infectivity', 0.1, 5.0)
    migration_fraction = 0 # trial.suggest_float('migration_fraction', 0.005, 0.10)
    seasonal_multiplier = trial.suggest_float('seasonal_multiplier', 0.5, 2.5)

    # Simulate the disease model with the chosen parameters and obtain the metrics
    # Replace this with your actual simulation code
    simulated_values = simulate_disease_model(base_infectivity, migration_fraction, seasonal_multiplier)
    print( f"simulated_values = {simulated_values}" )

    # Construct DataFrame from simulated values dictionary
    #sim_vals_df = pd.DataFrame.from_dict(simulated_values, orient='index', columns=['value']) 
    # Convert 'value' column to numeric type
    #sim_vals_df['value'] = pd.to_numeric(sim_vals_df['value'], errors='coerce')
    #print( f"sim_vals_df = {sim_vals_df}." )
    print( f"reference_values = {reference_values}." )

    # Calculate the difference between simulated and reference values
    #diff = sim_vals_df['value'] - reference_values['value']

    weights = {
        "mean_ccs_fraction_big_cities": 4.0,  # Adjust the weight factor as needed
        # Add weights for other metrics if necessary
    }
    diffs = []
    #pdb.set_trace()
    #for i in range(len(ref_values)):
    err = 0
    for metric in reference_values:
        ref_val = float(reference_values[metric])
        if metric in weights:
            weight = weights[metric]
        else:
            weight = 1.0  # Default weight if not specified

        if ref_val > 100:
            diff = 1 - float(simulated_values[metric]) / ref_val
        else:
            diff = np.fabs(float(simulated_values[metric]) - ref_val)
        #diff *= weight
        err += weight * np.abs(diff)
        #diffs.append(diff)

    print( f"err={err}." )

    # Calculate the objective score (sum of absolute differences)
    objective_score = err # np.abs(diff).sum()
    print( f"objective_score={objective_score}" )

    return objective_score

# Function to simulate the disease model with given parameters
def simulate_disease_model(base_infectivity, migration_fraction, seasonal_multiplier):
    # Replace this with your actual simulation code
    # This is just a placeholder
    try:
        parameters = {}
        parameters['base_infectivity'] = base_infectivity 
        parameters['migration_fraction'] = migration_fraction 
        parameters['seasonal_multiplier'] = seasonal_multiplier 
        print( parameters )
        response = requests.post(url, json=parameters, timeout=3600)
        print( response.content )
        if response.status_code == 200:
            sim_values = response.json()
            print( f"sim_values={sim_values}." )
            return sim_values
        else:
            # Print an error message if the request was not successful
            print("Error:", response.status_code)
            return float('inf')
    except Exception as ex:
        print( f"Model crashed: {ex}." )
        return float('inf')

if __name__ == "__main__":
    # Create a study object and optimize the objective function
    study = optuna.create_study(
            direction='minimize',
            study_name="no-name-72844ae3-8812-4fd1-8ae6-73de3cd35485",
            storage='sqlite:///laser_ew.db',
            load_if_exists=True
        )
    study.optimize(objective, n_trials=100)

    # Print the best parameters found
    print("Best parameters:", study.best_params)

    # Save the best parameters and corresponding simulated values to metrics.csv
    #best_values = simulate_disease_model(**study.best_params)
    #best_values.to_csv('calibrated.csv')

    # Plot optimization history
    optuna.visualization.plot_optimization_history(study)
    plt.show()

    # Plot slice plot
    optuna.visualization.plot_slice(study)
    plt.show()

    # Plot parallel coordinate plot
    optuna.visualization.plot_parallel_coordinate(study)
    plt.show()

    # Plot parameter importance
    optuna.visualization.plot_param_importances(study)
    plt.show()
