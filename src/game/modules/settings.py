"""Compile-time gameplay configuration; no DAT/stat or special-unit edits."""
import json
from pathlib import Path
from eudplib import EUDArray

ROOT = Path(__file__).resolve().parents[3]
config = json.loads((ROOT / 'src/data/diplomacy.json').read_text(encoding='utf-8'))
cities = json.loads((ROOT / 'src/data/city_markers.json').read_text(encoding='utf-8'))['cities']
for key in ('tax_per_city', 'tax_period_frames', 'garrison_per_city', 'peace_timeout_frames',
            'city_checks_per_frame', 'starting_minerals', 'starting_marines', 'start_countdown_frames'):
    if type(config[key]) is not int or config[key] <= 0:
        raise ValueError(f'{key} must be a positive integer')
if len(set(config['starting_groups'])) != 7:
    raise ValueError('Seven distinct starting groups are required')
CITY_COUNT = len(cities)
locations = EUDArray([c['original_location'] for c in cities])
weights = EUDArray([c['count'] for c in cities])
starts = EUDArray([next(i for i, c in enumerate(cities) if c['id'] == name) for name in config['starting_groups']])
centerX = EUDArray([c['center'][0] for c in cities])
centerY = EUDArray([c['center'][1] for c in cities])
markerOffsets = EUDArray([sum(p['count'] for p in cities[:i]) for i in range(len(cities))])
markerX = EUDArray([p[0] for city in cities for p in city['positions']])
markerY = EUDArray([p[1] for city in cities for p in city['positions']])
TAX = config['tax_per_city']
TAX_PERIOD = config['tax_period_frames']
GUARDS = config['garrison_per_city']
PEACE_TIMEOUT = config['peace_timeout_frames']
CHECKS = config['city_checks_per_frame']
START_MINERALS = config['starting_minerals']
START_MARINES = config['starting_marines']
START_COUNTDOWN = config['start_countdown_frames']
INTRO_FRAMES = config['intro_frames']
SELECTION_TIMEOUT = config['selection_timeout_frames']
