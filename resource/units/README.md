# 기본 병종 JSON

최상위 키는 UnitModel 속성 이름입니다. 기본 병종은 창병 spearman, 보병 light_infantry,
경기병 light_cavalry, 공성병 siege_unit, 기사 knight입니다.
특수 유닛은 아직 설정하지 않으며 도시·주둔군은 기존 unit_dat.eps에서 관리합니다.

| 파일 | 하위 항목 |
|---|---|
| combat.json | defense, attack.ground, attack.air, score |
| appearance.json | name, graphics, size.placement, size.bounds, sounds |
| properties.json | recruitment, production, weapons, flags, vision, orders, transport, buttons |

예를 들어 창병의 전투 설정은 다음과 같습니다.

```json
{
  "spearman": {
    "defense": { "hp": 1700, "armor": 18 },
    "attack": {
      "ground": { "damage": 55, "bonus": 1, "range": 15, "cooldown": 22, "upgrade": 7 },
      "air": {}
    },
    "score": { "kill": 4 }
  }
}
```

설정하지 않은 키, 빈 객체, null은 기존 DAT 값을 유지합니다.
0과 false는 실제로 적용합니다. 파일은 UTF-8 JSON으로 저장하며 주석은 넣지 않습니다.
초기 외형 항목은 비워 두어 원본 외형을 유지합니다.

- defense.hp는 표시 체력이며 적용할 때만 256을 곱합니다. defense.shield는 실드 최대값입니다.
- defense에는 armor, size_type, armor_upgrade를 설정할 수 있습니다.
- attack의 ground와 air에는 damage, bonus, range, cooldown, upgrade를 설정합니다.
- graphics는 flingy, portrait를 설정합니다.
- name은 표시 이름 문자열이며 TrgUnit.nameString으로 적용합니다. 초기 이름은 창병·보병·경기병·공성병·기사입니다.
- size.placement는 width와 height를 함께 입력하며 size.bounds는 left/top/right/bottom입니다.
- sounds.ready는 준비 사운드, sounds.what/pissed/yes는 각각 start와 end입니다.
- 사거리·배치 크기·충돌 경계는 픽셀, 공격 주기·생산 시간은 원시 엔진 값입니다.
- production.supply는 DAT 값이므로 인구 1은 2입니다.
- vision.seek_range와 vision.sight_range는 타일 단위입니다.
- flags.base_property는 숫자 또는 "0x..." 문자열입니다. flags.hero는 true/false입니다.
  flags.dont_become_guard, flags.ignore_strategic_suicide도 지원합니다.
- recruitment.cost/count는 디플로메시 모집 비용·개수로 unit_data.RECRUITMENT에 노출됩니다.
  모집 기능은 아직 구현하지 않습니다.
- production.minerals/gas/supply/time은 DAT 생산 설정이며 모집 비용과 별개입니다.
  기본 병종은 직접 생산하지 않으므로 초기 minerals는 0, time은 9999입니다.
- weapons.unit은 공격 수치의 대상 UnitModel 키입니다. 공성병은 siege_unit_weapon 포탑을 사용합니다.
  weapons.ground/air는 현재 병종 몸체의 무기 ID 연결이며 max_ground_hits/max_air_hits도 지원합니다.
- orders는 computer_idle, human_idle, return_idle, attack_unit, attack_move, right_click입니다.
- transport.space_required는 수송칸 값이며 buttons.clear는 버튼 제거 여부입니다.
- 무기를 공유하는 유닛은 무기 수치도 함께 바뀝니다.

JSON은 빌드 때 읽고 unit_data.init()에서 TrgUnit 초기화 트리거를 만듭니다.
게임 중 JSON을 읽지 않습니다. HP 변경은 DAT 최대값에만 적용하고 살아 있는 CUnit HP를 직접 대입하지 않습니다.
FranceDp는 기본 5병종·수치만 참고했으며 로더·특수 공격/방어 배율·특수 유닛 시스템은 가져오지 않았습니다.
