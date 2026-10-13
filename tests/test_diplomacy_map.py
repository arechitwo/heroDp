"""Verify player settings and city coverage persisted in the actual base map."""
from pathlib import Path
import struct
import unittest
from tools.prepare_base_map import Archive, DEFAULT_DLL, sections


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
            if kind == 195:
                self.assertEqual(units[i+16], 7)
                markers.append(i)
            if kind == 214:
                starts.append(units[i+16])
        self.assertEqual(len(markers), 260)
        self.assertEqual(sorted(starts), list(range(7)))

    def test_each_city_marker_has_one_region(self):
        units = self.data[b'UNIT']
        positions = [struct.unpack_from('<HH', units, i+4) for i in range(0, len(units), 36)
                     if struct.unpack_from('<H', units, i+8)[0] == 195 and units[i+16] == 7]
        hits = [0]*len(positions)
        regions = 0
        for location in range(1, 232):
            if location == 64:
                continue
            left, top, right, bottom = struct.unpack_from('<4I', self.data[b'MRGN'], (location-1)*20)
            if left == right or top == bottom:
                continue
            contained = [i for i, (x, y) in enumerate(positions) if left <= x <= right and top <= y <= bottom]
            self.assertIn(len(contained), (1, 2, 3))
            for i in contained:
                hits[i] += 1
            regions += 1
        self.assertEqual(regions, 230)
        self.assertEqual(hits, [1]*260)
