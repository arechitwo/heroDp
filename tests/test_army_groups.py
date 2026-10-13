"""Verify compile-time ownership and duplicate registration of hero UnitGroups."""
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class FakeGroup:
    def __init__(self, capacity):
        self.capacity = capacity


class ArmyRegistryTests(unittest.TestCase):
    def setUp(self):
        fake = types.ModuleType('eudplib')
        fake.UnitGroup = FakeGroup
        fake.EUDFunc = lambda function: function
        for name in ('EUDSwitch', 'EUDSwitchCase', 'EUDEndSwitch', 'f_bread_epd'):
            setattr(fake, name, lambda *args: None)
        with patch.dict(sys.modules, {'eudplib': fake}):
            self.module = runpy.run_path(str(ROOT / 'src/game/modules/army_groups.py'))

    def test_players_have_distinct_default_groups(self):
        defaults = self.module['DEFAULT_ARMIES']
        self.assertEqual(len(defaults), 7)
        self.assertEqual(len({id(group) for group in defaults}), 7)
        self.assertEqual(self.module['REGISTERED_GROUPS'], list(enumerate(defaults)))

    def test_multiple_heroes_join_the_same_players_registry(self):
        first, second = FakeGroup(100), FakeGroup(100)
        register = self.module['register_hero_group']
        register(2, first)
        register(2, second)
        self.assertEqual(self.module['PLAYER_GROUPS'][2][-2:], [first, second])
        self.assertEqual(self.module['REGISTERED_GROUPS'][-2:], [(2, first), (2, second)])

    def test_duplicate_and_invalid_player_are_rejected(self):
        group = FakeGroup(100)
        register = self.module['register_hero_group']
        register(0, group)
        with self.assertRaises(ValueError):
            register(1, group)
        with self.assertRaises(ValueError):
            register(7, FakeGroup(100))


if __name__ == '__main__':
    unittest.main()
