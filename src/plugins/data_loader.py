"""Load generated game data before the EPScript game entry point."""
import json
from pathlib import Path
from eudplib import Db, DoActions, EPD, EncodeUnit, SetMemory, SetMemoryX, SetTo, f_epdread_epd, f_repmovsd_epd

DATA = Path(settings.get('data_dir', 'build/generated'))
UNIT_REQUIRE_DATA = 0x514178
ORDER_REQUIRE_DATA = 0x514CF8
UNIT_REQUIRE_WORDS = (0x5145C0 - UNIT_REQUIRE_DATA) // 2
ORDER_REQUIRE_WORDS = (0x5151C2 - ORDER_REQUIRE_DATA) // 2
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
    actions = []
    def append_word(address, value):
        shift = (address & 2) * 8
        actions.append(SetMemoryX(address & ~3, SetTo, value << shift, 0xFFFF << shift))
    for model, words in overrides['units'].items():
        unit_offset = overrides['unit_word_offsets'][model]
        if not 0 < unit_offset or unit_offset + len(words) > UNIT_REQUIRE_WORDS:
            raise ValueError(f'Unit requirement exceeds its data region: {model}')
        append_word(0x660A70 + EncodeUnit(getattr(UnitModel, model)) * 2, unit_offset)
        for index, word in enumerate(words):
            value = EncodeUnit(getattr(UnitModel, word)) if isinstance(word, str) else word
            append_word(UNIT_REQUIRE_DATA + (unit_offset + index) * 2, value)
    for order, words in overrides.get('orders', {}).items():
        order_offset = overrides['order_word_offsets'][order]
        if not 0 < order_offset or order_offset + len(words) > ORDER_REQUIRE_WORDS:
            raise ValueError(f'Order requirement exceeds its data region: {order}')
        append_word(0x665580 + int(order) * 2, order_offset)
        for index, word in enumerate(words):
            value = EncodeUnit(getattr(UnitModel, word)) if isinstance(word, str) else word
            append_word(ORDER_REQUIRE_DATA + (order_offset + index) * 2, value)
    DoActions(actions)


def beforeTriggerExec():
    if manifest['require_data_enabled']:
        for table in manifest['offset_tables']:
            DoActions([SetMemory(table['address'] + i * 4, SetTo, value)
                       for i, value in enumerate(table['dwords'])])
    f_apply_unit_overrides()
