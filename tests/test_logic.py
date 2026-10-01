# -*- coding: utf-8 -*-
"""בדיקות לחוקי המשחק - רצות בלי חלון ובלי pygame."""

import random
import subprocess
import sys

import pytest
from pydantic import ValidationError

from dungeons_and_guns.data import CATALOG, Catalog
from dungeons_and_guns.models import (HOTBAR_SIZE, Crate, CrateKind, Inventory, ItemKind,
                                      PlayerInput, Recipe, Resource, ResourceKind, SlotItem, Tile,
                                      Weapon, WeaponCategory, WeaponKind, WheelOutcome)
from dungeons_and_guns.systems import (combat, crafting, crates, health, interaction, progression,
                                       ranks, shop, simulation)
from dungeons_and_guns.systems import wheel as wheel_system
from dungeons_and_guns.systems.shop import ShopKind, ShopRow
from dungeons_and_guns.world import START_TILE, build_level, make_enemy, path_exists


@pytest.fixture
def state():
    random.seed(1234)
    s = progression.new_game()
    s.level.enemies.clear()             # שקט - בלי אויבים שיורים בנו
    s.now = 10_000
    return s


def test_logic_does_not_import_pygame():
    code = ("import sys; import dungeons_and_guns.systems.simulation, dungeons_and_guns.systems.shop; "
            "sys.exit('pygame' in sys.modules)")
    assert subprocess.run([sys.executable, "-c", code]).returncode == 0


# ---------- קטלוג ----------
def test_catalog_ammo_defaults_follow_category():
    assert CATALOG.weapon("m16").ammo == "ammo_rifle"
    assert CATALOG.weapon("ak47").ammo == "ammo_ak"
    assert CATALOG.weapon("ruger101").ammo == "ammo_revolver"
    assert CATALOG.weapon("bow").ammo == "ammo_arrow"
    assert CATALOG.weapon("slingshot").ammo is None
    assert CATALOG.weapon("dagger").ammo is None


def test_enemy_weapons_are_sorted_guns_only():
    prices = [w.price for w in CATALOG.enemy_weapons]
    assert prices == sorted(prices)
    assert all(w.kind == WeaponKind.GUN and w.cat != WeaponCategory.COLD
               for w in CATALOG.enemy_weapons)


def test_weapon_rejects_bad_damage_range():
    with pytest.raises(ValidationError):
        Weapon(id="x", name="x", cat=WeaponCategory.PISTOLS, kind=WeaponKind.GUN,
               dmg=(10, 5), acc=0.5, rng=100, cooldown=100, price=1)


def test_catalog_rejects_unknown_ammo():
    bad = CATALOG.weapons + [Weapon(id="x", name="x", cat=WeaponCategory.PISTOLS,
                                    kind=WeaponKind.GUN, dmg=(1, 2), acc=0.5, rng=100,
                                    cooldown=100, price=1, ammo="nope")]
    fields = {name: getattr(CATALOG, name) for name in Catalog.model_fields}
    with pytest.raises(ValidationError, match="unknown ammo"):
        Catalog(**{**fields, "weapons": bad})


# ---------- עולם ----------
@pytest.mark.parametrize("number", [1, 3, 6])
def test_level_always_has_dry_path_to_exit(number):
    random.seed(number)
    level = build_level(number)
    assert path_exists(level.grid, START_TILE, level.exit_tile)
    assert any(t == Tile.FISH for row in level.grid for t in row)


# ---------- ירי ----------
def test_shooting_uses_ammo_and_respects_cooldown(state):
    before = state.inventory.ammo_count("ammo_pistol")
    combat.player_shoot(state)
    combat.player_shoot(state)              # עדיין בזמן ההמתנה של הנשק
    assert state.inventory.ammo_count("ammo_pistol") == before - 1
    assert len(state.level.bullets) == 1


def test_shooting_without_ammo_says_so(state):
    state.inventory.ammo["ammo_pistol"] = 0
    combat.player_shoot(state)
    assert not state.level.bullets
    assert "נגמרו" in state.feedback.message
    assert any(c.name == "no" for c in state.feedback.sounds)


def test_killing_enemy_pays_money(state):
    enemy = make_enemy(state.level, 100, 100)
    state.level.enemies.append(enemy)
    money = state.inventory.money
    combat.damage_enemy(state, enemy, 10_000)
    assert enemy not in state.level.enemies
    assert state.inventory.money > money


def test_twin_enemies_are_distinct(state):
    a = make_enemy(state.level, 50, 50)
    b = a.model_copy(update={"uid": a.uid + 10_000})
    state.level.enemies += [a, b]
    state.level.enemies.remove(b)
    assert state.level.enemies == [a]


# ---------- חיים ----------
def test_gear_reduces_damage(state):
    state.inventory.gear.add("vest")
    health.hurt(state, 10)
    assert state.player.hp == pytest.approx(93)


def test_death_plays_gameover_once(state):
    health.hurt(state, 1000)
    health.drain(state, 5)
    assert state.game_over
    assert [c.name for c in state.feedback.sounds].count("gameover") == 1


def test_only_large_potion_cures_sickness(state):
    health.infect(state)
    state.player.hp = 50
    state.inventory.add_potion("small")
    health.drink_potion(state)
    assert state.player.sick and state.player.hp == 50
    state.now += 1000
    state.inventory.add_potion("large")
    health.drink_potion(state)
    assert not state.player.sick and state.player.hp == 100


# ---------- חנות ----------
def test_buying_weapon_gives_ammo_pack(state):
    state.inventory.money = 5000
    state.player.points = 10_000                        # דרגה מספיק גבוהה לרובי סער
    m16 = CATALOG.weapon("m16")
    assert shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=m16))
    assert "m16" in state.inventory.weapons
    assert state.inventory.ammo_count("ammo_rifle") == CATALOG.ammo("ammo_rifle").pack
    assert state.inventory.money == 5000 - m16.price


def test_cannot_buy_without_money(state):
    state.inventory.money = 0
    assert not shop.buy(state, ShopRow(kind=ShopKind.TOOL, item=CATALOG.tool("saw")))
    assert "saw" not in state.inventory.tools


def test_shop_marks_owned_items(state):
    rows = [r for s in shop.shop_sections(state) for r in s.rows]
    glock = next(r for r in rows if r.item.id == "glock19")
    assert glock.owned


# ---------- דרגות ----------
def test_better_enemy_weapon_gives_more_points():
    assert ranks.kill_points(CATALOG.weapon("minigun")) > ranks.kill_points(CATALOG.weapon("m16"))
    assert ranks.kill_points(CATALOG.weapon("m16")) > ranks.kill_points(CATALOG.weapon("glock19"))
    assert ranks.kill_points(CATALOG.weapon("glock19")) > 0


def test_killing_enemy_gives_points(state):
    enemy = make_enemy(state.level, 100, 100)
    state.level.enemies.append(enemy)
    combat.damage_enemy(state, enemy, 10_000)
    assert state.player.points == ranks.kill_points(enemy.weapon)
    assert "נקודות" in state.feedback.message


def test_promotion_is_announced(state):
    state.player.points = CATALOG.unlock_rank("uzi").points - 1
    enemy = make_enemy(state.level, 100, 100)
    state.level.enemies.append(enemy)
    combat.damage_enemy(state, enemy, 10_000)
    assert "uzi" in ranks.current_rank(state).unlocks
    assert "עוזי" in state.feedback.message
    assert "עלית לדרגת" in state.feedback.message
    assert any(c.name == "rank_up" for c in state.feedback.sounds)


@pytest.mark.parametrize("weapon_id", ["uzi", "m16", "dragunov", "minigun"])
def test_strong_weapons_need_rank(state, weapon_id):
    state.inventory.money = 100_000
    row = ShopRow(kind=ShopKind.WEAPON, item=CATALOG.weapon(weapon_id))
    assert not shop.buy(state, row)
    assert weapon_id not in state.inventory.weapons
    assert state.inventory.money == 100_000
    assert "דרגת" in state.feedback.message
    state.player.points = CATALOG.unlock_rank(weapon_id).points
    assert shop.buy(state, row)
    assert weapon_id in state.inventory.weapons


@pytest.mark.parametrize("weapon_id", ["glock17", "shotgun", "sword", "bow"])
def test_basic_weapons_open_from_start(state, weapon_id):
    state.inventory.money = 100_000
    assert shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=CATALOG.weapon(weapon_id)))


def test_shop_shows_locked_weapons(state):
    rows = {r.item.id: r for s in shop.shop_sections(state) for r in s.rows}
    assert rows["uzi"].need_rank.name == 'רב"ט'
    assert rows["m16"].need_rank.name == 'סמ"ר'
    assert rows["glock17"].need_rank is None


def test_each_rank_opens_weapons_from_one_category():
    for rank in CATALOG.ranks:
        assert len({CATALOG.weapon(wid).cat for wid in rank.unlocks}) <= 1


def test_all_strong_weapons_are_locked():
    strong = {WeaponCategory.SMGS, WeaponCategory.RIFLES, WeaponCategory.SNIPERS,
              WeaponCategory.HEAVY}
    for w in CATALOG.weapons:
        if w.cat in strong:
            assert CATALOG.unlock_rank(w.id) is not None, w.id


def test_rank_opens_weapons_gradually(state):
    state.inventory.money = 100_000
    state.player.points = CATALOG.unlock_rank("uzi").points
    assert shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=CATALOG.weapon("uzi")))
    assert not shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=CATALOG.weapon("mp7")))


def test_catalog_rejects_unordered_ranks():
    bad = list(reversed(CATALOG.ranks))
    with pytest.raises(ValidationError):
        Catalog(**{**CATALOG.model_dump(), "ranks": bad})


# ---------- שורת המספרים ----------
def weapon_slot(weapon_id):
    return SlotItem(kind=ItemKind.WEAPON, id=weapon_id)


def test_new_game_starts_with_pistol_in_first_slot(state):
    inv = state.inventory
    assert len(inv.hotbar) == HOTBAR_SIZE
    assert inv.hotbar[0] == weapon_slot("glock19") and inv.selected == 0
    assert all(slot is None for slot in inv.hotbar[1:])


def test_new_things_go_to_next_empty_slot(state):
    state.inventory.money = 100_000
    shop.buy(state, ShopRow(kind=ShopKind.WEAPON, item=CATALOG.weapon("sword")))
    state.inventory.add_potion("small")
    state.inventory.add_potion("small")                 # אותה תרופה - לא נכנסת פעמיים
    assert state.inventory.hotbar[1] == weapon_slot("sword")
    assert state.inventory.hotbar[2] == SlotItem(kind=ItemKind.POTION, id="small")
    assert state.inventory.hotbar[3] is None


def test_full_hotbar_keeps_things_in_bag(state):
    inv = state.inventory
    for i in range(1, HOTBAR_SIZE):
        inv.set_slot(i, SlotItem(kind=ItemKind.FOOD, id="bread"))    # מחליף - נשאר אחד
    for i, wid in enumerate(["dagger", "sword", "spear", "bow", "slingshot", "shotgun",
                             "glock17", "beretta", "cz75", "czp"]):
        if weapon_slot(wid) not in inv.hotbar and None in inv.hotbar:
            inv.set_slot(inv.hotbar.index(None), weapon_slot(wid))
    assert None not in inv.hotbar
    inv.add_potion("large")
    assert inv.potion_count("large") == 1
    assert SlotItem(kind=ItemKind.POTION, id="large") not in inv.hotbar


def test_set_slot_swaps_when_item_already_in_row(state):
    inv = state.inventory
    inv.add_potion("small")                             # משבצת 1
    inv.set_slot(1, weapon_slot("glock19"))             # האקדח עובר ל-1, התרופה ל-0
    assert inv.hotbar[0] == SlotItem(kind=ItemKind.POTION, id="small")
    assert inv.hotbar[1] == weapon_slot("glock19")
    inv.clear_slot(0)
    assert inv.hotbar[0] is None


def test_hotbar_rejects_things_you_cannot_use():
    with pytest.raises(ValidationError):
        SlotItem(kind=ItemKind.AMMO, id="ammo_pistol")


def test_space_uses_what_is_selected(state):
    inv = state.inventory
    inv.add_potion("medium")                            # משבצת 1
    inv.add_food("bread")                               # משבצת 2
    state.player.hp = 30
    inv.select_slot(1)
    simulation.use_selected(state)
    assert inv.potion_count("medium") == 0 and state.player.hp == 90
    state.now += 1000
    inv.select_slot(2)
    simulation.use_selected(state)
    assert inv.food_count("bread") == 0 and state.player.hp == 100
    inv.select_slot(5)                                  # משבצת ריקה - לא קורה כלום
    simulation.use_selected(state)
    assert not state.level.bullets


def test_selected_small_potion_does_not_cure(state):
    health.infect(state)
    state.inventory.add_potion("small")
    state.inventory.add_potion("large")
    state.player.hp = 50
    state.inventory.select_slot(1)                      # התרופה הקטנה
    simulation.use_selected(state)
    assert state.player.sick and state.inventory.potion_count("small") == 1


def test_cycle_slot_wraps_around(state):
    state.inventory.cycle_slot(-1)
    assert state.inventory.selected == HOTBAR_SIZE - 1
    state.inventory.cycle_slot(1)
    assert state.inventory.selected == 0


def test_old_save_inventory_gets_a_hotbar():
    inv = Inventory.model_validate({"weapons": ["glock19", "m16"], "weapon_index": 1,
                                    "potions": {"small": 2}})
    assert inv.hotbar[:3] == [weapon_slot("glock19"), weapon_slot("m16"),
                              SlotItem(kind=ItemKind.POTION, id="small")]
    assert inv.selected == 1


# ---------- משאבים ----------
def test_fishing_gives_money_and_a_fish_to_eat(state):
    state.inventory.tools.add("rod")
    money = state.inventory.money
    interaction.go_fishing(state, (3, 3))
    assert state.inventory.money > money
    assert state.inventory.food_count("raw_fish") == 1
    assert SlotItem(kind=ItemKind.FOOD, id="raw_fish") in state.inventory.hotbar
    state.player.hp = 50
    health.eat(state, "raw_fish")
    assert state.player.hp == 50 + CATALOG.food("raw_fish").heal
    assert state.inventory.food_count("raw_fish") == 0


def test_no_fish_while_fish_are_away(state):
    state.inventory.tools.add("rod")
    interaction.go_fishing(state, (3, 3))
    interaction.go_fishing(state, (3, 3))               # הדגים עוד לא חזרו
    assert state.inventory.food_count("raw_fish") == 1


def test_harvest_gives_money_and_material(state):
    state.inventory.tools.add("pickaxe")
    iron = Resource(x=state.player.x, y=state.player.y, kind=ResourceKind.IRON)
    state.level.resources.append(iron)
    money = state.inventory.money
    interaction.harvest(state, iron)
    assert state.inventory.money > money
    assert state.inventory.material_count(ResourceKind.IRON) == 1
    assert "מטיל ברזל" in state.feedback.message
    assert iron not in state.level.resources


@pytest.mark.parametrize("roll, sick", [(0.04, True), (0.06, False)])
def test_cow_has_five_percent_to_make_you_sick(state, monkeypatch, roll, sick):
    monkeypatch.setattr(interaction.random, "random", lambda: roll)
    cow = Resource(x=state.player.x, y=state.player.y, kind=ResourceKind.COW)
    state.level.resources.append(cow)
    interaction.harvest(state, cow)
    assert state.player.sick == sick


def test_harvest_without_tool_gives_nothing(state):
    tree = Resource(x=state.player.x, y=state.player.y, kind=ResourceKind.TREE)
    state.level.resources.append(tree)
    interaction.harvest(state, tree)
    assert state.inventory.material_count(ResourceKind.TREE) == 0
    assert tree in state.level.resources


# ---------- סדנה ----------
def recipe_for(item_id):
    return next(r for r in CATALOG.recipes if r.item == item_id)


def test_workshop_makes_no_weapons_or_potions():
    assert all(r.kind in (ItemKind.AMMO, ItemKind.GEAR, ItemKind.FOOD, ItemKind.KEY, ItemKind.OVEN,
                          ItemKind.POISON) for r in CATALOG.recipes)


def test_craft_food_then_eat_it(state):
    recipe = recipe_for("dough")
    state.inventory.add_material(ResourceKind.WHEAT, 2)
    assert crafting.craft(state, recipe)
    assert state.inventory.food_count("dough") == 1
    state.player.hp = 50
    health.eat(state)
    assert state.player.hp == 50 + CATALOG.food("dough").heal
    assert state.inventory.food == {}


# ---------- רעל ----------
def bow_ready(state):
    from dungeons_and_guns.systems.inventory import give_weapon
    give_weapon(state.inventory, CATALOG.weapon("bow"))
    state.inventory.select_slot(state.inventory.hotbar_index(SlotItem(kind=ItemKind.WEAPON, id="bow")))


def test_buy_poison(state):
    state.inventory.money = 200
    assert shop.buy(state, ShopRow(kind=ShopKind.POISON, item=CATALOG.poison))
    assert state.inventory.money == 200 - 110
    assert state.inventory.poison_arrows == 15


def test_craft_poison_from_medium_potion_cotton_and_wool(state):
    recipe = recipe_for("poison")
    state.inventory.add_material(ResourceKind.COTTON, 1)
    state.inventory.add_material(ResourceKind.SHEEP, 1)
    assert not crafting.craft(state, recipe)                 # אין תרופה בינונית
    assert "תרופה בינונית" in state.feedback.message
    state.inventory.add_potion("medium")
    assert crafting.craft(state, recipe)
    assert state.inventory.poison_arrows == 15
    assert state.inventory.potion_count("medium") == 0
    assert state.inventory.materials == {}


def test_poison_goes_on_arrows_only(state):
    state.inventory.poison_arrows = 15
    combat.player_shoot(state)                               # גלוק - לא מורעל
    assert not state.level.bullets[-1].poison and state.inventory.poison_arrows == 15
    bow_ready(state)
    state.now += 5000
    combat.player_shoot(state)
    assert state.level.bullets[-1].poison and state.inventory.poison_arrows == 14


def test_poisoned_enemy_keeps_losing_hp_and_can_die(state):
    enemy = make_enemy(state.level, 500, 500)
    state.level.enemies.append(enemy)
    combat.poison_enemy(state, enemy)
    hp = enemy.hp
    state.now += 1000
    combat.update_poison(state)
    assert enemy.hp == hp - CATALOG.poison.dps
    state.now += 1000
    combat.update_poison(state)
    assert enemy.hp == hp - 2 * CATALOG.poison.dps
    enemy.hp = 1
    points = state.player.points
    state.now += 1000
    combat.update_poison(state)
    assert enemy not in state.level.enemies
    assert state.player.points > points and "רעל" in state.feedback.message


def test_poison_wears_off(state):
    enemy = make_enemy(state.level, 500, 500)
    state.level.enemies.append(enemy)
    combat.poison_enemy(state, enemy)
    for _ in range(20):
        state.now += 1000
        combat.update_poison(state)
    assert enemy.hp == enemy.max_hp - CATALOG.poison.dps * CATALOG.poison.seconds


# ---------- תנור ----------
def build_oven(state):
    recipe = recipe_for("oven")
    for kind, n in recipe.needs.items():
        state.inventory.add_material(kind, n)
    assert crafting.craft(state, recipe)


def test_oven_is_built_from_bricks_not_bought(state):
    assert recipe_for("oven").needs == {ResourceKind.BRICKS: 3}
    rows = [r for s in shop.shop_sections(state) for r in s.rows]
    assert not any(r.kind != ShopKind.CRAFT and r.item.id == "oven" for r in rows)
    build_oven(state)
    assert state.inventory.oven_uses == 3
    assert "תנור" in state.feedback.message


def test_cooking_turns_raw_into_cooked_and_uses_the_oven(state):
    build_oven(state)
    state.inventory.add_food("raw_fish", 2)
    raw = CATALOG.food("raw_fish")
    assert crafting.cook(state, raw)
    assert state.inventory.food_count("raw_fish") == 1
    assert state.inventory.food_count("fish") == 1
    assert state.inventory.oven_uses == 2


def test_oven_runs_out_after_three_cookings(state):
    build_oven(state)
    state.inventory.add_food("dough", 4)
    dough = CATALOG.food("dough")
    for _ in range(3):
        assert crafting.cook(state, dough)
    assert state.inventory.oven_uses == 0
    assert "נגמר" in state.feedback.message
    assert not crafting.cook(state, dough)
    assert state.inventory.food_count("dough") == 1 and state.inventory.food_count("bread") == 3


def test_cooked_food_takes_the_raw_hotbar_slot(state):
    build_oven(state)
    state.inventory.add_food("dough")
    slot = state.inventory.hotbar_index(SlotItem(kind=ItemKind.FOOD, id="dough"))
    crafting.cook(state, CATALOG.food("dough"))
    assert state.inventory.hotbar[slot] == SlotItem(kind=ItemKind.FOOD, id="bread")


def test_cannot_cook_without_oven(state):
    state.inventory.add_food("raw_fish")
    assert not crafting.cook(state, CATALOG.food("raw_fish"))
    assert state.inventory.food_count("raw_fish") == 1
    assert "תנור" in state.feedback.message


def test_raw_food_can_make_you_sick(state, monkeypatch):
    monkeypatch.setattr(health.random, "random", lambda: 0.01)     # בתוך ה-5%
    state.inventory.add_food("raw_fish")
    state.player.hp = 50
    health.eat(state, "raw_fish")
    assert state.player.sick


def test_raw_food_usually_fine(state, monkeypatch):
    monkeypatch.setattr(health.random, "random", lambda: 0.5)
    state.inventory.add_food("raw_fish")
    state.player.hp = 50
    health.eat(state, "raw_fish")
    assert not state.player.sick


def test_cooked_food_never_makes_you_sick(state, monkeypatch):
    monkeypatch.setattr(health.random, "random", lambda: 0.0)
    state.inventory.add_food("fish")
    state.inventory.add_food("cheese")                  # גבינה לא צריך לבשל
    state.player.hp = 10
    health.eat(state, "fish")
    state.now += 1000
    health.eat(state, "cheese")
    assert not state.player.sick


def test_eat_key_prefers_cooked_food(state):
    state.inventory.add_food("raw_fish")
    state.inventory.add_food("fish")
    state.player.hp = 50
    health.eat(state)
    assert state.inventory.food_count("fish") == 0 and state.inventory.food_count("raw_fish") == 1


def test_eat_picks_food_that_fits_missing_hp(state):
    state.inventory.add_food("bread")                   # 15
    state.inventory.add_food("cake")                    # 35
    state.player.hp = state.player.max_hp - 10
    health.eat(state)
    assert state.inventory.food_count("bread") == 0     # לא מבזבזים עוגה על 10 חיים
    assert state.inventory.food_count("cake") == 1
    state.now += 1000
    state.player.hp = 20
    health.eat(state)
    assert state.inventory.food_count("cake") == 0      # חסר הרבה - העוגה


def test_eat_with_full_hp_keeps_food(state):
    state.inventory.add_food("cheese")
    health.eat(state)
    assert state.inventory.food_count("cheese") == 1


def test_food_does_not_cure_sickness(state):
    health.infect(state)
    state.inventory.add_food("cake")
    state.player.hp = 50
    health.eat(state)
    assert state.player.sick


def test_craft_uses_up_materials(state):
    recipe = recipe_for("helmet")                        # 2 מטילי ברזל
    state.inventory.add_material(ResourceKind.IRON, 3)
    money = state.inventory.money
    assert crafting.craft(state, recipe)
    assert "helmet" in state.inventory.gear
    assert state.inventory.material_count(ResourceKind.IRON) == 1
    assert state.inventory.money == money               # בסדנה לא משלמים כסף
    assert not crafting.craft(state, recipe)             # קסדה מכינים רק פעם אחת


def test_craft_without_enough_materials_fails(state):
    recipe = recipe_for("ammo_pistol")
    state.inventory.add_material(ResourceKind.COPPER, 1)
    before = state.inventory.ammo_count("ammo_pistol")
    assert not crafting.craft(state, recipe)
    assert crafting.missing(state, recipe) == {ResourceKind.GAS: 1}
    assert state.inventory.ammo_count("ammo_pistol") == before
    assert state.inventory.material_count(ResourceKind.COPPER) == 1
    assert "מיכל גז" in state.feedback.message


def test_craft_ammo_gives_a_full_pack(state):
    recipe = recipe_for("ammo_arrow")
    for kind, n in recipe.needs.items():
        state.inventory.add_material(kind, n)
    before = state.inventory.ammo_count("ammo_arrow")
    row = next(r for r in shop.shop_sections(state)[0].rows if r.recipe == recipe)
    assert shop.buy(state, row)
    assert state.inventory.ammo_count("ammo_arrow") == before + CATALOG.ammo("ammo_arrow").pack
    assert state.inventory.materials == {}


def test_catalog_rejects_recipe_for_unknown_item():
    bad = CATALOG.recipes + [Recipe(kind=ItemKind.GEAR, item="jetpack", needs={ResourceKind.IRON: 1})]
    with pytest.raises(ValidationError):
        Catalog(**{**CATALOG.model_dump(), "recipes": bad})


def test_catalog_rejects_recipe_needing_cave():
    bad = CATALOG.recipes + [Recipe(kind=ItemKind.GEAR, item="helmet", needs={ResourceKind.CAVE: 1})]
    with pytest.raises(ValidationError):
        Catalog(**{**CATALOG.model_dump(), "recipes": bad})


# ---------- תיבות וגלגל ----------
def test_empty_crate_is_removed(state):
    crate = Crate(x=0, y=0, kind=CrateKind.EMPTY)
    state.level.crates.append(crate)
    crates.open_crate(state, crate)
    assert crate not in state.level.crates
    assert "ריקה" in state.feedback.message


def test_wheel_spins_down_and_pays_out(state):
    state.inventory.money = 1000
    wheel_system.spin(state)
    for _ in range(2000):
        wheel_system.update(state)
        if state.wheel.done:
            break
    assert state.wheel.done and state.wheel.text
    wheel_system.close(state)
    assert state.wheel is None


def test_wheel_heal_outcome(state):
    state.player.hp = 5
    slice_ = next(s for s in CATALOG.wheel_slices if s.id == WheelOutcome.HEAL)
    wheel_system.apply(state, slice_)
    assert state.player.hp == state.player.max_hp


def test_wheel_weapon_respects_rank(state):
    slice_ = next(s for s in CATALOG.wheel_slices if s.id == WheelOutcome.WEAPON)
    for _ in range(40):
        wheel_system.apply(state, slice_)
    assert state.inventory.weapons
    assert all(CATALOG.unlock_rank(w) is None for w in state.inventory.weapons)
    assert "הדרגה שלך" in wheel_system.apply(state, slice_)   # כל הנשק הפתוח כבר אצלך


def test_wheel_weapon_opens_up_with_rank(state):
    state.player.points = CATALOG.ranks[-1].points
    slice_ = next(s for s in CATALOG.wheel_slices if s.id == WheelOutcome.WEAPON)
    for _ in range(60):
        wheel_system.apply(state, slice_)
    assert any(CATALOG.unlock_rank(w) is not None for w in state.inventory.weapons)


# ---------- סימולציה ----------
def test_simulation_runs_many_frames(state):
    random.seed(7)
    state = progression.new_game()
    for frame in range(600):
        state.now = frame * 16
        simulation.step(state, PlayerInput(dx=1, dy=1, shoot=True, interact=True))
        if state.game_over:
            break
    assert state.player.x > 0


def test_paused_while_shop_open(state):
    x = state.player.x
    simulation.step(state, PlayerInput(dx=1), window_open=True)
    assert state.player.x == x
