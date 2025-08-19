# runtime/ops_nak.py

import ctypes
import mesa3d
import sys
import uuid
from tinygrad.runtime.autogen.drm import drmGetDevices2, drmFreeDevices, struct__drmDevice, uint32_t
from tinygrad.device import Compiled, Compiler, Renderer, Allocator
from tinygrad.dtype import dtypes
from tinygrad.engine.jit import MultiGraphRunner
from tinygrad.uop.ops import Ops, UOp
from tinygrad.renderer.nak import NakRenderer, _nak_nir_cache # Import the renderer and cache

drmGetDevices2.argtypes = [uint32_t, ctypes.POINTER(ctypes.POINTER(struct__drmDevice)), ctypes.c_int32]
drmGetDevices2.restype = ctypes.c_int32

drmFreeDevices.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__drmDevice)), ctypes.c_int32]
drmFreeDevices.restype = None

# Ensure constants are defined globally or imported
DRM_NODE_RENDER = 2
DRM_BUS_PCI = 0

import os

class MockNouveauDevice:
    def __init__(self, chipset_id, device_id):
        self.info = MockNouveauDeviceInfo(chipset_id, device_id)
        self.vendor_id = 0x10de

class MockNouveauDeviceInfo:
    def __init__(self, chipset_id, device_id):
        self.chipset = chipset_id
        self.device_id = device_id
        self.vendor_id = 0x10de

def find_drm_devices():
    """
    Finds and returns the first suitable Nouveau device.
    Returns the nouveau_ws_device object or None if not found.
    """
    if os.getenv("MOCK_NOUVEAU_DEVICE") == "rtx3060":
        print("MOCK_NOUVEAU_DEVICE environment variable is set. Returning a mock RTX 3060.")
        return MockNouveauDevice(chipset_id=0x170, device_id=0x2503)

    MAX_DEVICES = 64
    devices_ptr_array_type = ctypes.POINTER(struct__drmDevice) * MAX_DEVICES
    devices_ptr_array = devices_ptr_array_type()
    num_devices = drmGetDevices2(0, devices_ptr_array, MAX_DEVICES)

    if num_devices <= 0:
        print("No DRM devices found.")
        return None

    found_nouveau_device = None
    for i in range(num_devices):
        device_ptr = devices_ptr_array[i]
        if not device_ptr:
            continue
        device = device_ptr.contents

        has_render_node = (device.available_nodes & (1 << DRM_NODE_RENDER)) != 0
        is_pci_bus = device.bustype == DRM_BUS_PCI
        is_nvidia_vendor = False
        if is_pci_bus and device.deviceinfo.pci:
            vendor_id = device.deviceinfo.pci.contents.vendor_id
            is_nvidia_vendor = vendor_id == 0x10de

        if has_render_node and is_pci_bus and is_nvidia_vendor:
            print(f"Found a potential Nouveau device at index {i}!")
            device_address = ctypes.cast(device_ptr, ctypes.c_void_p)
            found_nouveau_device = mesa3d.nouveau_ws_device_new(device_address.value)
            if found_nouveau_device:
                print(f"Successfully created a new nouveau device: {found_nouveau_device}")
                drmFreeDevices(devices_ptr_array, num_devices)
                return found_nouveau_device
            else:
                print(f"Failed to create nouveau_ws_device for device at index {i}.")
        else:
            print(f"Device at index {i} is not a Nouveau device (render_node={has_render_node}, pci_bus={is_pci_bus}, nvidia_vendor={is_nvidia_vendor}).")

    drmFreeDevices(devices_ptr_array, num_devices)
    return None

class NakCompiler(Compiler):
  device = "NAK"

  def compile(self, prg: str) -> bytes:
    nak_nir_id = prg
    cached_data = _nak_nir_cache.get(nak_nir_id)
    if cached_data is None:
      raise ValueError("Could not find the cached data in the global cache.")

    builder = cached_data['builder']
    options = cached_data['options']

    dump_asm = False
    robust2_modes = mesa3d.nir_variable_mode(0)
    fs_key = None

    print("Searching for DRM devices...")
    nouveau_device = find_drm_devices()
    
    if nouveau_device:
        print("\nDRM device found. Proceeding with compiler creation.")
        info = nouveau_device.info
        nak_compiler = mesa3d.nak_compiler_create(info)
        print("NAK Compiler created successfully!")

        mesa3d.nir_print_shader(builder.shader, sys.stdout.fileno())

        print("Preprocessing")
        mesa3d.nak_preprocess_nir(builder.shader, nak_compiler)

        print("Compiling")
        nak_bin_struct_ptr = mesa3d.nak_compile_shader(builder.shader, dump_asm, nak_compiler, robust2_modes, fs_key)

    else:
        print("\nNo suitable Nouveau device found. Cannot create NAK compiler.")

    compiled_binary = b"actual_compiled_binary"

    del _nak_nir_cache[nak_nir_id]
    return compiled_binary

class NakProgram:
  def __init__(self, name:str, lib:bytes): pass
  def __call__(self, *bufs, global_size:tuple[int,int,int]=(1,1,1), local_size:tuple[int,int,int]=(1,1,1), vals:tuple[int, ...]=(), wait=False):
    return 1e-4

class NakAllocator(Allocator['NakDevice']):
  def _alloc(self, size, options): pass
  def _copyin(self, dest, src:memoryview): pass
  def _copyout(self, dest:memoryview, src): pass
  def _transfer(self, dest, src, sz:int, src_dev, dest_dev): pass

class NakGraph(MultiGraphRunner):
  def __call__(self, input_rawbuffers, var_vals, wait=False) -> float|None: return 1e-3

class NakDevice(Compiled):
  def __init__(self, device:str): super().__init__(device, NakAllocator(self), NakRenderer(), NakCompiler(), NakProgram, NakGraph)
