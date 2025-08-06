import unittest
from tinygrad import Tensor, TinyJit, Variable, dtypes
from tinygrad.helpers import Context
import numpy as np

class TestNak(unittest.TestCase):
  def test_hello(self):
    t1 = Tensor([1], dtype=dtypes.int32)
    t1 = t1 + 1
    print(t1.tolist())

if __name__ == '__main__':
  unittest.main()
