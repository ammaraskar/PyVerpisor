import os
import ctypes
from ctypes import pythonapi


pythonapi.PyMemoryView_FromMemory.argtypes = (
    ctypes.c_void_p,
    ctypes.c_ssize_t,
    ctypes.c_int,
)
pythonapi.PyMemoryView_FromMemory.restype = ctypes.py_object


# Separate implementations for windows and others.
if os.name == "nt":
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    MEM_COMMIT = 0x00001000
    MEM_RESERVE = 0x00002000
    PAGE_EXECUTE_READWRITE = 0x40

    VirtualAlloc = kernel32.VirtualAlloc
    VirtualAlloc.restype = ctypes.c_void_p


    def map_executable_page(num_bytes):
        buf = VirtualAlloc(
            # lpAddress, NULL to let system figure out where to put it.
            None,
            # dwSize, size of the region in bytes.
            num_bytes,
            MEM_COMMIT | MEM_RESERVE,
            # flProtect, rwx permissions.
            PAGE_EXECUTE_READWRITE,
        )

        memory_view = pythonapi.PyMemoryView_FromMemory(
            buf,
            num_bytes,
            # memory view flags = rw
            0x200,
        )

        return memory_view, buf

else:
    import mmap

    libc = ctypes.CDLL("libc.so.6")

    libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_long]
    libc.mmap.restype = ctypes.c_void_p

    def map_executable_page(num_bytes):
        # Map anonymous page with rwx.
        buf = libc.mmap(
            0, # addr
            num_bytes, # size
            mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
            mmap.MAP_ANON | mmap.MAP_PRIVATE,
            -1, # fd
            0 # offset
        )

        memory_view = pythonapi.PyMemoryView_FromMemory(
            buf,
            num_bytes,
            # memory view flags = rw
            0x200,
        )

        return memory_view, buf
