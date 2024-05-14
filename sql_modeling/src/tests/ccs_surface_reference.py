import numpy as np
import matplotlib.pyplot as plt
import pdb

def run_disease_model(beta, cbr, init_pop):
    # Define your disease model here
    # Run the model and return True if endemic, False if eliminated
    import numpy as np
    import matplotlib.pyplot as plt
    import sys
    from collections import deque

    # Parameters
    population = init_pop
    #cbr = 17.5  # Crude birth rate per 1000 people per year

    incubation_period = 7  # Incubation period in days
    infectious_period = 7  # Infectious period in days
    simulation_days = 7300  # Number of days to simulate

    # Calculate births per day
    births_per_day = int((population / 1000) * (cbr / 365))

    # Initial values
    #E_queue = deque([1000] * incubation_period)  # Exposed individuals queue
    #E_queue = deque([1000] * incubation_period)  # Exposed individuals queue
    E_queue = deque([5000] + [0] * (incubation_period-1))  # Exposed individuals queue
    I_queue = deque([0] * infectious_period)  # Infectious individuals queue (seeded outbreak)
    S = [int(population/(beta*infectious_period))]
    R = [int(population - S[0] - sum(E_queue) - sum(I_queue))]

    # Make reporting lists for E and I since we're modeling with queues
    E_reporting = [sum(E_queue )]
    I_reporting = [sum(I_queue )]
    NI = [0]

    # Simulation
    strikes = 0
    def get_beta( t ):
        # Define parameters
        period = 365
        minimum = 0.75
        maximum = 1/minimum
        num_points = 365  # Number of points in the sine wave
        seasonality = (np.sin(2 * np.pi * t / period) + 1) * (maximum - minimum) / 2 + minimum
        return beta * seasonality
    for t in range(1, simulation_days):
        # progress infections: E->I
        new_infections = E_queue.pop()
        # Push new infections into the infectious queue
        I_queue.appendleft(new_infections)
        # Update recovered population: I->R
        R.append(R[-1] + I_queue.pop())

        # Calculate new exposures
        eff_beta = get_beta(t)
        new_exposures = int(np.round(eff_beta * sum(I_queue) * S[-1] / population))
        #print( f"new_exposures = beta ({beta} * Infected ({sum(I_queue)}) * Susceptible ({S[-1]}) / population ({population}) ) = {new_exposures}" )
        # Calculate new infections (from the exposed population)

        # Push new exposures into the exposed queue
        E_queue.appendleft(new_exposures)

        # Update susceptible population, inc VD.
        S.append(S[-1] - new_exposures + births_per_day)

        population += births_per_day

        E_reporting.append( sum(E_queue ) )
        I_reporting.append( sum(I_queue ) )
        NI.append(new_exposures)

        if (I_reporting[-1] + E_reporting[-1]) == 0:
            #print( f"Eliminated at timestep {t}, beta={beta}, cbr={cbr}, init_pop={init_pop}." )
            strikes += 1
            if strikes == 3:
                return False
            else:
                E_queue = deque([4000] + [0] * (incubation_period-1))  # Exposed individuals queue

    return True  # Placeholder, replace with actual implementation

# Define the range of beta, cbr, and initial population values to sweep over
#beta_range = np.linspace(1, 5, num=5)
#cbr_range = np.linspace(10, 20, num=10)
beta_range = np.arange(0.5, 4.0, 0.5)
cbr_range = np.arange(10, 21, 1)
init_pop_range = np.arange(1e5, 3.0e6, 1e4)

# Initialize a 3D array to store the threshold population values
threshold_populations = np.zeros((len(beta_range), len(cbr_range)), dtype=float)

# Sweep over beta, cbr, and initial population values
for i, beta in enumerate(beta_range):
    for j, cbr in enumerate(cbr_range):
        for init_pop in init_pop_range:
            if run_disease_model(beta, cbr, init_pop):
                threshold_populations[i, j] = init_pop
                break
        else:
            threshold_populations[i, j] = np.nan  # Set NaN if no threshold is found

# Plot the results
#plt.imshow(threshold_populations, extent=[10, 50, 1, 20], origin='lower', cmap='viridis', aspect='auto')
plt.imshow(threshold_populations, extent=[10, 20, 0.5, 5.0], origin='lower', cmap='viridis', aspect='auto')
plt.xlabel('Crude Birth Rate (CBR)')
plt.ylabel('Transmission Rate (Beta)')
plt.title('Threshold Population for Endemicity')
plt.colorbar(label='Threshold Population')
plt.show()

