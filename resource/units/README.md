# 기본 병종 CSV

키 `unit`은 `UnitModel`의 속성 이름입니다. 숫자 유닛 ID는 키로 사용하지 않습니다.
현재 대상은 FranceDp `normalUnits_v2.csv`의 병종·수치를 참고한 다음 5종입니다.

| unit | 병종 | StarCraft 기반 유닛 |
|---|---|---|
| spearman | 창병 | Protoss Zealot |
| light_infantry | 보병 | Terran Marine |
| light_cavalry | 경기병 | Terran Vulture |
| siege_unit | 공성병 | Terran Siege Tank (Tank Mode) |
| knight | 기사 | Zerg Ultralisk |

`siege_unit_weapon`은 공성병의 포탑 참조이며 별도 병종이나 특수 유닛이 아닙니다.
`marine`은 기존 시작·디버그 코드 호환을 위한 `light_infantry` 별칭입니다.
특수 유닛 데이터는 아직 만들지 않습니다. 도시·주둔군은 기존 `unit_dat.eps`에서 관리합니다.

| 파일 | 관리 항목 |
|---|---|
| combat.csv | HP·실드·방어력·지상/공중 피해·추가 피해·사거리·공격 주기·공격 업그레이드·점수 |
| appearance.csv | flingy·초상화·배치 크기·충돌 경계·응답 사운드 |
| properties.csv | 모집 비용/개수·DAT 생산 비용·인구·생산 시간·무기 담당 유닛·기본 플래그·명령 AI·무기 연결·기타 속성 |

빈 칸은 기존 맵/DAT 값을 유지합니다. `0`은 실제로 0을 적용합니다.
외형 파일의 초기 항목은 비워 두어 원본 외형을 유지합니다. CSV는 UTF-8로 저장합니다.

- HP는 화면에 보이는 정수 체력이며 적용할 때만 256을 곱합니다.
- 사거리·배치 크기·충돌 경계는 픽셀, 공격 주기·생산 시간은 원시 엔진 값입니다.
- `placement_width`, `placement_height`는 함께 입력합니다. 좌우상하 경계는 각각 입력합니다.
- `supply_used`는 DAT 값이므로 인구 1은 2입니다. `seek_range`, `sight_range`는 타일 단위입니다.
- `base_property` 등 비트 플래그는 `0x...` 표기를 지원합니다. 불리언 항목은 0/1입니다.
- `recruit_cost`는 디플로메시 모집 비용, `recruit_count`는 한 번에 모집할 개수입니다.
  생산 시스템에서 `unit_data.RECRUITMENT`를 참조할 수 있으며 아직 모집 기능은 구현하지 않습니다.
- `mineral_cost`는 StarCraft DAT 생산 가격입니다. FranceDp의 기본 병종은 직접 생산하지 않으므로
  초기값을 0, `time_cost`를 9999로 두고 모집 비용은 따로 보존합니다.
- `weapon_unit`은 공격 값의 대상 UnitModel 키입니다. 공성병은 `siege_unit_weapon`을 사용합니다.
- `ground_weapon`·`air_weapon`은 무기 ID입니다. 비어 있으면 해당 유닛의 기존 무기를 사용합니다.
  포탑의 무기 연결 자체를 변경하려면 추후 포탑 속성 행을 추가하는 구조가 필요합니다.
- 무기를 공유하는 유닛은 무기 수치도 함께 바뀝니다. 독립 무기가 필요하면 무기 연결을 분리해야 합니다.

CSV는 빌드 때 Python이 읽고 `unit_data.init()`이 초기화 트리거를 만듭니다.
필드와 TrgUnit 멤버의 연결은 `src/game/modules/unit_data.py`에 있습니다.
FranceDp의 CSV 로더·특수 공격/방어 배율·라벨·특수 유닛 시스템은 가져오지 않았습니다.
`size_type`·`armor_upgrade` 같은 선택 항목은 기존 StarCraft DAT 값으로 입력합니다.
