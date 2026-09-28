# -*- coding: utf-8 -*-
"""בדיקות לשמירה וטעינה של משחקים."""

import json
import random

import pytest

from dungeons_and_guns.models import PlayerInput, ResourceKind
from dungeons_and_guns.saves import SAVE_VERSION, SaveError, SaveStore
from dungeons_and_guns.systems import combat, progression, simulation
from dungeons_and_guns.world import make_enemy


@pytest.fixture
def store(tmp_path):
    return SaveStore(str(tmp_path / "saves"))


@pytest.fixture
def state():
    random.seed(99)
    s = progression.new_game()
    s.now = 12_345
    return s


def test_round_trip_restores_everything(store, state):
    state.inventory.tools.add("rod")
    state.inventory.gear.add("vest")
    state.inventory.add_potion("large", 2)
    state.inventory.add_material(ResourceKind.IRON, 3)
    state.player.points = 321
    state.level.fish_cooldown[(3, 5)] = 20_000       # מפתחות tuple עוברים JSON כמחרוזת
    combat.player_shoot(state)
    state.feedback.sounds.clear()
    store.save(1, state)
    assert store.load(1) == state


def test_game_clock_survives_save(store, state):
    """זמנים כמו פתיל רימון נמדדים בשעון של המשחק, לא בשעון של המחשב."""
    state.level.resources[0].ready_at = state.now + 5000
    store.save(2, state)
    loaded = store.load(2)
    assert loaded.now == 12_345
    assert loaded.level.resources[0].ready_at - loaded.now == 5000


def test_loaded_game_keeps_running(store, state):
    store.save(1, state)
    loaded = store.load(1)
    for _ in range(120):
        loaded.now += 16
        simulation.step(loaded, PlayerInput(dx=1, shoot=True))


def test_new_entities_after_load_get_fresh_uids(store, state):
    store.save(1, state)
    loaded = store.load(1)
    taken = {e.uid for e in loaded.level.enemies}
    fresh = make_enemy(loaded.level, 0, 0)
    assert fresh.uid not in taken
    assert fresh.uid > max(taken)


def test_slot_info_summarizes_without_loading_into_game(store, state):
    state.inventory.money = 777
    store.save(3, state)
    infos = store.slots()
    assert [i.exists for i in infos] == [False, False, True]
    assert infos[2].money == 777 and infos[2].level == 1 and infos[2].loadable
    assert store.any_loadable()


def test_empty_slot_raises(store):
    with pytest.raises(SaveError):
        store.load(1)
    assert not store.any_loadable()


def test_damaged_file_is_reported_not_crashed(store, state):
    store.save(1, state)
    with open(store.path(1), "w", encoding="utf-8") as f:
        f.write("{ this is not json")
    assert store.slot_info(1).damaged
    with pytest.raises(SaveError):
        store.load(1)


def test_save_from_before_materials_still_loads(store, state):
    store.save(1, state)
    path = store.path(1)
    data = json.loads(open(path, encoding="utf-8").read())
    del data["state"]["inventory"]["materials"]
    open(path, "w", encoding="utf-8").write(json.dumps(data))
    assert store.load(1).inventory.materials == {}


def test_other_version_is_rejected(store, state):
    store.save(1, state)
    with open(store.path(1), encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = SAVE_VERSION + 1
    with open(store.path(1), "w", encoding="utf-8") as f:
        json.dump(data, f)
    with pytest.raises(SaveError, match="version"):
        store.load(1)


def test_overwrite_replaces_previous_save(store, state):
    store.save(1, state)
    state.inventory.money = 1
    store.save(1, state)
    assert store.load(1).inventory.money == 1
