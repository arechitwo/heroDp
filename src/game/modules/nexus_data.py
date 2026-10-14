"""Capital DAT and two scoped button sets, based on FranceDp's capital flow."""
import struct
from eudplib import Db, DoActions, EUDFunc, EncodeUnit, InitialWireframe, SetMemory, SetTo
from .unit_settings import Looks, UnitModel

BUTTON_TABLE = 0x5187E8
STATUS_TABLE = 0x5193A0
UNIT_STATUS_UPDATE = 4344192
UNIT_STATUS_DRAW = 4353872
BUTTON_ALWAYS = 0x4282D0
BUTTON_CAN_TRAIN = 0x428E60
BUTTON_TRAIN = 0x4234B0
BUTTON_WARP_BUILDING = 0x423DD0


def _button(position, icon, condition, action, condition_unit, action_unit,
            enabled_tooltip, disabled_tooltip):
    return struct.pack('<HHIIHHHH', position, icon, condition, action,
                       condition_unit, action_unit, enabled_tooltip, disabled_tooltip)


CAPITAL_BUTTONS = Db(_button(5, EncodeUnit(UnitModel.barracks), BUTTON_ALWAYS,
                            BUTTON_WARP_BUILDING, EncodeUnit(UnitModel.barracks),
                            EncodeUnit(UnitModel.barracks), 630, 631))
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
    capital.baseProperty = 0x44000800  # FranceDp single-entity remote capital
    capital.buildingDimensions = 16 + (16 << 16)
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
    gate.nameString = '\x05훈련소'
    gate.maxHp = 4800 * 256
    gate.armor = 50
    gate.hasShield = False
    gate.maxShield = 0
    gate.mineralCost = 100
    gate.gasCost = 0
    gate.timeCost = 280
    gate.supplyUsed = 0
    gate.buildingDimensions = 32 + (32 << 16)  # FranceDp 게이트웨이 배치 크기

    signal = UnitModel.nexus_signal
    signal.nameString = '\x04수도 소환'
    signal.mineralCost = 0
    signal.gasCost = 0
    signal.supplyUsed = 0
    signal.timeCost = 9999  # Queue is consumed by summonFromCity before completion.

    DoActions([
        SetMemory(BUTTON_TABLE + EncodeUnit(capital) * 12, SetTo, 1),
        SetMemory(BUTTON_TABLE + EncodeUnit(capital) * 12 + 4, SetTo, CAPITAL_BUTTONS),
        SetMemory(BUTTON_TABLE + EncodeUnit(UnitModel.small_city) * 12, SetTo, 1),
        SetMemory(BUTTON_TABLE + EncodeUnit(UnitModel.small_city) * 12 + 4, SetTo, CITY_BUTTONS),
    ])
