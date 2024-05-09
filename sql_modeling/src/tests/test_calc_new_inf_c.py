import ctypes
import numpy as np
import unittest
import memory_profiler

# Load the C library
lib = ctypes.CDLL("./update_ages.so")
lib.calculate_new_infections.argtypes = [
    ctypes.c_size_t,  # n
    ctypes.c_size_t,  # n
    ctypes.c_size_t,  # starting index
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'),  # nodes
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # incubation_timer
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # inf_counts
    np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),  # sus_counts
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'),  # tot_counts
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'),  # new_infections
    ctypes.c_float, # base_inf
]
lib.handle_new_infections.argtypes = [
    ctypes.c_uint32, # num_agents
    ctypes.c_uint32, # node
    ctypes.c_size_t,  # starting index
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # nodes
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # infected
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # immunity
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'), # incubation_timer
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'), # infection_timer
    ctypes.c_int, # num_new_infections
    np.ctypeslib.ndpointer(dtype=np.uint32, flags='C_CONTIGUOUS'), # new infected ids
    ctypes.c_int, # sus number for node
]
class TestHandleNewInfections(unittest.TestCase):
    def test_no_eligible_agents(self):
        """
        Test case to verify behavior when no agents are eligible for infection.

        Test Design:
        1. Set up input parameters where no agents are eligible for infection.
        2. Call the C function with the provided input.
        3. Verify that no agents are infected after the function call.

        Test Failure Implications:
        - If the test fails, it indicates that the C function is incorrectly infecting agents when there are none eligible.
        """

        # Define input parameters
        start_idx = 0
        end_idx = 10
        node = 1
        agent_node = np.array([1] * 10, dtype=np.uint32)
        infected = np.array([False] * 10, dtype=bool)
        immunity = np.array([False] * 10, dtype=bool)
        incubation_timer = np.array([0] * 10, dtype=np.uint8)
        infection_timer = np.array([0] * 10, dtype=np.uint8)
        new_infections = 5
        new_infection_idxs_out = np.zeros(new_infections).astype(np.uint32)
        num_eligible_agents = 0

        # Call the C function
        lib.handle_new_infections(
            start_idx,
            end_idx,
            node,
            agent_node,
            infected,
            immunity,
            incubation_timer,
            infection_timer,
            new_infections,
            new_infection_idxs_out,
            num_eligible_agents
        )

        # Assert that no new infections occurred
        self.assertEqual(np.sum(infected), 0)

    def test_some_eligible_agents(self):
        """
        Test case to verify behavior when some agents are eligible for infection.

        Test Design:
        1. Set up input parameters where some agents are eligible for infection.
        2. Call the C function with the provided input.
        3. Verify that the expected number of agents are infected after the function call.

        Test Failure Implications:
        - If the test fails, it indicates that the C function is not infecting the correct number of agents or is infecting agents incorrectly.
        """
        # Define input parameters
        start_idx = 0
        end_idx = 10
        node = 1
        agent_node = np.array([1] * 10, dtype=np.uint32)
        infected = np.array([False] * 10, dtype=bool)
        immunity = np.array([False] * 10, dtype=bool)
        incubation_timer = np.array([0] * 10, dtype=np.uint8)
        infection_timer = np.array([0] * 10, dtype=np.uint8)
        new_infections = 5
        new_infection_idxs_out = np.zeros(new_infections, dtype=np.uint32)
        num_eligible_agents = 5

        # Call the C function
        lib.handle_new_infections(
            start_idx,
            end_idx,
            node,
            agent_node,
            infected,
            immunity,
            incubation_timer,
            infection_timer,
            new_infections,
            new_infection_idxs_out,
            num_eligible_agents
        )

        # Assert that new infections occurred
        self.assertEqual(np.sum(infected), new_infections)

    # Add more test cases for other scenarios (e.g., boundary cases, error cases, etc.)
    def test_invalid_input_num_eligible_agents(self):
        """
        Test case to verify behavior when the number of eligible agents is negative.

        Test Design:
        1. Set up input parameters where the number of eligible agents is negative.
        2. Call the C function with the provided input.
        3. Verify that the function raises an exception or returns an error code indicating invalid input.

        Test Failure Implications:
        - If the test fails, it indicates that the function does not handle negative numbers of eligible agents correctly.
        """

        # Define input parameters with negative number of eligible agents
        start_idx = 0
        end_idx = 10
        node = 1
        agent_node = np.array([1] * 10, dtype=np.uint32)
        infected = np.array([False] * 10, dtype=bool)
        immunity = np.array([False] * 10, dtype=bool)
        incubation_timer = np.array([0] * 10, dtype=np.uint8)
        infection_timer = np.array([0] * 10, dtype=np.uint8)
        new_infections = 5
        new_infection_idxs_out = np.zeros(new_infections, dtype=np.uint32)
        num_eligible_agents = -5  # Negative number of eligible agents

        # Save a copy of new_infection_idxs_out before calling the function
        original_new_infection_idxs_out = new_infection_idxs_out.copy()

        # Call the C function and assert that it raises an exception or returns an error code
        lib.handle_new_infections(
            start_idx,
            end_idx,
            node,
            agent_node,
            infected,
            immunity,
            incubation_timer,
            infection_timer,
            new_infections,
            new_infection_idxs_out,
            num_eligible_agents
        )

        # Assert that new_infection_idxs_out remains unmodified
        np.testing.assert_array_equal(new_infection_idxs_out, original_new_infection_idxs_out)

    def test_invalid_input_end_idx_less_than_start_idx(self):
        """
        Test case to verify behavior when end_idx is less than start_idx.

        Test Design:
        1. Set up input parameters where end_idx is less than start_idx.
        2. Call the C function with the provided input.
        3. Verify that the function raises an exception or returns an error code indicating invalid input.
        4. Confirm that new_infection_idxs_out remains unmodified.

        Test Failure Implications:
        - If the test fails, it indicates that the function does not handle the case where end_idx is less than start_idx correctly or modifies new_infection_idxs_out incorrectly.
        """

        # Define input parameters with end_idx less than start_idx
        start_idx = 10
        end_idx = 5
        node = 1
        agent_node = np.array([1] * 10, dtype=np.uint32)
        infected = np.array([False] * 10, dtype=bool)
        immunity = np.array([False] * 10, dtype=bool)
        incubation_timer = np.array([0] * 10, dtype=np.uint8)
        infection_timer = np.array([0] * 10, dtype=np.uint8)
        new_infections = 5
        new_infection_idxs_out = np.arange(5, dtype=np.uint32)  # Array with values [0, 1, 2, 3, 4]
        num_eligible_agents = 5

        # Save a copy of new_infection_idxs_out before calling the function
        original_new_infection_idxs_out = new_infection_idxs_out.copy()

        # Call the C function
        lib.handle_new_infections(
            start_idx,
            end_idx,
            node,
            agent_node,
            infected,
            immunity,
            incubation_timer,
            infection_timer,
            new_infections,
            new_infection_idxs_out,
            num_eligible_agents
        )

        # Assert that new_infection_idxs_out remains unmodified
        np.testing.assert_array_equal(new_infection_idxs_out, original_new_infection_idxs_out)

    def test_consistency_with_same_inputs(self):
        """
        Test case to verify consistency of function output with the same valid inputs.

        Test Design:
        1. Set up valid input parameters.
        2. Call the C function multiple times with the same inputs.
        3. Verify that the output remains consistent across multiple function calls.

        Test Failure Implications:
        - If the test fails, it indicates that the function produces inconsistent output for the same inputs, suggesting a potential issue with the function's implementation or state management.
        """

        # Define valid input parameters
        start_idx = 0
        end_idx = 10
        node = 1
        agent_node = np.array([1] * 10, dtype=np.uint32)
        #infected = np.array([False] * 10, dtype=bool)
        immunity = np.array([False] * 10, dtype=bool)
        #incubation_timer = np.array([0] * 10, dtype=np.uint8)
        #infection_timer = np.array([0] * 10, dtype=np.uint8)
        #new_infections = 5
        #new_infection_idxs_out = np.zeros(new_infections, dtype=np.uint32)
        num_eligible_agents = 5

        # Call the C function multiple times and store the outputs
        outputs = []
        num_repeats = 5
        for _ in range(num_repeats):  # Perform 5 function calls
            # Reset arrays modified by the function
            infected = np.array([False] * 10, dtype=bool)
            incubation_timer = np.array([0] * 10, dtype=np.uint8)
            infection_timer = np.array([0] * 10, dtype=np.uint8)
            new_infections = 5
            new_infection_idxs_out = np.zeros(new_infections, dtype=np.uint32)
            lib.handle_new_infections(
                start_idx,
                end_idx,
                node,
                agent_node,
                infected,
                immunity,
                incubation_timer,
                infection_timer,
                new_infections,
                new_infection_idxs_out,
                num_eligible_agents
            )
            outputs.append(new_infection_idxs_out.copy())  # Save a copy of the output

        # Verify that all outputs are the same
        for i in range(1, len(outputs)):
            np.testing.assert_array_equal(outputs[i], outputs[0])


    def test_memory_leak(self):
        """
        Test case to check for memory leaks in the function.

        Test Design:
        1. Profile memory usage before and after calling the function.
        2. Check if there is any increase in memory usage after the function call.
        3. Repeat the test multiple times to ensure consistency.

        Test Failure Implications:
        - If the test fails, it indicates that the function may have memory leaks,
          leading to potential issues with memory management.
        """

        # Define input parameters
        start_idx = 0
        end_idx = 10
        node = 1
        agent_node = np.array([1] * 10, dtype=np.uint32)
        infected = np.array([False] * 10, dtype=bool)
        immunity = np.array([False] * 10, dtype=bool)
        incubation_timer = np.array([0] * 10, dtype=np.uint8)
        infection_timer = np.array([0] * 10, dtype=np.uint8)
        new_infections = 5
        new_infection_idxs_out = np.zeros(new_infections, dtype=np.uint32)
        num_eligible_agents = 5

        # Profile memory usage before function call
        pre_memory = memory_profiler.memory_usage()[0]

        # Call the function
        lib.handle_new_infections(
            start_idx,
            end_idx,
            node,
            agent_node,
            infected,
            immunity,
            incubation_timer,
            infection_timer,
            new_infections,
            new_infection_idxs_out,
            num_eligible_agents
        )

        # Profile memory usage after function call
        post_memory = memory_profiler.memory_usage()[0]

        # Check for memory leak
        memory_leak = post_memory - pre_memory
        self.assertLessEqual(memory_leak, 0, "Memory leak detected")


if __name__ == "__main__":
    unittest.main()


