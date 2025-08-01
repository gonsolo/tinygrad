all:
	DEBUG=2 NAK=1 pytest -s test/test_setitem.py::TestSetitemLoop::test_arange
edit:
	vi tinygrad/runtime/ops_nak.py
.PHONY: all edit
