"""28 contiguous hero slots; runtime function pointers contain no UnitGroup arguments."""
from eudplib import (CUnit, EUDVArray, EUDFunc, EUDTypedFunc, EUDFuncPtr,
                     EUDIf, EUDElse, EUDEndIf)
from .unit_orders import f_issue, ORDER_ATTACK_MOVE, ORDER_MOVE

SLOT_COUNT = 28
SkillFunc = EUDFuncPtr(4, 0)  # slot, hero EPD, target position, target EPD
MemberFunc = EUDFuncPtr(2, 0)  # slot, army member EPD
HEROES = EUDVArray(SLOT_COUNT, CUnit)()
GENERATIONS = EUDVArray(SLOT_COUNT)()
SKILLS = EUDVArray(SLOT_COUNT)()  # 함수 포인터 값 저장, 호출할 때 SkillFunc.cast
MEMBERS = EUDVArray(SLOT_COUNT)()  # 함수 포인터 값 저장, 호출할 때 MemberFunc.cast
SKILL_PENDING = EUDVArray(SLOT_COUNT)()
SKILL_POSITIONS = EUDVArray(SLOT_COUNT)()
SKILL_TARGETS = EUDVArray(SLOT_COUNT, CUnit)()
COMMANDS = EUDVArray(SLOT_COUNT)()
COMMAND_POSITIONS = EUDVArray(SLOT_COUNT)()


@EUDFunc
def f_lord_skill(slot, hero_epd, target_pos, target_epd):
    # 영주의 기본 화염 범위 공격은 엔진 패시브. 액티브 효과는 아직 정하지 않았습니다.
    SKILL_PENDING[slot] = 0


@EUDFunc
def f_command_member(slot, member_epd):
    unit = CUnit.cast(member_epd)
    if EUDIf()(COMMANDS[slot] == 1):
        f_issue(unit, ORDER_ATTACK_MOVE, COMMAND_POSITIONS[slot])
    if EUDElse()():
        f_issue(unit, ORDER_MOVE, COMMAND_POSITIONS[slot])
    EUDEndIf()


LORD_SKILL = SkillFunc(f_lord_skill)
COMMAND_MEMBER = MemberFunc(f_command_member)


@EUDTypedFunc([None, CUnit, SkillFunc, MemberFunc])
def f_bind(slot, unit, skill, member):
    HEROES[slot] = unit
    GENERATIONS[slot] = unit.uniquenessIdentifier
    SKILLS[slot] = skill
    MEMBERS[slot] = member
    SKILL_PENDING[slot] = 0
    COMMANDS[slot] = 0


@EUDFunc
def f_request_skill(slot, target_pos, target_epd):
    # 입력 동기화 뒤 호출합니다. 빈 슬롯은 tick에서 바로 건너뜁니다.
    SKILL_POSITIONS[slot] = target_pos
    SKILL_TARGETS[slot] = target_epd
    SKILL_PENDING[slot] = 1


@EUDFunc
def f_request_command(slot, command, target_pos):
    COMMANDS[slot] = command  # 1 부대 공격, 2 부대 이동
    COMMAND_POSITIONS[slot] = target_pos
