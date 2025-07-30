# -*- coding: utf-8 -*-
#
# TARGET arch is: []
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                type_ = type_._type_
                if hasattr(type_, 'as_dict'):
                    value = [type_.as_dict(v) for v in value]
                else:
                    value = [i for i in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass





# BITSET_WORD = unsigned int # macro

# values for enumeration 'bool'
bool__enumvalues = {
    0: 'false',
    1: 'true',
}
false = 0
true = 1
bool = ctypes.c_uint32 # enum

# values for enumeration 'ENUM_PACKED'
ENUM_PACKED__enumvalues = {
    0: 'nir_instr_type_alu',
    1: 'nir_instr_type_deref',
    2: 'nir_instr_type_call',
    3: 'nir_instr_type_tex',
    4: 'nir_instr_type_intrinsic',
    5: 'nir_instr_type_load_const',
    6: 'nir_instr_type_jump',
    7: 'nir_instr_type_undef',
    8: 'nir_instr_type_phi',
    9: 'nir_instr_type_parallel_copy',
}
nir_instr_type_alu = 0
nir_instr_type_deref = 1
nir_instr_type_call = 2
nir_instr_type_tex = 3
nir_instr_type_intrinsic = 4
nir_instr_type_load_const = 5
nir_instr_type_jump = 6
nir_instr_type_undef = 7
nir_instr_type_phi = 8
nir_instr_type_parallel_copy = 9
ENUM_PACKED = ctypes.c_uint32 # enum
nir_instr_type = ENUM_PACKED
nir_instr_type__enumvalues = ENUM_PACKED__enumvalues
class struct_exec_node(Structure):
    pass

struct_exec_node._pack_ = 1 # source:False
struct_exec_node._fields_ = [
    ('next', ctypes.POINTER(struct_exec_node)),
    ('prev', ctypes.POINTER(struct_exec_node)),
]


# values for enumeration 'nir_cf_node_type'
nir_cf_node_type__enumvalues = {
    0: 'nir_cf_node_block',
    1: 'nir_cf_node_if',
    2: 'nir_cf_node_loop',
    3: 'nir_cf_node_function',
}
nir_cf_node_block = 0
nir_cf_node_if = 1
nir_cf_node_loop = 2
nir_cf_node_function = 3
nir_cf_node_type = ctypes.c_uint32 # enum
class struct_nir_cf_node(Structure):
    pass

struct_nir_cf_node._pack_ = 1 # source:False
struct_nir_cf_node._fields_ = [
    ('node', struct_exec_node),
    ('type', nir_cf_node_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('parent', ctypes.POINTER(struct_nir_cf_node)),
]

nir_cf_node = struct_nir_cf_node
class struct_exec_list(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('head_sentinel', struct_exec_node),
    ('tail_sentinel', struct_exec_node),
     ]

class struct_nir_block(Structure):
    pass

class struct_set(Structure):
    pass

struct_nir_block._pack_ = 1 # source:False
struct_nir_block._fields_ = [
    ('cf_node', nir_cf_node),
    ('instr_list', struct_exec_list),
    ('index', ctypes.c_uint32),
    ('divergent', bool),
    ('successors', ctypes.POINTER(struct_nir_block) * 2),
    ('predecessors', ctypes.POINTER(struct_set)),
    ('imm_dom', ctypes.POINTER(struct_nir_block)),
    ('num_dom_children', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('dom_children', ctypes.POINTER(ctypes.POINTER(struct_nir_block))),
    ('dom_frontier', ctypes.POINTER(struct_set)),
    ('dom_pre_index', ctypes.c_uint32),
    ('dom_post_index', ctypes.c_uint32),
    ('start_ip', ctypes.c_uint32),
    ('end_ip', ctypes.c_uint32),
    ('live_in', ctypes.POINTER(ctypes.c_uint32)),
    ('live_out', ctypes.POINTER(ctypes.c_uint32)),
]

nir_block = struct_nir_block
class struct_nir_instr(Structure):
    pass

struct_nir_instr._pack_ = 1 # source:False
struct_nir_instr._fields_ = [
    ('node', struct_exec_node),
    ('block', ctypes.POINTER(struct_nir_block)),
    ('type', nir_instr_type),
    ('pass_flags', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 3),
    ('has_debug_info', bool),
    ('index', ctypes.c_uint32),
]

nir_instr = struct_nir_instr
__all__ = \
    ['ENUM_PACKED', 'bool', 'false', 'nir_block', 'nir_cf_node',
    'nir_cf_node_block', 'nir_cf_node_function', 'nir_cf_node_if',
    'nir_cf_node_loop', 'nir_cf_node_type', 'nir_instr',
    'nir_instr_type', 'nir_instr_type__enumvalues',
    'nir_instr_type_alu', 'nir_instr_type_call',
    'nir_instr_type_deref', 'nir_instr_type_intrinsic',
    'nir_instr_type_jump', 'nir_instr_type_load_const',
    'nir_instr_type_parallel_copy', 'nir_instr_type_phi',
    'nir_instr_type_tex', 'nir_instr_type_undef', 'struct_exec_list',
    'struct_exec_node', 'struct_nir_block', 'struct_nir_cf_node',
    'struct_nir_instr', 'struct_set', 'true']
