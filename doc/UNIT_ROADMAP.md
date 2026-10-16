# 다음 개발 목표

1. 유닛 스텟 정리: 기본 병종의 전투 수치, 외형·크기, 기본 속성을 기존 JSON 세 파일에서 정리한다.
2. 영웅 유닛 정리: 전사·궁수·법사 각 4종의 설계 초안은 HERO_DESIGN.md에 보관한다. 구현은 기본 게임 기능 완성 뒤로 보류한다.
3. 건설 목록 정리: 건설 가능한 건물, 수도 버튼, 건설 요구사항과 TBL 설명을 함께 정리한다.

첫 변경은 기본 창병의 외형을 브루들링으로 지정하는 것이다. 유닛 역할은 UnitModel.spearman(Protoss Zealot)을 유지하고, appearance.json의 graphics.look에서 Looks.broodling을 참조한다.
