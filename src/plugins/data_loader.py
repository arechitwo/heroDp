"""Load generated game data before the EPScript game entry point."""
import json
from pathlib import Path
from eudplib import Db, DoActions, EPD, EncodeUnit, SetMemory, SetTo, f_epdread_epd, f_repmovsd_epd, f_wwrite

DATA = Path(settings.get('data_dir', 'build/generated'))
# euddraft resolves relative paths from the recipe directory and does not set __file__.
manifest = json.loads((DATA / 'manifest.json').read_text(encoding='utf-8'))


def onPluginStart():
    if manifest['custom_tbl_enabled']:
        raw = (DATA / 'custom_txt.tbl').read_bytes()
        f_repmovsd_epd(f_epdread_epd(EPD(0x6D5A30)), EPD(Db(raw)), len(raw) // 4)
    if manifest['require_data_enabled']:
        raw = (DATA / 'RequireData').read_bytes()
        f_repmovsd_epd(EPD(0x514178), EPD(Db(raw)), len(raw) // 4)
    f_apply_unit_overrides()


def f_apply_unit_overrides():
    overrides = manifest.get('unit_overrides', {})
    if not overrides.get('enabled', False):
        return
    from modules.unit_settings import UnitModel
    offset = overrides['data_word_offset']
    for model, words in overrides['units'].items():
        f_wwrite(0x660A70 + EncodeUnit(getattr(UnitModel, model)) * 2, offset)
        for word in words:
            value = EncodeUnit(getattr(UnitModel, word)) if isinstance(word, str) else word
            f_wwrite(0x514178 + offset * 2, value)
            offset += 1


def beforeTriggerExec():
    if manifest['require_data_enabled']:
        for table in manifest['offset_tables']:
            DoActions([SetMemory(table['address'] + i * 4, SetTo, value)
                       for i, value in enumerate(table['dwords'])])
        f_apply_unit_overrides()
