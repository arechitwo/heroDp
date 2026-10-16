"""Shared direct CUnit orders for EPScript and hero function-pointer callbacks."""
from eudplib import CUnit, EUDTypedFunc, f_dwwrite_epd

ORDER_MOVE = 6
ORDER_ATTACK_MOVE = 14


@EUDTypedFunc([CUnit, None, None])
def f_issue(unit, order, target_pos):
    unit.orderTargetPos = target_pos
    f_dwwrite_epd(unit + 0x5C // 4, 0)
    f_dwwrite_epd(unit + 0x7C // 4, 0)
    unit.orderState = 0
    unit.orderTimer = 0
    unit.userActionFlags = 3
    unit.orderID = order
