"""유닛의 게임상 역할과 StarCraft 유닛 이름을 한곳에서 관리합니다."""
from eudplib import Flingy, Tech, TrgUnit, Upgrade


class TechModel:
    siege_construction = Tech("Tank Siege Mode")


class UpgradeModel:
    spearman_speed = Upgrade("Metabolic Boost")
    infantry_speed = Upgrade("Muscular Augments")
    infantry_range = Upgrade("Grooved Spines")
    longbow_range = Upgrade("Singularity Charge")
    infantry_armor = Upgrade("Terran Infantry Armor")
    armored_armor = Upgrade("Terran Vehicle Plating")
    hero_armor = Upgrade("Protoss Armor")
    garrison_armor = Upgrade("Terran Ship Plating")  # 주둔군 전용. 중갑 방어 아이콘·설명 사용.


class Looks:
    nexus = Flingy("Nexus")
    broodling = Flingy("Broodling")
    marine = Flingy("Marine")
    ghost = Flingy("Ghost")
    ultralisk = Flingy("Ultralisk")
    scv = Flingy("SCV")
    siege_hit = Flingy("Arclite Shock Cannon Hit")


class UnitModel:
    # 기본 병종. JSON의 최상위 키는 이 속성 이름을 사용합니다.
    spearman = TrgUnit("Zerg Zergling")
    spearman_icon = TrgUnit("Zerg Broodling")
    light_infantry = TrgUnit("Zerg Hydralisk")
    light_infantry_icon = TrgUnit("Terran Marine")
    light_cavalry = TrgUnit("Terran Vulture")
    longbowman = TrgUnit("Protoss Dragoon")
    longbowman_icon = TrgUnit("Terran Ghost")
    engineer = TrgUnit("Terran SCV")
    siege_turret = TrgUnit("Terran Missile Turret")
    siege_requirement = TrgUnit("Map Revealer")  # 공성 진지술 연구 완료 체크용
    knight = TrgUnit("Zerg Ultralisk")

    # 도시 마커 → 인게임 도시
    city_marker = TrgUnit("Terran Beacon")
    small_city = TrgUnit("Protoss Pylon")
    # 수도 건설 메뉴. 병법원은 기존 게이트웨이 역할을 이어받습니다.
    metropolis = TrgUnit("Protoss Arbiter Tribunal")
    army_camp = TrgUnit("Protoss Robotics Facility")
    drill_hall = TrgUnit("Protoss Forge")
    military_workshop = TrgUnit("Protoss Cybernetics Core")
    recovery_camp = TrgUnit("Protoss Shield Battery")
    tactics_school = TrgUnit("Protoss Gateway")
    knight_hall = TrgUnit("Protoss Citadel of Adun")
    hero_hall = TrgUnit("Protoss Templar Archives")
    barracks = tactics_school  # 도시 점령 시 함께 넘기는 기존 역할 이름.
    nexus_marker = TrgUnit("Protoss Beacon")
    nexus_unit = TrgUnit("Khaydarin Crystal Formation")
    nexus_wireframe = TrgUnit("Terran Command Center")  # FranceDp 수도 선택창 외형
    nexus_signal = TrgUnit("Kakaru (Twilight Critter)")  # 일반 더미 유닛: 수도 소환 요청
    nexus_requirement = TrgUnit("Mineral Field (Type 1)")

    # 마린 외형을 적용하는 주둔군. 실제 Marine과 다른 유닛입니다.
    defender = TrgUnit("Terran Civilian")
    marine = light_infantry
    debug_marine = TrgUnit("Jim Raynor (Marine)")

    # 전군 명령에서 제외하는 일꾼·맵 유닛
    scv = engineer
    drone = TrgUnit("Zerg Drone")
    probe = TrgUnit("Protoss Probe")
    map_revealer = TrgUnit("Map Revealer")
    start_location = TrgUnit("Start Location")
