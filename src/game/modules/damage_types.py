"""Three attack/defense roles using the engine's fixed-point damage table."""
import json
from pathlib import Path
from eudplib import DoActions, EUDFunc, Icon, SetMemory, SetTo
from .unit_settings import UpgradeModel


class AttackType:
    general = 3
    piercing = 2
    duel = 1


class DefenseType:
    infantry = 1
    armored = 2
    hero = 3


class AttackLabel:
    general = 1586
    piercing = 1587
    duel = 1588


class AttackIcon:
    general = Icon("Infantry Weapons")
    piercing = Icon("Vehicle Weapons")
    duel = Icon("Psi/Warp Blades")


DEFENSE_UPGRADES = {
    'infantry': UpgradeModel.infantry_armor,
    'armored': UpgradeModel.armored_armor,
    'hero': UpgradeModel.hero_armor,
}
DEFENSE_DISPLAY = (
    (UpgradeModel.infantry_armor, Icon("Infantry Armor"), 1583),
    (UpgradeModel.armored_armor, Icon("Vehicle Armor"), 1584),
    (UpgradeModel.hero_armor, Icon("Ground Armor"), 1585),
    (UpgradeModel.garrison_armor, Icon("Infantry Armor"), 1583),
)


DAMAGE_TABLE = 0x515B84
RATIOS = json.loads((Path(__file__).resolve().parents[3] /
                    'resource/units/damage_types.json').read_text(encoding='utf-8'))


@EUDFunc
def f_init():
    for upgrade, icon, label in DEFENSE_DISPLAY:
        upgrade.icon = icon
        upgrade.label = label
    actions = []
    for attack, defenses in RATIOS.items():
        for defense, percent in defenses.items():
            if type(percent) is not int or not 0 <= percent <= 200:
                raise ValueError(f'Invalid damage ratio: {attack}/{defense}: {percent}')
            address = DAMAGE_TABLE + getattr(AttackType, attack) * 20 + 4 + getattr(DefenseType, defense) * 4
            # 엔진은 1/256 단위이므로 가장 가까운 값으로 반올림합니다.
            actions.append(SetMemory(address, SetTo, (percent * 256 + 50) // 100))
    DoActions(actions)
