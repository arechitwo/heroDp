"""병법원: 엔진 생산 대기열로 필요한 병력만 개별 훈련합니다."""
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, SetMemory, SetTo
from .unit_settings import UnitModel
from .army_camp_data import _train_button
from .nexus_data import _button, BUTTON_TABLE


SCHOOL_BUTTONS = Db(b''.join([
    _train_button(1, UnitModel.engineer, 1589),
    _train_button(2, UnitModel.light_cavalry, 1591),
    _train_button(3, UnitModel.knight, 1593),
    _button(8, 249, 0x429520, 0x4244A0, 0, 0, 1595, 0),
    _button(9, 236, 0x428530, 0x423490, 0, 0, 1596, 0),
]))


@EUDFunc
def f_init():
    address = BUTTON_TABLE + EncodeUnit(UnitModel.tactics_school) * 12
    DoActions([
        SetMemory(address, SetTo, 5),
        SetMemory(address + 4, SetTo, SCHOOL_BUTTONS),
    ])
