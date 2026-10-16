"""SCV command card: native Terran construction and repair, without proxy orders."""
import struct

from eudplib import Db, DoActions, EUDFunc, EncodeTech, EncodeUnit, SetMemory, SetTo
from .unit_settings import TechModel, UnitModel

BUTTON_TABLE = 0x5187E8
BUTTON_ALWAYS = 0x4282D0
BUTTON_CAN_BUILD = 0x428E60
BUTTON_TERRAN_BUILD = 0x423EB0
BUTTON_HAS_TECH = 0x4294E0


def _button(position, icon, action, tooltip, *, condition=BUTTON_ALWAYS,
            parameter=0, condition_parameter=None, disabled=0):
    return struct.pack('<HHIIHHHH', position, icon, condition, action,
                       parameter if condition_parameter is None else condition_parameter,
                       parameter, tooltip, disabled)


ENGINEER_BUTTONS = Db(b''.join([
    _button(1, 228, 0x424440, 1568),  # Move
    _button(2, 229, 0x4233F0, 1569),  # Stop
    _button(3, 230, 0x424380, 1570),  # Attack
    _button(4, 231, 0x424140, 1571),  # Patrol
    _button(5, 255, 0x423370, 1572),  # Hold
    _button(6, 236, 0x423BD0, 1573),  # Native repair
    _button(7, EncodeUnit(UnitModel.siege_turret), BUTTON_TERRAN_BUILD, 1566,
            condition=BUTTON_HAS_TECH,
            condition_parameter=EncodeTech(TechModel.siege_construction),
            parameter=EncodeUnit(UnitModel.siege_turret),
            disabled=1567),
]))


@EUDFunc
def f_init():
    address = BUTTON_TABLE + EncodeUnit(UnitModel.engineer) * 12
    DoActions([
        SetMemory(address, SetTo, 7),
        SetMemory(address + 4, SetTo, ENGINEER_BUTTONS),
    ])
