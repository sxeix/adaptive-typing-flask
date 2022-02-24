"""
Unit tests for the data_handling_tools module
"""
import unittest
from data_handling_tools import find_users, load_stats


"""
Class for the tests case of the module, tests for each function are defined here
"""
class TestTools(unittest.TestCase):

    def test_find_users(self):
        self.assertNotEqual(find_users(), [], 'There are no users')

    def test_load_stats(self):
        self.assertNotEqual(load_stats('yasser'), [], 'Data is not loaded')

    def test_user_exists(self):
        self.assertTrue('yasser' in find_users())

if __name__ == '__main__':
    unittest.main()
