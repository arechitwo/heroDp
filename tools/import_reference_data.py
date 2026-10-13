"""One-time migration from FranceDp reference data into standalone editable JSON."""
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[1]


def main():
    reference = ROOT / 'BuildData_FanceDp'
    destination = ROOT / 'src/data'
    tbl = (reference / 'temp/custom_txt.tbl').read_bytes()
    count = struct.unpack_from('<H', tbl)[0]
    offsets = struct.unpack_from(f'<{count}H', tbl, 2)
    entries = []
    # Preserve embedded NULs (e.g. unit name + hotkey/tooltip aliases) exactly.
    for i, offset in enumerate(offsets):
        end = offsets[i+1] if i+1 < count else len(tbl)
        raw = tbl[offset:end]
        if not raw.endswith(b'\0'):
            raise ValueError('Malformed reference TBL entry')
        raw = raw[:-1]
        entry = {'id': i+1}
        try:
            entry['text'] = raw.decode('cp949')
        except UnicodeDecodeError:
            entry['hex'] = raw.hex()
        entries.append(entry)
    custom = {'version': 1, 'enabled': False, 'encoding': 'cp949',
              'source_note': 'FranceDp snapshot; disabled until explicitly enabled. Embedded NULs are preserved.',
              'copy_capacity_bytes': len(tbl), 'entries': entries}
    source = (reference / 'eudplibData/ExtraDataEditor.py').read_text(encoding='utf-8-sig')
    groups = {'units': (0x660A70, 228), 'upgrades': (0x6558C0, 60),
              'tech_research': (0x656198, 44), 'tech_use': (0x6562F8, 44), 'orders': (0x665580, 188)}
    tables = {}
    for name, (address, size) in groups.items():
        matches = re.findall(r'SetMemory\(0x' + f'{address:X}' + r' \+ (\d+), SetTo, (\d+)\)', source)
        data = bytearray(size * 2)
        assert len(matches) == size // 2
        for offset, value in matches:
            struct.pack_into('<I', data, int(offset), int(value))
        tables[name] = list(struct.unpack(f'<{size}H', data))
    raw = (reference / 'temp/RequireData').read_bytes()
    require = {'version': 1, 'enabled': False,
               'source_note': 'FranceDp complete requirement bytecode and offset tables; disabled until enabled.',
               'copy_capacity_bytes': len(raw), 'data_words': list(struct.unpack(f'<{len(raw)//2}H', raw)),
               'offset_tables': tables}
    for name, config in [('custom_tbl.json', custom), ('require_data.json', require)]:
        destination.joinpath(name).write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    from generate_game_data import compile_tbl, compile_require
    assert compile_tbl(custom) == tbl
    assert compile_require(require)[0] == raw
    print(f'Imported and verified {count} TBL entries and {len(raw)//2} requirement words')


if __name__ == '__main__':
    main()
