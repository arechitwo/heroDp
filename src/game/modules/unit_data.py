"""Nested JSON resources and runtime DAT initialization for normal troops."""
import json
from pathlib import Path
from eudplib import EUDFunc, EncodeUnit, SetMemory, SetTo
from .unit_settings import Looks, UnitModel
from .damage_types import AttackType, DefenseType

RESOURCE_DIR = Path(__file__).resolve().parents[3] / 'resource/units'
BUTTON_TABLE = 0x5187E8


def _read_json(filename):
    return json.loads((RESOURCE_DIR / filename).read_text(encoding='utf-8-sig'))


COMBAT = _read_json('combat.json')
APPEARANCE = _read_json('appearance.json')
PROPERTIES = _read_json('properties.json')

# These are gameplay values, separate from the DAT mineralCost production field.
RECRUITMENT = {key: (row['recruitment']['cost'], row['recruitment']['count'])
               for key, row in PROPERTIES.items()}

COMBAT_FIELDS = {
    'defense.armor': 'armor', 'defense.size_type': 'sizeType',
    'defense.armor_upgrade': 'armorUpgrade', 'score.kill': 'killScore',
}
APPEARANCE_FIELDS = {
    'graphics.flingy': 'flingy', 'graphics.portrait': 'portrait',
    'size.bounds.left': 'unitBoundsL', 'size.bounds.top': 'unitBoundsT',
    'size.bounds.right': 'unitBoundsR', 'size.bounds.bottom': 'unitBoundsB',
    'sounds.ready': 'readySound',
    'sounds.what.start': 'whatSoundStart', 'sounds.what.end': 'whatSoundEnd',
    'sounds.pissed.start': 'pissedSoundStart', 'sounds.pissed.end': 'pissedSoundEnd',
    'sounds.yes.start': 'yesSoundStart', 'sounds.yes.end': 'yesSoundEnd',
}
PROPERTY_FIELDS = {
    'production.minerals': 'mineralCost', 'production.gas': 'gasCost',
    'production.supply': 'supplyUsed', 'production.time': 'timeCost',
    'flags.base_property': 'baseProperty',
    'vision.seek_range': 'seekRange', 'vision.sight_range': 'sightRange',
    'weapons.ground': 'groundWeapon', 'weapons.air': 'airWeapon',
    'orders.computer_idle': 'computerIdleOrder', 'orders.human_idle': 'humanIdleOrder',
    'orders.return_idle': 'returnToIdleOrder', 'orders.attack_unit': 'attackUnitOrder',
    'orders.attack_move': 'attackMoveOrder', 'orders.right_click': 'rightClickAction',
    'transport.space_required': 'transportSpaceRequired',
    'weapons.max_ground_hits': 'maxGroundHits', 'weapons.max_air_hits': 'maxAirHits',
    'flags.dont_become_guard': 'dontBecomeGuard',
    'flags.ignore_strategic_suicide': 'ignoreStrategicSuicideMissions',
}
WEAPON_FIELDS = {
    'damage': 'damage', 'bonus': 'damageBonus', 'range': 'maxRange',
    'cooldown': 'cooldown', 'upgrade': 'upgrade',
}


def _value(data, path):
    """Compile-time lookup. Missing keys and null retain the existing DAT value."""
    for key in path.split('.'):
        if data is None:
            return None
        data = data.get(key)
    return int(data, 0) if isinstance(data, str) else data


@EUDFunc
def f_init():
    # Python loops below expand at build time; JSON is not read in game.
    for key, combat in COMBAT.items():
        unit = getattr(UnitModel, key)
        appearance = APPEARANCE[key]
        properties = PROPERTIES[key]

        # TrgUnit syntax: this changes DAT maximum HP, not any live CUnit's HP.
        hp = _value(combat, 'defense.hp')
        shield = _value(combat, 'defense.shield')
        if hp is not None:
            unit.maxHp = hp * 256
        if shield is not None:
            unit.hasShield = shield > 0
            unit.maxShield = shield
        defense_type = combat['defense'].get('type')
        if defense_type is not None:
            unit.sizeType = getattr(DefenseType, defense_type)
        for field, attribute in COMBAT_FIELDS.items():
            value = _value(combat, field)
            if value is not None:
                setattr(unit, attribute, value)

        name = appearance.get('name')
        if name is not None:
            unit.nameString = name
        for field, attribute in APPEARANCE_FIELDS.items():
            value = _value(appearance, field)
            if value is not None:
                setattr(unit, attribute, value)
        look = (appearance.get('graphics') or {}).get('look')
        if look is not None:
            unit.flingy = getattr(Looks, look)
        width = _value(appearance, 'size.placement.width')
        height = _value(appearance, 'size.placement.height')
        if width is not None and height is not None:
            unit.buildingDimensions = width + (height << 16)

        for field, attribute in PROPERTY_FIELDS.items():
            value = _value(properties, field)
            if value is not None:
                setattr(unit, attribute, value)
        hero = _value(properties, 'flags.hero')
        if hero is not None:
            unit.baseProperty.Hero = hero

        # A tank's attack fields belong to its turret, while HP belongs to its body.
        weapons = properties.get('weapons') or {}
        weapon_unit = getattr(UnitModel, weapons.get('unit') or key)
        for channel, attribute in (('ground', 'groundWeapon'), ('air', 'airWeapon')):
            attack_type = (combat['attack'].get(channel) or {}).get('type')
            if attack_type is not None:
                getattr(weapon_unit, attribute).damageType = getattr(AttackType, attack_type)
            fields = [(target, _value(combat, f'attack.{channel}.{field}'))
                      for field, target in WEAPON_FIELDS.items()
                      if _value(combat, f'attack.{channel}.{field}') is not None]
            if fields:
                weapon = getattr(weapon_unit, attribute)
                for target, value in fields:
                    setattr(weapon, target, value)

        if _value(properties, 'buttons.clear'):
            address = BUTTON_TABLE + EncodeUnit(unit) * 12
            SetMemory(address, SetTo, 0)
            SetMemory(address + 4, SetTo, 0)
