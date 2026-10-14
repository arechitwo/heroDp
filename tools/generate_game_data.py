"""Generate binary TBL and RequireData from checked-in JSON (stdlib only)."""
import json
from pathlib import Path
import struct


def integer(value, maximum):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f'Expected integer 0..{maximum}: {value!r}')
    return value


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def compile_tbl(config):
    if config.get('version') != 1 or type(config.get('enabled')) is not bool:
        raise ValueError('TBL version must be 1; enabled must be boolean')
    entries = config['entries']
    count = integer(len(entries), 65535)
    encoding = config['encoding']
    table = bytearray(struct.pack('<H', count))
    body = bytearray()
    offset = 2 + 2 * count
    for expected, entry in enumerate(entries, 1):
        if entry['id'] != expected:
            raise ValueError('TBL ids must be consecutive, starting at 1')
        if ('text' in entry) == ('hex' in entry):
            raise ValueError('Each TBL entry requires exactly one of text or hex')
        raw = entry['text'].encode(encoding) if 'text' in entry else bytes.fromhex(entry['hex'])
        table.extend(struct.pack('<H', integer(offset, 65535)))
        body.extend(raw + b'\0')
        offset += len(raw) + 1
    result = bytes(table + body)
    if len(result) > integer(config['copy_capacity_bytes'], 65535):
        raise ValueError('TBL exceeds configured copy capacity; shorten entries before applying')
    return result


def compile_require(config):
    if config.get('version') != 1 or type(config.get('enabled')) is not bool:
        raise ValueError('RequireData version must be 1; enabled must be boolean')
    words = config['data_words']
    raw = b''.join(struct.pack('<H', integer(word, 65535)) for word in words)
    if len(raw) > integer(config['copy_capacity_bytes'], 65535):
        raise ValueError('RequireData exceeds its original memory region')
    expected = {'units': (0x660A70, 228), 'upgrades': (0x6558C0, 60),
                'tech_research': (0x656198, 44), 'tech_use': (0x6562F8, 44),
                'orders': (0x665580, 188)}
    if set(config['offset_tables']) != set(expected):
        raise ValueError('All five requirement offset tables are required')
    tables = []
    for name, (address, size) in expected.items():
        values = config['offset_tables'][name]
        if len(values) != size:
            raise ValueError(f'{name} requires {size} uint16 offsets')
        encoded = b''.join(struct.pack('<H', integer(v, 65535)) for v in values)
        tables.append({'name': name, 'address': address,
                       'dwords': list(struct.unpack(f'<{len(encoded)//4}I', encoded))})
    return raw, tables


def generate(tbl_path, require_path, destination=None):
    tbl = load(tbl_path)
    req = load(require_path)
    tbl_raw = compile_tbl(tbl)
    require_raw, tables = compile_require(req)
    manifest = {'custom_tbl_enabled': tbl['enabled'], 'require_data_enabled': req['enabled'],
                'tbl_bytes': len(tbl_raw), 'require_bytes': len(require_raw), 'offset_tables': tables}
    manifest['unit_overrides'] = req.get('unit_overrides', {'enabled': False})
    manifest['unit_links'] = req.get('unit_links', {})
    if destination is not None:
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        # DWORD copy routines may read up to three bytes past the logical data.
        for name, raw in [('custom_txt.tbl', tbl_raw), ('RequireData', require_raw)]:
            destination.joinpath(name).write_bytes(raw + bytes((-len(raw)) % 4))
        destination.joinpath('manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest
