"""창병·경보병의 기본 명령: 저그 ID의 버로우·언버로우 버튼 제외."""
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, SetMemory, SetTo
from .unit_settings import UnitModel
from .engineer_data import _button, BUTTON_TABLE

INFANTRY_BUTTONS = Db(b''.join([
    _button(1, 228, 0x424440, 1568),  # Move
    _button(2, 229, 0x4233F0, 1569),  # Stop
    _button(3, 230, 0x424380, 1570),  # Attack
    _button(4, 'Patrol', 0x424140, 1571),
    _button(5, 255, 0x423370, 1572),  # Hold
]))


@EUDFunc
def f_init():
    for unit in (UnitModel.spearman, UnitModel.light_infantry):
        unit.baseProperty.Burrowable = False
        address = BUTTON_TABLE + EncodeUnit(unit) * 12
        DoActions([
            SetMemory(address, SetTo, 5),
            SetMemory(address + 4, SetTo, INFANTRY_BUTTONS),
        ])
