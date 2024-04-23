// update_ages.c

#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <unordered_map>
#include <deque>
#include <mutex>
#include <algorithm>
#include <cassert>
#include <math.h>


extern "C" {

/**
 * Update ages of individuals within a specified range by incrementing ages for non-negative values.
 *
 * This function increments the ages of individuals within a specified range by a constant value representing
 * one day. The function iterates over a range of indices in the `ages` array, starting from `start_idx` and
 * ending at `stop_idx` (inclusive). For each index `i` within the specified range, if the age value `ages[i]`
 * is non-negative, it is incremented by the constant value `one_day`, which represents one day in units of years.
 *
 * @param start_idx The index indicating the start of the range to update (inclusive).
 * @param stop_idx The index indicating the end of the range to update (inclusive).
 * @param ages Pointer to the array containing ages of individuals.
 *             The ages are expected to be in units of years.
 *             The array is modified in place.
 */
const float one_day = 1.0f/365.0f;
void update_ages(unsigned int start_idx, unsigned int stop_idx, float *ages) {
    //printf( "%s: from %d to %d.\n", __FUNCTION__, start_idx, stop_idx );
    for (size_t i = start_idx; i <= stop_idx; i++) {
        if( ages[i] < 0 )
        {
            continue;
        }
        ages[i] += one_day;
    }
}

/*
 * Progress all infections. Collect the indexes of those who recover. 
 * Assume recovered_idxs is pre-allocated to same size as infecteds.
 */
size_t progress_infections(
    int start_idx,
    int end_idx,
    unsigned char * infection_timer,
    unsigned char * incubation_timer,
    bool* infected,
    signed char * immunity_timer,
    bool* immunity,
    int* node,
    uint32_t * recovered_idxs
) {
    unsigned int activators = 0;
    unsigned recovered_counter = 0;
    //printf( "progress_infections: traversing from idx %d to %d.\n", start_idx, end_idx );

    for (int i = start_idx; i <= end_idx; ++i) {
        if (infected[i] ) { // everyone should be infected, possible tiny optimization by getting rid of this
            // Incubation timer: decrement for each person
            if (incubation_timer[i] >= 1) {
                incubation_timer[i] --;
                /*if( incubation_timer[i] == 0 )
                {
                    //printf( "Individual %d activating; incubation_timer= %f.\n", i, incubation_timer[i] );
                    activators++;
                }*/
            }

            // Infection timer: decrement for each infected person
            if (infection_timer[i] >= 1) {
                infection_timer[i] --;


                // Some people clear
                if ( infection_timer[i] == 0) {
                    infected[i] = 0;

                    // Recovereds gain immunity
                    //immunity_timer[i] = rand() % (30) + 10;  // Random integer between 10 and 40
                    // Make immunity permanent for now; we'll want this configurable at some point
                    immunity_timer[i] = -1;
                    immunity[i] = true;
                    //printf( "Recovery.\n" );
                    recovered_idxs[ recovered_counter++ ] = i;
                }
            }
        }
    }
    return recovered_counter;
}

void progress_immunities(
    int start_idx,
    int end_idx,
    signed char * immunity_timer,
    bool* immunity,
    int* node
) {
    for (int i = start_idx; i <= end_idx; ++i) {
        if( immunity[i] && immunity_timer[i] > 0 )
        {
            immunity_timer[i]--;
            if( immunity_timer[i] == 0 )
            {
                immunity[i] = false;
                //printf( "New Susceptible.\n" );
            }
        }    
    }
}


// Dang, this one is slower than the numpy version!?!?
// maybe I need to just use the 64-bit ints and avoid the casting
void calculate_new_infections(
    int start_idx, 
    int end_idx,
    int num_nodes,
    uint32_t * node,
    unsigned char  * incubation_timers,
    float * infected_fractions,
    float * susceptible_fractions, // also fractions
    uint32_t * totals,
    uint32_t * new_infs_out,
    float base_inf
) {
    // We need number of infected not incubating
    float exposed_counts_by_bin[ num_nodes ];
    memset( exposed_counts_by_bin, 0, sizeof(exposed_counts_by_bin) );

    // We are not yet counting E in our regular report, so we have to count them here.
    // Is that 'expensive'? Not sure yet.
    for (int i = start_idx; i <= end_idx; ++i) {
        if( incubation_timers[i] >= 1 ) {
            exposed_counts_by_bin[ node[ i ] ] ++;
            // printf( "DEBUG: incubation_timers[ %d ] = %f.\n", i, incubation_timers[i] );
        }
    }

    // new infections = Infecteds * infectivity * susceptibles
    for (int i = 0; i < num_nodes; ++i) {
        //printf( "exposed_counts_by_bin[%d] = %f.\n", i, exposed_counts_by_bin[i] );
        exposed_counts_by_bin[ i ] /= totals[ i ];
        if( exposed_counts_by_bin[ i ] > infected_fractions[ i ] )
        {
            printf( "Exposed should never be > infection.\n" );
            printf( "node = %d, exposed = %f, infected = %f.\n", i, exposed_counts_by_bin[ i ]*totals[i], infected_fractions[ i ]*totals[i] );
            exposed_counts_by_bin[ i ] = infected_fractions[ i ]; // HACK: Maybe an exposed count is dead?
            //abort();
        }
        infected_fractions[ i ] -= exposed_counts_by_bin[ i ];
        //printf( "infected_fractions[%d] = %f\n", i, infected_fractions[i] );
        float foi = infected_fractions[ i ] * base_inf;
        //assert( foi >= 0 );
        //printf( "foi[%d] = %f\n", i, foi );
        // We have to have a pop density factor if we're going to have CCS phenom otherwise absolute population total is 
        // divided out of all the math.
        //float density_factor = logistic_density_fn( totals[ i ] );
        //new_infs_out[ i ] = (int)( foi * sus[ i ] * density_factor );
        new_infs_out[ i ] = (int)( foi * susceptible_fractions[ i ] * totals[i] );
        //new_infs_out[ i ] = generate_new_infections( sus[ i ]*totals[i], foi );
        //printf( "new infs[%d] = foi(%f) * susceptible_fractions(%f) = %d.\n", i, foi, susceptible_fractions[i], new_infs_out[i] );
    }
}

void handle_new_infections(
    int start_idx,
    int end_idx,
    int node,
    uint32_t * agent_node,
    bool * infected,
    bool * immunity,
    unsigned char  * incubation_timer,
    unsigned char  * infection_timer,
    int new_infections,
    int * new_infection_idxs_out,
    int num_eligible_agents
) {
    //printf( "Infect %d new people.\n", new_infections );
    //printf( "start_idx=%d, end_idx=%d.\n", start_idx, end_idx );
    // Allocate memory for subquery_condition array
    unsigned int num_agents = end_idx-start_idx+1;
    bool *subquery_condition = (bool*)malloc(num_agents * sizeof(bool));
    // Apply conditions to identify eligible agents
    for (int i = start_idx; i <= end_idx; i++) {
        subquery_condition[i-start_idx] = !infected[i] && !immunity[i] && agent_node[i] == node;
    }

    /*
    // Count the number of eligible agents
    int num_eligible_agents_calc = 0;
    for (int i = 0; i <= end_idx-start_idx; i++) {
        if (subquery_condition[i]) {
            num_eligible_agents_calc++;
        }
    }
    if( num_eligible_agents_calc != num_eligible_agents )
    {
        printf( "WARNING: num_eligible_agents = %d for node %d but num_eligible_agents_calc = %d.\n", num_eligible_agents, node, num_eligible_agents_calc );
    }
    */
    //printf( "num_eligible_agents=%d.\n", num_eligible_agents );
    if( num_eligible_agents > 0 ) {
        // Allocate memory for selected_indices array
        int *selected_indices = (int*) malloc(num_eligible_agents * sizeof(int));

        // Randomly sample from eligible agents
        int count = 0;
        for (int i = 0; i <= end_idx-start_idx; i++) {
            if (subquery_condition[i]) {
                unsigned int selected_idx = i+start_idx;
                //assert( selected_idx >= start_idx );
                //assert( selected_idx <= end_idx );
                selected_indices[count++] = selected_idx;
                //printf( "selected_indices[%d] = %d.\n", count-1, selected_idx );
                if( count == num_eligible_agents ) {
                    // Note that we saw a bug where sometimes more agents were found to satisfy our sus condition than the value passed it! TBD
                    break;
                }
            }
        }

        int i, step, selected_count = 0;
        // Calculate the step size
        if (new_infections >= num_eligible_agents) {
            step = 1; // If we need to select all elements or more, select each one
        } else {
            step = num_eligible_agents/new_infections; // If we need to select less than N, calculate step size
        }
        //printf( "Selecting %d new infectees by skipping through %d candidates %d at a time.\n", new_infections, num_eligible_agents, step );
        for (i = 0; i < num_eligible_agents && selected_count < new_infections; i += step) {
            unsigned int selected_id = selected_indices[i];
            assert( selected_id >= start_idx );
            assert( selected_id <= end_idx );
            //printf( "Infecting index=%d.\n", selected_id );
            infected[selected_id] = true;
            incubation_timer[selected_id] = 7;
            infection_timer[selected_id] = 14 + rand() % 2;
            new_infection_idxs_out[ selected_count++ ] = selected_id;
        }
        
        //printf( "free-ing selected_indices.\n" );
        free(selected_indices);
    }

    // Free dynamically allocated memory
    //printf( "free-ing subquery_condition.\n" );
    free(subquery_condition);
}

void migrate( int num_agents, int start_idx, int end_idx, bool * infected, uint32_t * node ) {
    // This is just a very simplistic one-way linear type of infection migration
    // I prefer to hard code a few values for this function rather than add parameters
    // since it's most a test function.
    int fraction = (int)(0.02*1000); // this fraction of infecteds migrate
    unsigned int counter = 0;
    for (int i = start_idx; i < num_agents; ++i) {
        if( i==end_idx ) {
            return;
        }
        if( infected[ i ] && rand()%1000 < fraction )
        {
            if( node[ i ] > 0 )
            {
                node[ i ] --;
            }
            else
            {
                node[ i ] = 953; // this should be param
            }
        }
    }
}

void collect_report( 
    int num_agents,
    int start_idx,
    int eula_idx,
    uint32_t * node,
    bool * infected,
    bool * immunity,
    float * age,
    float * expected_lifespan, // so we can not count dead people
    uint32_t * infection_count,
    uint32_t * susceptible_count,
    uint32_t * recovered_count
)
{
    //printf( "%s called w/ num_agents = %d, start_idx = %d, eula_idx = %d.\n", __FUNCTION__, num_agents, start_idx, eula_idx );
    for (int i = start_idx; i <= eula_idx; ++i) {
        if( node[i] < 0 ) {
            continue;
        }
        int node_id = node[i];
        if( age[ i ] < expected_lifespan[ i ] ) {
            if( infected[ i ] ) {
                infection_count[ node_id ]+=1;
                //printf( "Incrementing I count for node %d = %d from idx %d.\n", node_id, infection_count[ node_id ], i );
            } else if( immunity[ i ] ) {
                recovered_count[ node_id ]+=1;
                //printf( "Incrementing R count for node %d = %d from idx %d.\n", node_id, recovered_count[ node_id ], i );
            } else {
                susceptible_count[ node_id ]+=1;
                //printf( "Incrementing S count for node %d = %d from idx %d.\n", node_id, susceptible_count[ node_id ], i );
            }
        }
    }
    for (int i = eula_idx; i < num_agents; ++i) {
        int node_id = node[i];
        recovered_count[ node_id ]++;
    }
}

unsigned int campaign(
    int num_agents,
    int start_idx,
    float coverage,
    int campaign_node,
    bool *immunity,
    signed char  *immunity_timer,
    float *age,
    int *node
)
{
    // We have in mind a vaccination campaign to a subset of the population based on age, in a particular node, at
    // a particular coverage level.
    // The intervention effect will be to make them permanently immune.
    // Create a boolean mask for the conditions specified in the WHERE clause
    unsigned int report_counter = 0;
    // printf( "DEBUG: Looking through %d susceptible agents in node %d under age %f with coverage %f to give immunity.\n", num_agents, campaign_node, 16.0f, coverage );
    for (int i = start_idx; i < num_agents; ++i) {
        if( age[i] < 16 &&
            age[i] > 0 &&
            node[i] == campaign_node &&
            immunity[i] == false &&
            rand()%100 < 100*coverage
        )
        {
            //printf( "Changing value of immunity at index %d.\n", i );
            immunity[i] = true;
            immunity_timer[i] = -1;
            report_counter ++;
        }
    }
    return report_counter;
}

unsigned int ria(
    int num_agents,
    int start_idx, // to count backwards
    float coverage,
    int campaign_node,
    bool *immunity,
    signed char  *immunity_timer,
    float *age,
    int *node,
    int *immunized_indices
)
{
    // We have in mind a vaccination campaign to a fraction of the population turning 9mo, in a particular node, at
    // a particular coverage level.
    // The intervention effect will be to make them permanently immune.
    // Create a boolean mask for the conditions specified in the WHERE clause
    unsigned int report_counter = 0; // not returned for now
    // printf( "DEBUG: Looking through %d susceptible agents in node %d under age %f with coverage %f to give immunity.\n", num_agents, campaign_node, 16.0f, coverage );
    unsigned int new_idx = start_idx;
    //printf( "%s called with start_idx=%d, counting down to %d.\n", __FUNCTION__, start_idx, num_agents );
    for (int i = start_idx; i > num_agents; --i) {
        printf( "age = %f.\n", age[i] );
        // keep decrementing until we get kids younger than 0.75
        if( age[i] < 0.75 ) {
            //printf( "age of individual at idx %d = %f. Cutting out of loop.\n", i, age[i] );
            new_idx = i;
            break;
        }

        float upper_bound = 0.75+30/365.; // We want to be able to hunt from oldest in pop down to "9 month old" 
                                          // without vaxxing them all. But then later we want to be able to grab
                                          // everyone who aged into 9months while we were away and vax them. Tricky.
        if( age[i] > upper_bound ) {
            //printf( "Too old. Keep counting down to find '9-month-olds'.\n" );
            continue; // keep counting down
        }

        if( node[i] == campaign_node &&
            immunity[i] == false &&
            rand()%100 < 0.75*coverage
        )
        {
            printf( "Changing value of immunity at index %d.\n", i );
            immunity[i] = true;
            immunity_timer[i] = -1;
            immunized_indices[ report_counter ++ ] = i;
        }
        else
        {
            printf( "Didn't match immunity and coverage filter.\n" );
        }
    }
    /*if( report_counter > 0 ) {
        printf( "Vaccinated %d 9-month-olds starting at idx %d and ending up at %d.\n", report_counter, start_idx, new_idx );
    }*/
    return new_idx;
}

void reconstitute(
    int start_idx,
    int num_new_babies,
    int* new_nodes,
    int *node,
    float *age
) {
    //printf( "%s: num_new_babies = %d\n", __FUNCTION__, num_new_babies );
    int counter = 0;
    for (int i = start_idx; i > 0; --i) {
        if( age[i] < 0 ) {
            node[i] = new_nodes[ counter ];
            age[i] = 0;
            counter ++;
            if( counter == num_new_babies ) {
                return;
            }
        }
        else {
            printf( "ERROR: Next U (idx=%d) wasn't the right age (%f) for some reason!.\n", i, age[i] );
        }
    }
    printf( "ERROR: We ran out of open slots for new babies!" );
    abort();
}

double random_double() {
    return (double) rand() / RAND_MAX;
}

// Function to generate a binomial random variable
int binomial(int n, double p) {
    int successes = 0;
    for (int i = 0; i < n; ++i) {
        if (random_double() < p) {
            successes++;
        }
    }
    return successes;
}

/*
 * Need access to the eula map/dict. Probably should pass in the sorted values as an array
 */
void progress_natural_mortality_binned(
    int* eula, // sorted values as an array
    int num_nodes,
    int num_age_bins,  // size of eula array
    float* probs,
    int timesteps_elapsed // how many timesteps are we covering
) {
    // Iterate over nodes and age bins
    for (int node = 0; node < num_nodes; ++node) {
        for (int age_bin = 0; age_bin < num_age_bins; ++age_bin) {
            // Compute expected deaths
            float prob = probs[age_bin]; // Implement this function as needed
            int count = eula[node * num_age_bins + age_bin];
            int expected_deaths = 0;
            for (int i = 0; i < timesteps_elapsed; ++i) {
                expected_deaths += binomial(count, prob); // Implement binomial function as needed
            }
            eula[node * num_age_bins + age_bin] -= expected_deaths;
        }
    }
}

/////////////////////////////
// DEPRECATED
/////////////////////////////

float logistic_density_fn(float x) {
    float L = 4.5; // Maximum value
    float x0 = 250000.0; // Midpoint
    float k = 0.0001; // Steepness parameter
    float ret = 0.5 + (L / (1.0 + exp(-k * (x - x0))));
    //printf( "ccs multiplier = %f.\n", ret );
    return ret;
}

// Function to generate a random number of new infections
int generate_new_infections(int N, double P) {
    // Generate a random number of new infections from a binomial distribution
    int new_infections = 0;
    for (int i = 0; i < N; i++) {
        double rand_num = (double)rand() / RAND_MAX;  // Generate a random number between 0 and 1
        if (rand_num < P) {  // Probability of infection
            new_infections++;
        }
    }
    //printf( "generate_new_infections returning %d for num sus = %d and prob = %f.\n", new_infections, N, P );
    return new_infections;
}


}
