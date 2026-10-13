"""Convert named city locations into P8 Terran Beacon markers, then clear MRGN."""
import argparse
from collections import Counter
from pathlib import Path
import re
import shutil
import struct

from prepare_base_map import Archive, DEFAULT_DLL, sections

OFFSETS = {
    1: [(0, 0)],
    2: [(-16, 0), (16, 0)],
    3: [(-16, 0), (16, -16), (16, 16)],
}


def read_map(path, dll):
    archive = Archive(path, dll)
    try:
        return sections(archive.read())
    finally:
        archive.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Original SCX with named locations')
    parser.add_argument('output', type=Path)
    parser.add_argument('--dll', default=DEFAULT_DLL)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        raise ValueError('Source must remain separate from output')
    original = read_map(args.source, args.dll)
    data = dict(original)
    strings = data[b'STR ']
    count = struct.unpack_from('<H', strings)[0]
    offsets = struct.unpack_from(f'<{count}H', strings, 2)
    names = [strings[offset:].split(b'\0', 1)[0].decode('cp949') for offset in offsets]
    width, height = struct.unpack('<HH', data[b'DIM '])
    unit = data[b'UNIT']
    assert len(unit) % 36 == 0
    serial = max((struct.unpack_from('<I', unit, i)[0] for i in range(0, len(unit), 36)), default=0) + 1
    markers = []
    cities = []
    distribution = Counter()
    for i in range(0, len(data[b'MRGN']), 20):
        left, top, right, bottom, name_id, flags = struct.unpack_from('<IIIIHH', data[b'MRGN'], i)
        if not name_id:
            continue
        name = names[name_id - 1]
        if name == 'Anywhere':
            continue
        match = re.fullmatch(r'(G\d+) \(([1-3]) cities\)', name)
        if not match:
            raise ValueError(f'Unexpected location name: {name}')
        amount = int(match[2])
        center_x, center_y = (left + right) // 2, (top + bottom) // 2
        positions = []
        for dx, dy in OFFSETS[amount]:
            x, y = center_x + dx, center_y + dy
            assert left <= x - 16 and x + 16 <= right
            assert top <= y - 16 and y + 16 <= bottom
            assert 16 <= x <= width * 32 - 16 and 16 <= y <= height * 32 - 16
            record = bytearray(36)
            struct.pack_into('<IHHH', record, 0, serial, x, y, 195)
            record[16:20] = bytes([7, 100, 100, 100])
            markers.append(bytes(record))
            positions.append([x, y])
            serial += 1
        distribution[amount] += 1
        cities.append({'id': match[1], 'original_location': i // 20 + 1, 'name': name,
                       'center': [center_x, center_y], 'count': amount, 'positions': positions})
    assert cities, 'No city locations found'
    positions = [position for city in cities for position in city['positions']]
    for i, (x, y) in enumerate(positions):
        for other_x, other_y in positions[i+1:]:
            assert abs(x-other_x) >= 32 or abs(y-other_y) >= 32, '32px marker footprints overlap'
    modified = [(tag, bytes(len(payload)) if tag == b'MRGN' else unit + b''.join(markers)
                 if tag == b'UNIT' else payload) for tag, payload in original]
    raw = b''.join(struct.pack('<4sI', tag, len(payload)) + payload for tag, payload in modified)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source, args.output)
    archive = Archive(args.output, args.dll)
    try:
        archive.write(raw)
    finally:
        archive.close()
    checked = read_map(args.output, args.dll)
    assert checked == modified, 'Saved map does not match intended CHK'
    assert not any(dict(checked)[b'MRGN'])
    print(f'Verified {len(cities)} groups, {len(markers)} markers; counts: {dict(sorted(distribution.items()))}')
    print(f'All locations cleared; 32px footprints do not overlap; all other CHK sections unchanged: {args.output}')


if __name__ == '__main__':
    main()
