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
    capital.buildingDimensions = 1 + (1 << 16)
    capital.unitBoundsL = 15
    capital.unitBoundsT = 15
    capital.unitBoundsR = 16
    capital.unitBoundsB = 16
    capital.computerIdleOrder = 3
    capital.humanIdleOrder = 3
    capital.returnToIdleOrder = 3
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
