
## 파일 타입 안내

- 이 프로젝트의 .eps 파일은 EPScript(EUD Editor 스크립트) 텍스트 코드이며, PostScript 이미지가 아니다.
- .eps 파일은 항상 일반 텍스트로 취급하고 Read/Edit 도구를 정상적으로 사용한다.
- Read 도구가 바이너리로 오인하더라도, `cat` 이나 텍스트 모드로 강제 읽어서 Edit(str_replace)로 부분 수정할 것. Python 스크립트로 전체 재작성하지 말 것.

## EUD 코드 작성 규칙

- 사용자가 별도로 요청하지 않으면 테스트를 만들거나 실행하지 않는다. 별도 코드 검증·검사용 빌드·린트·diff 검사도 수행하지 않는다. 사용자가 맵 빌드나 산출물을 요청하면 해당 빌드만 실행한다.

- 플레이어 슬롯·테란 종족·시작 위치·정적 로케이션은 `maps/base.scx`에 직접 저장한다. 도시별 고정 로케이션이나 도시 정보 JSON은 만들지 않는다. 도시 수는 UNIT 비콘에서 읽고 시작 거점만 시작 위치 로케이션을 사용한다.
- 로케이션은 `modules/map_data.py`의 `class Loc`에서 `EncodeLocation("맵에 저장한 이름")`으로 선언하고 EPScript에서도 역할 이름으로 참조한다. MSQC 마우스는 플레이어 순서, 선택 거점 영역은 선택지 순서대로 연속 슬롯을 유지한다. 선택 거점은 플레이어 번호가 아니라 지명을 사용하며 실제 Start Location 유닛과 구분한다. MSQC 변경 시 `main.eds` 번호도 함께 맞춘다.

- 알려진 메모리 주소의 0 여부는 읽어서 비교하지 말고 `Memory`/`MemoryEPD` 조건으로 직접 검사한다. 필요하면 `!`로 부정한다.
- 컴파일 타임 주소·EPD 상수 이름은 대문자로 작성한다.
- 유닛은 `modules/unit_settings.py`의 class enum `UnitModel`에서 `TrgUnit("StarCraft 유닛 이름")`으로 선언하고 게임 코드에서 역할 이름으로 참조한다. 유닛 ID 숫자를 반복해서 직접 쓰지 않는다.
- 유닛 종류를 여러 `||` 조건으로 나열하지 않는다. `epdswitch(epd + 0x64 / 4, 0xFF)`와 `case` 분기를 사용하며 하위 바이트 마스크를 명시한다.
- 도시 CUnit은 생성 직후 `EUDVArray(..., CUnit)()`에 저장한다. 매 틱 전체 도시를 처리하며 분할 검사 또는 전체 유닛 순회 후 도시 번호 역검색을 하지 않는다.
- 플레이어마다 전체 유닛을 다시 순회하지 않는다. 필요한 유닛을 등록하고 저장한 CUnit 또는 UnitGroup으로 순회한다.
- UnitGroup의 전군·부대 명령에 트리거 `Order()`를 쓰지 않는다. 저장한 CUnit의 목표 좌표·명령 상태·명령 ID를 직접 설정한다. 공통 함수는 `modules.unit_orders.issue`이며 이동 6, 어택땅 14를 사용한다.
- UnitGroup은 매 틱 `entry.dying`으로 죽은 항목을 제거한다. 영웅별 부대도 이 수명 관리 규칙을 적용한다.
- 군대는 플레이어별·영웅별 UnitGroup으로 분리한다. 전군 명령은 해당 플레이어에 등록된 모든 그룹에 적용하고, 명령 유무와 관계없이 모든 그룹을 매 틱 순회해 죽은 유닛을 정리한다.
- 인게임 도시 HP는 CUnit.hp에 직접 대입하지 않고 `ModifyUnitHitPoints`로 변경한다. 직접 대입은 불꽃/이미지 처리 누락으로 게임이 종료될 수 있다는 사용자 설명에 따른 규칙이다. DAT 최대 체력 설정은 별개다.
- `Loc.city_capture`는 원본 맵에서 320×320 크기로 고정한다. 도시 좌표에 `Loc.city_point`를 `setloc`으로 옮긴 뒤 `MoveLocation(Loc.city_capture, UnitModel.map_revealer, P9, Loc.city_point)`로 이동한다. P9의 Map Revealer는 생성하지 않는다.
- 자주 읽는 플레이어 ID 배열은 `EUDVArray(8, TrgPlayer)()`, 수치 배열은 `EUDVArray(...)()`를 사용한다. 플레이어 ID가 아닌 값에 TrgPlayer 타입을 붙이지 않는다.
- 빌드가 실패하면 자동으로 후속 수정을 진행하지 말고 사용자에게 오류와 해결 방향을 질문한다.
- Python의 런타임 함수는 `f_` 접두사를 붙이고, EPScript에서 호출할 때는 `f_`를 떼고 쓴다. `playerexist` 등 기존 호환성 예외를 일반 함수에 임의로 적용하지 않는다. 컴파일 타임 목록은 상수 데이터로 직접 순회한다.
