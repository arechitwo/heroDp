"""Nested JSON resources and runtime DAT initialization for normal troops."""
import json
from pathlib import Path
from eudplib import EUDFunc, EncodeUnit, InitialWireframe, SetMemory, SetTo, TrgUnit, Weapon
from .unit_settings import Looks, UnitModel
from .damage_types import AttackType, DefenseType, AttackLabel, AttackIcon, DEFENSE_UPGRADES

RESOURCE_DIR = Path(__file__).resolve().parents[3] / 'resource/units'
BUTTON_TABLE = 0x5187E8


def _read_json(filename):
    return json.loads((RESOURCE_DIR / filename).read_text(encoding='utf-8-sig'))


COMBAT = _read_json('combat.json')
# 건물을 먼저 생성할 수 있도록 빌드 타임에만 순서를 정합니다.
DEBUG_ROSTER = tuple(getattr(UnitModel, key)
                     for key in sorted(COMBAT, key=lambda key: key != 'siege_turret'))
APPEARANCE = _read_json('appearance.json')
PROPERTIES = _read_json('properties.json')
for key, appearance in APPEARANCE.items():
    graphics = appearance.get('graphics') or {}
    source = graphics.get('wireframe_from') or graphics.get('copy_from')
    if source:
        InitialWireframe.wireframes(EncodeUnit(getattr(UnitModel, key)), EncodeUnit(source))

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
    'min_range': 'minRange', 'hits': 'damageFactor', 'targets': 'targetFlags',
    'splash.explosion': 'explosionType',
    'splash.inner': 'splashInnerRadius', 'splash.middle': 'splashMiddleRadius',
    'splash.outer': 'splashOuterRadius',
}
MOVEMENT_FIELDS = {
    'top_speed': 'topSpeed', 'acceleration': 'acceleration',
    'halt_distance': 'haltDistance', 'turn_speed': 'turnSpeed',
    'control': 'movementControl',
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

        source = (appearance.get('graphics') or {}).get('copy_from')
        if source is not None:
            donor = TrgUnit(source)
            # 실체 ID는 업그레이드용으로 유지하고 외형·음성·충돌·기본 동작을 복사.
            for member in ('baseProperty', 'groupFlags', 'availabilityFlags', 'portrait',
                           'elevation', 'movementFlags', 'rank', 'buildingDimensions',
                           'transportSpaceRequired', 'transportSpaceProvided',
                           'readySound', 'whatSoundStart', 'whatSoundEnd',
                           'pissedSoundStart', 'pissedSoundEnd', 'yesSoundStart', 'yesSoundEnd',
                           'unitBoundsL', 'unitBoundsT', 'unitBoundsR', 'unitBoundsB',
                           'computerIdleOrder', 'humanIdleOrder', 'returnToIdleOrder',
                           'attackUnitOrder', 'attackMoveOrder', 'rightClickAction'):
                setattr(unit, member, getattr(donor, member))
            unit.baseProperty.Spellcaster = False

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
            unit.armorUpgrade = DEFENSE_UPGRADES[defense_type]
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
        movement = appearance.get('movement') or {}
        movement_look = movement.get('look')
        if movement_look is not None:
            flingy = getattr(Looks, movement_look)
            for field, attribute in MOVEMENT_FIELDS.items():
                value = _value(movement, field)
                if value is not None:
                    setattr(flingy, attribute, value)
        width = _value(appearance, 'size.placement.width')
        height = _value(appearance, 'size.placement.height')
        if width is not None and height is not None:
            unit.buildingDimensions = width + (height << 16)

        for field, attribute in PROPERTY_FIELDS.items():
            value = _value(properties, field)
            if value is not None:
                if '.' in attribute:
                    parent, member = attribute.split('.')
                    setattr(getattr(unit, parent), member, value)
                else:
                    setattr(unit, attribute, value)
        hero = _value(properties, 'flags.hero')
        if hero is not None:
            unit.baseProperty.Hero = hero
        detector = _value(properties, 'vision.detector')
        if detector is not None:
            unit.baseProperty.Detector = detector

        if key != 'siege_turret':
            # Men 등 다른 그룹 플래그는 유지하고 종족 표시만 통일해 계급을 숨깁니다.
            unit.groupFlags.Zerg = False
            unit.groupFlags.Terran = False
            unit.groupFlags.Protoss = True

        # A tank's attack fields belong to its turret, while HP belongs to its body.
        weapons = properties.get('weapons') or {}
        weapon_unit = getattr(UnitModel, weapons.get('unit') or key)
        for channel, attribute in (('ground', 'groundWeapon'), ('air', 'airWeapon')):
            weapon_appearance = (appearance.get('weapons') or {}).get(channel) or {}
            projectile_look = weapon_appearance.get('look')
            if projectile_look is not None:
                getattr(weapon_unit, attribute).flingy = getattr(Looks, projectile_look)
            delivery_from = weapon_appearance.get('delivery_from')
            if delivery_from is not None:
                # 초기화 때만 발사·명중 설정을 복사. 무기 번호와 전투 수치는 유지.
                source = Weapon(delivery_from)
                target = getattr(weapon_unit, attribute)
                for member in ('behavior', 'removeAfter', 'attackAngle',
                               'launchSpin', 'forwardOffset', 'verticalOffset'):
                    setattr(target, member, getattr(source, member))
            attack_type = (combat['attack'].get(channel) or {}).get('type')
            if attack_type is not None:
                weapon = getattr(weapon_unit, attribute)
                weapon.damageType = getattr(AttackType, attack_type)
                weapon.label = getattr(AttackLabel, attack_type)
                weapon.icon = getattr(AttackIcon, attack_type)
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
