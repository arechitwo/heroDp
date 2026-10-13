# NoE3s

EUD Editor의 `.e3s` 없이 EPScript/Python 소스와 텍스트 설정으로 빌드하는 신규 EUD 맵 프로젝트입니다.

```text
build_map.py              빌드 런처 (Python 3.9 이상)
config/build.json         입력·출력·진입점·euddraft 경로
main.eds                  관리하는 빌드 레시피 (데이터 플러그인 → main.eps)
maps/base.scx             지형·로케이션·배치의 베이스 맵
src/game/main.eps         신규 게임 진입점
src/game/modules/         게임 시스템 모듈
src/data/                 밸런스 CSV 및 데이터
src/plugins/              생성된 TBL·RequireData 적용 플러그인
assets/sounds/            사운드 원본
assets/images/            이미지 원본
build/<실행시각>/         자동 생성 .eds 및 중간 결과
build/logs/               빌드 로그
dist/NoE3s.scx            최종 맵
doc/                      기존 설계 문서 및 향후 신규 문서
BuildData_FanceDp/        FranceDp 레퍼런스 (빌드에 포함하지 않음)
reference/               이전 진입점과 설계 이미지 (로컬 참고용)
```

이전 `src/main.eps`, `src/main_backup.eps`와 설계 이미지는 `reference/`에 보존했습니다.
`BuildData_FanceDp/`와 `reference/`는 로컬 참고용으로 Git 추적에서 제외합니다.
기존 입력 SCX는 `maps/base.scx`로 통합하고, 이전 출력과 생성 캐시는 정리했습니다.
새 코드는 `src/game/`에 작성합니다. `.eps`는 텍스트 EPScript입니다.
진입점에는 주둔군·점령·세금·전군 명령·시작 UI가 연결되어 있습니다.
동작과 설정은 `doc/BASIC_DIPLOMACY.md`를 참고합니다.
파일런·마린 외형 주둔군 DAT는 `src/game/modules/unit_dat.eps`의 `TrgUnit` 문법으로 설정합니다.
특수유닛과 나머지 일반 유닛 DAT 스탯 변경은 아직 없습니다.

## 실행

```powershell
python build_map.py --check
python build_map.py
python build_map.py --euddraft C:/repo/programs/euddraft0.10.2.5/euddraft.exe
python build_map.py --output dist/NoE3s-dev.scx
```

Python이 PATH에 없다면 설치된 `python.exe`의 전체 경로로 실행합니다.
euddraft 선택 순서는 `--euddraft`, `EUDDRAFT_PATH` 환경변수, 설정 파일, PATH입니다.
모든 상대 경로는 프로젝트 루트를 기준으로 해석하므로 다른 폴더에서도 실행할 수 있습니다.
`--check`는 파일과 도구 경로만 검사하며 EPScript 컴파일 검사는 실제 빌드에서 수행합니다.

런처는 실행마다 일회성 `.eds`를 만들고 euddraft를 실행합니다.
성공한 새 결과가 있어야 최종 출력으로 이동하며, 실패하면 이전 출력은 보존합니다.
오류 상세는 `build/logs/`에서 확인합니다. `build/`, `dist/`, EPScript 캐시는 Git 추적에서 제외합니다.

현재 베이스는 PR #1의 유럽 내륙 v3 맵에 도시 마커 260개를 배치하고 로케이션을 비운 파일입니다.
자세한 배치 규칙은 `maps/README.md`, 거점 데이터는 `src/data/city_markers.json`을 참고합니다.
코드만으로 지형과 CHK까지 생성하는 기능은 아직 없습니다.
DAT 설정, MSQC, 채팅, 사운드 등은 신규 구현에 필요한 시점에 코드/플러그인으로 추가합니다.

빌드 형식 참고: [euddraft 공식 소스](https://github.com/armoha/euddraft/blob/main/euddraft.py).

트리거 개발 환경과 JSON 데이터 편집 방법은 `doc/TRIGGER_WORKFLOW.md`를 참고합니다.
`src/data/custom_tbl.json`, `src/data/require_data.json`에서 데이터를 편집하면 빌드 때 자동 생성됩니다.
두 파일의 FranceDp 스냅샷은 기본적으로 비활성화되어 있습니다.
