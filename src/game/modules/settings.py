"""Compile-time gameplay configuration; no DAT/stat or special-unit edits."""
import json
from pathlib import Path
import struct
from eudplib import EUDArray, GetChkTokenized, unProxy
from .unit_settings import UnitModel
from .map_data import START_LOCATIONS

ROOT = Path(__file__).resolve().parents[3]
config = json.loads((ROOT / 'src/data/diplomacy.json').read_text(encoding='utf-8'))
chk = GetChkTokenized()
unit_data = chk.getsection('UNIT')
marker_positions = [struct.unpack_from('<HH', unit_data, offset + 4)
                    for offset in range(0, len(unit_data), 36)
                    if struct.unpack_from('<H', unit_data, offset + 8)[0] == unProxy(UnitModel.city_marker)
                    and unit_data[offset + 16] == 7]
location_data = chk.getsection('MRGN')
start_counts = []
claimed_markers = set()
for location in START_LOCATIONS:
    left, top, right, bottom = struct.unpack_from('<4I', location_data, (location - 1) * 20)
    contained = {i for i, (x, y) in enumerate(marker_positions)
                 if left <= x <= right and top <= y <= bottom}
    if not 1 <= len(contained) <= 3 or claimed_markers & contained:
        raise ValueError(f'Start location {location} must contain 1..3 distinct P8 city markers')
    claimed_markers.update(contained)
    start_counts.append(len(contained))
for key in ('tax_per_city', 'tax_period_frames', 'garrison_per_city', 'peace_timeout_frames',
            'starting_minerals', 'starting_marines', 'start_countdown_frames'):
    if type(config[key]) is not int or config[key] <= 0:
        raise ValueError(f'{key} must be a positive integer')
CITY_COUNT = len(marker_positions)
START_CITY_COUNTS = EUDArray(start_counts)
TAX = config['tax_per_city']
TAX_PERIOD = config['tax_period_frames']
GUARDS = config['garrison_per_city']
PEACE_TIMEOUT = config['peace_timeout_frames']
START_MINERALS = config['starting_minerals']
START_MARINES = config['starting_marines']
START_COUNTDOWN = config['start_countdown_frames']
INTRO_FRAMES = config['intro_frames']
SELECTION_TIMEOUT = config['selection_timeout_frames']
DEBUG_ENABLED = config.get('debug_enabled', False)
DEBUG_PATTERNS = tuple((command, len(prefix.encode('utf-8'))) for command, prefix in (
    (1, '디버그 돈 '), (2, '디버그 가스 '), (3, '디버그 자원 '),
    (4, '디버그 마린 '), (5, '디버그 SCV '), (6, '디버그 세금타이머 '),
    (7, '디버그 주둔군타이머 '), (8, '디버그 시작타이머 '),
    (9, '디버그 값 '), (10, '디버그 개수 '), (11, '디버그 창병 '),
    (11, '디버그 질럿 ')))
