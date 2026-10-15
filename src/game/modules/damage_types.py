"""Three attack/defense roles using the engine's fixed-point damage table."""
import json
from pathlib import Path
from eudplib import DoActions, EUDFunc, SetMemory, SetTo


class AttackType:
    general = 3
    piercing = 2
    duel = 1


class DefenseType:
    infantry = 1
    armored = 2
    hero = 3


DAMAGE_TABLE = 0x515B84
RATIOS = json.loads((Path(__file__).resolve().parents[3] /
                    'resource/units/damage_types.json').read_text(encoding='utf-8'))


@EUDFunc
def f_init():
    actions = []
    for attack, defenses in RATIOS.items():
        for defense, percent in defenses.items():
            if type(percent) is not int or not 0 <= percent <= 200 or percent * 256 % 100:
                raise ValueError(f'Invalid exact damage ratio: {attack}/{defense}: {percent}')
            address = DAMAGE_TABLE + getattr(AttackType, attack) * 20 + 4 + getattr(DefenseType, defense) * 4
            actions.append(SetMemory(address, SetTo, percent * 256 // 100))
    DoActions(actions)
