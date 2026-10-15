"""Native training queue as a persistent, free-to-edit automatic recruitment list."""
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, SetMemory, SetTo
from .unit_settings import UnitModel
from .unit_data import RECRUITMENT, PROPERTIES
from .nexus_data import _button, BUTTON_TABLE, BUTTON_ALWAYS, BUTTON_CAN_TRAIN, BUTTON_TRAIN

SPEARMAN_COST = RECRUITMENT['spearman'][0]
INFANTRY_COST = RECRUITMENT['light_infantry'][0]
LONGBOW_COST = RECRUITMENT['longbowman'][0]
TRAINING_RESET_TIME = min(PROPERTIES[key]['production']['time']
                          for key in ('spearman', 'light_infantry', 'longbowman'))


def _train_button(position, unit, tooltip, *, icon=None):
    kind = EncodeUnit(unit)
    image = kind if icon is None else EncodeUnit(icon)
    return _button(position, image, BUTTON_CAN_TRAIN, BUTTON_TRAIN,
                   kind, kind, tooltip, tooltip + 1)


ARMY_BUTTONS = Db(b''.join([
    _train_button(1, UnitModel.spearman, 1574, icon=UnitModel.spearman_icon),
    _train_button(2, UnitModel.light_infantry, 1576),
    _train_button(3, UnitModel.longbowman, 1578),
    # 안내 버튼: 현재 군영 버튼셋으로 돌아가므로 게임 명령은 내리지 않습니다.
    _button(7, EncodeUnit(UnitModel.army_camp), BUTTON_ALWAYS, 0x459AF0,
            0, EncodeUnit(UnitModel.army_camp), 1580, 0),
    _button(8, 249, 0x429520, 0x4244A0, 0, 0, 1581, 0),  # Rally point
    _button(9, 236, 0x428530, 0x423490, 0, 0, 1582, 0),  # Cancel last entry
]))


@EUDFunc
def f_init():
    address = BUTTON_TABLE + EncodeUnit(UnitModel.army_camp) * 12
    DoActions([
        SetMemory(address, SetTo, 6),
        SetMemory(address + 4, SetTo, ARMY_BUTTONS),
    ])
