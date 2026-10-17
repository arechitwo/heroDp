"""Native training queue as a persistent, free-to-edit automatic recruitment list."""
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, SetMemory, SetTo
from .unit_settings import UnitModel
from .unit_data import RECRUITMENT, TRAINING_RESET_TIME
from .nexus_data import _button, BUTTON_TABLE, BUTTON_ALWAYS, BUTTON_CAN_TRAIN, BUTTON_TRAIN, BUILDING_COSTS

SPEARMAN_COST = RECRUITMENT['spearman'][0]
INFANTRY_COST = RECRUITMENT['light_infantry'][0]
LONGBOW_COST = RECRUITMENT['longbowman'][0]
RECOVERY_REFUND = BUILDING_COSTS['recovery_camp']['minerals'] // 2


def _train_button(position, unit, tooltip, *, icon=None):
    kind = EncodeUnit(unit)
    image = kind if icon is None else EncodeUnit(icon)
    return _button(position, image, BUTTON_CAN_TRAIN, BUTTON_TRAIN,
                   kind, image, tooltip, tooltip + 1)


ARMY_BUTTONS = Db(b''.join([
    _train_button(1, UnitModel.spearman, 1574, icon=UnitModel.spearman_icon),
    _train_button(2, UnitModel.light_infantry, 1576, icon=UnitModel.light_infantry_icon),
    _train_button(3, UnitModel.longbowman, 1578, icon=UnitModel.longbowman_icon),
    # 안내 버튼: 현재 군영 버튼셋으로 돌아가므로 게임 명령은 내리지 않습니다.
    _button(7, EncodeUnit(UnitModel.army_camp), BUTTON_ALWAYS, 0x459AF0,
            0, EncodeUnit(UnitModel.army_camp), 1580, 0),
    _button(8, 249, 0x429520, 0x4244A0, 0, 0, 1581, 0),  # Rally point
    _button(9, 236, 0x428530, 0x423490, 0, 0, 1582, 0),  # Cancel last entry
]))

# 소집 요청만 대기열에 등록합니다. 영웅 추첨과 실제 생성은 후속 구현.
HERO_CHOICES = (
    (UnitModel.hero_warrior_choice, 1, 1614),
    (UnitModel.hero_archer_choice, 2, 1616),
    (UnitModel.hero_mage_choice, 3, 1618),
    (UnitModel.hero_random_choice, 4, 1620),
)
HERO_BUTTONS = Db(b''.join(
    _train_button(position, unit, tooltip)
    for unit, position, tooltip in HERO_CHOICES
) + _button(9, 236, 0x428530, 0x423490, 0, 0, 1622, 0))
RECOVERY_BUTTONS = Db(_button(
    1, 308, BUTTON_ALWAYS, 0x459AF0, 0,
    EncodeUnit(UnitModel.recovery_camp), 1623, 0))


@EUDFunc
def f_init():
    address = BUTTON_TABLE + EncodeUnit(UnitModel.army_camp) * 12
    DoActions([
        SetMemory(address, SetTo, 6),
        SetMemory(address + 4, SetTo, ARMY_BUTTONS),
    ])
    for unit, position, tooltip in HERO_CHOICES:
        unit.mineralCost = 0
        unit.gasCost = 0
        unit.supplyUsed = 0
        unit.timeCost = TRAINING_RESET_TIME
    address = BUTTON_TABLE + EncodeUnit(UnitModel.hero_hall) * 12
    DoActions([
        SetMemory(address, SetTo, 5),
        SetMemory(address + 4, SetTo, HERO_BUTTONS),
    ])
    address = BUTTON_TABLE + EncodeUnit(UnitModel.recovery_camp) * 12
    DoActions([
        SetMemory(address, SetTo, 1),
        SetMemory(address + 4, SetTo, RECOVERY_BUTTONS),
    ])
