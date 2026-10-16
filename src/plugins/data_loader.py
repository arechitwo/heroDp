"""Load generated game data before the EPScript game entry point."""
import json
from pathlib import Path
from eudplib import Db, DoActions, EPD, EncodeUnit, SetMemory, SetMemoryX, SetTo, f_epdread_epd, f_repmovsd_epd

DATA = Path(settings.get('data_dir', 'build/generated'))
# euddraft resolves relative paths from the recipe directory and does not set __file__.
manifest = json.loads((DATA / 'manifest.json').read_text(encoding='utf-8'))


def onPluginStart():
    if manifest['custom_tbl_enabled']:
        # 생성기에서 문자열과 오프셋 표를 DWORD 정렬. armoha처럼 포인터 대상에 한 번 복사.
        raw = (DATA / 'custom_txt.tbl').read_bytes()
        f_repmovsd_epd(f_epdread_epd(EPD(0x6D5A30)), EPD(Db(raw)), len(raw) // 4)
    if manifest['require_data_enabled']:
        raw = (DATA / 'RequireData').read_bytes()
        f_repmovsd_epd(EPD(0x514178), EPD(Db(raw)), len(raw) // 4)
        f_apply_unit_links()


def f_apply_unit_links():
    from modules.unit_settings import UnitModel
    actions = []
    for model, offset in manifest.get('unit_links', {}).items():
        # 기존 유닛 요구사항 영역 내 프로그램만 연결하며 데이터는 쓰지 않음.
        if type(offset) is not int or not 0 < offset < 548:
            raise ValueError(f'Invalid existing unit requirement offset: {model}')
        address = 0x660A70 + EncodeUnit(getattr(UnitModel, model)) * 2
        shift = (address & 2) * 8
        actions.append(SetMemoryX(address & ~3, SetTo, offset << shift, 0xFFFF << shift))
    if actions:
        DoActions(actions)


def beforeTriggerExec():
    if manifest['require_data_enabled']:
        for table in manifest['offset_tables']:
            DoActions([SetMemory(table['address'] + i * 4, SetTo, value)
                       for i, value in enumerate(table['dwords'])])
        f_apply_unit_links()
