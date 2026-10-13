"""유닛의 게임상 역할과 StarCraft 유닛 이름을 한곳에서 관리합니다."""
from eudplib import TrgUnit


class UnitModel:
    # 도시 마커 → 인게임 도시
    city_marker = TrgUnit("Terran Beacon")
    small_city = TrgUnit("Protoss Pylon")

    # 마린 외형을 적용하는 주둔군. 실제 Marine과 다른 유닛입니다.
    defender = TrgUnit("Zerg Broodling")
    marine = TrgUnit("Terran Marine")

    # 전군 명령에서 제외하는 일꾼·맵 유닛
    scv = TrgUnit("Terran SCV")
    drone = TrgUnit("Zerg Drone")
    probe = TrgUnit("Protoss Probe")
    map_revealer = TrgUnit("Map Revealer")
    start_location = TrgUnit("Start Location")
