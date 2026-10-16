"""기사단 회관의 공성 진지술: 미사용 Tank Siege Mode 연구를 재사용."""
import json
from pathlib import Path
from eudplib import Db, DoActions, EUDFunc, EncodeTech, EncodeUnit, SetMemory, SetTo, f_bwrite
from .unit_settings import TechModel, UnitModel
from .nexus_data import _button, BUTTON_TABLE

RESEARCH = json.loads((Path(__file__).resolve().parents[3] /
                       'resource/research.json').read_text(encoding='utf-8'))
TECH_AVAILABLE = 0x58CE24
SIEGE_TECH = EncodeTech(TechModel.siege_construction)

HALL_BUTTONS = Db(b''.join([
    _button(1, EncodeUnit(UnitModel.siege_turret), 0x429500, 0x423350,
            SIEGE_TECH, SIEGE_TECH, 1597, 1598),
    _button(9, 236, 0x4288E0, 0x423330, 0, 0, 1599, 0),
]))


@EUDFunc
def f_init():
    tech = TechModel.siege_construction
    data = RESEARCH['siege_construction']
    tech.mineralCost = data['minerals']
    tech.gasCost = data['gas']
    tech.timeCost = data['time']
    tech.energyCost = 0
    tech.label = 1600
    tech.icon = EncodeUnit(UnitModel.siege_turret)
    tech.race = 2  # Protoss 연구 건물
    for player in range(7):
        f_bwrite(TECH_AVAILABLE + 24 * player + SIEGE_TECH, 1)
        tech[player] = 0
    address = BUTTON_TABLE + EncodeUnit(UnitModel.knight_hall) * 12
    DoActions([
        SetMemory(address, SetTo, 2),
        SetMemory(address + 4, SetTo, HALL_BUTTONS),
    ])
