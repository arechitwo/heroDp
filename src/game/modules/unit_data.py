"""Compile-time CSV data and runtime DAT initialization for normal troops."""
import csv
from pathlib import Path
from eudplib import EUDFunc, EncodeUnit, SetMemory, SetTo
from .unit_settings import UnitModel

RESOURCE_DIR = Path(__file__).resolve().parents[3] / 'resource/units'
BUTTON_TABLE = 0x5187E8


def _read_table(filename):
    """Read editable constants; blank cells retain the map's existing DAT value."""
    with (RESOURCE_DIR / filename).open(encoding='utf-8-sig', newline='') as stream:
        result = {}
        for row in csv.DictReader(stream):
            key = row.pop('unit').strip()
            result[key] = {
                field: value.strip() if field == 'weapon_unit' else int(value.strip(), 0)
                for field, value in row.items() if value and value.strip()
            }
        return result


COMBAT = _read_table('combat.csv')
APPEARANCE = _read_table('appearance.csv')
PROPERTIES = _read_table('properties.csv')

# These are gameplay values, separate from the DAT mineralCost production field.
RECRUITMENT = {key: (row['recruit_cost'], row['recruit_count'])
               for key, row in PROPERTIES.items()}

APPEARANCE_FIELDS = {
    'flingy': 'flingy', 'portrait': 'portrait',
    'bounds_left': 'unitBoundsL', 'bounds_top': 'unitBoundsT',
    'bounds_right': 'unitBoundsR', 'bounds_bottom': 'unitBoundsB',
    'ready_sound': 'readySound',
    'what_sound_start': 'whatSoundStart', 'what_sound_end': 'whatSoundEnd',
    'pissed_sound_start': 'pissedSoundStart', 'pissed_sound_end': 'pissedSoundEnd',
    'yes_sound_start': 'yesSoundStart', 'yes_sound_end': 'yesSoundEnd',
}
PROPERTY_FIELDS = {
    'mineral_cost': 'mineralCost', 'gas_cost': 'gasCost',
    'supply_used': 'supplyUsed', 'time_cost': 'timeCost',
    'base_property': 'baseProperty', 'seek_range': 'seekRange',
    'sight_range': 'sightRange', 'size_type': 'sizeType',
    'armor_upgrade': 'armorUpgrade',
    'ground_weapon': 'groundWeapon', 'air_weapon': 'airWeapon',
    'computer_idle_order': 'computerIdleOrder', 'human_idle_order': 'humanIdleOrder',
    'return_idle_order': 'returnToIdleOrder', 'attack_unit_order': 'attackUnitOrder',
    'attack_move_order': 'attackMoveOrder', 'right_click_action': 'rightClickAction',
    'transport_space': 'transportSpaceRequired',
    'max_ground_hits': 'maxGroundHits', 'max_air_hits': 'maxAirHits',
    'dont_become_guard': 'dontBecomeGuard',
    'ignore_strategic_suicide': 'ignoreStrategicSuicideMissions',
}
WEAPON_FIELDS = {
    'damage': 'damage', 'bonus': 'damageBonus', 'range': 'maxRange',
    'cooldown': 'cooldown', 'upgrade': 'upgrade',
}


@EUDFunc
def f_init():
    # Python loops below expand at build time; there is no in-game CSV parser.
    for key, combat in COMBAT.items():
        unit = getattr(UnitModel, key)
        appearance = APPEARANCE[key]
        properties = PROPERTIES[key]

        # TrgUnit syntax: this changes DAT maximum HP, not any live CUnit's HP.
        if 'hp' in combat:
            unit.maxHp = combat['hp'] * 256
        if 'shield' in combat:
            unit.hasShield = combat['shield'] > 0
            unit.maxShield = combat['shield']
        if 'armor' in combat:
            unit.armor = combat['armor']
        if 'kill_score' in combat:
            unit.killScore = combat['kill_score']

        for field, attribute in APPEARANCE_FIELDS.items():
            if field in appearance:
                setattr(unit, attribute, appearance[field])
        if 'placement_width' in appearance and 'placement_height' in appearance:
            unit.buildingDimensions = appearance['placement_width'] + (appearance['placement_height'] << 16)

        for field, attribute in PROPERTY_FIELDS.items():
            if field in properties:
                setattr(unit, attribute, properties[field])
        if 'is_hero' in properties:
            unit.baseProperty.Hero = properties['is_hero']

        # A tank's attack fields belong to its turret, while HP belongs to its body.
        weapon_unit = getattr(UnitModel, properties.get('weapon_unit', key))
        for channel, attribute in (('ground', 'groundWeapon'), ('air', 'airWeapon')):
            fields = [(field, target) for field, target in WEAPON_FIELDS.items()
                      if f'{channel}_{field}' in combat]
            if fields:
                weapon = getattr(weapon_unit, attribute)
                for field, target in fields:
                    setattr(weapon, target, combat[f'{channel}_{field}'])

        if properties.get('clear_buttons', 0):
            address = BUTTON_TABLE + EncodeUnit(unit) * 12
            SetMemory(address, SetTo, 0)
            SetMemory(address + 4, SetTo, 0)
