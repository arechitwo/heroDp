"""포지(연무관): 질럿 ID 창병의 네이티브 Leg Enhancements 연구."""
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, EncodeUpgrade, Icon, SetMemory, SetTo, f_bwrite, unProxy
from .unit_settings import UnitModel, UpgradeModel
from .knight_hall_data import RESEARCH
from .nexus_data import _button, BUTTON_TABLE

UPGRADE_LIMITS = 0x58D088
SPEARMAN_SPEED = EncodeUpgrade(UpgradeModel.spearman_speed)
SPEED_ICON = Icon("Leg Enhancements")
DRILL_BUTTONS = Db(b''.join([
    _button(1, unProxy(SPEED_ICON), 0x429450, 0x423310,
            SPEARMAN_SPEED, SPEARMAN_SPEED, 1611, 1612),
    _button(9, 236, 0x428900, 0x4232F0, 0, 0, 1607, 0),
]))


@EUDFunc
def f_init():
    upgrade = UpgradeModel.spearman_speed
    data = RESEARCH['spearman_speed']
    upgrade.mineralCostBase = data['minerals']
    upgrade.mineralCostFactor = 0
    upgrade.gasCostBase = data['gas']
    upgrade.gasCostFactor = 0
    upgrade.timeCostBase = data['time']
    upgrade.timeCostFactor = 0
    upgrade.maxLevel = 1
    upgrade.label = 1613
    upgrade.icon = SPEED_ICON
    upgrade.race = 2
    for player in range(7):
        f_bwrite(UPGRADE_LIMITS + 46 * player + SPEARMAN_SPEED, 1)
        upgrade[player] = 0
    address = BUTTON_TABLE + EncodeUnit(UnitModel.drill_hall) * 12
    DoActions([
        SetMemory(address, SetTo, 2),
        SetMemory(address + 4, SetTo, DRILL_BUTTONS),
    ])
