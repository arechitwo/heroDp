"""Verify the actual compile-time map plugin without an installed eudplib."""
import json
from pathlib import Path
import struct
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class FakeChk:
    def __init__(self):
        cities = json.loads((ROOT / 'src/data/city_markers.json').read_text())['cities']
        records = []
        for city in cities:
            for x, y in city['positions']:
                record = bytearray(36)
                struct.pack_into('<IHHH', record, 0, len(records)+1, x, y, 195)
                record[16] = 7
                records.append(bytes(record))
        self.data = {'UNIT': b''.join(records), 'MRGN': bytes(5100)}

    def getsection(self, name):
        return self.data[name]

    def setsection(self, name, data):
        self.data[name] = data


class DiplomacyMapTests(unittest.TestCase):
    def setUp(self):
        self.chk = FakeChk()
        self.original_units = self.chk.getsection('UNIT')
        self.refreshed = []
        fake = types.ModuleType('eudplib')
        fake.GetChkTokenized = lambda: self.chk
        playerinfo = types.ModuleType('eudplib.core.mapdata.playerinfo')
        playerinfo.init_player_info = self.refreshed.append
        with patch.dict(sys.modules, {'eudplib': fake, 'eudplib.core.mapdata.playerinfo': playerinfo}):
            exec(compile((ROOT / 'src/plugins/map_setup.py').read_text(), 'map_setup.py', 'exec'),
                 {'settings': {'project_root': str(ROOT)}})

    def test_playable_slots_and_cache_refresh(self):
        self.assertEqual(self.chk.getsection('OWNR'), bytes([6]*7 + [5] + [0]*4))
        self.assertEqual(self.chk.getsection('IOWN'), self.chk.getsection('OWNR'))
        self.assertEqual(self.refreshed, [self.chk])

    def test_markers_remain_for_conversion_after_dat_initialization(self):
        units = self.chk.getsection('UNIT')
        self.assertEqual(len(units)//36, 267)
        for offset in range(0, len(self.original_units), 36):
            self.assertEqual(struct.unpack_from('<H', units, offset+8)[0], 195)
            self.assertEqual(units[offset+4:offset+8], self.original_units[offset+4:offset+8])
            self.assertEqual(units[offset+16], 7)
        starts = [units[i:i+36] for i in range(len(self.original_units), len(units), 36)]
        self.assertEqual([r[16] for r in starts], list(range(7)))
        self.assertTrue(all(struct.unpack_from('<H', r, 8)[0] == 214 for r in starts))

    def test_engine_locations_do_not_mix_city_groups(self):
        cities = json.loads((ROOT / 'src/data/city_markers.json').read_text())['cities']
        locations = self.chk.getsection('MRGN')
        self.assertEqual(struct.unpack_from('<4I', locations, 63*20), (0, 0, 8192, 8192))
        for city in cities:
            left, top, right, bottom = struct.unpack_from('<4I', locations, (city['original_location']-1)*20)
            contained = [(other['id'], x, y) for other in cities for x, y in other['positions']
                         if left <= x <= right and top <= y <= bottom]
            self.assertEqual(len(contained), city['count'])
            self.assertTrue(all(name == city['id'] for name, x, y in contained))
        self.assertEqual(len({c['original_location'] for c in cities}), 230)


if __name__ == '__main__':
    unittest.main()
