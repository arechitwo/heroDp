"""Compile-time gameplay configuration; no DAT/stat or special-unit edits."""
import json
from pathlib import Path
import struct
from eudplib import EUDArray, GetChkTokenized, unProxy
from .unit_settings import UnitModel

ROOT = Path(__file__).resolve().parents[3]
config = json.loads((ROOT / 'src/data/diplomacy.json').read_text(encoding='utf-8'))
chk = GetChkTokenized()
unit_data = chk.getsection('UNIT')
marker_positions = [struct.unpack_from('<HH', unit_data, offset + 4)
                    for offset in range(0, len(unit_data), 36)
                    if struct.unpack_from('<H', unit_data, offset + 8)[0] == unProxy(UnitModel.city_marker)
                    and unit_data[offset + 16] == 7]
location_data = chk.getsection('MRGN')
cities = []
for location in range(1, 232):
    if location == 64:  # Anywhere
        continue
    left, top, right, bottom = struct.unpack_from('<4I', location_data, (location - 1) * 20)
    if left == right or top == bottom:
        continue
    count = sum(left <= x <= right and top <= y <= bottom for x, y in marker_positions)
    if not 1 <= count <= 3:
        raise ValueError(f'City location {location} must contain 1..3 P8 city markers')
    cities.append({'id': f'G{len(cities) + 1:03}', 'location': location, 'count': count})
for key in ('tax_per_city', 'tax_period_frames', 'garrison_per_city', 'peace_timeout_frames',
            'starting_minerals', 'starting_marines', 'start_countdown_frames'):
    if type(config[key]) is not int or config[key] <= 0:
        raise ValueError(f'{key} must be a positive integer')
if len(set(config['starting_groups'])) != 7:
    raise ValueError('Seven distinct starting groups are required')
REGION_COUNT = len(cities)
CITY_COUNT = len(marker_positions)
if sum(city['count'] for city in cities) != CITY_COUNT:
    raise ValueError('City locations must cover each marker exactly once')
locations = EUDArray([c['location'] for c in cities])
weights = EUDArray([c['count'] for c in cities])
starts = EUDArray([next(i for i, c in enumerate(cities) if c['id'] == name) for name in config['starting_groups']])
TAX = config['tax_per_city']
TAX_PERIOD = config['tax_period_frames']
GUARDS = config['garrison_per_city']
PEACE_TIMEOUT = config['peace_timeout_frames']
START_MINERALS = config['starting_minerals']
START_MARINES = config['starting_marines']
START_COUNTDOWN = config['start_countdown_frames']
INTRO_FRAMES = config['intro_frames']
SELECTION_TIMEOUT = config['selection_timeout_frames']
