"""Compile-time registry of player and hero UnitGroups, all serviced every tick."""
from eudplib import EUDSwitch, EUDSwitchCase, EUDEndSwitch, EUDFunc, UnitGroup, f_bread_epd
from .settings import DEBUG_ENABLED

class DebugArmyGroup(UnitGroup):
    _fields_ = [('debug_unique', 0)]


DEFAULT_ARMIES = [(DebugArmyGroup if DEBUG_ENABLED else UnitGroup)(1700)
                 for _ in range(7)]
for group in DEFAULT_ARMIES:
    group.debug_unique_checks = (True,) if DEBUG_ENABLED else ()
PLAYER_GROUPS = [[group] for group in DEFAULT_ARMIES]
REGISTERED_GROUPS = [(player, group) for player, group in enumerate(DEFAULT_ARMIES)]


def register_hero_group(player, group):
    """Register an existing hero group during module import, before tick compiles.

    The hero controller assigns its members with group.add(epd). A member must
    belong to only one army group; this function registers the group, not units.
    """
    if type(player) is not int or not 0 <= player < 7:
        raise ValueError('Player index must be 0..6')
    if any(group is existing for groups in PLAYER_GROUPS for existing in groups):
        raise ValueError('UnitGroup is already registered')
    group.debug_unique_checks = ()  # 이 테스트는 기본 부대에 신규 등록하는 유닛 대상.
    PLAYER_GROUPS[player].append(group)
    REGISTERED_GROUPS.append((player, group))


@EUDFunc
def f_add_default(unit_epd):
    owner = f_bread_epd(unit_epd + 0x4C // 4, 0)
    if DEBUG_ENABLED:
        unique = f_bread_epd(unit_epd + 0xA4 // 4, 1)
    EUDSwitch(owner)
    for player, group in enumerate(DEFAULT_ARMIES):
        if EUDSwitchCase()(player):
            if DEBUG_ENABLED:
                group.add(unit_epd, unique)
            else:
                group.add(unit_epd)
    EUDEndSwitch()
