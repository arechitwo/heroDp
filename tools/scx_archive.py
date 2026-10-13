"""Shared SCX archive access and CHK parsing through StormLib."""
import ctypes as c
import struct

DEFAULT_DLL = r"C:\repo\programs\SCArchive 2\StormLib64.dll"


class Archive:
    def __init__(self, path, dll, readonly=False):
        self.lib = c.WinDLL(dll, use_last_error=True)
        signatures = {
            'SFileOpenArchive': ([c.c_char_p, c.c_uint32, c.c_uint32, c.POINTER(c.c_void_p)], c.c_bool),
            'SFileOpenFileEx': ([c.c_void_p, c.c_char_p, c.c_uint32, c.POINTER(c.c_void_p)], c.c_bool),
            'SFileGetFileSize': ([c.c_void_p, c.POINTER(c.c_uint32)], c.c_uint32),
            'SFileReadFile': ([c.c_void_p, c.c_void_p, c.c_uint32, c.POINTER(c.c_uint32), c.c_void_p], c.c_bool),
            'SFileCloseFile': ([c.c_void_p], c.c_bool),
            'SFileCloseArchive': ([c.c_void_p], c.c_bool),
            'SFileCreateFile': ([c.c_void_p, c.c_char_p, c.c_uint64, c.c_uint32, c.c_uint32, c.c_uint32, c.POINTER(c.c_void_p)], c.c_bool),
            'SFileWriteFile': ([c.c_void_p, c.c_void_p, c.c_uint32, c.c_uint32], c.c_bool),
            'SFileFinishFile': ([c.c_void_p], c.c_bool),
        }
        for name, (args, result) in signatures.items():
            fn = getattr(self.lib, name)
            fn.argtypes, fn.restype = args, result
        self.handle = c.c_void_p()
        self.check(self.lib.SFileOpenArchive(str(path).encode('mbcs'), 0, 0x100 if readonly else 0, c.byref(self.handle)))

    def check(self, result):
        if not result:
            raise c.WinError(c.get_last_error())

    def read(self, name=b'staredit\\scenario.chk'):
        handle = c.c_void_p()
        self.check(self.lib.SFileOpenFileEx(self.handle, name, 0, c.byref(handle)))
        try:
            size = self.lib.SFileGetFileSize(handle, None)
            if size == 0xFFFFFFFF:
                raise c.WinError(c.get_last_error())
            buf = c.create_string_buffer(size)
            read = c.c_uint32()
            self.check(self.lib.SFileReadFile(handle, buf, size, c.byref(read), None))
            assert read.value == size
            return buf.raw
        finally:
            self.lib.SFileCloseFile(handle)

    def write(self, raw):
        handle = c.c_void_p()
        # REPLACEEXISTING | COMPRESS; zlib compression.
        self.check(self.lib.SFileCreateFile(self.handle, b'staredit\\scenario.chk', 0, len(raw), 0, 0x80000200, c.byref(handle)))
        try:
            self.check(self.lib.SFileWriteFile(handle, raw, len(raw), 2))
        finally:
            self.check(self.lib.SFileFinishFile(handle))

    def close(self):
        self.check(self.lib.SFileCloseArchive(self.handle))


def sections(raw):
    result = []
    offset = 0
    while offset < len(raw):
        tag, size = struct.unpack_from('<4sI', raw, offset)
        end = offset + 8 + size
        if end > len(raw):
            raise ValueError('Invalid CHK section')
        result.append((tag, raw[offset+8:end]))
        offset = end
    return result
