import ctypes
import mesa3d
from tinygrad.device import Compiled, Compiler, Renderer, Allocator
from tinygrad.dtype import dtypes
from tinygrad.engine.jit import MultiGraphRunner
from tinygrad.uop.ops import Ops, UOp

class NakRenderer(Renderer):
  device = "NAK"

  def get_or_create_ssa_def(self, uop, builder, ssa_defs):
    ssa_def = ssa_defs.get(uop)
    if ssa_def is not None:
      return ssa_def

    if uop.op == Ops.CONST:
      const_val = uop.arg
      const_dtype = uop.dtype

      if const_dtype == dtypes.int:
        const_def = mesa3d.nir_imm_int(builder, int(const_val))
      elif const_dtype == dtypes.float:
        const_def = mesa3d.nir_imm_float(builder, float(const_val))
      else:
        raise NotImplementedError(f"Unsupported constant type: {const_dtype}")

      ssa_defs[uop] = const_def
      return const_def

    raise ValueError(f"SSA definition for UOp {uop} not found and cannot be created.")

  def render(self, uops: list) -> str:
    stage = mesa3d.gl_shader_stage.COMPUTE
    options = mesa3d.nir_shader_compiler_options()
    builder = mesa3d.nir_builder_init_simple_shader(stage, options, "simple")
    mesa3d.glsl_type_singleton_init_or_ref()

    ssa_defs = {}
    nir_vars = {}
    unhandled_uops = set()
    handled_uops = set()

    print(f"Number of uops: {len(uops)}")
    #for idx, uop in enumerate(uops):
    #  print(f"UOp at index {idx}: {uop.op}, dtype: {uop.dtype}, arg: {uop.arg}, src: {uop.src}")

    for uop in uops:
      if uop.op == Ops.DEFINE_GLOBAL:
        handled_uops.add(uop.op)

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
        handled_uops.add(uop.op)

        const_val = uop.arg
        const_dtype = uop.dtype

        if const_dtype == dtypes.int:
          const_def = mesa3d.nir_imm_int(builder, int(const_val))
        elif const_dtype == dtypes.float:
          const_def = mesa3d.nir_imm_float(builder, float(const_val))
        else:
          raise NotImplementedError(f"Unsupported constant type: {const_dtype}")

        ssa_defs[uop] = const_def

      elif uop.op == Ops.INDEX:
        handled_uops.add(uop.op)
        ssbo_uop = uop.src[0]
        index_uop = uop.src[1]

        ssbo_var = nir_vars.get(ssbo_uop.arg)
        if ssbo_var is None:
          raise ValueError(f"SSBO variable for binding {ssbo_uop.arg} not found.")

        index_def = self.get_or_create_ssa_def(index_uop, builder, ssa_defs)

        element_type = ssbo_var.type
        while element_type.is_array():
            element_type = element_type.array

        element_size = mesa3d.glsl_get_explicit_size(element_type, True)
        offset_def = mesa3d.nir_imul_imm(builder, index_def, element_size)

        num_components = mesa3d.glsl_get_vector_elements(element_type)
        bit_size = mesa3d.glsl_get_bit_size(element_type)

        ssbo_deref = mesa3d.nir_build_deref_var(builder, ssbo_var)
        array_deref = mesa3d.nir_build_deref_array(builder, ssbo_deref, index_def)
        loaded_val_def = mesa3d.nir_load_deref(builder, array_deref)

        ssa_defs[uop] = loaded_val_def

      elif uop.op == Ops.SINK:
        unhandled_uops.add(uop.op)
        pass
      elif uop.op == Ops.LOAD:
        unhandled_uops.add(uop.op)
        pass
      elif uop.op == Ops.STORE:
        unhandled_uops.add(uop.op)
        pass
      elif uop.op == Ops.INDEX:
        unhandled_uops.add(uop.op)
        pass
      elif uop.op == Ops.ADD:
        unhandled_uops.add(uop.op)
        pass

    #  elif uop.op == Ops.STORE:
    #    dest_uop = uop.src[0]
    #    src_uop = uop.src[1]

    #    dest_def = self.get_or_create_ssa_def(dest_uop, builder, ssa_defs)
    #    src_def = self.get_or_create_ssa_def(src_uop, builder, ssa_defs)

    #  elif uop.op == Ops.SINK:
    #    for src_uop in uop.src:
    #      if src_uop.op == Ops.STORE:
    #        dest_uop = src_uop.src[0]
    #        src_uop_val = src_uop.src[1]

    #        dest_def = self.get_or_create_ssa_def(dest_uop, builder, ssa_defs)
    #        src_def = self.get_or_create_ssa_def(src_uop_val, builder, ssa_defs)

    print(f"Handled uops: {handled_uops}")
    print(f"Unhandled uops: {unhandled_uops}")

    #mesa3d.nir_validate_shader(builder.shader, None)
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
