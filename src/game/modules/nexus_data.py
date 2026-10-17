"""Capital DAT, main construction menu, and two scoped building pages."""
import struct
import json
from pathlib import Path
from eudplib import Db, DoActions, EUDFunc, EncodeIcon, EncodeUnit, InitialWireframe, SetMemory, SetTo
from .unit_settings import Looks, UnitModel, UpgradeModel
from .damage_types import DefenseType
from . import settings as cfg
from .nexus_menu import (BUILDINGS, PAGE_ONE_UNIT, PAGE_TWO_UNIT,
                         PAGE_ONE_TOOLTIP, PAGE_TWO_TOOLTIP, RETURN_TOOLTIP)

BUTTON_TABLE = 0x5187E8
STATUS_TABLE = 0x5193A0
UNIT_STATUS_UPDATE = 4344192
UNIT_STATUS_DRAW = 4353872
BUTTON_ALWAYS = 0x4282D0
BUTTON_CAN_TRAIN = 0x428E60
BUTTON_TRAIN = 0x4234B0
BUTTON_WARP_BUILDING = 0x423DD0
BUTTON_CHANGE_PAGE = 0x459AF0
BUILDING_COSTS = json.loads((Path(__file__).resolve().parents[3] /
                            'resource/buildings.json').read_text(encoding='utf-8'))


def _button(position, icon, condition, action, condition_unit, action_unit,
            enabled_tooltip, disabled_tooltip):
    return struct.pack('<HHIIHHHH', position, icon, condition, action,
                       condition_unit, action_unit, enabled_tooltip, disabled_tooltip)


def _building_buttons(page):
    return b''.join(
        _button(item.position, EncodeUnit(item.unit),
                BUTTON_CAN_TRAIN if item.role in (
                    'tactics_school', 'drill_hall', 'military_workshop', 'knight_hall'
                ) else BUTTON_ALWAYS,
                BUTTON_WARP_BUILDING, EncodeUnit(item.unit), EncodeUnit(item.unit),
                item.tooltip, item.tooltip + 1)
        for item in BUILDINGS if item.page == page
    )


CAPITAL_BUTTONS = Db(_button(
    7, EncodeIcon('Protoss Basic Buildings'), BUTTON_ALWAYS, BUTTON_CHANGE_PAGE,
    0, EncodeUnit(PAGE_ONE_UNIT), PAGE_ONE_TOOLTIP, 0) + _button(
    8, EncodeIcon('Protoss Advanced Buildings'), BUTTON_ALWAYS, BUTTON_CHANGE_PAGE,
    0, EncodeUnit(PAGE_TWO_UNIT), PAGE_TWO_TOOLTIP, 0))
RETURN_BUTTON = _button(
    9, 236, BUTTON_ALWAYS, BUTTON_CHANGE_PAGE, 0, EncodeUnit(UnitModel.nexus_unit),
    RETURN_TOOLTIP, 0)
CAPITAL_PAGE_ONE_BUTTONS = Db(_building_buttons(1) + RETURN_BUTTON)
CAPITAL_PAGE_TWO_BUTTONS = Db(_building_buttons(2) + RETURN_BUTTON)
CITY_BUTTONS = Db(_button(7, 154, BUTTON_CAN_TRAIN, BUTTON_TRAIN,
                         EncodeUnit(UnitModel.nexus_signal),
                         EncodeUnit(UnitModel.nexus_signal), 1049, 1050))

InitialWireframe.wirefram(EncodeUnit(UnitModel.nexus_unit), EncodeUnit(UnitModel.nexus_wireframe))


@EUDFunc
def f_init():
    capital = UnitModel.nexus_unit
    capital.flingy = Looks.nexus
    capital.nameString = '\x04수도'
    capital.maxHp = 6500 * 256
    capital.hasShield = True
    capital.maxShield = 500
    capital.armor = 50
    capital.sizeType = DefenseType.armored
    capital.armorUpgrade = UpgradeModel.armored_armor
    capital.baseProperty = 0x44000800  # FranceDp single-entity remote capital
    capital.buildingDimensions = 1 + (1 << 16)
    capital.unitBoundsL = 48
    capital.unitBoundsT = 48
    capital.unitBoundsR = 48
    capital.unitBoundsB = 48
    capital.computerIdleOrder = 156
    capital.humanIdleOrder = 23  # Nothing
    capital.returnToIdleOrder = 23
    capital.attackUnitOrder = 23
    capital.attackMoveOrder = 23
    capital.rightClickAction = 5
    capital.ignoreStrategicSuicideMissions = True
    capital.dontBecomeGuard = True  # 내부 AI 플래그 3
    capital.groupFlags = 0x14  # Protoss + Building
    capital.availabilityFlags = 0x1CF
    capital.sightRange = 11
    capital.portrait = 60
    capital.groundWeapon = 130
    capital.airWeapon = 130
    capital.supplyUsed = 0
    capital.mineralCost = 100
    capital.gasCost = 0
    capital.killScore = 25
    # FranceDp의 수도(168) 상태 정보: 건물 생산창 대신 유닛 정보창.
    DoActions([
        SetMemory(STATUS_TABLE + EncodeUnit(capital) * 12 + 4, SetTo, UNIT_STATUS_UPDATE),
        SetMemory(STATUS_TABLE + EncodeUnit(capital) * 12 + 8, SetTo, UNIT_STATUS_DRAW),
    ])

    gate = UnitModel.barracks
    gate.maxHp = 4800 * 256
    gate.armor = 50
    gate.sizeType = DefenseType.armored
    gate.armorUpgrade = UpgradeModel.armored_armor
    gate.hasShield = True
    gate.maxShield = 1
    gate.timeCost = 280
    gate.supplyUsed = 0
    gate.buildingDimensions = 128 + (96 << 16)  # 원본 게이트웨이: 4×3타일

    for item in BUILDINGS:
        item.unit.nameString = '\x04' + item.name
        item.unit.sizeType = DefenseType.armored
        item.unit.armorUpgrade = UpgradeModel.armored_armor
        if item.role != 'metropolis':
            cost = BUILDING_COSTS[item.role]
            item.unit.mineralCost = cost['minerals']
            item.unit.gasCost = cost['gas']

    metropolis = UnitModel.metropolis
    metropolis.mineralCost = cfg.METROPOLIS_COST
    metropolis.gasCost = 0
    metropolis.timeCost = cfg.METROPOLIS_BUILD_FRAMES
    metropolis.supplyProvided = 0
    metropolis.sizeType = DefenseType.armored
    metropolis.baseProperty.RequiresPsi = True
    # 배치 크기와 충돌 범위는 Arbiter Tribunal의 기본 DAT 값을 유지합니다.

    signal = UnitModel.nexus_signal
    signal.nameString = '\x04수도 소환'
    signal.mineralCost = 0
    signal.gasCost = 0
    signal.supplyUsed = 0
    signal.timeCost = 9999  # Queue is consumed by summonFromCity before completion.

    DoActions([
        SetMemory(BUTTON_TABLE + EncodeUnit(metropolis) * 12, SetTo, 0),
        SetMemory(BUTTON_TABLE + EncodeUnit(metropolis) * 12 + 4, SetTo, 0),
        SetMemory(BUTTON_TABLE + EncodeUnit(capital) * 12, SetTo, 2),
        SetMemory(BUTTON_TABLE + EncodeUnit(capital) * 12 + 4, SetTo, CAPITAL_BUTTONS),
        SetMemory(BUTTON_TABLE + EncodeUnit(PAGE_ONE_UNIT) * 12, SetTo, 6),
        SetMemory(BUTTON_TABLE + EncodeUnit(PAGE_ONE_UNIT) * 12 + 4, SetTo, CAPITAL_PAGE_ONE_BUTTONS),
        SetMemory(BUTTON_TABLE + EncodeUnit(PAGE_TWO_UNIT) * 12, SetTo, 4),
        SetMemory(BUTTON_TABLE + EncodeUnit(PAGE_TWO_UNIT) * 12 + 4, SetTo, CAPITAL_PAGE_TWO_BUTTONS),
        SetMemory(BUTTON_TABLE + EncodeUnit(UnitModel.small_city) * 12, SetTo, 1),
        SetMemory(BUTTON_TABLE + EncodeUnit(UnitModel.small_city) * 12 + 4, SetTo, CITY_BUTTONS),
    ])
