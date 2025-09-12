import ctypes
import mesa3d
import sys
import uuid
from tinygrad.dtype import dtypes, PtrDType
from tinygrad.renderer import Renderer
from tinygrad.uop.ops import Ops, UOp, PatternMatcher, UPat

_nak_nir_cache = {}

nak_matcher = PatternMatcher([
    # empty for now
])

string_rewrite = PatternMatcher([
    (UPat(Ops.DEFINE_GLOBAL, name="x"), lambda x: print("bla")),
])

#  if uop.op == Ops.DEFINE_GLOBAL:
#        var_type = uop.dtype
#        var_binding = uop.arg
#
#        if var_type.base == dtypes.int:
#          glsl_base_type = mesa3d.glsl_int_type()
#        elif var_type.base == dtypes.float:
#          glsl_base_type = mesa3d.glsl_float_type()
#        else:
#          raise NotImplementedError(f"Unsupported dtype: {var_type.base}")
#
#        nir_type = mesa3d.glsl_array_type(glsl_base_type, 0, 4)
#        nir_var = mesa3d.nir_variable_create(builder.shader,
#                                             mesa3d.nir_var_mem_ssbo,
#                                             nir_type,
#                                             f"ssbo_var_{var_binding}")
#        nir_var.data.binding = var_binding
#        nir_var.data.explicit_binding = True
#        nir_vars[var_binding] = nir_var

class NakRenderer(Renderer):
  device = "NAK"
  extra_matcher = nak_matcher

  def __init__(self):
    super().__init__()
    self.ssa_defs = {}
    self.nir_vars = {}
    self.deref_instrs = {}
    self.stage = mesa3d.gl_shader_stage.COMPUTE
    self.options = mesa3d.nir_shader_compiler_options()
    self.builder = mesa3d.nir_builder_init_simple_shader(self.stage, self.options, "simple")
    mesa3d.glsl_type_singleton_init_or_ref()

  def render(self, uops: list) -> str:
    self.ssa_defs.clear()
    self.nir_vars.clear()

    for uop in uops:
      if uop.op is Ops.NOOP:
        continue
      
      result = string_rewrite.rewrite(uop, ctx=self)
      
      if result is None:
        raise RuntimeError(f"Failed to generate NIR for {uop.op}")
      
      if uop.op == Ops.SINK:
        return result
    
    raise RuntimeError("No SINK operation found to finalize the NIR generation.")


