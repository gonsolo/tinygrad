import ctypes
import mesa3d
from tinygrad.device import Compiled, Compiler, Renderer, Allocator
from tinygrad.dtype import dtypes
from tinygrad.engine.jit import MultiGraphRunner
from tinygrad.uop.ops import Ops, UOp

DTYPE_TO_BIT_SIZE = {
    dtypes.float32: 32,
    dtypes.int32: 32,
    # ..
}

mem_ctx = mesa3d.ralloc_context(None)
stage = mesa3d.gl_shader_stage.COMPUTE
options = mesa3d.nir_shader_compiler_options()
si = mesa3d.shader_info()
si.stage = stage
shader = mesa3d.nir_shader_create(mem_ctx, stage, options, si)
mesa3d.ralloc_free(mem_ctx)

#name = "bla"
#function = nir_function_create(shader, name)
#function_impl = nir_function_impl_create(nir_function)
#builder = nir_builder_create(function_impl)
# libnir_mesa.nir_builder_init(ctypes.byref(nir_builder_inst), ...)

uop_to_nir_type = {
    #Ops.DEFINE_GLOBAL: nir_instr_type_intrinsic,
    # Ops.ALU: nir_instr_type_alu,
    # Ops.LOAD: ...
}

#def convert_uop_to_nir_instr(uop: UOp) -> nir_instr:
#  """
#  Converts a single Tinygrad UOp to a nir_instr structure.
#  """
#  nir_inst = nir_instr()
#
#  try:
#    uop_to_nir_type = {
#        Ops.DEFINE_GLOBAL: nir_instr_type_intrinsic,
#        # ...
#    }
#    nir_inst.type = uop_to_nir_type[uop.op]
#  except KeyError:
#    print(f"Warning: No mapping for UOp op {uop.op}. Using default type.")
#    nir_inst.type = nir_instr_type_undef
#
#  return nir_inst

class NakRenderer(Renderer):
  device = "NAK"
  code_for_op = {k:lambda:None for k in [Ops.EXP2, Ops.LOG2, Ops.SIN, Ops.SQRT]}
  has_local = False
  def render(self, uops:list) -> str:
    result = ""
    #seen = False
    #for uop in uops:
      #if not seen:
      #nir_inst = convert_uop_to_nir_instr(uop)
      #print(uop, nir_inst)
      #seen = True
    return result

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
