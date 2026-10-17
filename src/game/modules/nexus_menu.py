"""수도 건설 메뉴의 배치와 연결 대상. 건설 조건·비용·효과는 별도 구현합니다."""
from typing import NamedTuple

from .unit_settings import UnitModel


class BuildingButton(NamedTuple):
    role: str
    page: int
    position: int  # 각 페이지의 3×3 버튼 위치: 1..9.
    unit: object
    name: str
    tooltip: int


BUILDINGS = [
    BuildingButton('metropolis', 1, 1, UnitModel.metropolis, '대도시', 1548),
    BuildingButton('army_camp', 1, 4, UnitModel.army_camp, '군영', 1550),
    BuildingButton('drill_hall', 1, 5, UnitModel.drill_hall, '연무관', 1552),
    BuildingButton('military_workshop', 1, 7, UnitModel.military_workshop, '군비 공방', 1554),
    BuildingButton('recovery_camp', 1, 8, UnitModel.recovery_camp, '회복 군막', 1556),
    BuildingButton('tactics_school', 2, 1, UnitModel.tactics_school, '병법원', 1558),
    BuildingButton('knight_hall', 2, 2, UnitModel.knight_hall, '기사단 회관', 1560),
    BuildingButton('hero_hall', 2, 3, UnitModel.hero_hall, '영웅 소집소', 1562),
]

BUILDING_UNITS = tuple(item.unit for item in BUILDINGS)

# 시작 시 제거하는 도시·수도 비콘의 버튼셋을 건설 페이지용으로 예약합니다.
# 유닛을 생성하거나 선택한 수도의 종류를 바꾸지 않고 표시할 버튼셋만 전환합니다.
PAGE_ONE_UNIT = UnitModel.city_marker
PAGE_TWO_UNIT = UnitModel.nexus_marker
PAGE_ONE_TOOLTIP = 1564
PAGE_TWO_TOOLTIP = 1565
RETURN_TOOLTIP = 1624
