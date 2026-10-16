"""Compile-time registry of player and hero UnitGroups, all serviced every tick."""
from eudplib import EUDSwitch, EUDSwitchCase, EUDEndSwitch, EUDFunc, UnitGroup, f_bread_epd

DEFAULT_ARMIES = [UnitGroup(1700) for _ in range(7)]
PLAYER_GROUPS = [[group, UnitGroup(1700), UnitGroup(1700), UnitGroup(1700)]
                 for group in DEFAULT_ARMIES]
REGISTERED_GROUPS = [(player, group, player * 4 + slot)
                     for player, groups in enumerate(PLAYER_GROUPS)
                     for slot, group in enumerate(groups)]


@EUDFunc
def f_add_hero_member(slot, unit_epd):
    # 그룹은 고정되어 있으며 멤버만 런타임에 등록합니다. 기존 그룹과 중복 등록하지 않습니다.
    EUDSwitch(slot)
    for player, group, index in REGISTERED_GROUPS:
        if EUDSwitchCase()(index):
            group.add(unit_epd)
    EUDEndSwitch()


@EUDFunc
def f_add_default(unit_epd):
    owner = f_bread_epd(unit_epd + 0x4C // 4, 0)
    EUDSwitch(owner)
    for player, group in enumerate(DEFAULT_ARMIES):
        if EUDSwitchCase()(player):
            group.add(unit_epd)
    EUDEndSwitch()
