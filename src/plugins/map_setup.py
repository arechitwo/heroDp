"""Prepare playable slots, city units and engine locations in the compiled map only."""
import json
from pathlib import Path
import struct
from eudplib import GetChkTokenized
from eudplib.core.mapdata.playerinfo import init_player_info

root = Path(settings['project_root'])
cities = json.loads((root / 'src/data/city_markers.json').read_text(encoding='utf-8'))['cities']
config = json.loads((root / 'src/data/diplomacy.json').read_text(encoding='utf-8'))
chkt = GetChkTokenized()
chkt.setsection('OWNR', bytes([6]*7 + [5] + [0]*4))
chkt.setsection('IOWN', bytes([6]*7 + [5] + [0]*4))
chkt.setsection('SIDE', bytes([0]*8 + [0]*4))
chkt.setsection('PUNI', bytes([1])*5700)
locations = bytearray(255*20)
units = bytearray(chkt.getsection('UNIT'))
# Keep beacons in UNIT: runtime conversion follows Pylon DAT initialization.
# Only the compiled output gets engine locations. The source SCX remains clear.
for city in cities:
    x, y = city['center']
    struct.pack_into('<IIIIHH', locations, (city['original_location']-1)*20,
                     x-160, y-160, x+160, y+160, 0, 0)
struct.pack_into('<IIIIHH', locations, 63*20, 0, 0, 8192, 8192, 0, 0)
for player in range(7):
    # 240..246: synchronized mouse targets. 247..253: fixed start locations.
    struct.pack_into('<IIIIHH', locations, (239+player)*20, 0, 0, 32, 32, 0, 0)
    city = next(c for c in cities if c['id'] == config['starting_groups'][player])
    x, y = city['center']
    struct.pack_into('<IIIIHH', locations, (246+player)*20, x-96, y-96, x+96, y+96, 0, 0)
    record = bytearray(36)
    struct.pack_into('<IHHH', record, 0, 10000+player, x, y, 214)
    record[16] = player
    units.extend(record)
# 254: command selection; 255: MSQC temporary spawn region.
struct.pack_into('<IIIIHH', locations, 254*20, 0, 0, 256, 256, 0, 0)
chkt.setsection('MRGN', bytes(locations))
chkt.setsection('UNIT', bytes(units))
init_player_info(chkt)
