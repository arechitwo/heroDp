import copy
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools.generate_game_data import compile_require, compile_tbl, generate, load

ROOT = Path(__file__).resolve().parents[1]


class GameDataTests(unittest.TestCase):
    def test_tbl_internal_nul_encoding_and_offsets(self):
        config = {'version': 1, 'enabled': True, 'encoding': 'cp949', 'copy_capacity_bytes': 100,
                  'entries': [{'id': 1, 'text': '\x04도시\0alias'}, {'id': 2, 'hex': 'fffe'}]}
        raw = compile_tbl(config)
        count, first, second = struct.unpack_from('<3H', raw)
        self.assertEqual((count, first), (2, 6))
        self.assertEqual(raw[first:second], '\x04도시\0alias'.encode('cp949') + b'\0')
        self.assertEqual(raw[second:], b'\xff\xfe\0')

    def test_invalid_table_ids_and_capacity_are_rejected(self):
        config = {'version': 1, 'enabled': False, 'encoding': 'cp949', 'copy_capacity_bytes': 100,
                  'entries': [{'id': 2, 'text': 'city'}]}
        with self.assertRaises(ValueError):
            compile_tbl(config)
        config['entries'][0]['id'] = 1
        config['copy_capacity_bytes'] = 4
        with self.assertRaises(ValueError):
            compile_tbl(config)

    def test_requirement_dword_packing_and_invalid_table(self):
        config = load(ROOT / 'src/data/require_data.json')
        raw, tables = compile_require(config)
        self.assertEqual(len(raw), 4170)
        for table in tables:
            words = config['offset_tables'][table['name']]
            self.assertEqual(table['dwords'], [words[i] | words[i+1] << 16 for i in range(0, len(words), 2)])
        invalid = copy.deepcopy(config)
        invalid['offset_tables']['units'].pop()
        with self.assertRaises(ValueError):
            compile_require(invalid)

    def test_generated_padding_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = generate(ROOT / 'src/data/custom_tbl.json', ROOT / 'src/data/require_data.json', directory)
            for name, key in [('custom_txt.tbl', 'tbl_bytes'), ('RequireData', 'require_bytes')]:
                raw = Path(directory, name).read_bytes()
                self.assertEqual(len(raw) % 4, 0)
                self.assertFalse(any(raw[manifest[key]:]))
            self.assertEqual(json.loads(Path(directory, 'manifest.json').read_text()), manifest)


if __name__ == '__main__':
    unittest.main()
