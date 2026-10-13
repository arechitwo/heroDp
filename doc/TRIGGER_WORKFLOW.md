# 코드 기반 트리거 개발

## 진입점과 적용 순서

`src/game/main.eps`가 게임 진입점입니다. 신규 시스템은 `src/game/modules/*.eps`에 작성하고
`main.eps`에서 `import modules.모듈이름 as 별칭;`으로 불러옵니다.
`onPluginStart()`는 초기화, `beforeTriggerExec()`는 매 트리거 루프, `afterTriggerExec()`는 후처리에 사용합니다.

루트 `main.eds`는 Git으로 관리하는 실제 빌드 레시피입니다. 순서는 다음과 같습니다.

1. `src/plugins/map_setup.py`: 컴파일 대상 맵의 슬롯·도시·엔진 로케이션 설정
2. `src/plugins/data_loader.py`: 생성된 TBL·RequireData 적용
3. `chatEvent`: 시작 거점 선택 채팅 감지
4. `MSQC`: 채팅과 시작 UI·전군 명령의 키·마우스 동기화
5. `src/game/main.eps`: 신규 게임 트리거

게임에 진입하면 `onPluginStart()`에서 `unitDat.init()`으로 파일런·주둔군 DAT를 설정한 뒤
`cities.init()`에서 비콘을 파일런으로 바꿉니다. 빌드된 SCX의 배치 유닛은 여전히 비콘입니다.

기존 EUD Editor의 DataEditor.py, ExtraDataEditor.py, .e3s는 빌드에 사용하지 않습니다.
레퍼런스 폴더가 없어도 JSON과 코드만으로 정상 빌드됩니다.

## 빌드

```powershell
python build_map.py --check
python build_map.py
```

`--check`는 레시피·플러그인 경로와 JSON의 실제 바이너리 생성 가능 여부를 확인합니다.
정상 빌드는 `main.eds`를 읽고 실행별 `build/<시각>/data/`에 바이너리를 만든 뒤,
경로를 해석한 `map.eds`로 일회성 컴파일합니다. 최종 결과는 `dist/NoE3s.scx`입니다.

euddraft로 레시피를 직접 실행하려면 먼저 다음 순서로 실행합니다.

```powershell
python build_map.py --prepare
C:/repo/programs/euddraft0.10.2.5/euddraft.exe main.eds
```

직접 실행은 프로젝트 루트에서 하며 입력·출력·진입점은 `main.eds` 값을 사용합니다.
런처의 `config/build.json` 값과 CLI 오버라이드는 런처 빌드에만 적용됩니다.
JSON을 바꾼 뒤에는 `--prepare`를 다시 실행해야 직접 빌드에 반영됩니다.

## custom_tbl.json

`src/data/custom_tbl.json`에서 TBL을 편집합니다. 현재 1547개 항목은 FranceDp의 데이터 스냅샷입니다.
`enabled: false`이므로 신규 맵에 적용되지 않습니다. 적용하려면 `true`로 변경합니다.

- `encoding`: 현재 `cp949`.
- `entries`: 1부터 연속되는 TBL ID. `text` 또는 `hex` 중 하나를 사용합니다.
- `text`: JSON 표준 제어문자 표기 사용. 색상은 `\u0004`, 줄바꿈은 `\n`, 내부 NUL은 `\u0000`.
- `hex`: CP949로 해석되지 않는 원본 바이트를 그대로 보존합니다. 바꾸려면 `hex`를 삭제하고 `text`를 작성합니다.
- `copy_capacity_bytes`: 현재 42564. 원본 런타임 버퍼에 복사하는 방식이므로 용량을 임의로 늘리지 않습니다.

생성물은 `custom_txt.tbl`이며 uint16 항목 수, uint16 오프셋 테이블, NUL로 끝나는 바이트 문자열로 구성합니다.
내부 NUL도 보존하므로 유닛 이름·툴팁 복합 항목을 손실 없이 재생성합니다.
런타임에서는 기존 레퍼런스와 같이 `0x6D5A30`의 포인터가 가리키는 버퍼에 복사합니다.
전체 스냅샷을 켜면 FranceDp 문자열 전체가 적용됩니다. 신규 게임 문자열로 편집한 뒤 켜세요.

## require_data.json

`src/data/require_data.json`은 FranceDp의 완전한 요구 조건 스냅샷입니다.
`enabled: false`가 기본이며, `true`로 바꾸면 요구 조건 전체를 적용합니다.

- `data_words`: RequireData 바이너리의 uint16 워드 배열. 명령·피연산자·종료 코드가 포함된 저수준 바이트코드입니다.
- `offset_tables.units`: 유닛 228개 (`0x660A70`).
- `offset_tables.upgrades`: 업그레이드 60개 (`0x6558C0`).
- `offset_tables.tech_research`: 기술 연구 44개 (`0x656198`).
- `offset_tables.tech_use`: 기술 사용 44개 (`0x6562F8`).
- `offset_tables.orders`: 명령 188개 (`0x665580`).
- 각 배열의 인덱스는 해당 게임 데이터 ID이고 값은 원본 게임 요구 조건 테이블의 uint16 오프셋입니다.
- `copy_capacity_bytes`: 현재 4170. 데이터와 오프셋은 한 세트이며, 워드를 삽입·삭제하면 관련 오프셋도 맞춰야 합니다.

`data_words`를 little-endian으로 직렬화해 `RequireData`를 만들고, 초기화에서 `0x514178`로 복사합니다.
다섯 오프셋 테이블은 기존 레퍼런스와 동일하게 매 루프 적용합니다.
이 JSON은 고수준 조건식 DSL이 아닙니다. 임의의 조건 코드를 추측하지 말고 검증한 바이트코드를 사용합니다.

## 검증과 참고

`tools/import_reference_data.py`는 최초 스냅샷 이식용입니다. 다시 실행하면 JSON 편집 내용을 덮어쓰므로
평소 빌드에서는 실행하지 않습니다. 최초 이식 때 두 바이너리가 레퍼런스와 바이트 단위로 같은지 검사했습니다.
`tools/generate_game_data.py`가 일반 빌드 생성기이며 EUD Editor 또는 레퍼런스 파일에 의존하지 않습니다.
바이너리는 DWORD 복사용으로 끝에 최대 3바이트 패딩을 추가합니다.

게임 내 문자열 표시·생산 조건·기술 사용 등은 적용 옵션을 켠 뒤 실제 게임에서도 확인해야 합니다.
