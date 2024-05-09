import unittest
import numpy as np
import ctypes

class TestProgressImmunities(unittest.TestCase):
    def setUp(self):
        # Load the shared library
        self.lib = ctypes.CDLL("./update_ages.so")
        self.lib.progress_immunities.argtypes = [
            ctypes.c_int,  # start_idx
            ctypes.c_int,  # end_idx
            np.ctypeslib.ndpointer(dtype=np.int8, flags='C_CONTIGUOUS'),  # immunity_timer
            np.ctypeslib.ndpointer(dtype=bool, flags='C_CONTIGUOUS'),  # immunity
        ]
    def test_no_progress(self):
        """
        Test that no progress occurs when all immunity timers are zero.
        """
        # Define input parameters
        start_idx = 1
        end_idx = 10
        immunity_timer = np.zeros(12, dtype=np.int8)
        immunity = np.zeros(12, dtype=bool)

        # Call the C function
        self.lib.progress_immunities(start_idx, end_idx, immunity_timer, immunity)

        # Assert that no changes occurred
        self.assertTrue(np.all(immunity_timer == 0))
        self.assertTrue(np.all(immunity == False))

    def test_no_expires(self):
        """
        Test that no immunities expire when nobody's are still high
        """
        # Define input parameters
        start_idx = 1
        end_idx = 10
        immunity_timer = np.ones(12, dtype=np.int8)*44
        immunity_timer[0] = 1
        immunity_timer[11] = 1
        immunity = np.ones(12, dtype=bool)
        #immunity[0] = 0
        #immunity[11] = 0

        # Call the C function
        self.lib.progress_immunities(start_idx, end_idx, immunity_timer, immunity)

        # Assert that no changes occurred
        self.assertTrue(np.all(immunity_timer[1:10] == 43))
        self.assertTrue(np.all(immunity_timer[0] == 1))
        self.assertTrue(np.all(immunity_timer[11] == 1))
        self.assertTrue(np.all(immunity[1:10] == True))

    def test_some_progress(self):
        """
        Test that progress occurs for some individuals with non-zero immunity timers.
        """
        # Define input parameters
        start_idx = 1
        end_idx = 10
        immunity_timer = np.array([3, 2, 1, 0, 5, 4, 3, 0, 2, 1, 6, 7], dtype=np.int8)
        immunity = np.array([True, True, True, False, True, True, True, False, True, True, True, True], dtype=bool)

        # Call the C function
        self.lib.progress_immunities(start_idx, end_idx, immunity_timer, immunity)

        # Assert that progress occurred
        expected_immunity_timer = np.array([3, 1, 0, 0, 4, 3, 2, 0, 1, 0, 5, 7], dtype=np.int8)
        expected_immunity = np.array([True, True, False, False, True, True, True, False, True, False, True, True], dtype=bool)
        self.assertTrue(np.all(immunity_timer == expected_immunity_timer))
        #print( f"ref: {expected_immunity}" )
        #print( f"test: {immunity}" )
        self.assertTrue((immunity.tolist() == expected_immunity.tolist()), "Immunity state (true/false) after progression different from expected.")

if __name__ == "__main__":
    unittest.main()

