import unittest

class BaseTestCase(unittest.TestCase):
    """Base class for synchronous test cases."""
    pass

class AsyncBaseTestCase(unittest.IsolatedAsyncioTestCase):
    """Base class for asynchronous test cases (Python 3.8+)."""
    pass 