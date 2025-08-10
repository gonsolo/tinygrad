import ctypes
import mesa3d
import sys
import uuid
from tinygrad.runtime.autogen.drm import drmGetDevices2, drmFreeDevices, struct__drmDevice, uint32_t
from tinygrad.device import Compiled, Compiler, Renderer, Allocator
from tinygrad.dtype import dtypes
from tinygrad.engine.jit import MultiGraphRunner
from tinygrad.uop.ops import Ops, UOp

drmGetDevices2.argtypes = [uint32_t, ctypes.POINTER(ctypes.POINTER(struct__drmDevice)), ctypes.c_int32]
drmGetDevices2.restype = ctypes.c_int32

drmFreeDevices.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__drmDevice)), ctypes.c_int32]
drmFreeDevices.restype = None


import ctypes
import mesa3d
import sys
import uuid
from tinygrad.runtime.autogen.drm import drmGetDevices2, drmFreeDevices, struct__drmDevice, uint32_t

# Ensure constants are defined globally or imported
# (These should ideally come from your clang2py generated bindings if -k cdefstum is used)
DRM_NODE_RENDER = 2
DRM_BUS_PCI = 0

# You might need to adjust this depending on how mesa3d._drmDevice is actually defined or aliased
# If the pybind11 binding expects a specific type for the 'drm_device' argument,
# this alias might still be needed, but it depends on the pybind11 side.
# If nouveau_ws_device_new_wrapper in C++ takes uintptr_t, then this Python alias is not needed.
# mesa3d._drmDevice = struct__drmDevice # This line is likely not needed if using uintptr_t in C++ wrapper

def find_drm_devices():
    """
    Finds and returns the first suitable Nouveau device.
    Returns the nouveau_ws_device object or None if not found.
    """
    # Allocate space for device pointers
    MAX_DEVICES = 64
    devices_ptr_array_type = ctypes.POINTER(struct__drmDevice) * MAX_DEVICES
    devices_ptr_array = devices_ptr_array_type()

    # Call drmGetDevices2
    # Ensure drmGetDevices2's argtypes and restype are set correctly in your autogen/drm.py
    # or before calling it the first time. Example:
    # drmGetDevices2.argtypes = [uint32_t, ctypes.POINTER(ctypes.POINTER(struct__drmDevice)), ctypes.c_int32]
    # drmGetDevices2.restype = ctypes.c_int32
    num_devices = drmGetDevices2(0, devices_ptr_array, MAX_DEVICES)

    if num_devices <= 0:
        print("No DRM devices found.")
        return None

    found_nouveau_device = None
    for i in range(num_devices):
        device_ptr = devices_ptr_array[i] # This is the ctypes pointer (LP_struct__drmDevice)

        # Check if the pointer is valid before dereferencing
        if not device_ptr:
            continue

        device = device_ptr.contents # Dereference to get the struct__drmDevice object

        # 1. Check for a render node
        has_render_node = (device.available_nodes & (1 << DRM_NODE_RENDER)) != 0

        ## 2. Check the bus type
        is_pci_bus = device.bustype == DRM_BUS_PCI

        ## 3. Check the PCI vendor ID
        is_nvidia_vendor = False
        if is_pci_bus and device.deviceinfo.pci: # Ensure pci is not null before accessing contents
            vendor_id = device.deviceinfo.pci.contents.vendor_id
            is_nvidia_vendor = vendor_id == 0x10de

        # Combine the checks to identify a potential Nouveau device
        if has_render_node and is_pci_bus and is_nvidia_vendor:
            print(f"Found a potential Nouveau device at index {i}!")

            # Pass the memory address of the ctypes pointer's value
            # This relies on your pybind11 wrapper for nouveau_ws_device_new accepting uintptr_t
            device_address = ctypes.cast(device_ptr, ctypes.c_void_p)
            found_nouveau_device = mesa3d.nouveau_ws_device_new(device_address.value)

            if found_nouveau_device:
                print(f"Successfully created a new nouveau device: {found_nouveau_device}")
                # If you only want the first one, return immediately
                # Otherwise, you could store them in a list and return the list
                drmFreeDevices(devices_ptr_array, num_devices) # Free devices before returning
                return found_nouveau_device
            else:
                print(f"Failed to create nouveau_ws_device for device at index {i}.")
        else:
            print(f"Device at index {i} is not a Nouveau device (render_node={has_render_node}, pci_bus={is_pci_bus}, nvidia_vendor={is_nvidia_vendor}).")

    drmFreeDevices(devices_ptr_array, num_devices) # Free devices if loop completes without finding one
    return None # No suitable device found

_nak_nir_cache = {}

class NakRenderer(Renderer):
  device = "NAK"

  def render(self, uops: list) -> str:
    stage = mesa3d.gl_shader_stage.COMPUTE
    options = mesa3d.nir_shader_compiler_options()
    builder = mesa3d.nir_builder_init_simple_shader(stage, options, "simple")
    mesa3d.glsl_type_singleton_init_or_ref()

    ssa_defs = {}
    nir_vars = {}
    deref_instrs = {}

    #for uop in uops:
    #    print(uop)
    #sys.exit()

    for uop in uops:
      if uop.op == Ops.DEFINE_GLOBAL:
        var_type = uop.dtype
        var_binding = uop.arg
        #var_size = var_type.count

        if var_type.base == dtypes.int:
          glsl_base_type = mesa3d.glsl_int_type()
        elif var_type.base == dtypes.float:
          glsl_base_type = mesa3d.glsl_float_type()
        else:
          raise NotImplementedError(f"Unsupported dtype: {var_type.base}")

        nir_type = mesa3d.glsl_array_type(glsl_base_type, 0, 4)
        nir_var = mesa3d.nir_variable_create(builder.shader,
                                             mesa3d.nir_var_mem_ssbo,
                                             nir_type,
                                             f"ssbo_var_{var_binding}")
        nir_var.data.binding = var_binding
        nir_var.data.explicit_binding = True
        nir_vars[var_binding] = nir_var

      elif uop.op == Ops.SINK:
        store_uop = uop.src[0]
        if store_uop.op != Ops.STORE:
            raise ValueError("SINK UOp's source is not a STORE operation.")

        dst_uop = store_uop.src[0]
        src_uop = store_uop.src[1]

        dst_deref = self._get_or_create_deref_instr(dst_uop, builder, deref_instrs, nir_vars, ssa_defs)
        src_def = self._get_or_create_ssa_def(src_uop, builder, ssa_defs, deref_instrs, nir_vars)

        mesa3d.nir_store_deref(builder, dst_deref, src_def, 0xff)

        #mesa3d.ralloc_free(builder.shader);

        nak_nir_id = str(uuid.uuid4())
        _nak_nir_cache[nak_nir_id] = {'builder': builder, 'options': options}
        return nak_nir_id

  def _get_or_create_deref_instr(self, uop, builder, deref_instrs, nir_vars, ssa_defs):
    deref_instr = deref_instrs.get(uop)
    if deref_instr is not None:
        return deref_instr

    if uop.op == Ops.INDEX:
        ssbo_uop = uop.src[0]
        index_uop = uop.src[1]

        ssbo_var = nir_vars.get(ssbo_uop.arg)
        if ssbo_var is None:
            raise ValueError(f"SSBO variable for binding {ssbo_uop.arg} not found.")

        index_def = self._get_or_create_ssa_def(index_uop, builder, ssa_defs, deref_instrs, nir_vars)

        ssbo_deref = mesa3d.nir_build_deref_var(builder, ssbo_var)
        #deref_instr = mesa3d.nir_build_deref_ptr_as_array(builder, ssbo_deref, index_def)
        deref_instr = mesa3d.nir_build_deref_array(builder, ssbo_deref, index_def)

        deref_instrs[uop] = deref_instr
        return deref_instr
    else:
        raise NotImplementedError(f"Unsupported UOp type for dereference: {uop.op}")

  def _get_or_create_ssa_def(self, uop, builder, ssa_defs, deref_instrs, nir_vars):
    ssa_def = ssa_defs.get(uop)
    if ssa_def is not None:
        return ssa_def

    if uop.op == Ops.CONST:
        const_val = uop.arg
        const_dtype = uop.dtype
        if const_dtype == dtypes.int:
            ssa_def = mesa3d.nir_imm_int(builder, int(const_val))
        elif const_dtype == dtypes.float:
            ssa_def = mesa3d.nir_imm_float(builder, float(const_val))
        else:
            raise NotImplementedError(f"Unsupported constant type: {const_dtype}")

    elif uop.op == Ops.ADD:
        src_defs = [self._get_or_create_ssa_def(src, builder, ssa_defs, deref_instrs, nir_vars) for src in uop.src]
        ssa_def = mesa3d.nir_iadd(builder, src_defs[0], src_defs[1])

    elif uop.op == Ops.MUL:
        src_defs = [self._get_or_create_ssa_def(src, builder, ssa_defs, deref_instrs, nir_vars) for src in uop.src]
        ssa_def = mesa3d.nir_imul(builder, src_defs[0], src_defs[1])

    elif uop.op == Ops.LOAD:
        deref_chain = self._get_or_create_deref_instr(uop.src[0], builder, deref_instrs, nir_vars, ssa_defs)
        ssa_def = mesa3d.nir_load_deref(builder, deref_chain)

    elif uop.op == Ops.SPECIAL:
        src_defs = [self._get_or_create_ssa_def(src, builder, ssa_defs, deref_instrs, nir_vars) for src in uop.src]

        if isinstance(uop.arg, tuple) and uop.arg[0] == 'lidx0':
            lidx_def = mesa3d.nir_load_local_invocation_id(builder)
            print(f"gonsolo lidx0 channel index: {uop.arg[1]}")
            ssa_def = mesa3d.nir_channel(builder, lidx_def, uop.arg[1])
        elif isinstance(uop.arg, tuple) and uop.arg[0] == 'gidx0':

            global_shape = ...

            gidx_def = mesa3d.nir_load_global_invocation_id(builder, 32)

            ssa_def = mesa3d.nir_channel(builder, gidx_def, 0)

            for i in range(1, len(global_shape)):
                current_id = None
                if i < 3:
                    current_id = mesa3d.nir_channel(builder, gidx_def, i)
                else:
                    current_id = mesa3d.nir_imm_int(builder, 0)

                ssa_def = mesa3d.nir_imul_imm(builder, ssa_def, global_shape[i])
                ssa_def = mesa3d.nir_iadd(builder, ssa_def, current_id)

        else:
            raise NotImplementedError(f"Handling for SPECIAL UOp with arg '{uop.arg}' is not yet implemented.")

    elif uop.op == Ops.WHERE:
        cond_def = self._get_or_create_ssa_def(uop.src[0], builder, ssa_defs, deref_instrs, nir_vars)
        true_def = self._get_or_create_ssa_def(uop.src[1], builder, ssa_defs, deref_instrs, nir_vars)
        false_def = self._get_or_create_ssa_def(uop.src[2], builder, ssa_defs, deref_instrs, nir_vars)

        # In NIR, the condition for a select instruction must be a boolean.
        # We assume the condition UOp produces a boolean-like integer.
        # This converts it to a boolean value.
        bool_cond = mesa3d.nir_ine_imm(builder, cond_def, 0)
        ssa_def = mesa3d.nir_bcsel(builder, bool_cond, true_def, false_def)

    elif uop.op == Ops.CMPLT:
        src_defs = [self._get_or_create_ssa_def(src, builder, ssa_defs, deref_instrs, nir_vars) for src in uop.src]
        ssa_def = mesa3d.nir_ilt(builder, src_defs[0], src_defs[1])

    else:
        raise NotImplementedError(f"Unsupported UOp type: {uop.op}")

    ssa_defs[uop] = ssa_def
    return ssa_def

class NakCompiler(Compiler):
  # Set the target device
  device = "NAK"

  def compile(self, prg: str) -> bytes:
    nak_nir_id = prg
    cached_data = _nak_nir_cache.get(nak_nir_id)
    if cached_data is None:
      raise ValueError("Could not find the cached data in the global cache.")

    builder = cached_data['builder']
    options = cached_data['options']

    #print("Original shader:")
    #mesa3d.nir_print_shader(builder.shader, sys.stdout.fileno())

    dump_asm = False
    robust2_modes = mesa3d.nir_variable_mode(0)
    fs_key = None # For a compute shader, this is typically NULL

    # --- Main part of your script ---
    print("Searching for DRM devices...")
    nouveau_device = find_drm_devices()
    
    if nouveau_device:
        print("\nDRM device found. Proceeding with compiler creation.")
        # Use the returned nouveau_device object
        # This line assumes 'nouveau_device' has an attribute 'nv_dev_info' as expected by nak_compiler_create
        # You might need to adjust this access based on the actual structure of nouveau_ws_device
        info = nouveau_device.info
        nak_compiler = mesa3d.nak_compiler_create(info)
        print("NAK Compiler created successfully!")

        #mesa3d.nir_print_shader(builder.shader, sys.stdout.fileno())

        mesa3d.nak_preprocess_nir(builder.shader, nak_compiler)

        #mesa3d.nir_lower_io(builder.shader)
        mesa3d.nir_lower_vars_to_ssa(builder.shader)
        
        # From nvk_lower_nir:
        mesa3d.nir_lower_explicit_io_ssbo_simple(builder.shader)

        mesa3d.nir_opt_dce(builder.shader)
        mesa3d.nir_opt_algebraic(builder.shader)
        mesa3d.nir_opt_constant_folding(builder.shader)

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

