all:
	LD_PRELOAD=/usr/lib/libasan.so.8 ASAN_OPTIONS=detect_leaks=0 PYTHONPATH=/home/gonsolo/work/mesa/build/src/compiler \
	DEBUG=2 NAK=1 pytest -s test/test_setitem.py::TestSetitemLoop::test_arange
edit:
	vi tinygrad/runtime/ops_nak.py
gdb:
	DEBUG=2 NAK=1 gdb -ex=r --directory=../python-mesa3d/subprojects --args python -m pytest -s test/test_setitem.py::TestSetitemLoop::test_arange
.PHONY: all edit
