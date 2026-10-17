"""Compile-time registry of player and hero UnitGroups, all serviced every tick."""
from eudplib import EUDSwitch, EUDSwitchCase, EUDEndSwitch, EUDFunc, UnitGroup, f_bread_epd

DEFAULT_ARMIES = [UnitGroup(1700) for _ in range(7)]
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
    PLAYER_GROUPS[player].append(group)
    REGISTERED_GROUPS.append((player, group))


@EUDFunc
def f_add_default(unit_epd):
    owner = f_bread_epd(unit_epd + 0x4C // 4, 0)
    EUDSwitch(owner)
    for player, group in enumerate(DEFAULT_ARMIES):
        if EUDSwitchCase()(player):
            group.add(unit_epd)
    EUDEndSwitch()
