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



c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))



class FunctionFactoryStub:
    def __getattr__(self, _):
      return ctypes.CFUNCTYPE(lambda y:y)

# libraries['FIXME_STUB'] explanation
# As you did not list (-l libraryname.so) a library that exports this function
# This is a non-working stub instead. 
# You can either re-run clan2py with -l /path/to/library.so
# Or manually fix this by comment the ctypes.CDLL loading
_libraries = {}
_libraries['FIXME_STUB'] = FunctionFactoryStub() #  ctypes.CDLL('FIXME_STUB')
_libraries['libdrm.so.2'] = ctypes.CDLL('/usr/lib/libdrm.so.2')


class struct___va_list_tag(Structure):
    pass

struct___va_list_tag._pack_ = 1 # source:False
struct___va_list_tag._fields_ = [
    ('gp_offset', ctypes.c_uint32),
    ('fp_offset', ctypes.c_uint32),
    ('overflow_arg_area', ctypes.POINTER(None)),
    ('reg_save_area', ctypes.POINTER(None)),
]

__gnuc_va_list = struct___va_list_tag * 1
va_list = struct___va_list_tag * 1
__u_char = ctypes.c_ubyte
__u_short = ctypes.c_uint16
__u_int = ctypes.c_uint32
__u_long = ctypes.c_uint64
__int8_t = ctypes.c_byte
__uint8_t = ctypes.c_ubyte
__int16_t = ctypes.c_int16
__uint16_t = ctypes.c_uint16
__int32_t = ctypes.c_int32
__uint32_t = ctypes.c_uint32
__int64_t = ctypes.c_int64
__uint64_t = ctypes.c_uint64
__int_least8_t = ctypes.c_byte
__uint_least8_t = ctypes.c_ubyte
__int_least16_t = ctypes.c_int16
__uint_least16_t = ctypes.c_uint16
__int_least32_t = ctypes.c_int32
__uint_least32_t = ctypes.c_uint32
__int_least64_t = ctypes.c_int64
__uint_least64_t = ctypes.c_uint64
__quad_t = ctypes.c_int64
__u_quad_t = ctypes.c_uint64
__intmax_t = ctypes.c_int64
__uintmax_t = ctypes.c_uint64
__dev_t = ctypes.c_uint64
__uid_t = ctypes.c_uint32
__gid_t = ctypes.c_uint32
__ino_t = ctypes.c_uint64
__ino64_t = ctypes.c_uint64
__mode_t = ctypes.c_uint32
__nlink_t = ctypes.c_uint64
__off_t = ctypes.c_int64
__off64_t = ctypes.c_int64
__pid_t = ctypes.c_int32
class struct___fsid_t(Structure):
    pass

struct___fsid_t._pack_ = 1 # source:False
struct___fsid_t._fields_ = [
    ('__val', ctypes.c_int32 * 2),
]

__fsid_t = struct___fsid_t
__clock_t = ctypes.c_int64
__rlim_t = ctypes.c_uint64
__rlim64_t = ctypes.c_uint64
__id_t = ctypes.c_uint32
__time_t = ctypes.c_int64
__useconds_t = ctypes.c_uint32
__suseconds_t = ctypes.c_int64
__suseconds64_t = ctypes.c_int64
__daddr_t = ctypes.c_int32
__key_t = ctypes.c_int32
__clockid_t = ctypes.c_int32
__timer_t = ctypes.POINTER(None)
__blksize_t = ctypes.c_int64
__blkcnt_t = ctypes.c_int64
__blkcnt64_t = ctypes.c_int64
__fsblkcnt_t = ctypes.c_uint64
__fsblkcnt64_t = ctypes.c_uint64
__fsfilcnt_t = ctypes.c_uint64
__fsfilcnt64_t = ctypes.c_uint64
__fsword_t = ctypes.c_int64
__ssize_t = ctypes.c_int64
__syscall_slong_t = ctypes.c_int64
__syscall_ulong_t = ctypes.c_uint64
__loff_t = ctypes.c_int64
__caddr_t = ctypes.POINTER(ctypes.c_char)
__intptr_t = ctypes.c_int64
__socklen_t = ctypes.c_uint32
__sig_atomic_t = ctypes.c_int32
u_char = ctypes.c_ubyte
u_short = ctypes.c_uint16
u_int = ctypes.c_uint32
u_long = ctypes.c_uint64
quad_t = ctypes.c_int64
u_quad_t = ctypes.c_uint64
fsid_t = struct___fsid_t
loff_t = ctypes.c_int64
ino_t = ctypes.c_uint64
dev_t = ctypes.c_uint64
gid_t = ctypes.c_uint32
mode_t = ctypes.c_uint32
nlink_t = ctypes.c_uint64
uid_t = ctypes.c_uint32
off_t = ctypes.c_int64
pid_t = ctypes.c_int32
id_t = ctypes.c_uint32
ssize_t = ctypes.c_int64
daddr_t = ctypes.c_int32
caddr_t = ctypes.POINTER(ctypes.c_char)
key_t = ctypes.c_int32
clock_t = ctypes.c_int64
clockid_t = ctypes.c_int32
time_t = ctypes.c_int64
timer_t = ctypes.POINTER(None)
size_t = ctypes.c_uint64
ulong = ctypes.c_uint64
ushort = ctypes.c_uint16
uint = ctypes.c_uint32
int8_t = ctypes.c_int8
int16_t = ctypes.c_int16
int32_t = ctypes.c_int32
int64_t = ctypes.c_int64
u_int8_t = ctypes.c_ubyte
u_int16_t = ctypes.c_uint16
u_int32_t = ctypes.c_uint32
u_int64_t = ctypes.c_uint64
register_t = ctypes.c_int64
try:
    __bswap_16 = _libraries['FIXME_STUB'].__bswap_16
    __bswap_16.restype = __uint16_t
    __bswap_16.argtypes = [__uint16_t]
except AttributeError:
    pass
try:
    __bswap_32 = _libraries['FIXME_STUB'].__bswap_32
    __bswap_32.restype = __uint32_t
    __bswap_32.argtypes = [__uint32_t]
except AttributeError:
    pass
try:
    __bswap_64 = _libraries['FIXME_STUB'].__bswap_64
    __bswap_64.restype = __uint64_t
    __bswap_64.argtypes = [__uint64_t]
except AttributeError:
    pass
try:
    __uint16_identity = _libraries['FIXME_STUB'].__uint16_identity
    __uint16_identity.restype = __uint16_t
    __uint16_identity.argtypes = [__uint16_t]
except AttributeError:
    pass
try:
    __uint32_identity = _libraries['FIXME_STUB'].__uint32_identity
    __uint32_identity.restype = __uint32_t
    __uint32_identity.argtypes = [__uint32_t]
except AttributeError:
    pass
try:
    __uint64_identity = _libraries['FIXME_STUB'].__uint64_identity
    __uint64_identity.restype = __uint64_t
    __uint64_identity.argtypes = [__uint64_t]
except AttributeError:
    pass
class struct___sigset_t(Structure):
    pass

struct___sigset_t._pack_ = 1 # source:False
struct___sigset_t._fields_ = [
    ('__val', ctypes.c_uint64 * 16),
]

__sigset_t = struct___sigset_t
sigset_t = struct___sigset_t
class struct_timeval(Structure):
    pass

struct_timeval._pack_ = 1 # source:False
struct_timeval._fields_ = [
    ('tv_sec', ctypes.c_int64),
    ('tv_usec', ctypes.c_int64),
]

class struct_timespec(Structure):
    pass

struct_timespec._pack_ = 1 # source:False
struct_timespec._fields_ = [
    ('tv_sec', ctypes.c_int64),
    ('tv_nsec', ctypes.c_int64),
]

suseconds_t = ctypes.c_int64
__fd_mask = ctypes.c_int64
class struct_fd_set(Structure):
    pass

struct_fd_set._pack_ = 1 # source:False
struct_fd_set._fields_ = [
    ('__fds_bits', ctypes.c_int64 * 16),
]

fd_set = struct_fd_set
fd_mask = ctypes.c_int64
try:
    select = _libraries['FIXME_STUB'].select
    select.restype = ctypes.c_int32
    select.argtypes = [ctypes.c_int32, ctypes.POINTER(struct_fd_set), ctypes.POINTER(struct_fd_set), ctypes.POINTER(struct_fd_set), ctypes.POINTER(struct_timeval)]
except AttributeError:
    pass
try:
    pselect = _libraries['FIXME_STUB'].pselect
    pselect.restype = ctypes.c_int32
    pselect.argtypes = [ctypes.c_int32, ctypes.POINTER(struct_fd_set), ctypes.POINTER(struct_fd_set), ctypes.POINTER(struct_fd_set), ctypes.POINTER(struct_timespec), ctypes.POINTER(struct___sigset_t)]
except AttributeError:
    pass
blksize_t = ctypes.c_int64
blkcnt_t = ctypes.c_int64
fsblkcnt_t = ctypes.c_uint64
fsfilcnt_t = ctypes.c_uint64
class union___atomic_wide_counter(Union):
    pass

class struct___atomic_wide_counter___value32(Structure):
    pass

struct___atomic_wide_counter___value32._pack_ = 1 # source:False
struct___atomic_wide_counter___value32._fields_ = [
    ('__low', ctypes.c_uint32),
    ('__high', ctypes.c_uint32),
]

union___atomic_wide_counter._pack_ = 1 # source:False
union___atomic_wide_counter._fields_ = [
    ('__value64', ctypes.c_uint64),
    ('__value32', struct___atomic_wide_counter___value32),
]

__atomic_wide_counter = union___atomic_wide_counter
class struct___pthread_internal_list(Structure):
    pass

struct___pthread_internal_list._pack_ = 1 # source:False
struct___pthread_internal_list._fields_ = [
    ('__prev', ctypes.POINTER(struct___pthread_internal_list)),
    ('__next', ctypes.POINTER(struct___pthread_internal_list)),
]

__pthread_list_t = struct___pthread_internal_list
class struct___pthread_internal_slist(Structure):
    pass

struct___pthread_internal_slist._pack_ = 1 # source:False
struct___pthread_internal_slist._fields_ = [
    ('__next', ctypes.POINTER(struct___pthread_internal_slist)),
]

__pthread_slist_t = struct___pthread_internal_slist
class struct___pthread_mutex_s(Structure):
    pass

struct___pthread_mutex_s._pack_ = 1 # source:False
struct___pthread_mutex_s._fields_ = [
    ('__lock', ctypes.c_int32),
    ('__count', ctypes.c_uint32),
    ('__owner', ctypes.c_int32),
    ('__nusers', ctypes.c_uint32),
    ('__kind', ctypes.c_int32),
    ('__spins', ctypes.c_int16),
    ('__elision', ctypes.c_int16),
    ('__list', globals()['__pthread_list_t']),
]

class struct___pthread_rwlock_arch_t(Structure):
    pass

struct___pthread_rwlock_arch_t._pack_ = 1 # source:False
struct___pthread_rwlock_arch_t._fields_ = [
    ('__readers', ctypes.c_uint32),
    ('__writers', ctypes.c_uint32),
    ('__wrphase_futex', ctypes.c_uint32),
    ('__writers_futex', ctypes.c_uint32),
    ('__pad3', ctypes.c_uint32),
    ('__pad4', ctypes.c_uint32),
    ('__cur_writer', ctypes.c_int32),
    ('__shared', ctypes.c_int32),
    ('__rwelision', ctypes.c_byte),
    ('__pad1', ctypes.c_ubyte * 7),
    ('__pad2', ctypes.c_uint64),
    ('__flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct___pthread_cond_s(Structure):
    pass

struct___pthread_cond_s._pack_ = 1 # source:False
struct___pthread_cond_s._fields_ = [
    ('__wseq', globals()['__atomic_wide_counter']),
    ('__g1_start', globals()['__atomic_wide_counter']),
    ('__g_size', ctypes.c_uint32 * 2),
    ('__g1_orig_size', ctypes.c_uint32),
    ('__wrefs', ctypes.c_uint32),
    ('__g_signals', ctypes.c_uint32 * 2),
    ('__unused_initialized_1', ctypes.c_uint32),
    ('__unused_initialized_2', ctypes.c_uint32),
]

__tss_t = ctypes.c_uint32
__thrd_t = ctypes.c_uint64
class struct___once_flag(Structure):
    pass

struct___once_flag._pack_ = 1 # source:False
struct___once_flag._fields_ = [
    ('__data', ctypes.c_int32),
]

__once_flag = struct___once_flag
pthread_t = ctypes.c_uint64
class union_pthread_mutexattr_t(Union):
    pass

union_pthread_mutexattr_t._pack_ = 1 # source:False
union_pthread_mutexattr_t._fields_ = [
    ('__size', ctypes.c_char * 4),
    ('__align', ctypes.c_int32),
]

pthread_mutexattr_t = union_pthread_mutexattr_t
class union_pthread_condattr_t(Union):
    pass

union_pthread_condattr_t._pack_ = 1 # source:False
union_pthread_condattr_t._fields_ = [
    ('__size', ctypes.c_char * 4),
    ('__align', ctypes.c_int32),
]

pthread_condattr_t = union_pthread_condattr_t
pthread_key_t = ctypes.c_uint32
pthread_once_t = ctypes.c_int32
class union_pthread_attr_t(Union):
    pass

union_pthread_attr_t._pack_ = 1 # source:False
union_pthread_attr_t._fields_ = [
    ('__size', ctypes.c_char * 56),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 48),
]

pthread_attr_t = union_pthread_attr_t
class union_pthread_mutex_t(Union):
    pass

union_pthread_mutex_t._pack_ = 1 # source:False
union_pthread_mutex_t._fields_ = [
    ('__data', struct___pthread_mutex_s),
    ('__size', ctypes.c_char * 40),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 32),
]

pthread_mutex_t = union_pthread_mutex_t
class union_pthread_cond_t(Union):
    pass

union_pthread_cond_t._pack_ = 1 # source:False
union_pthread_cond_t._fields_ = [
    ('__data', struct___pthread_cond_s),
    ('__size', ctypes.c_char * 48),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 40),
]

pthread_cond_t = union_pthread_cond_t
class union_pthread_rwlock_t(Union):
    pass

union_pthread_rwlock_t._pack_ = 1 # source:False
union_pthread_rwlock_t._fields_ = [
    ('__data', struct___pthread_rwlock_arch_t),
    ('__size', ctypes.c_char * 56),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 48),
]

pthread_rwlock_t = union_pthread_rwlock_t
class union_pthread_rwlockattr_t(Union):
    pass

union_pthread_rwlockattr_t._pack_ = 1 # source:False
union_pthread_rwlockattr_t._fields_ = [
    ('__size', ctypes.c_char * 8),
    ('__align', ctypes.c_int64),
]

pthread_rwlockattr_t = union_pthread_rwlockattr_t
pthread_spinlock_t = ctypes.c_int32
class union_pthread_barrier_t(Union):
    pass

union_pthread_barrier_t._pack_ = 1 # source:False
union_pthread_barrier_t._fields_ = [
    ('__size', ctypes.c_char * 32),
    ('__align', ctypes.c_int64),
    ('PADDING_0', ctypes.c_ubyte * 24),
]

pthread_barrier_t = union_pthread_barrier_t
class union_pthread_barrierattr_t(Union):
    pass

union_pthread_barrierattr_t._pack_ = 1 # source:False
union_pthread_barrierattr_t._fields_ = [
    ('__size', ctypes.c_char * 4),
    ('__align', ctypes.c_int32),
]

pthread_barrierattr_t = union_pthread_barrierattr_t
uint8_t = ctypes.c_uint8
uint16_t = ctypes.c_uint16
uint32_t = ctypes.c_uint32
uint64_t = ctypes.c_uint64
int_least8_t = ctypes.c_byte
int_least16_t = ctypes.c_int16
int_least32_t = ctypes.c_int32
int_least64_t = ctypes.c_int64
uint_least8_t = ctypes.c_ubyte
uint_least16_t = ctypes.c_uint16
uint_least32_t = ctypes.c_uint32
uint_least64_t = ctypes.c_uint64
int_fast8_t = ctypes.c_byte
int_fast16_t = ctypes.c_int64
int_fast32_t = ctypes.c_int64
int_fast64_t = ctypes.c_int64
uint_fast8_t = ctypes.c_ubyte
uint_fast16_t = ctypes.c_uint64
uint_fast32_t = ctypes.c_uint64
uint_fast64_t = ctypes.c_uint64
intptr_t = ctypes.c_int64
uintptr_t = ctypes.c_uint64
intmax_t = ctypes.c_int64
uintmax_t = ctypes.c_uint64
__s8 = ctypes.c_byte
__u8 = ctypes.c_ubyte
__s16 = ctypes.c_int16
__u16 = ctypes.c_uint16
__s32 = ctypes.c_int32
__u32 = ctypes.c_uint32
__s64 = ctypes.c_int64
__u64 = ctypes.c_uint64
class struct___kernel_fd_set(Structure):
    pass

struct___kernel_fd_set._pack_ = 1 # source:False
struct___kernel_fd_set._fields_ = [
    ('fds_bits', ctypes.c_uint64 * 16),
]

__kernel_fd_set = struct___kernel_fd_set
__kernel_sighandler_t = ctypes.CFUNCTYPE(None, ctypes.c_int32)
__kernel_key_t = ctypes.c_int32
__kernel_mqd_t = ctypes.c_int32
__kernel_old_uid_t = ctypes.c_uint16
__kernel_old_gid_t = ctypes.c_uint16
__kernel_old_dev_t = ctypes.c_uint64
__kernel_long_t = ctypes.c_int64
__kernel_ulong_t = ctypes.c_uint64
__kernel_ino_t = ctypes.c_uint64
__kernel_mode_t = ctypes.c_uint32
__kernel_pid_t = ctypes.c_int32
__kernel_ipc_pid_t = ctypes.c_int32
__kernel_uid_t = ctypes.c_uint32
__kernel_gid_t = ctypes.c_uint32
__kernel_suseconds_t = ctypes.c_int64
__kernel_daddr_t = ctypes.c_int32
__kernel_uid32_t = ctypes.c_uint32
__kernel_gid32_t = ctypes.c_uint32
__kernel_size_t = ctypes.c_uint64
__kernel_ssize_t = ctypes.c_int64
__kernel_ptrdiff_t = ctypes.c_int64
class struct___kernel_fsid_t(Structure):
    pass

struct___kernel_fsid_t._pack_ = 1 # source:False
struct___kernel_fsid_t._fields_ = [
    ('val', ctypes.c_int32 * 2),
]

__kernel_fsid_t = struct___kernel_fsid_t
__kernel_off_t = ctypes.c_int64
__kernel_loff_t = ctypes.c_int64
__kernel_old_time_t = ctypes.c_int64
__kernel_time_t = ctypes.c_int64
__kernel_time64_t = ctypes.c_int64
__kernel_clock_t = ctypes.c_int64
__kernel_timer_t = ctypes.c_int32
__kernel_clockid_t = ctypes.c_int32
__kernel_caddr_t = ctypes.POINTER(ctypes.c_char)
__kernel_uid16_t = ctypes.c_uint16
__kernel_gid16_t = ctypes.c_uint16
__s128 = c_int128
__u128 = c_uint128
__le16 = ctypes.c_uint16
__be16 = ctypes.c_uint16
__le32 = ctypes.c_uint32
__be32 = ctypes.c_uint32
__le64 = ctypes.c_uint64
__be64 = ctypes.c_uint64
__sum16 = ctypes.c_uint16
__wsum = ctypes.c_uint32
__poll_t = ctypes.c_uint32
drm_handle_t = ctypes.c_uint32
drm_context_t = ctypes.c_uint32
drm_drawable_t = ctypes.c_uint32
drm_magic_t = ctypes.c_uint32
class struct_drm_clip_rect(Structure):
    pass

struct_drm_clip_rect._pack_ = 1 # source:False
struct_drm_clip_rect._fields_ = [
    ('x1', ctypes.c_uint16),
    ('y1', ctypes.c_uint16),
    ('x2', ctypes.c_uint16),
    ('y2', ctypes.c_uint16),
]

class struct_drm_drawable_info(Structure):
    pass

struct_drm_drawable_info._pack_ = 1 # source:False
struct_drm_drawable_info._fields_ = [
    ('num_rects', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('rects', ctypes.POINTER(struct_drm_clip_rect)),
]

class struct_drm_tex_region(Structure):
    pass

struct_drm_tex_region._pack_ = 1 # source:False
struct_drm_tex_region._fields_ = [
    ('next', ctypes.c_ubyte),
    ('prev', ctypes.c_ubyte),
    ('in_use', ctypes.c_ubyte),
    ('padding', ctypes.c_ubyte),
    ('age', ctypes.c_uint32),
]

class struct_drm_hw_lock(Structure):
    pass

struct_drm_hw_lock._pack_ = 1 # source:False
struct_drm_hw_lock._fields_ = [
    ('lock', ctypes.c_uint32),
    ('padding', ctypes.c_char * 60),
]

class struct_drm_version(Structure):
    pass

struct_drm_version._pack_ = 1 # source:False
struct_drm_version._fields_ = [
    ('version_major', ctypes.c_int32),
    ('version_minor', ctypes.c_int32),
    ('version_patchlevel', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('name_len', ctypes.c_uint64),
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('date_len', ctypes.c_uint64),
    ('date', ctypes.POINTER(ctypes.c_char)),
    ('desc_len', ctypes.c_uint64),
    ('desc', ctypes.POINTER(ctypes.c_char)),
]

class struct_drm_unique(Structure):
    pass

struct_drm_unique._pack_ = 1 # source:False
struct_drm_unique._fields_ = [
    ('unique_len', ctypes.c_uint64),
    ('unique', ctypes.POINTER(ctypes.c_char)),
]

class struct_drm_list(Structure):
    pass

struct_drm_list._pack_ = 1 # source:False
struct_drm_list._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('version', ctypes.POINTER(struct_drm_version)),
]

class struct_drm_block(Structure):
    pass

struct_drm_block._pack_ = 1 # source:False
struct_drm_block._fields_ = [
    ('unused', ctypes.c_int32),
]

class struct_drm_control(Structure):
    pass


# values for unnamed enumeration
__enumvalues = {
    0: 'DRM_ADD_COMMAND',
    1: 'DRM_RM_COMMAND',
    2: 'DRM_INST_HANDLER',
    3: 'DRM_UNINST_HANDLER',
}
DRM_ADD_COMMAND = 0
DRM_RM_COMMAND = 1
DRM_INST_HANDLER = 2
DRM_UNINST_HANDLER = 3
struct_drm_control._pack_ = 1 # source:False
struct_drm_control._fields_ = [
    ('func', ctypes.c_int32),
    ('irq', ctypes.c_int32),
]


# values for enumeration 'drm_map_type'
drm_map_type__enumvalues = {
    0: '_DRM_FRAME_BUFFER',
    1: '_DRM_REGISTERS',
    2: '_DRM_SHM',
    3: '_DRM_AGP',
    4: '_DRM_SCATTER_GATHER',
    5: '_DRM_CONSISTENT',
}
_DRM_FRAME_BUFFER = 0
_DRM_REGISTERS = 1
_DRM_SHM = 2
_DRM_AGP = 3
_DRM_SCATTER_GATHER = 4
_DRM_CONSISTENT = 5
drm_map_type = ctypes.c_uint32 # enum

# values for enumeration 'drm_map_flags'
drm_map_flags__enumvalues = {
    1: '_DRM_RESTRICTED',
    2: '_DRM_READ_ONLY',
    4: '_DRM_LOCKED',
    8: '_DRM_KERNEL',
    16: '_DRM_WRITE_COMBINING',
    32: '_DRM_CONTAINS_LOCK',
    64: '_DRM_REMOVABLE',
    128: '_DRM_DRIVER',
}
_DRM_RESTRICTED = 1
_DRM_READ_ONLY = 2
_DRM_LOCKED = 4
_DRM_KERNEL = 8
_DRM_WRITE_COMBINING = 16
_DRM_CONTAINS_LOCK = 32
_DRM_REMOVABLE = 64
_DRM_DRIVER = 128
drm_map_flags = ctypes.c_uint32 # enum
class struct_drm_ctx_priv_map(Structure):
    pass

struct_drm_ctx_priv_map._pack_ = 1 # source:False
struct_drm_ctx_priv_map._fields_ = [
    ('ctx_id', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('handle', ctypes.POINTER(None)),
]

class struct_drm_map(Structure):
    pass

struct_drm_map._pack_ = 1 # source:False
struct_drm_map._fields_ = [
    ('offset', ctypes.c_uint64),
    ('size', ctypes.c_uint64),
    ('type', drm_map_type),
    ('flags', drm_map_flags),
    ('handle', ctypes.POINTER(None)),
    ('mtrr', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_drm_client(Structure):
    pass

struct_drm_client._pack_ = 1 # source:False
struct_drm_client._fields_ = [
    ('idx', ctypes.c_int32),
    ('auth', ctypes.c_int32),
    ('pid', ctypes.c_uint64),
    ('uid', ctypes.c_uint64),
    ('magic', ctypes.c_uint64),
    ('iocs', ctypes.c_uint64),
]


# values for enumeration 'drm_stat_type'
drm_stat_type__enumvalues = {
    0: '_DRM_STAT_LOCK',
    1: '_DRM_STAT_OPENS',
    2: '_DRM_STAT_CLOSES',
    3: '_DRM_STAT_IOCTLS',
    4: '_DRM_STAT_LOCKS',
    5: '_DRM_STAT_UNLOCKS',
    6: '_DRM_STAT_VALUE',
    7: '_DRM_STAT_BYTE',
    8: '_DRM_STAT_COUNT',
    9: '_DRM_STAT_IRQ',
    10: '_DRM_STAT_PRIMARY',
    11: '_DRM_STAT_SECONDARY',
    12: '_DRM_STAT_DMA',
    13: '_DRM_STAT_SPECIAL',
    14: '_DRM_STAT_MISSED',
}
_DRM_STAT_LOCK = 0
_DRM_STAT_OPENS = 1
_DRM_STAT_CLOSES = 2
_DRM_STAT_IOCTLS = 3
_DRM_STAT_LOCKS = 4
_DRM_STAT_UNLOCKS = 5
_DRM_STAT_VALUE = 6
_DRM_STAT_BYTE = 7
_DRM_STAT_COUNT = 8
_DRM_STAT_IRQ = 9
_DRM_STAT_PRIMARY = 10
_DRM_STAT_SECONDARY = 11
_DRM_STAT_DMA = 12
_DRM_STAT_SPECIAL = 13
_DRM_STAT_MISSED = 14
drm_stat_type = ctypes.c_uint32 # enum
class struct_drm_stats(Structure):
    pass

class struct_drm_stats_0(Structure):
    pass

struct_drm_stats_0._pack_ = 1 # source:False
struct_drm_stats_0._fields_ = [
    ('value', ctypes.c_uint64),
    ('type', drm_stat_type),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

struct_drm_stats._pack_ = 1 # source:False
struct_drm_stats._fields_ = [
    ('count', ctypes.c_uint64),
    ('data', struct_drm_stats_0 * 15),
]


# values for enumeration 'drm_lock_flags'
drm_lock_flags__enumvalues = {
    1: '_DRM_LOCK_READY',
    2: '_DRM_LOCK_QUIESCENT',
    4: '_DRM_LOCK_FLUSH',
    8: '_DRM_LOCK_FLUSH_ALL',
    16: '_DRM_HALT_ALL_QUEUES',
    32: '_DRM_HALT_CUR_QUEUES',
}
_DRM_LOCK_READY = 1
_DRM_LOCK_QUIESCENT = 2
_DRM_LOCK_FLUSH = 4
_DRM_LOCK_FLUSH_ALL = 8
_DRM_HALT_ALL_QUEUES = 16
_DRM_HALT_CUR_QUEUES = 32
drm_lock_flags = ctypes.c_uint32 # enum
class struct_drm_lock(Structure):
    pass

struct_drm_lock._pack_ = 1 # source:False
struct_drm_lock._fields_ = [
    ('context', ctypes.c_int32),
    ('flags', drm_lock_flags),
]


# values for enumeration 'drm_dma_flags'
drm_dma_flags__enumvalues = {
    1: '_DRM_DMA_BLOCK',
    2: '_DRM_DMA_WHILE_LOCKED',
    4: '_DRM_DMA_PRIORITY',
    16: '_DRM_DMA_WAIT',
    32: '_DRM_DMA_SMALLER_OK',
    64: '_DRM_DMA_LARGER_OK',
}
_DRM_DMA_BLOCK = 1
_DRM_DMA_WHILE_LOCKED = 2
_DRM_DMA_PRIORITY = 4
_DRM_DMA_WAIT = 16
_DRM_DMA_SMALLER_OK = 32
_DRM_DMA_LARGER_OK = 64
drm_dma_flags = ctypes.c_uint32 # enum
class struct_drm_buf_desc(Structure):
    pass

struct_drm_buf_desc._pack_ = 1 # source:False
struct_drm_buf_desc._fields_ = [
    ('count', ctypes.c_int32),
    ('size', ctypes.c_int32),
    ('low_mark', ctypes.c_int32),
    ('high_mark', ctypes.c_int32),
    ('flags', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('agp_start', ctypes.c_uint64),
]

class struct_drm_buf_info(Structure):
    pass

struct_drm_buf_info._pack_ = 1 # source:False
struct_drm_buf_info._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('list', ctypes.POINTER(struct_drm_buf_desc)),
]

class struct_drm_buf_free(Structure):
    pass

struct_drm_buf_free._pack_ = 1 # source:False
struct_drm_buf_free._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('list', ctypes.POINTER(ctypes.c_int32)),
]

class struct_drm_buf_pub(Structure):
    pass

struct_drm_buf_pub._pack_ = 1 # source:False
struct_drm_buf_pub._fields_ = [
    ('idx', ctypes.c_int32),
    ('total', ctypes.c_int32),
    ('used', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('address', ctypes.POINTER(None)),
]

class struct_drm_buf_map(Structure):
    pass

struct_drm_buf_map._pack_ = 1 # source:False
struct_drm_buf_map._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('virtual', ctypes.POINTER(None)),
    ('list', ctypes.POINTER(struct_drm_buf_pub)),
]

class struct_drm_dma(Structure):
    pass

struct_drm_dma._pack_ = 1 # source:False
struct_drm_dma._fields_ = [
    ('context', ctypes.c_int32),
    ('send_count', ctypes.c_int32),
    ('send_indices', ctypes.POINTER(ctypes.c_int32)),
    ('send_sizes', ctypes.POINTER(ctypes.c_int32)),
    ('flags', drm_dma_flags),
    ('request_count', ctypes.c_int32),
    ('request_size', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('request_indices', ctypes.POINTER(ctypes.c_int32)),
    ('request_sizes', ctypes.POINTER(ctypes.c_int32)),
    ('granted_count', ctypes.c_int32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]


# values for enumeration 'drm_ctx_flags'
drm_ctx_flags__enumvalues = {
    1: '_DRM_CONTEXT_PRESERVED',
    2: '_DRM_CONTEXT_2DONLY',
}
_DRM_CONTEXT_PRESERVED = 1
_DRM_CONTEXT_2DONLY = 2
drm_ctx_flags = ctypes.c_uint32 # enum
class struct_drm_ctx(Structure):
    pass

struct_drm_ctx._pack_ = 1 # source:False
struct_drm_ctx._fields_ = [
    ('handle', ctypes.c_uint32),
    ('flags', drm_ctx_flags),
]

class struct_drm_ctx_res(Structure):
    pass

struct_drm_ctx_res._pack_ = 1 # source:False
struct_drm_ctx_res._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('contexts', ctypes.POINTER(struct_drm_ctx)),
]

class struct_drm_draw(Structure):
    pass

struct_drm_draw._pack_ = 1 # source:False
struct_drm_draw._fields_ = [
    ('handle', ctypes.c_uint32),
]


# values for enumeration 'drm_drawable_info_type_t'
drm_drawable_info_type_t__enumvalues = {
    0: 'DRM_DRAWABLE_CLIPRECTS',
}
DRM_DRAWABLE_CLIPRECTS = 0
drm_drawable_info_type_t = ctypes.c_uint32 # enum
class struct_drm_update_draw(Structure):
    pass

struct_drm_update_draw._pack_ = 1 # source:False
struct_drm_update_draw._fields_ = [
    ('handle', ctypes.c_uint32),
    ('type', ctypes.c_uint32),
    ('num', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('data', ctypes.c_uint64),
]

class struct_drm_auth(Structure):
    pass

struct_drm_auth._pack_ = 1 # source:False
struct_drm_auth._fields_ = [
    ('magic', ctypes.c_uint32),
]

class struct_drm_irq_busid(Structure):
    pass

struct_drm_irq_busid._pack_ = 1 # source:False
struct_drm_irq_busid._fields_ = [
    ('irq', ctypes.c_int32),
    ('busnum', ctypes.c_int32),
    ('devnum', ctypes.c_int32),
    ('funcnum', ctypes.c_int32),
]


# values for enumeration 'drm_vblank_seq_type'
drm_vblank_seq_type__enumvalues = {
    0: '_DRM_VBLANK_ABSOLUTE',
    1: '_DRM_VBLANK_RELATIVE',
    62: '_DRM_VBLANK_HIGH_CRTC_MASK',
    67108864: '_DRM_VBLANK_EVENT',
    134217728: '_DRM_VBLANK_FLIP',
    268435456: '_DRM_VBLANK_NEXTONMISS',
    536870912: '_DRM_VBLANK_SECONDARY',
    1073741824: '_DRM_VBLANK_SIGNAL',
}
_DRM_VBLANK_ABSOLUTE = 0
_DRM_VBLANK_RELATIVE = 1
_DRM_VBLANK_HIGH_CRTC_MASK = 62
_DRM_VBLANK_EVENT = 67108864
_DRM_VBLANK_FLIP = 134217728
_DRM_VBLANK_NEXTONMISS = 268435456
_DRM_VBLANK_SECONDARY = 536870912
_DRM_VBLANK_SIGNAL = 1073741824
drm_vblank_seq_type = ctypes.c_uint32 # enum
class struct_drm_wait_vblank_request(Structure):
    pass

struct_drm_wait_vblank_request._pack_ = 1 # source:False
struct_drm_wait_vblank_request._fields_ = [
    ('type', drm_vblank_seq_type),
    ('sequence', ctypes.c_uint32),
    ('signal', ctypes.c_uint64),
]

class struct_drm_wait_vblank_reply(Structure):
    pass

struct_drm_wait_vblank_reply._pack_ = 1 # source:False
struct_drm_wait_vblank_reply._fields_ = [
    ('type', drm_vblank_seq_type),
    ('sequence', ctypes.c_uint32),
    ('tval_sec', ctypes.c_int64),
    ('tval_usec', ctypes.c_int64),
]

class union_drm_wait_vblank(Union):
    _pack_ = 1 # source:False
    _fields_ = [
    ('request', struct_drm_wait_vblank_request),
    ('reply', struct_drm_wait_vblank_reply),
     ]

class struct_drm_modeset_ctl(Structure):
    pass

struct_drm_modeset_ctl._pack_ = 1 # source:False
struct_drm_modeset_ctl._fields_ = [
    ('crtc', ctypes.c_uint32),
    ('cmd', ctypes.c_uint32),
]

class struct_drm_agp_mode(Structure):
    pass

struct_drm_agp_mode._pack_ = 1 # source:False
struct_drm_agp_mode._fields_ = [
    ('mode', ctypes.c_uint64),
]

class struct_drm_agp_buffer(Structure):
    pass

struct_drm_agp_buffer._pack_ = 1 # source:False
struct_drm_agp_buffer._fields_ = [
    ('size', ctypes.c_uint64),
    ('handle', ctypes.c_uint64),
    ('type', ctypes.c_uint64),
    ('physical', ctypes.c_uint64),
]

class struct_drm_agp_binding(Structure):
    pass

struct_drm_agp_binding._pack_ = 1 # source:False
struct_drm_agp_binding._fields_ = [
    ('handle', ctypes.c_uint64),
    ('offset', ctypes.c_uint64),
]

class struct_drm_agp_info(Structure):
    pass

struct_drm_agp_info._pack_ = 1 # source:False
struct_drm_agp_info._fields_ = [
    ('agp_version_major', ctypes.c_int32),
    ('agp_version_minor', ctypes.c_int32),
    ('mode', ctypes.c_uint64),
    ('aperture_base', ctypes.c_uint64),
    ('aperture_size', ctypes.c_uint64),
    ('memory_allowed', ctypes.c_uint64),
    ('memory_used', ctypes.c_uint64),
    ('id_vendor', ctypes.c_uint16),
    ('id_device', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_drm_scatter_gather(Structure):
    pass

struct_drm_scatter_gather._pack_ = 1 # source:False
struct_drm_scatter_gather._fields_ = [
    ('size', ctypes.c_uint64),
    ('handle', ctypes.c_uint64),
]

class struct_drm_set_version(Structure):
    pass

struct_drm_set_version._pack_ = 1 # source:False
struct_drm_set_version._fields_ = [
    ('drm_di_major', ctypes.c_int32),
    ('drm_di_minor', ctypes.c_int32),
    ('drm_dd_major', ctypes.c_int32),
    ('drm_dd_minor', ctypes.c_int32),
]

class struct_drm_gem_close(Structure):
    pass

struct_drm_gem_close._pack_ = 1 # source:False
struct_drm_gem_close._fields_ = [
    ('handle', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_gem_flink(Structure):
    pass

struct_drm_gem_flink._pack_ = 1 # source:False
struct_drm_gem_flink._fields_ = [
    ('handle', ctypes.c_uint32),
    ('name', ctypes.c_uint32),
]

class struct_drm_gem_open(Structure):
    pass

struct_drm_gem_open._pack_ = 1 # source:False
struct_drm_gem_open._fields_ = [
    ('name', ctypes.c_uint32),
    ('handle', ctypes.c_uint32),
    ('size', ctypes.c_uint64),
]

class struct_drm_get_cap(Structure):
    pass

struct_drm_get_cap._pack_ = 1 # source:False
struct_drm_get_cap._fields_ = [
    ('capability', ctypes.c_uint64),
    ('value', ctypes.c_uint64),
]

class struct_drm_set_client_cap(Structure):
    pass

struct_drm_set_client_cap._pack_ = 1 # source:False
struct_drm_set_client_cap._fields_ = [
    ('capability', ctypes.c_uint64),
    ('value', ctypes.c_uint64),
]

class struct_drm_prime_handle(Structure):
    pass

struct_drm_prime_handle._pack_ = 1 # source:False
struct_drm_prime_handle._fields_ = [
    ('handle', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('fd', ctypes.c_int32),
]

class struct_drm_syncobj_create(Structure):
    pass

struct_drm_syncobj_create._pack_ = 1 # source:False
struct_drm_syncobj_create._fields_ = [
    ('handle', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

class struct_drm_syncobj_destroy(Structure):
    pass

struct_drm_syncobj_destroy._pack_ = 1 # source:False
struct_drm_syncobj_destroy._fields_ = [
    ('handle', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_syncobj_handle(Structure):
    pass

struct_drm_syncobj_handle._pack_ = 1 # source:False
struct_drm_syncobj_handle._fields_ = [
    ('handle', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('fd', ctypes.c_int32),
    ('pad', ctypes.c_uint32),
    ('point', ctypes.c_uint64),
]

class struct_drm_syncobj_transfer(Structure):
    pass

struct_drm_syncobj_transfer._pack_ = 1 # source:False
struct_drm_syncobj_transfer._fields_ = [
    ('src_handle', ctypes.c_uint32),
    ('dst_handle', ctypes.c_uint32),
    ('src_point', ctypes.c_uint64),
    ('dst_point', ctypes.c_uint64),
    ('flags', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_syncobj_wait(Structure):
    pass

struct_drm_syncobj_wait._pack_ = 1 # source:False
struct_drm_syncobj_wait._fields_ = [
    ('handles', ctypes.c_uint64),
    ('timeout_nsec', ctypes.c_int64),
    ('count_handles', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('first_signaled', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
    ('deadline_nsec', ctypes.c_uint64),
]

class struct_drm_syncobj_timeline_wait(Structure):
    pass

struct_drm_syncobj_timeline_wait._pack_ = 1 # source:False
struct_drm_syncobj_timeline_wait._fields_ = [
    ('handles', ctypes.c_uint64),
    ('points', ctypes.c_uint64),
    ('timeout_nsec', ctypes.c_int64),
    ('count_handles', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('first_signaled', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
    ('deadline_nsec', ctypes.c_uint64),
]

class struct_drm_syncobj_eventfd(Structure):
    pass

struct_drm_syncobj_eventfd._pack_ = 1 # source:False
struct_drm_syncobj_eventfd._fields_ = [
    ('handle', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('point', ctypes.c_uint64),
    ('fd', ctypes.c_int32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_syncobj_array(Structure):
    pass

struct_drm_syncobj_array._pack_ = 1 # source:False
struct_drm_syncobj_array._fields_ = [
    ('handles', ctypes.c_uint64),
    ('count_handles', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_syncobj_timeline_array(Structure):
    pass

struct_drm_syncobj_timeline_array._pack_ = 1 # source:False
struct_drm_syncobj_timeline_array._fields_ = [
    ('handles', ctypes.c_uint64),
    ('points', ctypes.c_uint64),
    ('count_handles', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
]

class struct_drm_crtc_get_sequence(Structure):
    pass

struct_drm_crtc_get_sequence._pack_ = 1 # source:False
struct_drm_crtc_get_sequence._fields_ = [
    ('crtc_id', ctypes.c_uint32),
    ('active', ctypes.c_uint32),
    ('sequence', ctypes.c_uint64),
    ('sequence_ns', ctypes.c_int64),
]

class struct_drm_crtc_queue_sequence(Structure):
    pass

struct_drm_crtc_queue_sequence._pack_ = 1 # source:False
struct_drm_crtc_queue_sequence._fields_ = [
    ('crtc_id', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('sequence', ctypes.c_uint64),
    ('user_data', ctypes.c_uint64),
]

class struct_drm_set_client_name(Structure):
    pass

struct_drm_set_client_name._pack_ = 1 # source:False
struct_drm_set_client_name._fields_ = [
    ('name_len', ctypes.c_uint64),
    ('name', ctypes.c_uint64),
]

class struct_drm_mode_modeinfo(Structure):
    pass

struct_drm_mode_modeinfo._pack_ = 1 # source:False
struct_drm_mode_modeinfo._fields_ = [
    ('clock', ctypes.c_uint32),
    ('hdisplay', ctypes.c_uint16),
    ('hsync_start', ctypes.c_uint16),
    ('hsync_end', ctypes.c_uint16),
    ('htotal', ctypes.c_uint16),
    ('hskew', ctypes.c_uint16),
    ('vdisplay', ctypes.c_uint16),
    ('vsync_start', ctypes.c_uint16),
    ('vsync_end', ctypes.c_uint16),
    ('vtotal', ctypes.c_uint16),
    ('vscan', ctypes.c_uint16),
    ('vrefresh', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('type', ctypes.c_uint32),
    ('name', ctypes.c_char * 32),
]

class struct_drm_mode_card_res(Structure):
    pass

struct_drm_mode_card_res._pack_ = 1 # source:False
struct_drm_mode_card_res._fields_ = [
    ('fb_id_ptr', ctypes.c_uint64),
    ('crtc_id_ptr', ctypes.c_uint64),
    ('connector_id_ptr', ctypes.c_uint64),
    ('encoder_id_ptr', ctypes.c_uint64),
    ('count_fbs', ctypes.c_uint32),
    ('count_crtcs', ctypes.c_uint32),
    ('count_connectors', ctypes.c_uint32),
    ('count_encoders', ctypes.c_uint32),
    ('min_width', ctypes.c_uint32),
    ('max_width', ctypes.c_uint32),
    ('min_height', ctypes.c_uint32),
    ('max_height', ctypes.c_uint32),
]

class struct_drm_mode_crtc(Structure):
    pass

struct_drm_mode_crtc._pack_ = 1 # source:False
struct_drm_mode_crtc._fields_ = [
    ('set_connectors_ptr', ctypes.c_uint64),
    ('count_connectors', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
    ('fb_id', ctypes.c_uint32),
    ('x', ctypes.c_uint32),
    ('y', ctypes.c_uint32),
    ('gamma_size', ctypes.c_uint32),
    ('mode_valid', ctypes.c_uint32),
    ('mode', struct_drm_mode_modeinfo),
]

class struct_drm_mode_set_plane(Structure):
    pass

struct_drm_mode_set_plane._pack_ = 1 # source:False
struct_drm_mode_set_plane._fields_ = [
    ('plane_id', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
    ('fb_id', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('crtc_x', ctypes.c_int32),
    ('crtc_y', ctypes.c_int32),
    ('crtc_w', ctypes.c_uint32),
    ('crtc_h', ctypes.c_uint32),
    ('src_x', ctypes.c_uint32),
    ('src_y', ctypes.c_uint32),
    ('src_h', ctypes.c_uint32),
    ('src_w', ctypes.c_uint32),
]

class struct_drm_mode_get_plane(Structure):
    pass

struct_drm_mode_get_plane._pack_ = 1 # source:False
struct_drm_mode_get_plane._fields_ = [
    ('plane_id', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
    ('fb_id', ctypes.c_uint32),
    ('possible_crtcs', ctypes.c_uint32),
    ('gamma_size', ctypes.c_uint32),
    ('count_format_types', ctypes.c_uint32),
    ('format_type_ptr', ctypes.c_uint64),
]

class struct_drm_mode_get_plane_res(Structure):
    pass

struct_drm_mode_get_plane_res._pack_ = 1 # source:False
struct_drm_mode_get_plane_res._fields_ = [
    ('plane_id_ptr', ctypes.c_uint64),
    ('count_planes', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_drm_mode_get_encoder(Structure):
    pass

struct_drm_mode_get_encoder._pack_ = 1 # source:False
struct_drm_mode_get_encoder._fields_ = [
    ('encoder_id', ctypes.c_uint32),
    ('encoder_type', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
    ('possible_crtcs', ctypes.c_uint32),
    ('possible_clones', ctypes.c_uint32),
]


# values for enumeration 'drm_mode_subconnector'
drm_mode_subconnector__enumvalues = {
    0: 'DRM_MODE_SUBCONNECTOR_Automatic',
    0: 'DRM_MODE_SUBCONNECTOR_Unknown',
    1: 'DRM_MODE_SUBCONNECTOR_VGA',
    3: 'DRM_MODE_SUBCONNECTOR_DVID',
    4: 'DRM_MODE_SUBCONNECTOR_DVIA',
    5: 'DRM_MODE_SUBCONNECTOR_Composite',
    6: 'DRM_MODE_SUBCONNECTOR_SVIDEO',
    8: 'DRM_MODE_SUBCONNECTOR_Component',
    9: 'DRM_MODE_SUBCONNECTOR_SCART',
    10: 'DRM_MODE_SUBCONNECTOR_DisplayPort',
    11: 'DRM_MODE_SUBCONNECTOR_HDMIA',
    15: 'DRM_MODE_SUBCONNECTOR_Native',
    18: 'DRM_MODE_SUBCONNECTOR_Wireless',
}
DRM_MODE_SUBCONNECTOR_Automatic = 0
DRM_MODE_SUBCONNECTOR_Unknown = 0
DRM_MODE_SUBCONNECTOR_VGA = 1
DRM_MODE_SUBCONNECTOR_DVID = 3
DRM_MODE_SUBCONNECTOR_DVIA = 4
DRM_MODE_SUBCONNECTOR_Composite = 5
DRM_MODE_SUBCONNECTOR_SVIDEO = 6
DRM_MODE_SUBCONNECTOR_Component = 8
DRM_MODE_SUBCONNECTOR_SCART = 9
DRM_MODE_SUBCONNECTOR_DisplayPort = 10
DRM_MODE_SUBCONNECTOR_HDMIA = 11
DRM_MODE_SUBCONNECTOR_Native = 15
DRM_MODE_SUBCONNECTOR_Wireless = 18
drm_mode_subconnector = ctypes.c_uint32 # enum
class struct_drm_mode_get_connector(Structure):
    pass

struct_drm_mode_get_connector._pack_ = 1 # source:False
struct_drm_mode_get_connector._fields_ = [
    ('encoders_ptr', ctypes.c_uint64),
    ('modes_ptr', ctypes.c_uint64),
    ('props_ptr', ctypes.c_uint64),
    ('prop_values_ptr', ctypes.c_uint64),
    ('count_modes', ctypes.c_uint32),
    ('count_props', ctypes.c_uint32),
    ('count_encoders', ctypes.c_uint32),
    ('encoder_id', ctypes.c_uint32),
    ('connector_id', ctypes.c_uint32),
    ('connector_type', ctypes.c_uint32),
    ('connector_type_id', ctypes.c_uint32),
    ('connection', ctypes.c_uint32),
    ('mm_width', ctypes.c_uint32),
    ('mm_height', ctypes.c_uint32),
    ('subpixel', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_mode_property_enum(Structure):
    pass

struct_drm_mode_property_enum._pack_ = 1 # source:False
struct_drm_mode_property_enum._fields_ = [
    ('value', ctypes.c_uint64),
    ('name', ctypes.c_char * 32),
]

class struct_drm_mode_get_property(Structure):
    pass

struct_drm_mode_get_property._pack_ = 1 # source:False
struct_drm_mode_get_property._fields_ = [
    ('values_ptr', ctypes.c_uint64),
    ('enum_blob_ptr', ctypes.c_uint64),
    ('prop_id', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('name', ctypes.c_char * 32),
    ('count_values', ctypes.c_uint32),
    ('count_enum_blobs', ctypes.c_uint32),
]

class struct_drm_mode_connector_set_property(Structure):
    pass

struct_drm_mode_connector_set_property._pack_ = 1 # source:False
struct_drm_mode_connector_set_property._fields_ = [
    ('value', ctypes.c_uint64),
    ('prop_id', ctypes.c_uint32),
    ('connector_id', ctypes.c_uint32),
]

class struct_drm_mode_obj_get_properties(Structure):
    pass

struct_drm_mode_obj_get_properties._pack_ = 1 # source:False
struct_drm_mode_obj_get_properties._fields_ = [
    ('props_ptr', ctypes.c_uint64),
    ('prop_values_ptr', ctypes.c_uint64),
    ('count_props', ctypes.c_uint32),
    ('obj_id', ctypes.c_uint32),
    ('obj_type', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_drm_mode_obj_set_property(Structure):
    pass

struct_drm_mode_obj_set_property._pack_ = 1 # source:False
struct_drm_mode_obj_set_property._fields_ = [
    ('value', ctypes.c_uint64),
    ('prop_id', ctypes.c_uint32),
    ('obj_id', ctypes.c_uint32),
    ('obj_type', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

class struct_drm_mode_get_blob(Structure):
    pass

struct_drm_mode_get_blob._pack_ = 1 # source:False
struct_drm_mode_get_blob._fields_ = [
    ('blob_id', ctypes.c_uint32),
    ('length', ctypes.c_uint32),
    ('data', ctypes.c_uint64),
]

class struct_drm_mode_fb_cmd(Structure):
    pass

struct_drm_mode_fb_cmd._pack_ = 1 # source:False
struct_drm_mode_fb_cmd._fields_ = [
    ('fb_id', ctypes.c_uint32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('pitch', ctypes.c_uint32),
    ('bpp', ctypes.c_uint32),
    ('depth', ctypes.c_uint32),
    ('handle', ctypes.c_uint32),
]

class struct_drm_mode_fb_cmd2(Structure):
    pass

struct_drm_mode_fb_cmd2._pack_ = 1 # source:False
struct_drm_mode_fb_cmd2._fields_ = [
    ('fb_id', ctypes.c_uint32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('pixel_format', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('handles', ctypes.c_uint32 * 4),
    ('pitches', ctypes.c_uint32 * 4),
    ('offsets', ctypes.c_uint32 * 4),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('modifier', ctypes.c_uint64 * 4),
]

class struct_drm_mode_fb_dirty_cmd(Structure):
    pass

struct_drm_mode_fb_dirty_cmd._pack_ = 1 # source:False
struct_drm_mode_fb_dirty_cmd._fields_ = [
    ('fb_id', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('color', ctypes.c_uint32),
    ('num_clips', ctypes.c_uint32),
    ('clips_ptr', ctypes.c_uint64),
]

class struct_drm_mode_mode_cmd(Structure):
    pass

struct_drm_mode_mode_cmd._pack_ = 1 # source:False
struct_drm_mode_mode_cmd._fields_ = [
    ('connector_id', ctypes.c_uint32),
    ('mode', struct_drm_mode_modeinfo),
]

class struct_drm_mode_cursor(Structure):
    pass

struct_drm_mode_cursor._pack_ = 1 # source:False
struct_drm_mode_cursor._fields_ = [
    ('flags', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
    ('x', ctypes.c_int32),
    ('y', ctypes.c_int32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('handle', ctypes.c_uint32),
]

class struct_drm_mode_cursor2(Structure):
    pass

struct_drm_mode_cursor2._pack_ = 1 # source:False
struct_drm_mode_cursor2._fields_ = [
    ('flags', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
    ('x', ctypes.c_int32),
    ('y', ctypes.c_int32),
    ('width', ctypes.c_uint32),
    ('height', ctypes.c_uint32),
    ('handle', ctypes.c_uint32),
    ('hot_x', ctypes.c_int32),
    ('hot_y', ctypes.c_int32),
]

class struct_drm_mode_crtc_lut(Structure):
    pass

struct_drm_mode_crtc_lut._pack_ = 1 # source:False
struct_drm_mode_crtc_lut._fields_ = [
    ('crtc_id', ctypes.c_uint32),
    ('gamma_size', ctypes.c_uint32),
    ('red', ctypes.c_uint64),
    ('green', ctypes.c_uint64),
    ('blue', ctypes.c_uint64),
]

class struct_drm_color_ctm(Structure):
    pass

struct_drm_color_ctm._pack_ = 1 # source:False
struct_drm_color_ctm._fields_ = [
    ('matrix', ctypes.c_uint64 * 9),
]

class struct_drm_color_lut(Structure):
    pass

struct_drm_color_lut._pack_ = 1 # source:False
struct_drm_color_lut._fields_ = [
    ('red', ctypes.c_uint16),
    ('green', ctypes.c_uint16),
    ('blue', ctypes.c_uint16),
    ('reserved', ctypes.c_uint16),
]

class struct_drm_plane_size_hint(Structure):
    pass

struct_drm_plane_size_hint._pack_ = 1 # source:False
struct_drm_plane_size_hint._fields_ = [
    ('width', ctypes.c_uint16),
    ('height', ctypes.c_uint16),
]

class struct_hdr_metadata_infoframe(Structure):
    pass

class struct_hdr_metadata_infoframe_0(Structure):
    pass

struct_hdr_metadata_infoframe_0._pack_ = 1 # source:False
struct_hdr_metadata_infoframe_0._fields_ = [
    ('x', ctypes.c_uint16),
    ('y', ctypes.c_uint16),
]

class struct_hdr_metadata_infoframe_white_point(Structure):
    pass

struct_hdr_metadata_infoframe_white_point._pack_ = 1 # source:False
struct_hdr_metadata_infoframe_white_point._fields_ = [
    ('x', ctypes.c_uint16),
    ('y', ctypes.c_uint16),
]

struct_hdr_metadata_infoframe._pack_ = 1 # source:False
struct_hdr_metadata_infoframe._fields_ = [
    ('eotf', ctypes.c_ubyte),
    ('metadata_type', ctypes.c_ubyte),
    ('display_primaries', struct_hdr_metadata_infoframe_0 * 3),
    ('white_point', struct_hdr_metadata_infoframe_white_point),
    ('max_display_mastering_luminance', ctypes.c_uint16),
    ('min_display_mastering_luminance', ctypes.c_uint16),
    ('max_cll', ctypes.c_uint16),
    ('max_fall', ctypes.c_uint16),
]

class struct_hdr_output_metadata(Structure):
    pass

class union_hdr_output_metadata_0(Union):
    _pack_ = 1 # source:False
    _fields_ = [
    ('hdmi_metadata_type1', struct_hdr_metadata_infoframe),
     ]

struct_hdr_output_metadata._pack_ = 1 # source:False
struct_hdr_output_metadata._anonymous_ = ('_0',)
struct_hdr_output_metadata._fields_ = [
    ('metadata_type', ctypes.c_uint32),
    ('_0', union_hdr_output_metadata_0),
    ('PADDING_0', ctypes.c_ubyte * 2),
]

class struct_drm_mode_crtc_page_flip(Structure):
    pass

struct_drm_mode_crtc_page_flip._pack_ = 1 # source:False
struct_drm_mode_crtc_page_flip._fields_ = [
    ('crtc_id', ctypes.c_uint32),
    ('fb_id', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32),
    ('user_data', ctypes.c_uint64),
]

class struct_drm_mode_crtc_page_flip_target(Structure):
    pass

struct_drm_mode_crtc_page_flip_target._pack_ = 1 # source:False
struct_drm_mode_crtc_page_flip_target._fields_ = [
    ('crtc_id', ctypes.c_uint32),
    ('fb_id', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('sequence', ctypes.c_uint32),
    ('user_data', ctypes.c_uint64),
]

class struct_drm_mode_create_dumb(Structure):
    pass

struct_drm_mode_create_dumb._pack_ = 1 # source:False
struct_drm_mode_create_dumb._fields_ = [
    ('height', ctypes.c_uint32),
    ('width', ctypes.c_uint32),
    ('bpp', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('handle', ctypes.c_uint32),
    ('pitch', ctypes.c_uint32),
    ('size', ctypes.c_uint64),
]

class struct_drm_mode_map_dumb(Structure):
    pass

struct_drm_mode_map_dumb._pack_ = 1 # source:False
struct_drm_mode_map_dumb._fields_ = [
    ('handle', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
    ('offset', ctypes.c_uint64),
]

class struct_drm_mode_destroy_dumb(Structure):
    pass

struct_drm_mode_destroy_dumb._pack_ = 1 # source:False
struct_drm_mode_destroy_dumb._fields_ = [
    ('handle', ctypes.c_uint32),
]

class struct_drm_mode_atomic(Structure):
    pass

struct_drm_mode_atomic._pack_ = 1 # source:False
struct_drm_mode_atomic._fields_ = [
    ('flags', ctypes.c_uint32),
    ('count_objs', ctypes.c_uint32),
    ('objs_ptr', ctypes.c_uint64),
    ('count_props_ptr', ctypes.c_uint64),
    ('props_ptr', ctypes.c_uint64),
    ('prop_values_ptr', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64),
    ('user_data', ctypes.c_uint64),
]

class struct_drm_format_modifier_blob(Structure):
    pass

struct_drm_format_modifier_blob._pack_ = 1 # source:False
struct_drm_format_modifier_blob._fields_ = [
    ('version', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('count_formats', ctypes.c_uint32),
    ('formats_offset', ctypes.c_uint32),
    ('count_modifiers', ctypes.c_uint32),
    ('modifiers_offset', ctypes.c_uint32),
]

class struct_drm_format_modifier(Structure):
    pass

struct_drm_format_modifier._pack_ = 1 # source:False
struct_drm_format_modifier._fields_ = [
    ('formats', ctypes.c_uint64),
    ('offset', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
    ('modifier', ctypes.c_uint64),
]

class struct_drm_mode_create_blob(Structure):
    pass

struct_drm_mode_create_blob._pack_ = 1 # source:False
struct_drm_mode_create_blob._fields_ = [
    ('data', ctypes.c_uint64),
    ('length', ctypes.c_uint32),
    ('blob_id', ctypes.c_uint32),
]

class struct_drm_mode_destroy_blob(Structure):
    pass

struct_drm_mode_destroy_blob._pack_ = 1 # source:False
struct_drm_mode_destroy_blob._fields_ = [
    ('blob_id', ctypes.c_uint32),
]

class struct_drm_mode_create_lease(Structure):
    pass

struct_drm_mode_create_lease._pack_ = 1 # source:False
struct_drm_mode_create_lease._fields_ = [
    ('object_ids', ctypes.c_uint64),
    ('object_count', ctypes.c_uint32),
    ('flags', ctypes.c_uint32),
    ('lessee_id', ctypes.c_uint32),
    ('fd', ctypes.c_uint32),
]

class struct_drm_mode_list_lessees(Structure):
    pass

struct_drm_mode_list_lessees._pack_ = 1 # source:False
struct_drm_mode_list_lessees._fields_ = [
    ('count_lessees', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
    ('lessees_ptr', ctypes.c_uint64),
]

class struct_drm_mode_get_lease(Structure):
    pass

struct_drm_mode_get_lease._pack_ = 1 # source:False
struct_drm_mode_get_lease._fields_ = [
    ('count_objects', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
    ('objects_ptr', ctypes.c_uint64),
]

class struct_drm_mode_revoke_lease(Structure):
    pass

struct_drm_mode_revoke_lease._pack_ = 1 # source:False
struct_drm_mode_revoke_lease._fields_ = [
    ('lessee_id', ctypes.c_uint32),
]

class struct_drm_mode_rect(Structure):
    pass

struct_drm_mode_rect._pack_ = 1 # source:False
struct_drm_mode_rect._fields_ = [
    ('x1', ctypes.c_int32),
    ('y1', ctypes.c_int32),
    ('x2', ctypes.c_int32),
    ('y2', ctypes.c_int32),
]

class struct_drm_mode_closefb(Structure):
    pass

struct_drm_mode_closefb._pack_ = 1 # source:False
struct_drm_mode_closefb._fields_ = [
    ('fb_id', ctypes.c_uint32),
    ('pad', ctypes.c_uint32),
]

class struct_drm_event(Structure):
    pass

struct_drm_event._pack_ = 1 # source:False
struct_drm_event._fields_ = [
    ('type', ctypes.c_uint32),
    ('length', ctypes.c_uint32),
]

class struct_drm_event_vblank(Structure):
    pass

struct_drm_event_vblank._pack_ = 1 # source:False
struct_drm_event_vblank._fields_ = [
    ('base', struct_drm_event),
    ('user_data', ctypes.c_uint64),
    ('tv_sec', ctypes.c_uint32),
    ('tv_usec', ctypes.c_uint32),
    ('sequence', ctypes.c_uint32),
    ('crtc_id', ctypes.c_uint32),
]

class struct_drm_event_crtc_sequence(Structure):
    pass

struct_drm_event_crtc_sequence._pack_ = 1 # source:False
struct_drm_event_crtc_sequence._fields_ = [
    ('base', struct_drm_event),
    ('user_data', ctypes.c_uint64),
    ('time_ns', ctypes.c_int64),
    ('sequence', ctypes.c_uint64),
]

drm_clip_rect_t = struct_drm_clip_rect
drm_drawable_info_t = struct_drm_drawable_info
drm_tex_region_t = struct_drm_tex_region
drm_hw_lock_t = struct_drm_hw_lock
drm_version_t = struct_drm_version
drm_unique_t = struct_drm_unique
drm_list_t = struct_drm_list
drm_block_t = struct_drm_block
drm_control_t = struct_drm_control
drm_map_type_t = drm_map_type
drm_map_type_t__enumvalues = drm_map_type__enumvalues
drm_map_flags_t = drm_map_flags
drm_map_flags_t__enumvalues = drm_map_flags__enumvalues
drm_ctx_priv_map_t = struct_drm_ctx_priv_map
drm_map_t = struct_drm_map
drm_client_t = struct_drm_client
drm_stat_type_t = drm_stat_type
drm_stat_type_t__enumvalues = drm_stat_type__enumvalues
drm_stats_t = struct_drm_stats
drm_lock_flags_t = drm_lock_flags
drm_lock_flags_t__enumvalues = drm_lock_flags__enumvalues
drm_lock_t = struct_drm_lock
drm_dma_flags_t = drm_dma_flags
drm_dma_flags_t__enumvalues = drm_dma_flags__enumvalues
drm_buf_desc_t = struct_drm_buf_desc
drm_buf_info_t = struct_drm_buf_info
drm_buf_free_t = struct_drm_buf_free
drm_buf_pub_t = struct_drm_buf_pub
drm_buf_map_t = struct_drm_buf_map
drm_dma_t = struct_drm_dma
drm_wait_vblank_t = union_drm_wait_vblank
drm_agp_mode_t = struct_drm_agp_mode
drm_ctx_flags_t = drm_ctx_flags
drm_ctx_flags_t__enumvalues = drm_ctx_flags__enumvalues
drm_ctx_t = struct_drm_ctx
drm_ctx_res_t = struct_drm_ctx_res
drm_draw_t = struct_drm_draw
drm_update_draw_t = struct_drm_update_draw
drm_auth_t = struct_drm_auth
drm_irq_busid_t = struct_drm_irq_busid
drm_vblank_seq_type_t = drm_vblank_seq_type
drm_vblank_seq_type_t__enumvalues = drm_vblank_seq_type__enumvalues
drm_agp_buffer_t = struct_drm_agp_buffer
drm_agp_binding_t = struct_drm_agp_binding
drm_agp_info_t = struct_drm_agp_info
drm_scatter_gather_t = struct_drm_scatter_gather
drm_set_version_t = struct_drm_set_version
drmSize = ctypes.c_uint32
drmSizePtr = ctypes.POINTER(ctypes.c_uint32)
drmAddress = ctypes.POINTER(None)
drmAddressPtr = ctypes.POINTER(ctypes.POINTER(None))
class struct__drmServerInfo(Structure):
    pass

struct__drmServerInfo._pack_ = 1 # source:False
struct__drmServerInfo._fields_ = [
    ('debug_print', ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.POINTER(ctypes.c_char), ctypes.POINTER(struct___va_list_tag))),
    ('load_module', ctypes.CFUNCTYPE(ctypes.c_int32, ctypes.POINTER(ctypes.c_char))),
    ('get_perms', ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32))),
]

drmServerInfo = struct__drmServerInfo
drmServerInfoPtr = ctypes.POINTER(struct__drmServerInfo)
class struct_drmHashEntry(Structure):
    pass

struct_drmHashEntry._pack_ = 1 # source:False
struct_drmHashEntry._fields_ = [
    ('fd', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('f', ctypes.CFUNCTYPE(None, ctypes.c_int32, ctypes.POINTER(None), ctypes.POINTER(None))),
    ('tagTable', ctypes.POINTER(None)),
]

drmHashEntry = struct_drmHashEntry
try:
    drmIoctl = _libraries['libdrm.so.2'].drmIoctl
    drmIoctl.restype = ctypes.c_int32
    drmIoctl.argtypes = [ctypes.c_int32, ctypes.c_uint64, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmGetHashTable = _libraries['libdrm.so.2'].drmGetHashTable
    drmGetHashTable.restype = ctypes.POINTER(None)
    drmGetHashTable.argtypes = []
except AttributeError:
    pass
try:
    drmGetEntry = _libraries['libdrm.so.2'].drmGetEntry
    drmGetEntry.restype = ctypes.POINTER(struct_drmHashEntry)
    drmGetEntry.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
class struct__drmVersion(Structure):
    pass

struct__drmVersion._pack_ = 1 # source:False
struct__drmVersion._fields_ = [
    ('version_major', ctypes.c_int32),
    ('version_minor', ctypes.c_int32),
    ('version_patchlevel', ctypes.c_int32),
    ('name_len', ctypes.c_int32),
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('date_len', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('date', ctypes.POINTER(ctypes.c_char)),
    ('desc_len', ctypes.c_int32),
    ('PADDING_1', ctypes.c_ubyte * 4),
    ('desc', ctypes.POINTER(ctypes.c_char)),
]

drmVersion = struct__drmVersion
drmVersionPtr = ctypes.POINTER(struct__drmVersion)
class struct__drmStats(Structure):
    pass

class struct__drmStats_0(Structure):
    pass

struct__drmStats_0._pack_ = 1 # source:False
struct__drmStats_0._fields_ = [
    ('value', ctypes.c_uint64),
    ('long_format', ctypes.POINTER(ctypes.c_char)),
    ('long_name', ctypes.POINTER(ctypes.c_char)),
    ('rate_format', ctypes.POINTER(ctypes.c_char)),
    ('rate_name', ctypes.POINTER(ctypes.c_char)),
    ('isvalue', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('mult_names', ctypes.POINTER(ctypes.c_char)),
    ('mult', ctypes.c_int32),
    ('verbose', ctypes.c_int32),
]

struct__drmStats._pack_ = 1 # source:False
struct__drmStats._fields_ = [
    ('count', ctypes.c_uint64),
    ('data', struct__drmStats_0 * 15),
]

drmStatsT = struct__drmStats

# values for enumeration 'drmMapType'
drmMapType__enumvalues = {
    0: 'DRM_FRAME_BUFFER',
    1: 'DRM_REGISTERS',
    2: 'DRM_SHM',
    3: 'DRM_AGP',
    4: 'DRM_SCATTER_GATHER',
    5: 'DRM_CONSISTENT',
}
DRM_FRAME_BUFFER = 0
DRM_REGISTERS = 1
DRM_SHM = 2
DRM_AGP = 3
DRM_SCATTER_GATHER = 4
DRM_CONSISTENT = 5
drmMapType = ctypes.c_uint32 # enum

# values for enumeration 'drmMapFlags'
drmMapFlags__enumvalues = {
    1: 'DRM_RESTRICTED',
    2: 'DRM_READ_ONLY',
    4: 'DRM_LOCKED',
    8: 'DRM_KERNEL',
    16: 'DRM_WRITE_COMBINING',
    32: 'DRM_CONTAINS_LOCK',
    64: 'DRM_REMOVABLE',
}
DRM_RESTRICTED = 1
DRM_READ_ONLY = 2
DRM_LOCKED = 4
DRM_KERNEL = 8
DRM_WRITE_COMBINING = 16
DRM_CONTAINS_LOCK = 32
DRM_REMOVABLE = 64
drmMapFlags = ctypes.c_uint32 # enum

# values for enumeration 'drmDMAFlags'
drmDMAFlags__enumvalues = {
    1: 'DRM_DMA_BLOCK',
    2: 'DRM_DMA_WHILE_LOCKED',
    4: 'DRM_DMA_PRIORITY',
    16: 'DRM_DMA_WAIT',
    32: 'DRM_DMA_SMALLER_OK',
    64: 'DRM_DMA_LARGER_OK',
}
DRM_DMA_BLOCK = 1
DRM_DMA_WHILE_LOCKED = 2
DRM_DMA_PRIORITY = 4
DRM_DMA_WAIT = 16
DRM_DMA_SMALLER_OK = 32
DRM_DMA_LARGER_OK = 64
drmDMAFlags = ctypes.c_uint32 # enum

# values for enumeration 'drmBufDescFlags'
drmBufDescFlags__enumvalues = {
    1: 'DRM_PAGE_ALIGN',
    2: 'DRM_AGP_BUFFER',
    4: 'DRM_SG_BUFFER',
    8: 'DRM_FB_BUFFER',
    16: 'DRM_PCI_BUFFER_RO',
}
DRM_PAGE_ALIGN = 1
DRM_AGP_BUFFER = 2
DRM_SG_BUFFER = 4
DRM_FB_BUFFER = 8
DRM_PCI_BUFFER_RO = 16
drmBufDescFlags = ctypes.c_uint32 # enum

# values for enumeration 'drmLockFlags'
drmLockFlags__enumvalues = {
    1: 'DRM_LOCK_READY',
    2: 'DRM_LOCK_QUIESCENT',
    4: 'DRM_LOCK_FLUSH',
    8: 'DRM_LOCK_FLUSH_ALL',
    16: 'DRM_HALT_ALL_QUEUES',
    32: 'DRM_HALT_CUR_QUEUES',
}
DRM_LOCK_READY = 1
DRM_LOCK_QUIESCENT = 2
DRM_LOCK_FLUSH = 4
DRM_LOCK_FLUSH_ALL = 8
DRM_HALT_ALL_QUEUES = 16
DRM_HALT_CUR_QUEUES = 32
drmLockFlags = ctypes.c_uint32 # enum

# values for enumeration 'drm_context_tFlags'
drm_context_tFlags__enumvalues = {
    1: 'DRM_CONTEXT_PRESERVED',
    2: 'DRM_CONTEXT_2DONLY',
}
DRM_CONTEXT_PRESERVED = 1
DRM_CONTEXT_2DONLY = 2
drm_context_tFlags = ctypes.c_uint32 # enum
drm_context_tFlagsPtr = ctypes.POINTER(drm_context_tFlags)
class struct__drmBufDesc(Structure):
    pass

struct__drmBufDesc._pack_ = 1 # source:False
struct__drmBufDesc._fields_ = [
    ('count', ctypes.c_int32),
    ('size', ctypes.c_int32),
    ('low_mark', ctypes.c_int32),
    ('high_mark', ctypes.c_int32),
]

drmBufDesc = struct__drmBufDesc
drmBufDescPtr = ctypes.POINTER(struct__drmBufDesc)
class struct__drmBufInfo(Structure):
    pass

struct__drmBufInfo._pack_ = 1 # source:False
struct__drmBufInfo._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('list', ctypes.POINTER(struct__drmBufDesc)),
]

drmBufInfo = struct__drmBufInfo
drmBufInfoPtr = ctypes.POINTER(struct__drmBufInfo)
class struct__drmBuf(Structure):
    pass

struct__drmBuf._pack_ = 1 # source:False
struct__drmBuf._fields_ = [
    ('idx', ctypes.c_int32),
    ('total', ctypes.c_int32),
    ('used', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('address', ctypes.POINTER(None)),
]

drmBuf = struct__drmBuf
drmBufPtr = ctypes.POINTER(struct__drmBuf)
class struct__drmBufMap(Structure):
    pass

struct__drmBufMap._pack_ = 1 # source:False
struct__drmBufMap._fields_ = [
    ('count', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('list', ctypes.POINTER(struct__drmBuf)),
]

drmBufMap = struct__drmBufMap
drmBufMapPtr = ctypes.POINTER(struct__drmBufMap)
class struct__drmLock(Structure):
    pass

struct__drmLock._pack_ = 1 # source:False
struct__drmLock._fields_ = [
    ('lock', ctypes.c_uint32),
    ('padding', ctypes.c_char * 60),
]

drmLock = struct__drmLock
drmLockPtr = ctypes.POINTER(struct__drmLock)
class struct__drmDMAReq(Structure):
    pass

struct__drmDMAReq._pack_ = 1 # source:False
struct__drmDMAReq._fields_ = [
    ('context', ctypes.c_uint32),
    ('send_count', ctypes.c_int32),
    ('send_list', ctypes.POINTER(ctypes.c_int32)),
    ('send_sizes', ctypes.POINTER(ctypes.c_int32)),
    ('flags', drmDMAFlags),
    ('request_count', ctypes.c_int32),
    ('request_size', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('request_list', ctypes.POINTER(ctypes.c_int32)),
    ('request_sizes', ctypes.POINTER(ctypes.c_int32)),
    ('granted_count', ctypes.c_int32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

drmDMAReq = struct__drmDMAReq
drmDMAReqPtr = ctypes.POINTER(struct__drmDMAReq)
class struct__drmRegion(Structure):
    pass

struct__drmRegion._pack_ = 1 # source:False
struct__drmRegion._fields_ = [
    ('handle', ctypes.c_uint32),
    ('offset', ctypes.c_uint32),
    ('size', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('map', ctypes.POINTER(None)),
]

drmRegion = struct__drmRegion
drmRegionPtr = ctypes.POINTER(struct__drmRegion)
class struct__drmTextureRegion(Structure):
    pass

struct__drmTextureRegion._pack_ = 1 # source:False
struct__drmTextureRegion._fields_ = [
    ('next', ctypes.c_ubyte),
    ('prev', ctypes.c_ubyte),
    ('in_use', ctypes.c_ubyte),
    ('padding', ctypes.c_ubyte),
    ('age', ctypes.c_uint32),
]

drmTextureRegion = struct__drmTextureRegion
drmTextureRegionPtr = ctypes.POINTER(struct__drmTextureRegion)

# values for enumeration 'drmVBlankSeqType'
drmVBlankSeqType__enumvalues = {
    0: 'DRM_VBLANK_ABSOLUTE',
    1: 'DRM_VBLANK_RELATIVE',
    62: 'DRM_VBLANK_HIGH_CRTC_MASK',
    67108864: 'DRM_VBLANK_EVENT',
    134217728: 'DRM_VBLANK_FLIP',
    268435456: 'DRM_VBLANK_NEXTONMISS',
    536870912: 'DRM_VBLANK_SECONDARY',
    1073741824: 'DRM_VBLANK_SIGNAL',
}
DRM_VBLANK_ABSOLUTE = 0
DRM_VBLANK_RELATIVE = 1
DRM_VBLANK_HIGH_CRTC_MASK = 62
DRM_VBLANK_EVENT = 67108864
DRM_VBLANK_FLIP = 134217728
DRM_VBLANK_NEXTONMISS = 268435456
DRM_VBLANK_SECONDARY = 536870912
DRM_VBLANK_SIGNAL = 1073741824
drmVBlankSeqType = ctypes.c_uint32 # enum
class struct__drmVBlankReq(Structure):
    pass

struct__drmVBlankReq._pack_ = 1 # source:False
struct__drmVBlankReq._fields_ = [
    ('type', drmVBlankSeqType),
    ('sequence', ctypes.c_uint32),
    ('signal', ctypes.c_uint64),
]

drmVBlankReq = struct__drmVBlankReq
drmVBlankReqPtr = ctypes.POINTER(struct__drmVBlankReq)
class struct__drmVBlankReply(Structure):
    pass

struct__drmVBlankReply._pack_ = 1 # source:False
struct__drmVBlankReply._fields_ = [
    ('type', drmVBlankSeqType),
    ('sequence', ctypes.c_uint32),
    ('tval_sec', ctypes.c_int64),
    ('tval_usec', ctypes.c_int64),
]

drmVBlankReply = struct__drmVBlankReply
drmVBlankReplyPtr = ctypes.POINTER(struct__drmVBlankReply)
class union__drmVBlank(Union):
    _pack_ = 1 # source:False
    _fields_ = [
    ('request', drmVBlankReq),
    ('reply', drmVBlankReply),
     ]

drmVBlank = union__drmVBlank
drmVBlankPtr = ctypes.POINTER(union__drmVBlank)
class struct__drmSetVersion(Structure):
    pass

struct__drmSetVersion._pack_ = 1 # source:False
struct__drmSetVersion._fields_ = [
    ('drm_di_major', ctypes.c_int32),
    ('drm_di_minor', ctypes.c_int32),
    ('drm_dd_major', ctypes.c_int32),
    ('drm_dd_minor', ctypes.c_int32),
]

drmSetVersion = struct__drmSetVersion
drmSetVersionPtr = ctypes.POINTER(struct__drmSetVersion)
try:
    drmAvailable = _libraries['libdrm.so.2'].drmAvailable
    drmAvailable.restype = ctypes.c_int32
    drmAvailable.argtypes = []
except AttributeError:
    pass
try:
    drmOpen = _libraries['libdrm.so.2'].drmOpen
    drmOpen.restype = ctypes.c_int32
    drmOpen.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    drmOpenWithType = _libraries['libdrm.so.2'].drmOpenWithType
    drmOpenWithType.restype = ctypes.c_int32
    drmOpenWithType.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char), ctypes.c_int32]
except AttributeError:
    pass
try:
    drmOpenControl = _libraries['libdrm.so.2'].drmOpenControl
    drmOpenControl.restype = ctypes.c_int32
    drmOpenControl.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmOpenRender = _libraries['libdrm.so.2'].drmOpenRender
    drmOpenRender.restype = ctypes.c_int32
    drmOpenRender.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmClose = _libraries['libdrm.so.2'].drmClose
    drmClose.restype = ctypes.c_int32
    drmClose.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetVersion = _libraries['libdrm.so.2'].drmGetVersion
    drmGetVersion.restype = drmVersionPtr
    drmGetVersion.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetLibVersion = _libraries['libdrm.so.2'].drmGetLibVersion
    drmGetLibVersion.restype = drmVersionPtr
    drmGetLibVersion.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetCap = _libraries['libdrm.so.2'].drmGetCap
    drmGetCap.restype = ctypes.c_int32
    drmGetCap.argtypes = [ctypes.c_int32, uint64_t, ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    drmFreeVersion = _libraries['libdrm.so.2'].drmFreeVersion
    drmFreeVersion.restype = None
    drmFreeVersion.argtypes = [drmVersionPtr]
except AttributeError:
    pass
try:
    drmGetMagic = _libraries['libdrm.so.2'].drmGetMagic
    drmGetMagic.restype = ctypes.c_int32
    drmGetMagic.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmGetBusid = _libraries['libdrm.so.2'].drmGetBusid
    drmGetBusid.restype = ctypes.POINTER(ctypes.c_char)
    drmGetBusid.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetInterruptFromBusID = _libraries['libdrm.so.2'].drmGetInterruptFromBusID
    drmGetInterruptFromBusID.restype = ctypes.c_int32
    drmGetInterruptFromBusID.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetMap = _libraries['libdrm.so.2'].drmGetMap
    drmGetMap.restype = ctypes.c_int32
    drmGetMap.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(drmMapType), ctypes.POINTER(drmMapFlags), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmGetClient = _libraries['libdrm.so.2'].drmGetClient
    drmGetClient.restype = ctypes.c_int32
    drmGetClient.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    drmGetStats = _libraries['libdrm.so.2'].drmGetStats
    drmGetStats.restype = ctypes.c_int32
    drmGetStats.argtypes = [ctypes.c_int32, ctypes.POINTER(struct__drmStats)]
except AttributeError:
    pass
try:
    drmSetInterfaceVersion = _libraries['libdrm.so.2'].drmSetInterfaceVersion
    drmSetInterfaceVersion.restype = ctypes.c_int32
    drmSetInterfaceVersion.argtypes = [ctypes.c_int32, ctypes.POINTER(struct__drmSetVersion)]
except AttributeError:
    pass
try:
    drmCommandNone = _libraries['libdrm.so.2'].drmCommandNone
    drmCommandNone.restype = ctypes.c_int32
    drmCommandNone.argtypes = [ctypes.c_int32, ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmCommandRead = _libraries['libdrm.so.2'].drmCommandRead
    drmCommandRead.restype = ctypes.c_int32
    drmCommandRead.argtypes = [ctypes.c_int32, ctypes.c_uint64, ctypes.POINTER(None), ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmCommandWrite = _libraries['libdrm.so.2'].drmCommandWrite
    drmCommandWrite.restype = ctypes.c_int32
    drmCommandWrite.argtypes = [ctypes.c_int32, ctypes.c_uint64, ctypes.POINTER(None), ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmCommandWriteRead = _libraries['libdrm.so.2'].drmCommandWriteRead
    drmCommandWriteRead.restype = ctypes.c_int32
    drmCommandWriteRead.argtypes = [ctypes.c_int32, ctypes.c_uint64, ctypes.POINTER(None), ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmFreeBusid = _libraries['libdrm.so.2'].drmFreeBusid
    drmFreeBusid.restype = None
    drmFreeBusid.argtypes = [ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    drmSetBusid = _libraries['libdrm.so.2'].drmSetBusid
    drmSetBusid.restype = ctypes.c_int32
    drmSetBusid.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    drmAuthMagic = _libraries['libdrm.so.2'].drmAuthMagic
    drmAuthMagic.restype = ctypes.c_int32
    drmAuthMagic.argtypes = [ctypes.c_int32, drm_magic_t]
except AttributeError:
    pass
try:
    drmAddMap = _libraries['libdrm.so.2'].drmAddMap
    drmAddMap.restype = ctypes.c_int32
    drmAddMap.argtypes = [ctypes.c_int32, drm_handle_t, drmSize, drmMapType, drmMapFlags, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmRmMap = _libraries['libdrm.so.2'].drmRmMap
    drmRmMap.restype = ctypes.c_int32
    drmRmMap.argtypes = [ctypes.c_int32, drm_handle_t]
except AttributeError:
    pass
try:
    drmAddContextPrivateMapping = _libraries['libdrm.so.2'].drmAddContextPrivateMapping
    drmAddContextPrivateMapping.restype = ctypes.c_int32
    drmAddContextPrivateMapping.argtypes = [ctypes.c_int32, drm_context_t, drm_handle_t]
except AttributeError:
    pass
try:
    drmAddBufs = _libraries['libdrm.so.2'].drmAddBufs
    drmAddBufs.restype = ctypes.c_int32
    drmAddBufs.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, drmBufDescFlags, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmMarkBufs = _libraries['libdrm.so.2'].drmMarkBufs
    drmMarkBufs.restype = ctypes.c_int32
    drmMarkBufs.argtypes = [ctypes.c_int32, ctypes.c_double, ctypes.c_double]
except AttributeError:
    pass
try:
    drmCreateContext = _libraries['libdrm.so.2'].drmCreateContext
    drmCreateContext.restype = ctypes.c_int32
    drmCreateContext.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmSetContextFlags = _libraries['libdrm.so.2'].drmSetContextFlags
    drmSetContextFlags.restype = ctypes.c_int32
    drmSetContextFlags.argtypes = [ctypes.c_int32, drm_context_t, drm_context_tFlags]
except AttributeError:
    pass
try:
    drmGetContextFlags = _libraries['libdrm.so.2'].drmGetContextFlags
    drmGetContextFlags.restype = ctypes.c_int32
    drmGetContextFlags.argtypes = [ctypes.c_int32, drm_context_t, drm_context_tFlagsPtr]
except AttributeError:
    pass
try:
    drmAddContextTag = _libraries['libdrm.so.2'].drmAddContextTag
    drmAddContextTag.restype = ctypes.c_int32
    drmAddContextTag.argtypes = [ctypes.c_int32, drm_context_t, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmDelContextTag = _libraries['libdrm.so.2'].drmDelContextTag
    drmDelContextTag.restype = ctypes.c_int32
    drmDelContextTag.argtypes = [ctypes.c_int32, drm_context_t]
except AttributeError:
    pass
try:
    drmGetContextTag = _libraries['libdrm.so.2'].drmGetContextTag
    drmGetContextTag.restype = ctypes.POINTER(None)
    drmGetContextTag.argtypes = [ctypes.c_int32, drm_context_t]
except AttributeError:
    pass
try:
    drmGetReservedContextList = _libraries['libdrm.so.2'].drmGetReservedContextList
    drmGetReservedContextList.restype = ctypes.POINTER(ctypes.c_uint32)
    drmGetReservedContextList.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmFreeReservedContextList = _libraries['libdrm.so.2'].drmFreeReservedContextList
    drmFreeReservedContextList.restype = None
    drmFreeReservedContextList.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmSwitchToContext = _libraries['libdrm.so.2'].drmSwitchToContext
    drmSwitchToContext.restype = ctypes.c_int32
    drmSwitchToContext.argtypes = [ctypes.c_int32, drm_context_t]
except AttributeError:
    pass
try:
    drmDestroyContext = _libraries['libdrm.so.2'].drmDestroyContext
    drmDestroyContext.restype = ctypes.c_int32
    drmDestroyContext.argtypes = [ctypes.c_int32, drm_context_t]
except AttributeError:
    pass
try:
    drmCreateDrawable = _libraries['libdrm.so.2'].drmCreateDrawable
    drmCreateDrawable.restype = ctypes.c_int32
    drmCreateDrawable.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmDestroyDrawable = _libraries['libdrm.so.2'].drmDestroyDrawable
    drmDestroyDrawable.restype = ctypes.c_int32
    drmDestroyDrawable.argtypes = [ctypes.c_int32, drm_drawable_t]
except AttributeError:
    pass
try:
    drmUpdateDrawableInfo = _libraries['libdrm.so.2'].drmUpdateDrawableInfo
    drmUpdateDrawableInfo.restype = ctypes.c_int32
    drmUpdateDrawableInfo.argtypes = [ctypes.c_int32, drm_drawable_t, drm_drawable_info_type_t, ctypes.c_uint32, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmCtlInstHandler = _libraries['libdrm.so.2'].drmCtlInstHandler
    drmCtlInstHandler.restype = ctypes.c_int32
    drmCtlInstHandler.argtypes = [ctypes.c_int32, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmCtlUninstHandler = _libraries['libdrm.so.2'].drmCtlUninstHandler
    drmCtlUninstHandler.restype = ctypes.c_int32
    drmCtlUninstHandler.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmSetClientCap = _libraries['libdrm.so.2'].drmSetClientCap
    drmSetClientCap.restype = ctypes.c_int32
    drmSetClientCap.argtypes = [ctypes.c_int32, uint64_t, uint64_t]
except AttributeError:
    pass
try:
    drmCrtcGetSequence = _libraries['libdrm.so.2'].drmCrtcGetSequence
    drmCrtcGetSequence.restype = ctypes.c_int32
    drmCrtcGetSequence.argtypes = [ctypes.c_int32, uint32_t, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
except AttributeError:
    pass
try:
    drmCrtcQueueSequence = _libraries['libdrm.so.2'].drmCrtcQueueSequence
    drmCrtcQueueSequence.restype = ctypes.c_int32
    drmCrtcQueueSequence.argtypes = [ctypes.c_int32, uint32_t, uint32_t, uint64_t, ctypes.POINTER(ctypes.c_uint64), uint64_t]
except AttributeError:
    pass
try:
    drmMap = _libraries['libdrm.so.2'].drmMap
    drmMap.restype = ctypes.c_int32
    drmMap.argtypes = [ctypes.c_int32, drm_handle_t, drmSize, drmAddressPtr]
except AttributeError:
    pass
try:
    drmUnmap = _libraries['libdrm.so.2'].drmUnmap
    drmUnmap.restype = ctypes.c_int32
    drmUnmap.argtypes = [drmAddress, drmSize]
except AttributeError:
    pass
try:
    drmGetBufInfo = _libraries['libdrm.so.2'].drmGetBufInfo
    drmGetBufInfo.restype = drmBufInfoPtr
    drmGetBufInfo.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmMapBufs = _libraries['libdrm.so.2'].drmMapBufs
    drmMapBufs.restype = drmBufMapPtr
    drmMapBufs.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmUnmapBufs = _libraries['libdrm.so.2'].drmUnmapBufs
    drmUnmapBufs.restype = ctypes.c_int32
    drmUnmapBufs.argtypes = [drmBufMapPtr]
except AttributeError:
    pass
try:
    drmDMA = _libraries['libdrm.so.2'].drmDMA
    drmDMA.restype = ctypes.c_int32
    drmDMA.argtypes = [ctypes.c_int32, drmDMAReqPtr]
except AttributeError:
    pass
try:
    drmFreeBufs = _libraries['libdrm.so.2'].drmFreeBufs
    drmFreeBufs.restype = ctypes.c_int32
    drmFreeBufs.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmGetLock = _libraries['libdrm.so.2'].drmGetLock
    drmGetLock.restype = ctypes.c_int32
    drmGetLock.argtypes = [ctypes.c_int32, drm_context_t, drmLockFlags]
except AttributeError:
    pass
try:
    drmUnlock = _libraries['libdrm.so.2'].drmUnlock
    drmUnlock.restype = ctypes.c_int32
    drmUnlock.argtypes = [ctypes.c_int32, drm_context_t]
except AttributeError:
    pass
try:
    drmFinish = _libraries['libdrm.so.2'].drmFinish
    drmFinish.restype = ctypes.c_int32
    drmFinish.argtypes = [ctypes.c_int32, ctypes.c_int32, drmLockFlags]
except AttributeError:
    pass
try:
    drmGetContextPrivateMapping = _libraries['libdrm.so.2'].drmGetContextPrivateMapping
    drmGetContextPrivateMapping.restype = ctypes.c_int32
    drmGetContextPrivateMapping.argtypes = [ctypes.c_int32, drm_context_t, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmAgpAcquire = _libraries['libdrm.so.2'].drmAgpAcquire
    drmAgpAcquire.restype = ctypes.c_int32
    drmAgpAcquire.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpRelease = _libraries['libdrm.so.2'].drmAgpRelease
    drmAgpRelease.restype = ctypes.c_int32
    drmAgpRelease.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpEnable = _libraries['libdrm.so.2'].drmAgpEnable
    drmAgpEnable.restype = ctypes.c_int32
    drmAgpEnable.argtypes = [ctypes.c_int32, ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmAgpAlloc = _libraries['libdrm.so.2'].drmAgpAlloc
    drmAgpAlloc.restype = ctypes.c_int32
    drmAgpAlloc.argtypes = [ctypes.c_int32, ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmAgpFree = _libraries['libdrm.so.2'].drmAgpFree
    drmAgpFree.restype = ctypes.c_int32
    drmAgpFree.argtypes = [ctypes.c_int32, drm_handle_t]
except AttributeError:
    pass
try:
    drmAgpBind = _libraries['libdrm.so.2'].drmAgpBind
    drmAgpBind.restype = ctypes.c_int32
    drmAgpBind.argtypes = [ctypes.c_int32, drm_handle_t, ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmAgpUnbind = _libraries['libdrm.so.2'].drmAgpUnbind
    drmAgpUnbind.restype = ctypes.c_int32
    drmAgpUnbind.argtypes = [ctypes.c_int32, drm_handle_t]
except AttributeError:
    pass
try:
    drmAgpVersionMajor = _libraries['libdrm.so.2'].drmAgpVersionMajor
    drmAgpVersionMajor.restype = ctypes.c_int32
    drmAgpVersionMajor.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpVersionMinor = _libraries['libdrm.so.2'].drmAgpVersionMinor
    drmAgpVersionMinor.restype = ctypes.c_int32
    drmAgpVersionMinor.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpGetMode = _libraries['libdrm.so.2'].drmAgpGetMode
    drmAgpGetMode.restype = ctypes.c_uint64
    drmAgpGetMode.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpBase = _libraries['libdrm.so.2'].drmAgpBase
    drmAgpBase.restype = ctypes.c_uint64
    drmAgpBase.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpSize = _libraries['libdrm.so.2'].drmAgpSize
    drmAgpSize.restype = ctypes.c_uint64
    drmAgpSize.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpMemoryUsed = _libraries['libdrm.so.2'].drmAgpMemoryUsed
    drmAgpMemoryUsed.restype = ctypes.c_uint64
    drmAgpMemoryUsed.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpMemoryAvail = _libraries['libdrm.so.2'].drmAgpMemoryAvail
    drmAgpMemoryAvail.restype = ctypes.c_uint64
    drmAgpMemoryAvail.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpVendorId = _libraries['libdrm.so.2'].drmAgpVendorId
    drmAgpVendorId.restype = ctypes.c_uint32
    drmAgpVendorId.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmAgpDeviceId = _libraries['libdrm.so.2'].drmAgpDeviceId
    drmAgpDeviceId.restype = ctypes.c_uint32
    drmAgpDeviceId.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmScatterGatherAlloc = _libraries['libdrm.so.2'].drmScatterGatherAlloc
    drmScatterGatherAlloc.restype = ctypes.c_int32
    drmScatterGatherAlloc.argtypes = [ctypes.c_int32, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmScatterGatherFree = _libraries['libdrm.so.2'].drmScatterGatherFree
    drmScatterGatherFree.restype = ctypes.c_int32
    drmScatterGatherFree.argtypes = [ctypes.c_int32, drm_handle_t]
except AttributeError:
    pass
try:
    drmWaitVBlank = _libraries['libdrm.so.2'].drmWaitVBlank
    drmWaitVBlank.restype = ctypes.c_int32
    drmWaitVBlank.argtypes = [ctypes.c_int32, drmVBlankPtr]
except AttributeError:
    pass
try:
    drmSetServerInfo = _libraries['libdrm.so.2'].drmSetServerInfo
    drmSetServerInfo.restype = None
    drmSetServerInfo.argtypes = [drmServerInfoPtr]
except AttributeError:
    pass
try:
    drmError = _libraries['libdrm.so.2'].drmError
    drmError.restype = ctypes.c_int32
    drmError.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    drmMalloc = _libraries['libdrm.so.2'].drmMalloc
    drmMalloc.restype = ctypes.POINTER(None)
    drmMalloc.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmFree = _libraries['libdrm.so.2'].drmFree
    drmFree.restype = None
    drmFree.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmHashCreate = _libraries['libdrm.so.2'].drmHashCreate
    drmHashCreate.restype = ctypes.POINTER(None)
    drmHashCreate.argtypes = []
except AttributeError:
    pass
try:
    drmHashDestroy = _libraries['libdrm.so.2'].drmHashDestroy
    drmHashDestroy.restype = ctypes.c_int32
    drmHashDestroy.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmHashLookup = _libraries['libdrm.so.2'].drmHashLookup
    drmHashLookup.restype = ctypes.c_int32
    drmHashLookup.argtypes = [ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmHashInsert = _libraries['libdrm.so.2'].drmHashInsert
    drmHashInsert.restype = ctypes.c_int32
    drmHashInsert.argtypes = [ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmHashDelete = _libraries['libdrm.so.2'].drmHashDelete
    drmHashDelete.restype = ctypes.c_int32
    drmHashDelete.argtypes = [ctypes.POINTER(None), ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmHashFirst = _libraries['libdrm.so.2'].drmHashFirst
    drmHashFirst.restype = ctypes.c_int32
    drmHashFirst.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmHashNext = _libraries['libdrm.so.2'].drmHashNext
    drmHashNext.restype = ctypes.c_int32
    drmHashNext.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmRandomCreate = _libraries['libdrm.so.2'].drmRandomCreate
    drmRandomCreate.restype = ctypes.POINTER(None)
    drmRandomCreate.argtypes = [ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmRandomDestroy = _libraries['libdrm.so.2'].drmRandomDestroy
    drmRandomDestroy.restype = ctypes.c_int32
    drmRandomDestroy.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmRandom = _libraries['libdrm.so.2'].drmRandom
    drmRandom.restype = ctypes.c_uint64
    drmRandom.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmRandomDouble = _libraries['libdrm.so.2'].drmRandomDouble
    drmRandomDouble.restype = ctypes.c_double
    drmRandomDouble.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmSLCreate = _libraries['libdrm.so.2'].drmSLCreate
    drmSLCreate.restype = ctypes.POINTER(None)
    drmSLCreate.argtypes = []
except AttributeError:
    pass
try:
    drmSLDestroy = _libraries['libdrm.so.2'].drmSLDestroy
    drmSLDestroy.restype = ctypes.c_int32
    drmSLDestroy.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmSLLookup = _libraries['libdrm.so.2'].drmSLLookup
    drmSLLookup.restype = ctypes.c_int32
    drmSLLookup.argtypes = [ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmSLInsert = _libraries['libdrm.so.2'].drmSLInsert
    drmSLInsert.restype = ctypes.c_int32
    drmSLInsert.argtypes = [ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmSLDelete = _libraries['libdrm.so.2'].drmSLDelete
    drmSLDelete.restype = ctypes.c_int32
    drmSLDelete.argtypes = [ctypes.POINTER(None), ctypes.c_uint64]
except AttributeError:
    pass
try:
    drmSLNext = _libraries['libdrm.so.2'].drmSLNext
    drmSLNext.restype = ctypes.c_int32
    drmSLNext.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmSLFirst = _libraries['libdrm.so.2'].drmSLFirst
    drmSLFirst.restype = ctypes.c_int32
    drmSLFirst.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmSLDump = _libraries['libdrm.so.2'].drmSLDump
    drmSLDump.restype = None
    drmSLDump.argtypes = [ctypes.POINTER(None)]
except AttributeError:
    pass
try:
    drmSLLookupNeighbors = _libraries['libdrm.so.2'].drmSLLookupNeighbors
    drmSLLookupNeighbors.restype = ctypes.c_int32
    drmSLLookupNeighbors.argtypes = [ctypes.POINTER(None), ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None)), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.POINTER(None))]
except AttributeError:
    pass
try:
    drmOpenOnce = _libraries['libdrm.so.2'].drmOpenOnce
    drmOpenOnce.restype = ctypes.c_int32
    drmOpenOnce.argtypes = [ctypes.POINTER(None), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmOpenOnceWithType = _libraries['libdrm.so.2'].drmOpenOnceWithType
    drmOpenOnceWithType.restype = ctypes.c_int32
    drmOpenOnceWithType.argtypes = [ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]
except AttributeError:
    pass
try:
    drmCloseOnce = _libraries['libdrm.so.2'].drmCloseOnce
    drmCloseOnce.restype = None
    drmCloseOnce.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmMsg = _libraries['libdrm.so.2'].drmMsg
    drmMsg.restype = None
    drmMsg.argtypes = [ctypes.POINTER(ctypes.c_char)]
except AttributeError:
    pass
try:
    drmSetMaster = _libraries['libdrm.so.2'].drmSetMaster
    drmSetMaster.restype = ctypes.c_int32
    drmSetMaster.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmDropMaster = _libraries['libdrm.so.2'].drmDropMaster
    drmDropMaster.restype = ctypes.c_int32
    drmDropMaster.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmIsMaster = _libraries['libdrm.so.2'].drmIsMaster
    drmIsMaster.restype = ctypes.c_int32
    drmIsMaster.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
class struct__drmEventContext(Structure):
    pass

struct__drmEventContext._pack_ = 1 # source:False
struct__drmEventContext._fields_ = [
    ('version', ctypes.c_int32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('vblank_handler', ctypes.CFUNCTYPE(None, ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(None))),
    ('page_flip_handler', ctypes.CFUNCTYPE(None, ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(None))),
    ('page_flip_handler2', ctypes.CFUNCTYPE(None, ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(None))),
    ('sequence_handler', ctypes.CFUNCTYPE(None, ctypes.c_int32, ctypes.c_uint64, ctypes.c_uint64, ctypes.c_uint64)),
]

drmEventContext = struct__drmEventContext
drmEventContextPtr = ctypes.POINTER(struct__drmEventContext)
try:
    drmHandleEvent = _libraries['libdrm.so.2'].drmHandleEvent
    drmHandleEvent.restype = ctypes.c_int32
    drmHandleEvent.argtypes = [ctypes.c_int32, drmEventContextPtr]
except AttributeError:
    pass
try:
    drmGetDeviceNameFromFd = _libraries['libdrm.so.2'].drmGetDeviceNameFromFd
    drmGetDeviceNameFromFd.restype = ctypes.POINTER(ctypes.c_char)
    drmGetDeviceNameFromFd.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetDeviceNameFromFd2 = _libraries['libdrm.so.2'].drmGetDeviceNameFromFd2
    drmGetDeviceNameFromFd2.restype = ctypes.POINTER(ctypes.c_char)
    drmGetDeviceNameFromFd2.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetNodeTypeFromFd = _libraries['libdrm.so.2'].drmGetNodeTypeFromFd
    drmGetNodeTypeFromFd.restype = ctypes.c_int32
    drmGetNodeTypeFromFd.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmPrimeHandleToFD = _libraries['libdrm.so.2'].drmPrimeHandleToFD
    drmPrimeHandleToFD.restype = ctypes.c_int32
    drmPrimeHandleToFD.argtypes = [ctypes.c_int32, uint32_t, uint32_t, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmPrimeFDToHandle = _libraries['libdrm.so.2'].drmPrimeFDToHandle
    drmPrimeFDToHandle.restype = ctypes.c_int32
    drmPrimeFDToHandle.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmCloseBufferHandle = _libraries['libdrm.so.2'].drmCloseBufferHandle
    drmCloseBufferHandle.restype = ctypes.c_int32
    drmCloseBufferHandle.argtypes = [ctypes.c_int32, uint32_t]
except AttributeError:
    pass
try:
    drmGetPrimaryDeviceNameFromFd = _libraries['libdrm.so.2'].drmGetPrimaryDeviceNameFromFd
    drmGetPrimaryDeviceNameFromFd.restype = ctypes.POINTER(ctypes.c_char)
    drmGetPrimaryDeviceNameFromFd.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetRenderDeviceNameFromFd = _libraries['libdrm.so.2'].drmGetRenderDeviceNameFromFd
    drmGetRenderDeviceNameFromFd.restype = ctypes.POINTER(ctypes.c_char)
    drmGetRenderDeviceNameFromFd.argtypes = [ctypes.c_int32]
except AttributeError:
    pass
class struct__drmPciBusInfo(Structure):
    pass

struct__drmPciBusInfo._pack_ = 1 # source:False
struct__drmPciBusInfo._fields_ = [
    ('domain', ctypes.c_uint16),
    ('bus', ctypes.c_ubyte),
    ('dev', ctypes.c_ubyte),
    ('func', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte),
]

drmPciBusInfo = struct__drmPciBusInfo
drmPciBusInfoPtr = ctypes.POINTER(struct__drmPciBusInfo)
class struct__drmPciDeviceInfo(Structure):
    pass

struct__drmPciDeviceInfo._pack_ = 1 # source:False
struct__drmPciDeviceInfo._fields_ = [
    ('vendor_id', ctypes.c_uint16),
    ('device_id', ctypes.c_uint16),
    ('subvendor_id', ctypes.c_uint16),
    ('subdevice_id', ctypes.c_uint16),
    ('revision_id', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte),
]

drmPciDeviceInfo = struct__drmPciDeviceInfo
drmPciDeviceInfoPtr = ctypes.POINTER(struct__drmPciDeviceInfo)
class struct__drmUsbBusInfo(Structure):
    pass

struct__drmUsbBusInfo._pack_ = 1 # source:False
struct__drmUsbBusInfo._fields_ = [
    ('bus', ctypes.c_ubyte),
    ('dev', ctypes.c_ubyte),
]

drmUsbBusInfo = struct__drmUsbBusInfo
drmUsbBusInfoPtr = ctypes.POINTER(struct__drmUsbBusInfo)
class struct__drmUsbDeviceInfo(Structure):
    pass

struct__drmUsbDeviceInfo._pack_ = 1 # source:False
struct__drmUsbDeviceInfo._fields_ = [
    ('vendor', ctypes.c_uint16),
    ('product', ctypes.c_uint16),
]

drmUsbDeviceInfo = struct__drmUsbDeviceInfo
drmUsbDeviceInfoPtr = ctypes.POINTER(struct__drmUsbDeviceInfo)
class struct__drmPlatformBusInfo(Structure):
    pass

struct__drmPlatformBusInfo._pack_ = 1 # source:False
struct__drmPlatformBusInfo._fields_ = [
    ('fullname', ctypes.c_char * 512),
]

drmPlatformBusInfo = struct__drmPlatformBusInfo
drmPlatformBusInfoPtr = ctypes.POINTER(struct__drmPlatformBusInfo)
class struct__drmPlatformDeviceInfo(Structure):
    pass

struct__drmPlatformDeviceInfo._pack_ = 1 # source:False
struct__drmPlatformDeviceInfo._fields_ = [
    ('compatible', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
]

drmPlatformDeviceInfo = struct__drmPlatformDeviceInfo
drmPlatformDeviceInfoPtr = ctypes.POINTER(struct__drmPlatformDeviceInfo)
class struct__drmHost1xBusInfo(Structure):
    pass

struct__drmHost1xBusInfo._pack_ = 1 # source:False
struct__drmHost1xBusInfo._fields_ = [
    ('fullname', ctypes.c_char * 512),
]

drmHost1xBusInfo = struct__drmHost1xBusInfo
drmHost1xBusInfoPtr = ctypes.POINTER(struct__drmHost1xBusInfo)
class struct__drmHost1xDeviceInfo(Structure):
    pass

struct__drmHost1xDeviceInfo._pack_ = 1 # source:False
struct__drmHost1xDeviceInfo._fields_ = [
    ('compatible', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
]

drmHost1xDeviceInfo = struct__drmHost1xDeviceInfo
drmHost1xDeviceInfoPtr = ctypes.POINTER(struct__drmHost1xDeviceInfo)
class struct__drmDevice(Structure):
    pass

class union__drmDevice_businfo(Union):
    pass

union__drmDevice_businfo._pack_ = 1 # source:False
union__drmDevice_businfo._fields_ = [
    ('pci', ctypes.POINTER(struct__drmPciBusInfo)),
    ('usb', ctypes.POINTER(struct__drmUsbBusInfo)),
    ('platform', ctypes.POINTER(struct__drmPlatformBusInfo)),
    ('host1x', ctypes.POINTER(struct__drmHost1xBusInfo)),
]

class union__drmDevice_deviceinfo(Union):
    pass

union__drmDevice_deviceinfo._pack_ = 1 # source:False
union__drmDevice_deviceinfo._fields_ = [
    ('pci', ctypes.POINTER(struct__drmPciDeviceInfo)),
    ('usb', ctypes.POINTER(struct__drmUsbDeviceInfo)),
    ('platform', ctypes.POINTER(struct__drmPlatformDeviceInfo)),
    ('host1x', ctypes.POINTER(struct__drmHost1xDeviceInfo)),
]

struct__drmDevice._pack_ = 1 # source:False
struct__drmDevice._fields_ = [
    ('nodes', ctypes.POINTER(ctypes.POINTER(ctypes.c_char))),
    ('available_nodes', ctypes.c_int32),
    ('bustype', ctypes.c_int32),
    ('businfo', union__drmDevice_businfo),
    ('deviceinfo', union__drmDevice_deviceinfo),
]

drmDevice = struct__drmDevice
drmDevicePtr = ctypes.POINTER(struct__drmDevice)
try:
    drmGetDevice = _libraries['libdrm.so.2'].drmGetDevice
    drmGetDevice.restype = ctypes.c_int32
    drmGetDevice.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.POINTER(struct__drmDevice))]
except AttributeError:
    pass
try:
    drmFreeDevice = _libraries['libdrm.so.2'].drmFreeDevice
    drmFreeDevice.restype = None
    drmFreeDevice.argtypes = [ctypes.POINTER(ctypes.POINTER(struct__drmDevice))]
except AttributeError:
    pass
try:
    drmGetDevices = _libraries['libdrm.so.2'].drmGetDevices
    drmGetDevices.restype = ctypes.c_int32
    drmGetDevices.argtypes = [ctypes.POINTER(struct__drmDevice) * 0, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmFreeDevices = _libraries['libdrm.so.2'].drmFreeDevices
    drmFreeDevices.restype = None
    drmFreeDevices.argtypes = [ctypes.POINTER(struct__drmDevice) * 0, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetDevice2 = _libraries['libdrm.so.2'].drmGetDevice2
    drmGetDevice2.restype = ctypes.c_int32
    drmGetDevice2.argtypes = [ctypes.c_int32, uint32_t, ctypes.POINTER(ctypes.POINTER(struct__drmDevice))]
except AttributeError:
    pass
try:
    drmGetDevices2 = _libraries['libdrm.so.2'].drmGetDevices2
    drmGetDevices2.restype = ctypes.c_int32
    drmGetDevices2.argtypes = [uint32_t, ctypes.POINTER(struct__drmDevice) * 0, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmGetDeviceFromDevId = _libraries['libdrm.so.2'].drmGetDeviceFromDevId
    drmGetDeviceFromDevId.restype = ctypes.c_int32
    drmGetDeviceFromDevId.argtypes = [dev_t, uint32_t, ctypes.POINTER(ctypes.POINTER(struct__drmDevice))]
except AttributeError:
    pass
try:
    drmGetNodeTypeFromDevId = _libraries['libdrm.so.2'].drmGetNodeTypeFromDevId
    drmGetNodeTypeFromDevId.restype = ctypes.c_int32
    drmGetNodeTypeFromDevId.argtypes = [dev_t]
except AttributeError:
    pass
try:
    drmDevicesEqual = _libraries['libdrm.so.2'].drmDevicesEqual
    drmDevicesEqual.restype = ctypes.c_int32
    drmDevicesEqual.argtypes = [drmDevicePtr, drmDevicePtr]
except AttributeError:
    pass
try:
    drmSyncobjCreate = _libraries['libdrm.so.2'].drmSyncobjCreate
    drmSyncobjCreate.restype = ctypes.c_int32
    drmSyncobjCreate.argtypes = [ctypes.c_int32, uint32_t, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmSyncobjDestroy = _libraries['libdrm.so.2'].drmSyncobjDestroy
    drmSyncobjDestroy.restype = ctypes.c_int32
    drmSyncobjDestroy.argtypes = [ctypes.c_int32, uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjHandleToFD = _libraries['libdrm.so.2'].drmSyncobjHandleToFD
    drmSyncobjHandleToFD.restype = ctypes.c_int32
    drmSyncobjHandleToFD.argtypes = [ctypes.c_int32, uint32_t, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmSyncobjFDToHandle = _libraries['libdrm.so.2'].drmSyncobjFDToHandle
    drmSyncobjFDToHandle.restype = ctypes.c_int32
    drmSyncobjFDToHandle.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmSyncobjImportSyncFile = _libraries['libdrm.so.2'].drmSyncobjImportSyncFile
    drmSyncobjImportSyncFile.restype = ctypes.c_int32
    drmSyncobjImportSyncFile.argtypes = [ctypes.c_int32, uint32_t, ctypes.c_int32]
except AttributeError:
    pass
try:
    drmSyncobjExportSyncFile = _libraries['libdrm.so.2'].drmSyncobjExportSyncFile
    drmSyncobjExportSyncFile.restype = ctypes.c_int32
    drmSyncobjExportSyncFile.argtypes = [ctypes.c_int32, uint32_t, ctypes.POINTER(ctypes.c_int32)]
except AttributeError:
    pass
try:
    drmSyncobjWait = _libraries['libdrm.so.2'].drmSyncobjWait
    drmSyncobjWait.restype = ctypes.c_int32
    drmSyncobjWait.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, int64_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmSyncobjReset = _libraries['libdrm.so.2'].drmSyncobjReset
    drmSyncobjReset.restype = ctypes.c_int32
    drmSyncobjReset.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjSignal = _libraries['libdrm.so.2'].drmSyncobjSignal
    drmSyncobjSignal.restype = ctypes.c_int32
    drmSyncobjSignal.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjTimelineSignal = _libraries['libdrm.so.2'].drmSyncobjTimelineSignal
    drmSyncobjTimelineSignal.restype = ctypes.c_int32
    drmSyncobjTimelineSignal.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64), uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjTimelineWait = _libraries['libdrm.so.2'].drmSyncobjTimelineWait
    drmSyncobjTimelineWait.restype = ctypes.c_int32
    drmSyncobjTimelineWait.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint32, int64_t, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
except AttributeError:
    pass
try:
    drmSyncobjQuery = _libraries['libdrm.so.2'].drmSyncobjQuery
    drmSyncobjQuery.restype = ctypes.c_int32
    drmSyncobjQuery.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64), uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjQuery2 = _libraries['libdrm.so.2'].drmSyncobjQuery2
    drmSyncobjQuery2.restype = ctypes.c_int32
    drmSyncobjQuery2.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint64), uint32_t, uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjTransfer = _libraries['libdrm.so.2'].drmSyncobjTransfer
    drmSyncobjTransfer.restype = ctypes.c_int32
    drmSyncobjTransfer.argtypes = [ctypes.c_int32, uint32_t, uint64_t, uint32_t, uint64_t, uint32_t]
except AttributeError:
    pass
try:
    drmSyncobjEventfd = _libraries['libdrm.so.2'].drmSyncobjEventfd
    drmSyncobjEventfd.restype = ctypes.c_int32
    drmSyncobjEventfd.argtypes = [ctypes.c_int32, uint32_t, uint64_t, ctypes.c_int32, uint32_t]
except AttributeError:
    pass
try:
    drmGetFormatModifierVendor = _libraries['libdrm.so.2'].drmGetFormatModifierVendor
    drmGetFormatModifierVendor.restype = ctypes.POINTER(ctypes.c_char)
    drmGetFormatModifierVendor.argtypes = [uint64_t]
except AttributeError:
    pass
try:
    drmGetFormatModifierName = _libraries['libdrm.so.2'].drmGetFormatModifierName
    drmGetFormatModifierName.restype = ctypes.POINTER(ctypes.c_char)
    drmGetFormatModifierName.argtypes = [uint64_t]
except AttributeError:
    pass
try:
    drmGetFormatName = _libraries['libdrm.so.2'].drmGetFormatName
    drmGetFormatName.restype = ctypes.POINTER(ctypes.c_char)
    drmGetFormatName.argtypes = [uint32_t]
except AttributeError:
    pass
__all__ = \
    ['DRM_ADD_COMMAND', 'DRM_AGP', 'DRM_AGP_BUFFER', 'DRM_CONSISTENT',
    'DRM_CONTAINS_LOCK', 'DRM_CONTEXT_2DONLY',
    'DRM_CONTEXT_PRESERVED', 'DRM_DMA_BLOCK', 'DRM_DMA_LARGER_OK',
    'DRM_DMA_PRIORITY', 'DRM_DMA_SMALLER_OK', 'DRM_DMA_WAIT',
    'DRM_DMA_WHILE_LOCKED', 'DRM_DRAWABLE_CLIPRECTS', 'DRM_FB_BUFFER',
    'DRM_FRAME_BUFFER', 'DRM_HALT_ALL_QUEUES', 'DRM_HALT_CUR_QUEUES',
    'DRM_INST_HANDLER', 'DRM_KERNEL', 'DRM_LOCKED', 'DRM_LOCK_FLUSH',
    'DRM_LOCK_FLUSH_ALL', 'DRM_LOCK_QUIESCENT', 'DRM_LOCK_READY',
    'DRM_MODE_SUBCONNECTOR_Automatic',
    'DRM_MODE_SUBCONNECTOR_Component',
    'DRM_MODE_SUBCONNECTOR_Composite', 'DRM_MODE_SUBCONNECTOR_DVIA',
    'DRM_MODE_SUBCONNECTOR_DVID', 'DRM_MODE_SUBCONNECTOR_DisplayPort',
    'DRM_MODE_SUBCONNECTOR_HDMIA', 'DRM_MODE_SUBCONNECTOR_Native',
    'DRM_MODE_SUBCONNECTOR_SCART', 'DRM_MODE_SUBCONNECTOR_SVIDEO',
    'DRM_MODE_SUBCONNECTOR_Unknown', 'DRM_MODE_SUBCONNECTOR_VGA',
    'DRM_MODE_SUBCONNECTOR_Wireless', 'DRM_PAGE_ALIGN',
    'DRM_PCI_BUFFER_RO', 'DRM_READ_ONLY', 'DRM_REGISTERS',
    'DRM_REMOVABLE', 'DRM_RESTRICTED', 'DRM_RM_COMMAND',
    'DRM_SCATTER_GATHER', 'DRM_SG_BUFFER', 'DRM_SHM',
    'DRM_UNINST_HANDLER', 'DRM_VBLANK_ABSOLUTE', 'DRM_VBLANK_EVENT',
    'DRM_VBLANK_FLIP', 'DRM_VBLANK_HIGH_CRTC_MASK',
    'DRM_VBLANK_NEXTONMISS', 'DRM_VBLANK_RELATIVE',
    'DRM_VBLANK_SECONDARY', 'DRM_VBLANK_SIGNAL',
    'DRM_WRITE_COMBINING', '_DRM_AGP', '_DRM_CONSISTENT',
    '_DRM_CONTAINS_LOCK', '_DRM_CONTEXT_2DONLY',
    '_DRM_CONTEXT_PRESERVED', '_DRM_DMA_BLOCK', '_DRM_DMA_LARGER_OK',
    '_DRM_DMA_PRIORITY', '_DRM_DMA_SMALLER_OK', '_DRM_DMA_WAIT',
    '_DRM_DMA_WHILE_LOCKED', '_DRM_DRIVER', '_DRM_FRAME_BUFFER',
    '_DRM_HALT_ALL_QUEUES', '_DRM_HALT_CUR_QUEUES', '_DRM_KERNEL',
    '_DRM_LOCKED', '_DRM_LOCK_FLUSH', '_DRM_LOCK_FLUSH_ALL',
    '_DRM_LOCK_QUIESCENT', '_DRM_LOCK_READY', '_DRM_READ_ONLY',
    '_DRM_REGISTERS', '_DRM_REMOVABLE', '_DRM_RESTRICTED',
    '_DRM_SCATTER_GATHER', '_DRM_SHM', '_DRM_STAT_BYTE',
    '_DRM_STAT_CLOSES', '_DRM_STAT_COUNT', '_DRM_STAT_DMA',
    '_DRM_STAT_IOCTLS', '_DRM_STAT_IRQ', '_DRM_STAT_LOCK',
    '_DRM_STAT_LOCKS', '_DRM_STAT_MISSED', '_DRM_STAT_OPENS',
    '_DRM_STAT_PRIMARY', '_DRM_STAT_SECONDARY', '_DRM_STAT_SPECIAL',
    '_DRM_STAT_UNLOCKS', '_DRM_STAT_VALUE', '_DRM_VBLANK_ABSOLUTE',
    '_DRM_VBLANK_EVENT', '_DRM_VBLANK_FLIP',
    '_DRM_VBLANK_HIGH_CRTC_MASK', '_DRM_VBLANK_NEXTONMISS',
    '_DRM_VBLANK_RELATIVE', '_DRM_VBLANK_SECONDARY',
    '_DRM_VBLANK_SIGNAL', '_DRM_WRITE_COMBINING',
    '__atomic_wide_counter', '__be16', '__be32', '__be64',
    '__blkcnt64_t', '__blkcnt_t', '__blksize_t', '__bswap_16',
    '__bswap_32', '__bswap_64', '__caddr_t', '__clock_t',
    '__clockid_t', '__daddr_t', '__dev_t', '__fd_mask',
    '__fsblkcnt64_t', '__fsblkcnt_t', '__fsfilcnt64_t',
    '__fsfilcnt_t', '__fsid_t', '__fsword_t', '__gid_t',
    '__gnuc_va_list', '__id_t', '__ino64_t', '__ino_t', '__int16_t',
    '__int32_t', '__int64_t', '__int8_t', '__int_least16_t',
    '__int_least32_t', '__int_least64_t', '__int_least8_t',
    '__intmax_t', '__intptr_t', '__kernel_caddr_t',
    '__kernel_clock_t', '__kernel_clockid_t', '__kernel_daddr_t',
    '__kernel_fd_set', '__kernel_fsid_t', '__kernel_gid16_t',
    '__kernel_gid32_t', '__kernel_gid_t', '__kernel_ino_t',
    '__kernel_ipc_pid_t', '__kernel_key_t', '__kernel_loff_t',
    '__kernel_long_t', '__kernel_mode_t', '__kernel_mqd_t',
    '__kernel_off_t', '__kernel_old_dev_t', '__kernel_old_gid_t',
    '__kernel_old_time_t', '__kernel_old_uid_t', '__kernel_pid_t',
    '__kernel_ptrdiff_t', '__kernel_sighandler_t', '__kernel_size_t',
    '__kernel_ssize_t', '__kernel_suseconds_t', '__kernel_time64_t',
    '__kernel_time_t', '__kernel_timer_t', '__kernel_uid16_t',
    '__kernel_uid32_t', '__kernel_uid_t', '__kernel_ulong_t',
    '__key_t', '__le16', '__le32', '__le64', '__loff_t', '__mode_t',
    '__nlink_t', '__off64_t', '__off_t', '__once_flag', '__pid_t',
    '__poll_t', '__pthread_list_t', '__pthread_slist_t', '__quad_t',
    '__rlim64_t', '__rlim_t', '__s128', '__s16', '__s32', '__s64',
    '__s8', '__sig_atomic_t', '__sigset_t', '__socklen_t',
    '__ssize_t', '__sum16', '__suseconds64_t', '__suseconds_t',
    '__syscall_slong_t', '__syscall_ulong_t', '__thrd_t', '__time_t',
    '__timer_t', '__tss_t', '__u128', '__u16', '__u32', '__u64',
    '__u8', '__u_char', '__u_int', '__u_long', '__u_quad_t',
    '__u_short', '__uid_t', '__uint16_identity', '__uint16_t',
    '__uint32_identity', '__uint32_t', '__uint64_identity',
    '__uint64_t', '__uint8_t', '__uint_least16_t', '__uint_least32_t',
    '__uint_least64_t', '__uint_least8_t', '__uintmax_t',
    '__useconds_t', '__wsum', 'blkcnt_t', 'blksize_t', 'caddr_t',
    'clock_t', 'clockid_t', 'daddr_t', 'dev_t', 'drmAddBufs',
    'drmAddContextPrivateMapping', 'drmAddContextTag', 'drmAddMap',
    'drmAddress', 'drmAddressPtr', 'drmAgpAcquire', 'drmAgpAlloc',
    'drmAgpBase', 'drmAgpBind', 'drmAgpDeviceId', 'drmAgpEnable',
    'drmAgpFree', 'drmAgpGetMode', 'drmAgpMemoryAvail',
    'drmAgpMemoryUsed', 'drmAgpRelease', 'drmAgpSize', 'drmAgpUnbind',
    'drmAgpVendorId', 'drmAgpVersionMajor', 'drmAgpVersionMinor',
    'drmAuthMagic', 'drmAvailable', 'drmBuf', 'drmBufDesc',
    'drmBufDescFlags', 'drmBufDescPtr', 'drmBufInfo', 'drmBufInfoPtr',
    'drmBufMap', 'drmBufMapPtr', 'drmBufPtr', 'drmClose',
    'drmCloseBufferHandle', 'drmCloseOnce', 'drmCommandNone',
    'drmCommandRead', 'drmCommandWrite', 'drmCommandWriteRead',
    'drmCreateContext', 'drmCreateDrawable', 'drmCrtcGetSequence',
    'drmCrtcQueueSequence', 'drmCtlInstHandler',
    'drmCtlUninstHandler', 'drmDMA', 'drmDMAFlags', 'drmDMAReq',
    'drmDMAReqPtr', 'drmDelContextTag', 'drmDestroyContext',
    'drmDestroyDrawable', 'drmDevice', 'drmDevicePtr',
    'drmDevicesEqual', 'drmDropMaster', 'drmError', 'drmEventContext',
    'drmEventContextPtr', 'drmFinish', 'drmFree', 'drmFreeBufs',
    'drmFreeBusid', 'drmFreeDevice', 'drmFreeDevices',
    'drmFreeReservedContextList', 'drmFreeVersion', 'drmGetBufInfo',
    'drmGetBusid', 'drmGetCap', 'drmGetClient', 'drmGetContextFlags',
    'drmGetContextPrivateMapping', 'drmGetContextTag', 'drmGetDevice',
    'drmGetDevice2', 'drmGetDeviceFromDevId',
    'drmGetDeviceNameFromFd', 'drmGetDeviceNameFromFd2',
    'drmGetDevices', 'drmGetDevices2', 'drmGetEntry',
    'drmGetFormatModifierName', 'drmGetFormatModifierVendor',
    'drmGetFormatName', 'drmGetHashTable', 'drmGetInterruptFromBusID',
    'drmGetLibVersion', 'drmGetLock', 'drmGetMagic', 'drmGetMap',
    'drmGetNodeTypeFromDevId', 'drmGetNodeTypeFromFd',
    'drmGetPrimaryDeviceNameFromFd', 'drmGetRenderDeviceNameFromFd',
    'drmGetReservedContextList', 'drmGetStats', 'drmGetVersion',
    'drmHandleEvent', 'drmHashCreate', 'drmHashDelete',
    'drmHashDestroy', 'drmHashEntry', 'drmHashFirst', 'drmHashInsert',
    'drmHashLookup', 'drmHashNext', 'drmHost1xBusInfo',
    'drmHost1xBusInfoPtr', 'drmHost1xDeviceInfo',
    'drmHost1xDeviceInfoPtr', 'drmIoctl', 'drmIsMaster', 'drmLock',
    'drmLockFlags', 'drmLockPtr', 'drmMalloc', 'drmMap', 'drmMapBufs',
    'drmMapFlags', 'drmMapType', 'drmMarkBufs', 'drmMsg', 'drmOpen',
    'drmOpenControl', 'drmOpenOnce', 'drmOpenOnceWithType',
    'drmOpenRender', 'drmOpenWithType', 'drmPciBusInfo',
    'drmPciBusInfoPtr', 'drmPciDeviceInfo', 'drmPciDeviceInfoPtr',
    'drmPlatformBusInfo', 'drmPlatformBusInfoPtr',
    'drmPlatformDeviceInfo', 'drmPlatformDeviceInfoPtr',
    'drmPrimeFDToHandle', 'drmPrimeHandleToFD', 'drmRandom',
    'drmRandomCreate', 'drmRandomDestroy', 'drmRandomDouble',
    'drmRegion', 'drmRegionPtr', 'drmRmMap', 'drmSLCreate',
    'drmSLDelete', 'drmSLDestroy', 'drmSLDump', 'drmSLFirst',
    'drmSLInsert', 'drmSLLookup', 'drmSLLookupNeighbors', 'drmSLNext',
    'drmScatterGatherAlloc', 'drmScatterGatherFree', 'drmServerInfo',
    'drmServerInfoPtr', 'drmSetBusid', 'drmSetClientCap',
    'drmSetContextFlags', 'drmSetInterfaceVersion', 'drmSetMaster',
    'drmSetServerInfo', 'drmSetVersion', 'drmSetVersionPtr',
    'drmSize', 'drmSizePtr', 'drmStatsT', 'drmSwitchToContext',
    'drmSyncobjCreate', 'drmSyncobjDestroy', 'drmSyncobjEventfd',
    'drmSyncobjExportSyncFile', 'drmSyncobjFDToHandle',
    'drmSyncobjHandleToFD', 'drmSyncobjImportSyncFile',
    'drmSyncobjQuery', 'drmSyncobjQuery2', 'drmSyncobjReset',
    'drmSyncobjSignal', 'drmSyncobjTimelineSignal',
    'drmSyncobjTimelineWait', 'drmSyncobjTransfer', 'drmSyncobjWait',
    'drmTextureRegion', 'drmTextureRegionPtr', 'drmUnlock',
    'drmUnmap', 'drmUnmapBufs', 'drmUpdateDrawableInfo',
    'drmUsbBusInfo', 'drmUsbBusInfoPtr', 'drmUsbDeviceInfo',
    'drmUsbDeviceInfoPtr', 'drmVBlank', 'drmVBlankPtr',
    'drmVBlankReply', 'drmVBlankReplyPtr', 'drmVBlankReq',
    'drmVBlankReqPtr', 'drmVBlankSeqType', 'drmVersion',
    'drmVersionPtr', 'drmWaitVBlank', 'drm_agp_binding_t',
    'drm_agp_buffer_t', 'drm_agp_info_t', 'drm_agp_mode_t',
    'drm_auth_t', 'drm_block_t', 'drm_buf_desc_t', 'drm_buf_free_t',
    'drm_buf_info_t', 'drm_buf_map_t', 'drm_buf_pub_t',
    'drm_client_t', 'drm_clip_rect_t', 'drm_context_t',
    'drm_context_tFlags', 'drm_context_tFlagsPtr', 'drm_control_t',
    'drm_ctx_flags', 'drm_ctx_flags_t', 'drm_ctx_flags_t__enumvalues',
    'drm_ctx_priv_map_t', 'drm_ctx_res_t', 'drm_ctx_t',
    'drm_dma_flags', 'drm_dma_flags_t', 'drm_dma_flags_t__enumvalues',
    'drm_dma_t', 'drm_draw_t', 'drm_drawable_info_t',
    'drm_drawable_info_type_t', 'drm_drawable_t', 'drm_handle_t',
    'drm_hw_lock_t', 'drm_irq_busid_t', 'drm_list_t',
    'drm_lock_flags', 'drm_lock_flags_t',
    'drm_lock_flags_t__enumvalues', 'drm_lock_t', 'drm_magic_t',
    'drm_map_flags', 'drm_map_flags_t', 'drm_map_flags_t__enumvalues',
    'drm_map_t', 'drm_map_type', 'drm_map_type_t',
    'drm_map_type_t__enumvalues', 'drm_mode_subconnector',
    'drm_scatter_gather_t', 'drm_set_version_t', 'drm_stat_type',
    'drm_stat_type_t', 'drm_stat_type_t__enumvalues', 'drm_stats_t',
    'drm_tex_region_t', 'drm_unique_t', 'drm_update_draw_t',
    'drm_vblank_seq_type', 'drm_vblank_seq_type_t',
    'drm_vblank_seq_type_t__enumvalues', 'drm_version_t',
    'drm_wait_vblank_t', 'fd_mask', 'fd_set', 'fsblkcnt_t',
    'fsfilcnt_t', 'fsid_t', 'gid_t', 'id_t', 'ino_t', 'int16_t',
    'int32_t', 'int64_t', 'int8_t', 'int_fast16_t', 'int_fast32_t',
    'int_fast64_t', 'int_fast8_t', 'int_least16_t', 'int_least32_t',
    'int_least64_t', 'int_least8_t', 'intmax_t', 'intptr_t', 'key_t',
    'loff_t', 'mode_t', 'nlink_t', 'off_t', 'pid_t', 'pselect',
    'pthread_attr_t', 'pthread_barrier_t', 'pthread_barrierattr_t',
    'pthread_cond_t', 'pthread_condattr_t', 'pthread_key_t',
    'pthread_mutex_t', 'pthread_mutexattr_t', 'pthread_once_t',
    'pthread_rwlock_t', 'pthread_rwlockattr_t', 'pthread_spinlock_t',
    'pthread_t', 'quad_t', 'register_t', 'select', 'sigset_t',
    'size_t', 'ssize_t', 'struct___atomic_wide_counter___value32',
    'struct___fsid_t', 'struct___kernel_fd_set',
    'struct___kernel_fsid_t', 'struct___once_flag',
    'struct___pthread_cond_s', 'struct___pthread_internal_list',
    'struct___pthread_internal_slist', 'struct___pthread_mutex_s',
    'struct___pthread_rwlock_arch_t', 'struct___sigset_t',
    'struct___va_list_tag', 'struct__drmBuf', 'struct__drmBufDesc',
    'struct__drmBufInfo', 'struct__drmBufMap', 'struct__drmDMAReq',
    'struct__drmDevice', 'struct__drmEventContext',
    'struct__drmHost1xBusInfo', 'struct__drmHost1xDeviceInfo',
    'struct__drmLock', 'struct__drmPciBusInfo',
    'struct__drmPciDeviceInfo', 'struct__drmPlatformBusInfo',
    'struct__drmPlatformDeviceInfo', 'struct__drmRegion',
    'struct__drmServerInfo', 'struct__drmSetVersion',
    'struct__drmStats', 'struct__drmStats_0',
    'struct__drmTextureRegion', 'struct__drmUsbBusInfo',
    'struct__drmUsbDeviceInfo', 'struct__drmVBlankReply',
    'struct__drmVBlankReq', 'struct__drmVersion',
    'struct_drmHashEntry', 'struct_drm_agp_binding',
    'struct_drm_agp_buffer', 'struct_drm_agp_info',
    'struct_drm_agp_mode', 'struct_drm_auth', 'struct_drm_block',
    'struct_drm_buf_desc', 'struct_drm_buf_free',
    'struct_drm_buf_info', 'struct_drm_buf_map', 'struct_drm_buf_pub',
    'struct_drm_client', 'struct_drm_clip_rect',
    'struct_drm_color_ctm', 'struct_drm_color_lut',
    'struct_drm_control', 'struct_drm_crtc_get_sequence',
    'struct_drm_crtc_queue_sequence', 'struct_drm_ctx',
    'struct_drm_ctx_priv_map', 'struct_drm_ctx_res', 'struct_drm_dma',
    'struct_drm_draw', 'struct_drm_drawable_info', 'struct_drm_event',
    'struct_drm_event_crtc_sequence', 'struct_drm_event_vblank',
    'struct_drm_format_modifier', 'struct_drm_format_modifier_blob',
    'struct_drm_gem_close', 'struct_drm_gem_flink',
    'struct_drm_gem_open', 'struct_drm_get_cap', 'struct_drm_hw_lock',
    'struct_drm_irq_busid', 'struct_drm_list', 'struct_drm_lock',
    'struct_drm_map', 'struct_drm_mode_atomic',
    'struct_drm_mode_card_res', 'struct_drm_mode_closefb',
    'struct_drm_mode_connector_set_property',
    'struct_drm_mode_create_blob', 'struct_drm_mode_create_dumb',
    'struct_drm_mode_create_lease', 'struct_drm_mode_crtc',
    'struct_drm_mode_crtc_lut', 'struct_drm_mode_crtc_page_flip',
    'struct_drm_mode_crtc_page_flip_target', 'struct_drm_mode_cursor',
    'struct_drm_mode_cursor2', 'struct_drm_mode_destroy_blob',
    'struct_drm_mode_destroy_dumb', 'struct_drm_mode_fb_cmd',
    'struct_drm_mode_fb_cmd2', 'struct_drm_mode_fb_dirty_cmd',
    'struct_drm_mode_get_blob', 'struct_drm_mode_get_connector',
    'struct_drm_mode_get_encoder', 'struct_drm_mode_get_lease',
    'struct_drm_mode_get_plane', 'struct_drm_mode_get_plane_res',
    'struct_drm_mode_get_property', 'struct_drm_mode_list_lessees',
    'struct_drm_mode_map_dumb', 'struct_drm_mode_mode_cmd',
    'struct_drm_mode_modeinfo', 'struct_drm_mode_obj_get_properties',
    'struct_drm_mode_obj_set_property',
    'struct_drm_mode_property_enum', 'struct_drm_mode_rect',
    'struct_drm_mode_revoke_lease', 'struct_drm_mode_set_plane',
    'struct_drm_modeset_ctl', 'struct_drm_plane_size_hint',
    'struct_drm_prime_handle', 'struct_drm_scatter_gather',
    'struct_drm_set_client_cap', 'struct_drm_set_client_name',
    'struct_drm_set_version', 'struct_drm_stats',
    'struct_drm_stats_0', 'struct_drm_syncobj_array',
    'struct_drm_syncobj_create', 'struct_drm_syncobj_destroy',
    'struct_drm_syncobj_eventfd', 'struct_drm_syncobj_handle',
    'struct_drm_syncobj_timeline_array',
    'struct_drm_syncobj_timeline_wait', 'struct_drm_syncobj_transfer',
    'struct_drm_syncobj_wait', 'struct_drm_tex_region',
    'struct_drm_unique', 'struct_drm_update_draw',
    'struct_drm_version', 'struct_drm_wait_vblank_reply',
    'struct_drm_wait_vblank_request', 'struct_fd_set',
    'struct_hdr_metadata_infoframe',
    'struct_hdr_metadata_infoframe_0',
    'struct_hdr_metadata_infoframe_white_point',
    'struct_hdr_output_metadata', 'struct_timespec', 'struct_timeval',
    'suseconds_t', 'time_t', 'timer_t', 'u_char', 'u_int',
    'u_int16_t', 'u_int32_t', 'u_int64_t', 'u_int8_t', 'u_long',
    'u_quad_t', 'u_short', 'uid_t', 'uint', 'uint16_t', 'uint32_t',
    'uint64_t', 'uint8_t', 'uint_fast16_t', 'uint_fast32_t',
    'uint_fast64_t', 'uint_fast8_t', 'uint_least16_t',
    'uint_least32_t', 'uint_least64_t', 'uint_least8_t', 'uintmax_t',
    'uintptr_t', 'ulong', 'union___atomic_wide_counter',
    'union__drmDevice_businfo', 'union__drmDevice_deviceinfo',
    'union__drmVBlank', 'union_drm_wait_vblank',
    'union_hdr_output_metadata_0', 'union_pthread_attr_t',
    'union_pthread_barrier_t', 'union_pthread_barrierattr_t',
    'union_pthread_cond_t', 'union_pthread_condattr_t',
    'union_pthread_mutex_t', 'union_pthread_mutexattr_t',
    'union_pthread_rwlock_t', 'union_pthread_rwlockattr_t', 'ushort',
    'va_list']
