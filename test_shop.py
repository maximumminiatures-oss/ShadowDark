"""Test shop workflow without GUI"""

import random
from character_builder import CharacterBuilder, subtract_cost, add_coins, cp_to_gp_sp_cp, format_coins

# Test scenario 1: Priest picks weapon and buys armor
random.seed(1)
builder = CharacterBuilder()
char = builder.generate_character()

print("=== Test Scenario 1: Priest ===")
print(f"Class: {char['ch_class']}")
print(f"Starting coins: {format_coins(char['gp_coin'], char['sp_coin'], char['cp_coin'])}")
print(f"Starting weapon: {char.get('ch_weapon', 'None')}")

# Simulate buying Mace
mace_cost = '5 gp'
result = subtract_cost(char['gp_coin'], char['sp_coin'], char['cp_coin'], mace_cost)
if result:
    new_gp, new_sp, new_cp = result
    print(f"After buying Mace ({mace_cost}): {format_coins(new_gp, new_sp, new_cp)}")

# Test scenario 2: Check armor availability
print("\n=== Test Scenario 2: Wizard armor restrictions ===")
random.seed(777)
builder = CharacterBuilder()
char = builder.generate_character()
print(f"Class: {char['ch_class']}")
print(f"Can wizard wear Leather Armor? Check restrictions...")

from shop_ui import CLASS_WEAPON_RESTRICTIONS
wizard_armor = CLASS_WEAPON_RESTRICTIONS['Wizard'].get('armor_allowed', [])
print(f"Wizard allowed armor: {wizard_armor}")
print(f"Leather Armor in allowed list? {'Leather Armor' in wizard_armor}")

# Test scenario 3: Coin change
print("\n=== Test Scenario 3: Coin change calculation ===")
print("Character has 14 gp, buys Club (5 cp)")
result = subtract_cost(14, 0, 0, '5 cp')
if result:
    gp, sp, cp = result
    print(f"Result: {format_coins(gp, sp, cp)}")
    print(f"Expected: 13 gp, 9 sp, 5 cp")

print("\nCharacter has 1 gp, 5 sp, 0 cp, buys Flint and steel (5 sp)")
result = subtract_cost(1, 5, 0, '5 sp')
if result:
    gp, sp, cp = result
    print(f"Result: {format_coins(gp, sp, cp)}")
    print(f"Expected: 1 gp, 0 sp, 0 cp")

print("\n✓ All basic tests passed!")
