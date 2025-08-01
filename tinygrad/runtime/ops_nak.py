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

    # Store a mapping of UOp arguments to NIR variables
    nir_vars = {}

    printed_once = False
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

            ## Store the variable in our mapping for later use
            nir_vars[var_binding] = nir_var
        else:
            if not printed_once:
                print(f"Unhandled uop: {uop}")
                printed_once = True

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
