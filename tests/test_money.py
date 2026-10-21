# -*- coding: utf-8 -*-
"""בדיקות לכסף (מטבע, דולר, מטיל זהב, יהלום), למשאבים החד-פעמיים ולדיג."""

import random

import pytest

from dungeons_and_guns.data import CATALOG
from dungeons_and_guns.models import Coin, Inventory, Resource, ResourceKind
from dungeons_and_guns.systems import interaction, money, progression, shop
from dungeons_and_guns.systems.shop import ShopKind, ShopRow


@pytest.fixture
def state():
    random.seed(77)
    s = progression.new_game()
    s.level.enemies.clear()
    s.mission = None
    s.now = 10_000
    return s


def wallet(inv):
    return {c: inv.coin_count(c) for c in Coin}


def set_wallet(inv, coins=0, dollars=0, gold=0, diamonds=0):
    inv.money = 0
    inv.coins, inv.dollars = coins, dollars
    if gold:
        inv.materials[ResourceKind.GOLD] = gold
    if diamonds:
        inv.materials[ResourceKind.DIAMOND] = diamonds


# ---------- כסף ----------
def test_new_game_starts_with_100_coins_as_10_dollars(state):
    assert state.inventory.money == 100
    assert state.inventory.dollars == 10 and state.inventory.coins == 0


def test_each_kind_is_worth_ten_of_the_one_before(state):
    inv = state.inventory
    set_wallet(inv, coins=4, dollars=3, gold=2, diamonds=1)
    assert inv.money == 4 + 30 + 200 + 1000


def test_earning_comes_in_fewest_pieces(state):
    inv = state.inventory
    set_wallet(inv)
    assert money.earn(state, 1234) == "1 יהלום, 2 מטילי זהב, 3 דולר ו-4 מטבעות"
    assert wallet(inv) == {Coin.COIN: 4, Coin.DOLLAR: 3, Coin.GOLD: 2, Coin.DIAMOND: 1}


def test_paying_uses_small_money_first_and_gives_change(state):
    inv = state.inventory
    set_wallet(inv, coins=5, dollars=2, gold=1)              # 125
    change = money.pay(state, 30)
    assert inv.money == 95
    assert wallet(inv) == {Coin.COIN: 5, Coin.DOLLAR: 9, Coin.GOLD: 0, Coin.DIAMOND: 0}
    assert "עודף" in change and "9 דולר" in change


def test_exact_payment_has_no_change(state):
    set_wallet(state.inventory, dollars=9)
    assert money.pay(state, 90) == ""
    assert state.inventory.money == 0


def test_cannot_pay_more_than_you_have(state):
    set_wallet(state.inventory, dollars=2)
    assert money.pay(state, 30) is None
    assert state.inventory.dollars == 2


def test_lose_never_goes_below_zero(state):
    set_wallet(state.inventory, coins=7)
    assert state.inventory.lose(50) == 7
    assert state.inventory.money == 0


def test_exchange_up_and_down(state):
    inv = state.inventory
    set_wallet(inv, coins=12)
    money.exchange(state, Coin.COIN, up=True)
    assert inv.coins == 2 and inv.dollars == 1
    money.exchange(state, Coin.COIN, up=True)                 # רק 2 מטבעות - אי אפשר
    assert inv.coins == 2 and "10" in state.feedback.message
    money.exchange(state, Coin.DOLLAR, up=False)
    assert inv.coins == 12 and inv.dollars == 0
    set_wallet(inv, gold=1)
    money.exchange(state, Coin.GOLD, up=False)
    assert inv.dollars == 10 and inv.material_count(ResourceKind.GOLD) == 0
    money.exchange(state, Coin.COIN, up=False)                # מטבע הוא הכי קטן
    assert inv.money == 100


def test_shop_purchase_pays_and_reports_change(state):
    inv = state.inventory
    set_wallet(inv, gold=1)                                  # 100
    assert shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=CATALOG.weapon("beretta")))
    assert inv.money == 100 - CATALOG.weapon("beretta").price
    assert "עודף" in state.feedback.message


def test_mine_gold_bar_and_diamond_are_money(state):
    inv = state.inventory
    inv.tools.add("pickaxe")
    before = inv.money
    for kind in (ResourceKind.GOLD, ResourceKind.DIAMOND):
        res = Resource(x=state.player.x, y=state.player.y, kind=kind)
        state.level.resources.append(res)
        interaction.harvest(state, res)
    assert inv.money == before + 100 + 1000
    assert inv.coin_count(Coin.GOLD) == 1 and inv.coin_count(Coin.DIAMOND) == 1


def test_old_save_money_is_converted():
    inv = Inventory.model_validate({"money": 345, "materials": {"gold": 1}})
    assert inv.money == 345 + 100
    assert inv.dollars == 4 and inv.coins == 5 and inv.material_count(ResourceKind.GOLD) == 4


# ---------- משאבים ודגים ----------
def test_every_resource_is_used_up():
    assert all(r.renew == 0 for r in CATALOG.resources)


def test_farm_animals_disappear_after_one_harvest(state):
    cow = Resource(x=state.player.x, y=state.player.y, kind=ResourceKind.CHICKEN)
    state.level.resources.append(cow)
    interaction.harvest(state, cow)
    assert cow not in state.level.resources


def test_fishing_same_spot_pays_half_each_time(state, monkeypatch):
    monkeypatch.setattr(interaction.random, "randint", lambda a, b: 16)
    inv = state.inventory
    inv.tools.add("rod")
    gains = []
    for _ in range(5):
        before = inv.money
        interaction.go_fishing(state, (3, 3))
        gains.append(inv.money - before)
        state.now += interaction.FISH_COOLDOWN_MS + 1
    assert gains == [16, 8, 4, 2, 1]
    assert inv.food_count("raw_fish") == 5                   # דג מקבלים כל פעם
    before = inv.money
    interaction.go_fishing(state, (5, 5))                    # מקום אחר - שוב מלא
    assert inv.money - before == 16
