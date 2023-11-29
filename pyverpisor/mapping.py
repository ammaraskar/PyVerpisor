import os


# Separate implementations for windows and others.
if os.name == "nt":
    import ctypes
    from ctypes import pythonapi

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    MEM_COMMIT = 0x00001000
    MEM_RESERVE = 0x00002000
    PAGE_EXECUTE_READWRITE = 0x40

    VirtualAlloc = kernel32.VirtualAlloc
    VirtualAlloc.restype = ctypes.c_void_p

    pythonapi.PyMemoryView_FromMemory.argtypes = (
        ctypes.c_void_p,
        ctypes.c_ssize_t,
        ctypes.c_int,
    )
    pythonapi.PyMemoryView_FromMemory.restype = ctypes.py_object

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
    import ctypes
    import mmap

    def map_executable_page(num_bytes):
        # Map anonymous page with rwx.
        mem = mmap.mmap(
            -1,
            num_bytes,
            prot=mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC,
            flags=mmap.MAP_ANON | mmap.MAP_PRIVATE,
        )

        return memoryview(map), ctypes.c_void_p.from_buffer(mem)
