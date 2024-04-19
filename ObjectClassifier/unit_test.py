import unittest
from object_classifier import verify_distance


class MyTestCase(unittest.TestCase):
    def test_correct_distance(self):
        self.assertEqual(verify_distance("1 8.0"), True)

    def test_incorrect_distance(self):
        self.assertEqual(verify_distance("1 10.0"), False)

    def test_no_object_detected(self):
        self.assertEqual(verify_distance("0 9.0"), False)


if __name__ == '__main__':
    unittest.main()
