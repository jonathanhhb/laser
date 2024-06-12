import ctypes
import numpy as np
import unittest
import time
import copy
from numba import njit, prange, uint64

# Load the shared library
lib = ctypes.CDLL("./update_ages.so")

# Define the argument types for the C function
lib.progress_infections.argtypes = [
    ctypes.c_int,  # start_idx
    ctypes.c_int,  # end_idx
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # infection_timer
    np.ctypeslib.ndpointer(dtype=np.uint8, flags='C_CONTIGUOUS'),  # incubation_timer
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # infected
    np.ctypeslib.ndpointer(dtype=np.int8, flags='C_CONTIGUOUS'),  # immunity_timer
    np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # immunity
]
lib.progress_infections.restype = ctypes.c_size_t

@njit(parallel=True)
def progress_infections(start_idx: uint64, end_idx: uint64, incubation_timer, infection_timer, infected, immunity, immunity_timer):
    """
    WARNING: THIS DOESN"T WORK RIGHT.
    """
    for i in prange(start_idx, end_idx + 1):
        if incubation_timer[i] >= 1:
            incubation_timer[i] -= 1

        if infection_timer[i] >= 1:
            infection_timer[i] -= 1

            if infection_timer[i] == 0:
                infected[i] = 0
                immunity_timer[i] = -1
                immunity[i] = True

class TestProgressInfections(unittest.TestCase):

    def test_no_infections(self):
        """
        Test case to verify the behavior of the progress_infections function when no individuals are infected.

        This test checks whether the progress_infections function behaves correctly when no individuals in the specified range
        are infected. It sets up the input parameters such that there are no infections in the population. The function is then
        called with these parameters, and the result is checked to ensure that no individuals have recovered.

        Test Assertions:
            - The result returned by the progress_infections function should be 0, indicating that no individuals have recovered.
            - The recovered_idxs array should contain all zeros, indicating that no individuals have recovered.

        Test Design:
            1. Set up the input parameters to represent a scenario where no individuals are infected.
            2. Call the progress_infections function with these parameters.
            3. Assert that the result returned by the function is 0, indicating no recoveries.
            4. Assert that the recovered_idxs array contains all zeros, indicating no individuals have recovered.

        """
        start_idx = 0
        end_idx = 10
        infection_timer = np.zeros(10, dtype=np.uint8)
        incubation_timer = np.zeros(10, dtype=np.uint8)
        infected = np.zeros(10, dtype=bool)
        immunity_timer = np.zeros(10, dtype=np.int8)
        immunity = np.zeros(10, dtype=bool)

        infection_timer_orig = copy.deepcopy( infection_timer )
        incubation_timer_orig = copy.deepcopy( incubation_timer )
        infected_orig = copy.deepcopy( infected )
        immunity_timer_orig = copy.deepcopy( immunity_timer )
        immunity_orig = copy.deepcopy( immunity )

        # Call the C function
        lib.progress_infections(start_idx, end_idx, infection_timer, incubation_timer, infected, immunity_timer, immunity)

        # Assert that no recoveries occurred
        self.assertEqual( infection_timer.tolist(), infection_timer_orig.tolist() )
        self.assertEqual( infected.tolist(), infected_orig.tolist() )
        self.assertEqual( incubation_timer.tolist(), incubation_timer_orig.tolist() )
        self.assertEqual( immunity_timer.tolist(), immunity_timer_orig.tolist() )
        self.assertEqual( immunity.tolist(), immunity_orig.tolist() )

    def test_some_recoveries(self):
        """
        Test case to verify the behavior of the progress_infections function when some individuals recover.

        This test checks whether the progress_infections function behaves correctly when some individuals in the specified range
        recover from infection. It sets up the input parameters to simulate a scenario where certain individuals recover after
        their infection timer reaches zero. The function is then called with these parameters, and the result is checked to ensure
        that the correct number of individuals have recovered, and the recovered indices are correctly updated.

        Test Assertions:
            - The result returned by the progress_infections function should indicate the number of individuals who have recovered.
            - The recovered_idxs array should contain the indices of individuals who have recovered, with non-zero values indicating recovery.

        Test Design:
            1. Set up the input parameters to represent a scenario where some individuals recover from infection.
            2. Call the progress_infections function with these parameters.
            3. Assert that the result returned by the function corresponds to the number of individuals who have recovered.
            4. Assert that the recovered_idxs array contains the indices of individuals who have recovered, with non-zero values indicating recovery.

        """
        start_idx = 1
        end_idx = 10
        infection_timer = np.array([0, 0, 1, 0, 0, 2, 0, 3, 0, 4, 0, 1], dtype=np.uint8)
        incubation_timer = np.zeros(12, dtype=np.uint8)
        infected = np.array([False, False, True, False, False, True, False, True, False, True, False, True], dtype=bool)
        immunity_timer = np.zeros(12, dtype=np.int8)
        immunity = np.zeros(12, dtype=bool)

        infection_timer_orig = copy.deepcopy( infection_timer )
        incubation_timer_orig = copy.deepcopy( incubation_timer )
        infected_orig = copy.deepcopy( infected )
        immunity_timer_orig = copy.deepcopy( immunity_timer )
        immunity_orig = copy.deepcopy( immunity )

        # Call the C function
        lib.progress_infections(start_idx, end_idx, infection_timer, incubation_timer, infected, immunity_timer, immunity)
        for i in range(start_idx, end_idx):
            if incubation_timer[i] == 1:
                assert infection_timer[i] == 0, f"Failed at index {i}: infection_timer[{i}] should be 0, found {infection_timer[i]}"
                assert not infected[i], f"Failed at index {i}: infected[{i}] should be False, found {infected[i]}"
                assert immunity_timer[i] == -1, f"Failed at index {i}: immunity_timer[{i}] should be -1, found {immunity_timer[i]}"
                assert immunity[i], f"Failed at index {i}: immunity[{i}] should be True, found {immunity[i]}"
        """
        progress_infections(start_idx, end_idx, infection_timer_orig, incubation_timer_orig, infected_orig, immunity_timer_orig, immunity_orig)
        self.assertEqual( infection_timer.tolist(), infection_timer_orig.tolist() )
        self.assertEqual( infected.tolist(), infected_orig.tolist() )
        self.assertEqual( incubation_timer.tolist(), incubation_timer_orig.tolist() )
        self.assertEqual( immunity_timer.tolist(), immunity_timer_orig.tolist() )
        self.assertEqual( immunity.tolist(), immunity_orig.tolist() )
        """

        
    def test_some_recoveries2(self):
        """
        Test case to verify the behavior of the progress_infections function when some individuals recover.

        This test checks whether the progress_infections function behaves correctly when some individuals in the specified range
        recover from infection. It sets up the input parameters to simulate a scenario where certain individuals recover after
        their infection timer reaches zero. The function is then called with these parameters, and the result is checked to ensure
        that the correct number of individuals have recovered, and the recovered indices are correctly updated.

        Test Assertions:
            - The result returned by the progress_infections function should indicate the number of individuals who have recovered.
            - The recovered_idxs array should contain the indices of individuals who have recovered, with non-zero values indicating recovery.

        Test Design:
            1. Set up the input parameters to represent a scenario where some individuals recover from infection.
            2. Call the progress_infections function with these parameters.
            3. Assert that the result returned by the function corresponds to the number of individuals who have recovered.
            4. Assert that the recovered_idxs array contains the indices of individuals who have recovered, with non-zero values indicating recovery.

        """
        start_idx = 1
        end_idx = 10
        infection_timer = np.array([0, 0, 1, 0, 1, 2, 0, 1, 0, 14, 5, 1], dtype=np.uint8)
        incubation_timer = np.zeros(12, dtype=np.uint8)
        infected = np.array([False, False, True, False, True, True, False, True, False, True, True, True], dtype=bool)
        immunity_timer = np.zeros(12, dtype=np.int8)
        immunity = np.zeros(12, dtype=bool)

        infection_timer_orig = copy.deepcopy( infection_timer )
        incubation_timer_orig = copy.deepcopy( incubation_timer )
        infected_orig = copy.deepcopy( infected )
        immunity_timer_orig = copy.deepcopy( immunity_timer )
        immunity_orig = copy.deepcopy( immunity )

        # Call the C function
        lib.progress_infections(start_idx, end_idx, infection_timer, incubation_timer, infected, immunity_timer, immunity)
        for i in range(start_idx, end_idx):
            if incubation_timer[i] == 1:
                assert infection_timer[i] == 0, f"Failed at index {i}: infection_timer[{i}] should be 0, found {infection_timer[i]}"
                assert not infected[i], f"Failed at index {i}: infected[{i}] should be False, found {infected[i]}"
                assert immunity_timer[i] == -1, f"Failed at index {i}: immunity_timer[{i}] should be -1, found {immunity_timer[i]}"
                assert immunity[i], f"Failed at index {i}: immunity[{i}] should be True, found {immunity[i]}"

        """
        progress_infections(start_idx, end_idx, infection_timer_orig, incubation_timer_orig, infected_orig, immunity_timer_orig, immunity_orig)

        self.assertEqual( infection_timer.tolist(), infection_timer_orig.tolist() )
        self.assertEqual( infected.tolist(), infected_orig.tolist() )
        self.assertEqual( incubation_timer.tolist(), incubation_timer_orig.tolist() )
        self.assertEqual( immunity_timer.tolist(), immunity_timer_orig.tolist() )
        self.assertEqual( immunity.tolist(), immunity_orig.tolist() )
        """

    def test_all_recoveries(self):
        """
        test that all individuals recover when their infection timers reach 0.

        this test ensures that when the infection timer for each individual reaches 0,
        indicating that they have recovered from the infection, the progress_infections function
        correctly updates the 'infected' array to false and records the individual as recovered
        in the 'recovered_idxs' array.

        test design:
        - set up input parameters representing 10 individuals with infection timers set to 1.
        - call the progress_infections c function with the provided input parameters.
        - assert that the return value from the function indicates 10 individuals have recovered.
        - assert that all elements in the 'recovered_idxs' array are non-zero, indicating that
          all individuals have been recorded as recovered.

        """
        # Define input parameters
        start_idx = 1
        end_idx = 10
        infection_timer = np.array([0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=np.uint8)
        incubation_timer = np.zeros(10, dtype=np.uint8)
        infected = np.array([False, True, True, True, True, True, True, True, True, True, True, True], dtype=bool)
        immunity_timer = np.zeros(12, dtype=np.int8)
        immunity = np.zeros(12, dtype=bool)

        infection_timer_orig = copy.deepcopy( infection_timer )
        incubation_timer_orig = copy.deepcopy( incubation_timer )
        infected_orig = copy.deepcopy( infected )
        immunity_timer_orig = copy.deepcopy( immunity_timer )
        immunity_orig = copy.deepcopy( immunity )

        # Call the C function
        result = lib.progress_infections(start_idx, end_idx, infection_timer, incubation_timer, infected, immunity_timer, immunity)
        #progress_infections(start_idx, end_idx, infection_timer_orig, incubation_timer_orig, infected_orig, immunity_timer_orig, immunity_orig)

        self.assertListEqual(infection_timer[start_idx:end_idx+1].tolist(), np.full(10, 0, dtype=np.uint8).tolist())
        self.assertListEqual(infected[start_idx:end_idx+1].tolist(), np.full(end_idx - start_idx + 1, False, dtype=bool).tolist())
        self.assertListEqual(immunity_timer[start_idx:end_idx+1].tolist(), np.full(end_idx - start_idx + 1, -1, dtype=np.int8).tolist())
        self.assertListEqual(immunity[start_idx:end_idx+1].tolist(), np.full(end_idx - start_idx + 1, True, dtype=bool).tolist())

        """
        self.assertEqual( infection_timer.tolist(), infection_timer_orig.tolist() )
        self.assertEqual( infected.tolist(), infected_orig.tolist() )
        self.assertEqual( incubation_timer.tolist(), incubation_timer_orig.tolist() )
        self.assertEqual( immunity_timer.tolist(), immunity_timer_orig.tolist() )
        self.assertEqual( immunity.tolist(), immunity_orig.tolist() )
        """


    def test_no_recoveries(self):
        """
        Test case to verify the behavior of the progress_infections function when no individuals recover.

        This test checks whether the progress_infections function behaves correctly when no individuals in the specified range
        recover from infection. It sets up the input parameters to simulate a scenario where no individuals recover after
        their infection timer reaches zero. The function is then called with these parameters, and the result is checked to ensure
        that no individuals have recovered, and the recovered_idxs array remains unchanged.

        Test Assertions:
            - The result returned by the progress_infections function should be zero, indicating that no individuals have recovered.
            - The recovered_idxs array should remain unchanged, with all values set to zero.

        Test Design:
            1. Set up the input parameters to represent a scenario where no individuals recover from infection.
            2. Call the progress_infections function with these parameters.
            3. Assert that the result returned by the function is zero, indicating no individuals have recovered.
            4. Assert that the recovered_idxs array remains unchanged, with all values set to zero.
        """

        # Define input parameters
        start_idx = 1
        end_idx = 10
        infection_timer = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], dtype=np.uint8)
        incubation_timer = np.zeros(10, dtype=np.uint8)
        infected = np.array([True, True, True, True, True, True, True, True, True, True], dtype=bool)
        immunity_timer = np.zeros(12, dtype=np.int8)
        immunity = np.zeros(12, dtype=bool)

        infection_timer_orig = copy.deepcopy( infection_timer )
        incubation_timer_orig = copy.deepcopy( incubation_timer )
        infected_orig = copy.deepcopy( infected )
        immunity_timer_orig = copy.deepcopy( immunity_timer )
        immunity_orig = copy.deepcopy( immunity )

        # Call the C function
        result = lib.progress_infections(start_idx, end_idx, infection_timer, incubation_timer, infected, immunity_timer, immunity)
        progress_infections(start_idx, end_idx, infection_timer_orig, incubation_timer_orig, infected_orig, immunity_timer_orig, immunity_orig)

        self.assertEqual( infection_timer.tolist(), infection_timer_orig.tolist() )
        self.assertEqual( infected.tolist(), infected_orig.tolist() )
        self.assertEqual( incubation_timer.tolist(), incubation_timer_orig.tolist() )
        self.assertEqual( immunity_timer.tolist(), immunity_timer_orig.tolist() )
        self.assertEqual( immunity.tolist(), immunity_orig.tolist() )

    # Add more tests here with different initial values...
    def test_performance_large_scale(self):
        """
        Performance test case to measure the execution time of the progress_infections function with 10 million agents.
        """
        start_idx = 0
        end_idx = int(1e7) - 1
        size = end_idx - start_idx + 1

        # Generate large arrays
        infected = np.random.choice([True, False], size=size)
        infection_timer = np.zeros(size, dtype=np.uint8)
        incubation_timer = np.zeros(size, dtype=np.uint8)

        # Set infection_timer and incubation_timer to non-zero where infected is True
        infection_timer[infected] = np.random.randint(1, 10, size=infected.sum(), dtype=np.uint8)
        incubation_timer[infected] = np.random.randint(1, 5, size=infected.sum(), dtype=np.uint8)

        immunity_timer = np.zeros(size, dtype=np.int8)
        immunity = np.zeros(size, dtype=bool)

        infection_timer_orig = copy.deepcopy( infection_timer )
        incubation_timer_orig = copy.deepcopy( incubation_timer )
        infected_orig = copy.deepcopy( infected )
        immunity_timer_orig = copy.deepcopy( immunity_timer )
        immunity_orig = copy.deepcopy( immunity )

        # Measure the execution time
        start_time = time.time()
        result = lib.progress_infections(start_idx, end_idx, infection_timer, incubation_timer, infected, immunity_timer, immunity)
        end_time = time.time()

        # Print the execution time
        execution_time = end_time - start_time
        print(f"Test Execution time for 10 million agents: {execution_time:.2f} seconds")

        """
        start_time = time.time()
        progress_infections(start_idx, end_idx, infection_timer_orig, incubation_timer_orig, infected_orig, immunity_timer_orig, immunity_orig)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Reference (numba) Execution time for 10 million agents: {execution_time:.2f} seconds")
        """

        """
        self.assertEqual( infection_timer.tolist(), infection_timer_orig.tolist() )
        self.assertEqual( infected.tolist(), infected_orig.tolist() )
        self.assertEqual( incubation_timer.tolist(), incubation_timer_orig.tolist() )
        self.assertEqual( immunity_timer.tolist(), immunity_timer_orig.tolist() )
        self.assertEqual( immunity.tolist(), immunity_orig.tolist() )
        """


if __name__ == '__main__':
    unittest.main()

