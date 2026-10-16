"""군비 공방: 실체 유닛 ID에 연결된 네이티브 사거리·이동 업그레이드."""
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, EncodeUpgrade, Icon, SetMemory, SetTo, f_bwrite, unProxy
from .unit_settings import UnitModel, UpgradeModel
from .knight_hall_data import RESEARCH
from .nexus_data import _button, BUTTON_TABLE

UPGRADE_LIMITS = 0x58D088
UPGRADES = (
    ('infantry_range', UpgradeModel.infantry_range, Icon("U-238 Shells"), 1601, 1),
    ('infantry_speed', UpgradeModel.infantry_speed, Icon("Metabolic Boost"), 1603, 2),
    ('longbow_range', UpgradeModel.longbow_range, Icon("Singularity Charge"), 1605, 3),
)
WORKSHOP_BUTTONS = Db(b''.join(
    _button(position, unProxy(icon), 0x429450, 0x423310,
            EncodeUpgrade(upgrade), EncodeUpgrade(upgrade), tooltip, tooltip + 1)
    for role, upgrade, icon, tooltip, position in UPGRADES
) + _button(9, 236, 0x428900, 0x4232F0, 0, 0, 1607, 0))


@EUDFunc
def f_init():
    for role, upgrade, icon, tooltip, position in UPGRADES:
        data = RESEARCH[role]
        upgrade.mineralCostBase = data['minerals']
        upgrade.mineralCostFactor = 0
        upgrade.gasCostBase = data['gas']
        upgrade.gasCostFactor = 0
        upgrade.timeCostBase = data['time']
        upgrade.timeCostFactor = 0
        upgrade.maxLevel = 1
        upgrade.label = 1607 + position
        upgrade.icon = icon
        upgrade.race = 2
        for player in range(7):
            f_bwrite(UPGRADE_LIMITS + 46 * player + EncodeUpgrade(upgrade), 1)
            upgrade[player] = 0
    address = BUTTON_TABLE + EncodeUnit(UnitModel.military_workshop) * 12
    DoActions([
        SetMemory(address, SetTo, 4),
        SetMemory(address + 4, SetTo, WORKSHOP_BUTTONS),
    ])
