# 코드 기반 트리거 개발

## 진입점과 적용 순서

`src/game/main.eps`가 게임 진입점입니다. 신규 시스템은 `src/game/modules/*.eps`에 작성하고
`main.eps`에서 `import modules.모듈이름 as 별칭;`으로 불러옵니다.
`onPluginStart()`는 초기화, `beforeTriggerExec()`는 매 트리거 루프, `afterTriggerExec()`는 후처리에 사용합니다.

루트 `main.eds`는 Git으로 관리하는 실제 빌드 레시피입니다. 순서는 다음과 같습니다.

1. `src/plugins/data_loader.py`: 생성된 TBL·RequireData 적용
2. `chatEvent`: 시작 거점 선택 채팅 감지
3. `MSQC`: 채팅과 시작 UI·전군 명령의 키·마우스 동기화
4. `src/game/main.eps`: 신규 게임 트리거

플레이어·테란 종족·시작 위치·로케이션은 `maps/base.scx`에 직접 저장합니다.
도시 수는 UNIT 비콘에서, 시작 거점 정보는 시작 위치 로케이션에서 읽습니다.
도시별 고정 로케이션은 없으며 공용 로케이션은 `map_data.py`의 `Loc`에 `EncodeLocation` 이름으로 선언합니다.

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
경로를 해석한 `map.eds`로 일회성 컴파일합니다. 최종 결과는 `config/build.json`의 `output_dir`에 저장합니다.
기본 폴더는 `C:\Users\shigi\Documents\StarCraft\Maps`이며 파일명은 `map_data.py`의 `map_version`에서 읽습니다.
`map_version = "NoE3s0.01"`이면 `NoE3s0.01.scx`로 저장합니다. 버전은 문자열 리터럴로 작성합니다.

euddraft로 레시피를 직접 실행하려면 먼저 다음 순서로 실행합니다.

```powershell
python build_map.py --prepare
C:/repo/programs/euddraft0.10.2.5/euddraft.exe main.eds
```

직접 실행은 프로젝트 루트에서 하며 입력·출력·진입점은 `main.eds` 값을 사용합니다.
`--prepare`는 생성 데이터와 함께 `main.eds`의 입력·출력을 현재 설정과 `map_version`에 맞춥니다.
JSON을 바꾼 뒤에는 `--prepare`를 다시 실행해야 직접 빌드에 반영됩니다.

## custom_tbl.json

`src/data/custom_tbl.json`에서 TBL을 편집합니다. FranceDp 스냅샷에 현재 맵의 설명문을 추가한 데이터이며 `enabled: true`로 적용합니다. false이면 기존 data_loader가 TBL 복사를 생략합니다.

- `encoding`: 현재 `cp949`.
- `entries`: 1부터 연속되는 TBL ID. `text` 또는 `hex` 중 하나를 사용합니다.
- `text`: JSON 표준 제어문자 표기 사용. 색상은 `\u0004`, 줄바꿈은 `\n`, 내부 NUL은 `\u0000`.
- 활성 버튼 설명은 단축키 뒤에 용도별 한정자를 넣습니다(건설·생산 0x01, 업그레이드 연구 0x02, 기술 연구 0x04). 비활성 버튼 설명은 단축키 바이트·한정자·[Q] 같은 표시를 모두 빼고 제목과 사용 조건만 일반 문자열로 적습니다. 비활성 설명에 활성 형식을 넣으면 q[Q] 등이 그대로 표시됩니다.
- 활성 설명의 본문은 무엇을 하는지(기능·효과)를 설명하고, 선행 건물·해금 연구·필요 자원 같은 사용 조건은 비활성 설명에만 적습니다. 비활성 설명은 막연히 '조건 충족 필요'라고 하지 않고 필요한 건물·연구·자원·빈 칸을 구체적으로 적습니다.
- `hex`: CP949로 해석되지 않는 원본 바이트를 그대로 보존합니다. 바꾸려면 `hex`를 삭제하고 `text`를 작성합니다.
- TBL에는 `copy_capacity_bytes`를 사용하지 않습니다. 원본 파일 크기 42564를 버퍼 한도로 취급했던 프로젝트 자체 제한은 근거가 없어 제거했습니다. uint16 항목 수·오프셋 표현 범위 검사는 유지하며 armoha의 정렬 처리에도 해당 형식 범위가 적용됩니다.

생성물은 `custom_txt.tbl`이며 uint16 항목 수, uint16 오프셋 테이블, NUL로 끝나는 바이트 문자열로 구성합니다.
내부 NUL도 보존하므로 유닛 이름·툴팁 복합 항목을 손실 없이 재생성합니다.
기존 JSON 생성기·data_loader 구조를 유지합니다. tools/generate_game_data.py가 armoha `_AddStatText()`와 같은 방식으로 헤더와 각 문자열을 DWORD 정렬하고, 패딩을 포함한 오프셋을 재계산합니다. 내부 NUL과 단축키 뒤 한정자를 보존합니다. data_loader는 armoha `_f_initstattext()`와 동일하게 `0x6D5A30`의 포인터 대상에 완성 데이터를 한 번 복사합니다. dataDumper 플러그인이나 private 함수 등록 호출은 추가하지 않습니다. F5 빌드는 실행별 생성 파일 경로를, --prepare는 build/generated 경로를 사용합니다.

이는 원래 게임 버퍼의 실제 할당 크기를 측정하거나 버퍼를 재할당하는 구현이 아닙니다. 조사한 armoha 코드도 버퍼 크기를 검사하거나 재할당하지 않습니다. 따라서 원본 파일 크기를 엔진 최대 용량으로 단정하지 않으며, 형식상 uint16 범위와 실게임 동작 한계를 구분합니다.

근거: https://github.com/armoha/euddraft/blob/main/pluginLoader.py 및 https://github.com/armoha/eudplib/blob/main/src/eudplib/string/tblprint.py .

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

최초 스냅샷 이식 도구는 작업 완료 후 삭제했습니다. 최초 이식 때 두 바이너리가 레퍼런스와 바이트 단위로 같은지 검사했습니다.
`tools/generate_game_data.py`가 일반 빌드 생성기이며 EUD Editor 또는 레퍼런스 파일에 의존하지 않습니다.
바이너리는 DWORD 복사용으로 끝에 최대 3바이트 패딩을 추가합니다.

게임 내 문자열 표시·생산 조건·기술 사용 등은 적용 옵션을 켠 뒤 실제 게임에서도 확인해야 합니다.
