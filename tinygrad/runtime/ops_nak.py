import ctypes
import mesa3d
from tinygrad.device import Compiled, Compiler, Renderer, Allocator
from tinygrad.dtype import dtypes
from tinygrad.engine.jit import MultiGraphRunner
from tinygrad.uop.ops import Ops, UOp

import mesa3d


class NakRenderer(Renderer):
  device = "NAK"

  def render(self, uops: list) -> str:
    stage = mesa3d.gl_shader_stage.COMPUTE
    options = mesa3d.nir_shader_compiler_options()
    builder = mesa3d.nir_builder_init_simple_shader(stage, options, "simple")
    main = mesa3d.nir_shader_get_function_for_name(builder.shader, "main");
    mesa3d.glsl_type_singleton_init_or_ref()

    ssa_defs = {}
    nir_vars = {}
    unhandled_uops = set()
    printed = False

    for uop in uops:
        if uop.op == Ops.DEFINE_GLOBAL:
            var_type = uop.dtype
            var_binding = uop.arg
            var_size = var_type.count

            if var_type.base == dtypes.int:
                glsl_base_type = mesa3d.glsl_int_type()
            elif var_type.base == dtypes.float:
                glsl_base_type = mesa3d.glsl_float_type()
            else:
                raise NotImplementedError(f"Unsupported dtype: {var_type.base}")

            nir_type = mesa3d.glsl_array_type(glsl_base_type, var_size, 0)
            nir_var = mesa3d.nir_variable_create(builder.shader,
                                                 mesa3d.nir_var_mem_ssbo,
                                                 nir_type,
                                                 f"ssbo_var_{var_binding}")
            nir_var.data.binding = var_binding
            nir_var.data.explicit_binding = True

            nir_vars[var_binding] = nir_var

        elif uop.op == Ops.CONST:
            const_val = uop.arg
            const_dtype = uop.dtype

            if const_dtype == dtypes.int:
                const_def = mesa3d.nir_imm_int(builder, int(const_val))
            elif const_dtype == dtypes.float:
                const_def = mesa3d.nir_imm_float(builder, float(const_val))
            else:
                raise NotImplementedError(f"Unsupported constant type: {const_dtype}")

            ssa_defs[uop] = const_def

        #elif uop.op == Ops.INDEX:
        #    ssbo_uop = uop.src[0]
        #    index_uop = uop.src[1]

        #    # Look up the SSBO variable by its binding
        #    ssbo_var = nir_vars.get(ssbo_uop.arg)
        #    if ssbo_var is None:
        #        raise ValueError(f"SSBO variable for binding {ssbo_uop.arg} not found.")

        #    # Get the SSA definition for the index
        #    index_def = ssa_defs.get(index_uop)
        #    if index_def is None:
        #        raise ValueError(f"SSA definition for index UOp not found.")

        #    ssbo_type = ssbo_var.type
        #    if ssbo_type.is_array():
        #        array_element_type = ssbo_type.array
        #        while array_element_type and array_element_type.is_array():
        #            array_element_type = array_element_type.array
        #        if array_element_type:
        #            element_type = array_element_type
        #    else:
        #        element_type = ssbo_type
        #    # Get the size of a single element in bytes
        #    element_size = mesa3d.glsl_get_explicit_size(element_type, True)

        #    # Calculate the byte offset: index * element_size
        #    offset_def = mesa3d.nir_imul_imm(builder, index_def, element_size)

        #    # Load the value from the SSBO at the calculated offset
        #    num_components = mesa3d.glsl_get_vector_elements(element_type)
        #    bit_size = mesa3d.glsl_get_bit_size(element_type)

        #    loaded_val_def = mesa3d.nir_load_ssbo(builder, num_components, bit_size,
        #                                          mesa3d.nir_load_var(builder, ssbo_var),
        #                                          offset_def)

        #    # Store the loaded value's SSA definition for later use
        #    ssa_defs[uop] = loaded_val_def

        else:
            if not printed:
                print(uop)
                printed = True
            unhandled_uops.add(uop.op)

    #print(unhandled_uops)
    mesa3d.nir_validate_shader(builder.shader, None)
    return "Ok"

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
  def __init__(self, device:str): super().__init__(device, NakAllocator(self), NakRenderer(), Compiler(), NakProgram, NakGraph)
