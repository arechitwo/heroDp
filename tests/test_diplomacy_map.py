"""Verify player settings and city coverage persisted in the actual base map."""
from pathlib import Path
import ast
import configparser
import struct
import unittest
from tools.scx_archive import Archive, DEFAULT_DLL, sections


class DiplomacyMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        archive = Archive(Path(__file__).resolve().parents[1] / 'maps/base.scx', DEFAULT_DLL, readonly=True)
        try:
            cls.data = dict(sections(archive.read()))
        finally:
            archive.close()

    def test_playable_slots_and_terran_race(self):
        self.assertEqual(self.data[b'OWNR'], bytes([6]*7 + [5] + [0]*4))
        self.assertEqual(self.data[b'IOWN'], self.data[b'OWNR'])
        self.assertEqual(self.data[b'SIDE'][:8], bytes([1]*8))

    def test_markers_and_starts(self):
        units = self.data[b'UNIT']
        markers, starts = [], []
        for i in range(0, len(units), 36):
            kind = struct.unpack_from('<H', units, i+8)[0]
            self.assertFalse(kind == 101 and units[i+16] == 8,
                             'MoveLocation fallback requires no P9 Map Revealer')
            if kind == 195:
                self.assertEqual(units[i+16], 7)
                markers.append(i)
            if kind == 214:
                starts.append(units[i+16])
        self.assertEqual(len(markers), 260)
        self.assertEqual(sorted(starts), list(range(7)))

    def test_named_locations_and_start_regions(self):
        root = Path(__file__).resolve().parents[1]
        tag = b'STRx' if b'STRx' in self.data else b'STR '
        word = 'I' if tag == b'STRx' else 'H'
        strings = self.data[tag]
        count = struct.unpack_from('<'+word, strings)[0]
        offsets = struct.unpack_from('<'+str(count)+word, strings, struct.calcsize(word))
        names = [strings[offset:].split(b'\0', 1)[0].decode('cp949') for offset in offsets]
        named = {}
        for location in range(1, 256):
            record = self.data[b'MRGN'][(location-1)*20:location*20]
            name_id = struct.unpack_from('<H', record, 16)[0]
            if name_id:
                named[names[name_id-1]] = location
            else:
                self.assertEqual(record, bytes(20), 'Unallocated locations must remain empty')
        tree = ast.parse((root / 'src/game/modules/map_data.py').read_text())
        enum = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'Loc')
        declared = {node.value.args[0].value for node in enum.body if isinstance(node, ast.Assign)}
        self.assertEqual(set(named), declared)
        self.assertEqual(len(named), 21)
        self.assertEqual([named[f'start_p{i}'] for i in range(1, 8)], list(range(12, 19)))
        self.assertEqual([named[f'mouse_p{i}'] for i in range(1, 8)], list(range(5, 12)))
        recipe = configparser.ConfigParser(delimiters=(':',), interpolation=None)
        recipe.read(root / 'main.eds', encoding='utf-8')
        self.assertEqual(recipe.getint('MSQC', 'QCLoc'), named['msqc'])
        self.assertEqual(recipe.getint('MSQC', 'mouse'), named['mouse_p1'])
        left, top, right, bottom = struct.unpack_from('<4I', self.data[b'MRGN'], (named['city_capture']-1)*20)
        self.assertEqual((right-left, bottom-top), (320, 320))
        units = self.data[b'UNIT']
        positions = [struct.unpack_from('<HH', units, i+4) for i in range(0, len(units), 36)
                     if struct.unpack_from('<H', units, i+8)[0] == 195 and units[i+16] == 7]
        hits = [0]*len(positions)
        for location in [named[f'start_p{i}'] for i in range(1, 8)]:
            left, top, right, bottom = struct.unpack_from('<4I', self.data[b'MRGN'], (location-1)*20)
            contained = [i for i, (x, y) in enumerate(positions) if left <= x <= right and top <= y <= bottom]
            self.assertIn(len(contained), (1, 2, 3))
            for i in contained:
                hits[i] += 1
        self.assertTrue(all(hit <= 1 for hit in hits), 'Start regions must not overlap')
