VARS=LD_PRELOAD=/usr/lib/libasan.so.8 ASAN_OPTIONS=detect_leaks=0 PYTHONPATH=/home/gonsolo/work/mesa/build/src DEBUG=2 NAK=1 #MOCK_NOUVEAU_DEVICE=rtx3060
#TEST=test/test_setitem.py::TestSetitemLoop::test_arange
TEST=test/test_nak.py::TestNak::test_hello
all:
	$(VARS) pytest -s $(TEST)
edit_ops:
	vi tinygrad/runtime/ops_nak.py
edit_renderer:
	vi tinygrad/renderer/nak.py
gdb:
	$(VARS) gdb -ex=r --directory=../mesa --args python -m pytest -s $(TEST)
.PHONY: all edit
