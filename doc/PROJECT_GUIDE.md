# FranceDp Project Guide

> 이 문서는 `BuildData_FanceDp` 레퍼런스의 기존 구조 설명입니다.
> 신규 NoE3s 진입점은 `src/game/main.eps`이며, 신규 빌드 방법은 루트 `README.md`를 기준으로 합니다.

작성 기준: 2026-07-27 현재 코드 기준. 오래된 기획 문서보다 `BuildData_FanceDp/eudplibData/TriggerEditor` 아래의 EPScript와 CSV를 우선한다.

## 프로젝트 개요

FranceDp는 스타크래프트 유즈맵 디플로메시 프로젝트다. 핵심 루프는 도시를 점령하고, 도시 수입으로 병력을 생산하며, 특수 지역을 확보해 일반 유닛 생산을 특수 유닛으로 치환하는 구조다.

현재 구현은 EUD Editor / EPScript 기반이며, `.eps`는 PostScript 이미지가 아니라 텍스트 코드다. 인게임 출력 문자열 중 일부는 인코딩이 섞여 있으므로 파일을 통째로 재저장하기보다 필요한 부분만 수정하는 편이 안전하다.

## 주요 경로

| 경로 | 역할 |
|---|---|
| `FanceDp.e3s` | EUD Editor 프로젝트 파일 |
| `src/main.eps` | 루트 진입점 사본 |
| `BuildData_FanceDp/eudplibData/TriggerEditor/main.eps` | 빌드 데이터 쪽 진입점 |
| `BuildData_FanceDp/eudplibData/TriggerEditor/modules/*.eps` | 실제 게임 로직 모듈 |
| `BuildData_FanceDp/eudplibData/TriggerEditor/modules/unit_setting_dict.py` | 유닛, 건물, 라벨, 지역 데이터 로더 |
| `BuildData_FanceDp/eudplibData/TriggerEditor/modules/resource/*.csv` | 밸런스와 지역 데이터의 원본 테이블 |
| `BuildData_FanceDp/eudplibData/DataEditor.py` | EUD Editor 데이터 편집 산출물 |
| `doc/unit_balance_design.md` | 현재 유닛 밸런스 의도 설명 |
| `doc/special_unit_final_v6.md` | 현재 19개 특수 지역 설계 설명 |

`BuildData_FanceDp` 아래 파일은 EUD Editor 빌드 산출물과 수동 작성 코드가 섞여 있다. 변경 전에 어떤 파일이 생성물인지 확인하고, `__pycache__`, `__epspy__`, 백업 파일은 추적 대상에서 제외하는 것이 맞다.

## 실행 흐름

`main.eps`는 다음 모듈을 불러온다.

```eps
import modules.Diplomacy as diplomacy;
import modules.CityData as city;
import modules.Income as income;
import modules.Chat as chat;
import modules.UnitsData as unit;
import modules.Debug as debug;
import modules.System as system;
import modules.Commander as commander;
```

초기화는 `onPluginStart()`에서 수행된다.

1. `randomize()` 실행
2. 게임 속도 메모리 설정
3. `diplomacy.init()`로 초기 동맹, P8 시야, 색상 설정
4. `unit.init()`로 유닛 라벨, CSV 데이터, 특수 지역, 수비대 방어 보정 초기화
5. `city.init()`로 도시/수도/훈련소/강화소용 맵 배치 치환
6. `income.init()` 호출
7. 카운트다운 타이머 180 설정

매 트리거 루프는 `beforeTriggerExec()`에서 돈다.

1. 디버그 시작 처리
2. 인트로, 게임 모드 선택, 국가 선택 진행
3. 킬스코어 기반 경험치와 가스 보상 갱신
4. 도시 전투와 점령 상태 처리
5. 외교 동맹 맵과 공유 시야 갱신
6. 특수 지역 UI와 특수 유닛 해금 상태 처리
7. 수도 명령, F키 명령, 생산/건설 처리
8. 도시 수입 지급
9. 특수 지역 순회 단축키와 외부 플레이어 유닛 정리
10. 채팅 명령 처리

`afterTriggerExec()`에서는 외교 타이머를 90으로 재설정하고 채팅 입력 파싱 후처리를 한다.

## 모듈별 책임

| 모듈 | 책임 |
|---|---|
| `System.eps` | 인트로, 게임 모드/국가 선택, 경험치/레벨 보상, 상태 메시지, 특수 지역 카메라 이동, P12 유닛 정리 |
| `System_helper.eps` | 국가 선택 상태, 팀 모드 배정, 국가 지급 보조 함수 |
| `Diplomacy.eps` | 동맹 상태 메모리 관리, 상호 동맹 확정, 팀 모드 동맹 강제, 공유 시야 펄스 |
| `Diplomacy_helper.eps` | 동맹 바이트 조작, 색상 변경, 외교 알림 출력 |
| `CityData.eps` | 초기 맵 유닛을 도시/수도/건물로 치환, 소도시 전투 상태, 수도 건설 처리 |
| `CityData_helper.eps` | 위치 내 최다 점유 플레이어 계산 |
| `UnitsData.eps` | 유닛 라벨, 특수 지역 생성, 특수 유닛 전환, 생산소/강화소/방어타워 처리, 업그레이드 동기화 |
| `UnitData_helper.eps` | 유닛을 factories로 지정, 특수 유닛 소유자 덱 관리, 일반 유닛을 특수 유닛으로 변환 |
| `Commander.eps` | 수도의 건설/기술 명령을 프록시 일꾼 생성 방식으로 실행, F키 명령 처리 |
| `Income.eps` | 타이머 0일 때 도시 수에 따른 미네랄 수입 지급, 생산 지출 표시 |
| `Chat.eps` | 채팅 패턴 파싱, 자원/유닛/영토 양도, 쿨다운, 디버그 채팅 연동 |
| `Debug.eps` | 개발용 채팅 명령, 클릭 유닛 검사, 단독 테스트 시작 처리 |

## 데이터 구조

`unit_setting_dict.py`는 `modules/resource`의 CSV를 읽어 런타임 딕셔너리로 만든다.

| CSV | 로딩 대상 | 내용 |
|---|---|---|
| `normalUnits_v2.csv` | `normalUnits` | 일반 병종 5종: 창병, 경보병, 경기병, 공성병, 기사 |
| `specialUnits_v2.csv` | `specialUnits` | 특수 유닛 19종의 스탯과 비용 |
| `supportUnits_v2.csv` | `supportUnits` | 의무관, 스파이, 열기구, 주둔군 |
| `buildings.csv` | `buildings` | 수도, 도시, 훈련소, 강화소, 타워, 외교 시설 등 |
| `specialRegions.csv` | `specialRegions` | 특수 지역 19곳의 위치, 원본 유닛, 특수 유닛, 선택 가능 여부 |
| `upgradeCosts.csv` | 현재 미사용 | 업그레이드 비용 테이블 후보. 로더는 있으나 현재 `upgradeCosts` 로딩은 주석 처리됨 |

현재 실제로 쓰는 일반 병종은 5종이다.

| id | 역할 | 기본 SC 유닛 | 비용 | 타입 |
|---|---|---|---:|---|
| `spearman` | 창병 | Protoss Zealot | 20 | Standard / Standard armor |
| `light_infantry` | 경보병 | Terran Marine | 20 | Standard / Standard armor |
| `light_cavalry` | 경기병 | Terran Vulture | 35 | Standard / Standard armor |
| `siege_unit` | 공성병 | Terran Siege Tank | 45 | Siege / Standard armor |
| `knight` | 기사 | Zerg Ultralisk | 70 | Knight / Knight armor |

특수 지역은 `specialRegions.csv` 기준으로 19곳이다. `selectable=1`인 7곳은 시작/선택 거점 성격이고, 나머지 12곳은 점령으로 특수 유닛 생산 전환을 여는 요충지다.

## 핵심 시스템

### 도시와 점령

`CityData.init()`는 맵에 배치된 특정 유닛 번호를 실제 게임 오브젝트로 치환한다. 예를 들어 기존 마커 유닛을 P8 소유의 `small_city`, `nexus_unit`, `barracks`, `upgradeCenter` 등으로 바꾸고 관련 `UnitGroup`에 넣는다.

`CityData.runWar()`는 `smallCityGroup`을 순회하면서 도시가 공격받는지 확인한다. 공격 시작 시 주둔군을 생성하고 도시 HP를 낮춘다. 전투가 끝나면 주둔군을 제거하고 도시 HP를 복구한다. 수도 건설은 소도시의 빌드 큐를 감지해 `nexus_unit`을 생성하는 방식이다.

### 특수 유닛

`UnitsData.initSpecialRegion()`은 `specialRegions.csv`를 순회하며 특수 지역 표시 유닛을 만들고, 지역 이름과 버튼 텍스트 TBL을 준비한다. 지역 소유자가 바뀌면 `checkUserSpecialUnit()`이 일반 유닛과 특수 유닛의 매핑을 소유자별 덱에 추가/삭제한다.

훈련소 생산은 `runBarraksUnitGroup()`에서 처리한다. 생산 큐의 유닛을 읽고, 자원이 충분하면 `helper.getSpecialUnit(player, trainUnit)`을 통해 일반 유닛을 현재 소유 특수 지역에 맞는 유닛으로 바꿔 생성한다. 실제 비용은 일반 유닛 비용 기준으로 차감된다.

### 생산과 건설

플레이어는 수도에서 건설 명령을 넣고, `Commander.eps`가 이를 프록시 일꾼 명령으로 변환한다. 허용된 건물은 훈련소, 지원 본부, 강화소, 방어타워 계열이다. 방어타워는 도시 근처 조건을 확인한 뒤 `photo_cannon`을 거쳐 실제 `tower` 여러 기로 변환된다.

### 수입과 자원

`Income.distributeIncome()`은 카운트다운 타이머가 0일 때 실행된다. `System.printCurrentMsg()`가 캐시한 도시 수(`pylonCount_`)에 `buildings["small_city"]["tax"]`를 곱해 미네랄을 지급한다. 생산 비용은 `UnitsData.mineralCostDeathUnit` 데스값에 누적했다가 수입 주기에 표시 후 초기화한다.

킬스코어는 `System.updateExp()`에서 경험치로 전환된다. 경험치가 일정량 누적되면 가스도 지급된다. 레벨업 보상은 쉴드/공방 업그레이드 보정으로 들어간다.

### 외교

`Diplomacy.init()`는 게임 시작 시 인간 플레이어끼리 동맹으로 시작하게 만들고 P8은 컴퓨터/중립 방어자 역할로 둔다. 일반 모드에서는 양쪽이 동맹을 켠 상태가 500틱 안에 맞물려야 동맹이 확정되고, 한쪽이 끊으면 즉시 해제된다. 팀 모드에서는 `System_helper.playerTeam_` 기준으로 동맹이 강제된다.

공유 시야는 매 프레임 항상 켜는 방식이 아니라 카운트다운 타이머 펄스에 맞춰 갱신한다. 타이머는 `afterTriggerExec()`의 `diplomacy.setTimer()`에서 90으로 되돌린다.

### 채팅 명령

`Chat.eps`는 패턴 파싱 결과를 `chatAction_`에 넣고, 자원 양도, 유닛 양도, 영토 양도를 처리한다. 각 기능은 플레이어별 쿨다운 배열을 가진다. 팀 모드에서는 같은 팀 여부 검사가 끼어든다.

## 변경할 때 보는 순서

1. 게임 루프를 바꾸려면 `main.eps`의 호출 순서를 먼저 확인한다.
2. 유닛/건물 수치를 바꾸려면 CSV를 수정하고 `unit_setting_dict.py` 로더가 해당 컬럼을 읽는지 확인한다.
3. 특수 지역을 바꾸려면 `specialRegions.csv`, `specialUnits_v2.csv`, `UnitModel`, `UnitName`, `RegionName`을 함께 맞춘다.
4. 생산 로직을 바꾸려면 `UnitsData.runBarraksUnitGroup()`과 `UnitData_helper.getSpecialUnit()`을 같이 본다.
5. 도시 점령/수도/주둔군을 바꾸려면 `CityData.eps`와 `buildings.csv`를 같이 본다.
6. 국가 선택이나 팀 모드는 `System.eps`와 `System_helper.eps`를 같이 본다.
7. 외교 버그는 `Diplomacy.eps`의 `allyMap`, `allyExpireTick`, `teamModeActive_` 흐름부터 본다.

## 문서 유지 원칙

`doc`의 문서는 현재 코드 이해에 직접 필요한 것만 남긴다.

- 현재 코드 구조 설명은 이 파일을 우선한다.
- 유닛 수치 의도는 `unit_balance_design.md`를 참고한다.
- 특수 유닛 배치 의도는 `special_unit_final_v6.md`를 참고한다.
- 실제 값은 항상 CSV와 EPScript를 최종 기준으로 본다.
- `development_plan`, `handover`, `special_unit_final`처럼 과거 단계의 계획/초안 문서는 다시 만들지 않는다.
