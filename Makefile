all:
	DEBUG=2 NAK=1 pytest -s test/test_setitem.py::TestSetitemLoop::test_arange
