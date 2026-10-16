"""Common starting lord DAT; combat identity stays separate from mutable hero slots."""
from eudplib import EUDFunc
from .unit_settings import UnitModel, UpgradeModel
from .damage_types import DefenseType, AttackType, AttackLabel, AttackIcon


@EUDFunc
def f_init():
    lord = UnitModel.lord
    lord.nameString = '\x04영주 구이 몬태그'
    lord.maxHp = 8000 * 256
    lord.hasShield = True
    lord.maxShield = 1
    lord.armor = 30
    lord.sizeType = DefenseType.hero
    lord.armorUpgrade = UpgradeModel.hero_armor
    lord.baseProperty.Hero = True
    lord.baseProperty.Spellcaster = False
    lord.supplyUsed = 0
    lord.groundWeapon.damage = 200
    lord.groundWeapon.damageBonus = 1
    lord.groundWeapon.damageType = AttackType.general
    lord.groundWeapon.label = AttackLabel.general
    lord.groundWeapon.icon = AttackIcon.general
    lord.groundWeapon.cooldown = 30
