"""Edit raw SCX through StormLib; preserve terrain and other CHK sections."""
import argparse
import ctypes as c
from collections import Counter
import json
from pathlib import Path
import shutil
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


def summary(items):
    data = dict(items)
    unit = data.get(b'UNIT', b'')
    assert len(unit) % 36 == 0
    counts = Counter(struct.unpack_from('<H', unit, i+8)[0] for i in range(0, len(unit), 36))
    locations = data.get(b'MRGN', b'')
    return {'units': dict(counts), 'active_locations': sum(any(locations[i:i+20]) for i in range(0, len(locations), 20))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('map', type=Path)
    parser.add_argument('--dll', default=DEFAULT_DLL)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--clear-locations-only', action='store_true', help='Clear locations without placing markers')
    args = parser.parse_args()
    archive = Archive(args.map, args.dll)
    try:
        original = archive.read()
        items = sections(original)
        print(json.dumps(summary(items), indent=2))
        if not (args.apply or args.clear_locations_only):
            return
        backup = args.map.with_suffix('.original.scx')
        if backup.exists():
            raise ValueError(f'Backup already exists: {backup}')
        shutil.copy2(args.map, backup)
        unit = dict(items)[b'UNIT']
        records = [unit[i:i+36] for i in range(0, len(unit), 36)]
        pylons = [r for r in records if struct.unpack_from('<H', r, 8)[0] == 156]
        if not pylons and not args.clear_locations_only:
            raise ValueError('No pylons found; refusing to edit')
        serial = max((struct.unpack_from('<I', r)[0] for r in records), default=0) + 1
        existing = {(struct.unpack_from('<HH', r, 4), r[16]) for r in records if struct.unpack_from('<H', r, 8)[0] == 195}
        markers = []
        for pylon in ([] if args.clear_locations_only else pylons):
            x, y = struct.unpack_from('<HH', pylon, 4)
            if ((x, y), 7) in existing:
                continue
            marker = bytearray(36)
            struct.pack_into('<IHHH', marker, 0, serial, x, y, 195)
            marker[16:20] = bytes([7, 100, 100, 100])
            records.append(bytes(marker))
            markers.append((x, y))
            existing.add(((x, y), 7))
            serial += 1
        modified = [(tag, bytes(len(data)) if tag == b'MRGN' else b''.join(records) if tag == b'UNIT' else data) for tag, data in items]
        raw = b''.join(struct.pack('<4sI', tag, len(data)) + data for tag, data in modified)
        archive.write(raw)
    finally:
        archive.close()
    archive = Archive(args.map, args.dll)
    try:
        checked = sections(archive.read())
        assert checked == modified, 'Saved CHK differs from expected data'
        assert summary(checked)['active_locations'] == 0
        assert dict(checked)[b'UNIT'][:len(unit)] == unit
        print(f'Verified: {len(pylons)} pylons; {len(markers)} P8 Terran Beacon markers added. Backup: {backup}')
    finally:
        archive.close()


if __name__ == '__main__':
    main()
