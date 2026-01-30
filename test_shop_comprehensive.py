"""Comprehensive test of the shop system"""

import random
from character_builder import (
    CharacterBuilder, 
    sell_item, 
    subtract_cost, 
    add_coins, 
    cp_to_gp_sp_cp, 
    format_coins
)
from shop_ui import CLASS_WEAPON_RESTRICTIONS

print("=" * 60)
print("COMPREHENSIVE SHOP SYSTEM TEST")
print("=" * 60)

# Test 1: Character generation with proper coin allocation
print("\nTest 1: Character Generation")
print("-" * 40)
for seed in [1, 42, 777, 100]:
    random.seed(seed)
    builder = CharacterBuilder()
    char = builder.generate_character()
    print(f"Seed {seed}: {char['ch_class']:8} - {format_coins(char['gp_coin'], char['sp_coin'], char['cp_coin']):20} - "
          f"Weapons slots: STR={char['STR_score']} (base slots)")
    assert char['gp_coin'] > 0, f"Seed {seed}: No gold coins generated!"

# Test 2: Weapon restrictions by class
print("\nTest 2: Weapon Restrictions by Class")
print("-" * 40)
test_weapons = ['Dagger', 'Longsword', 'Staff', 'Shortbow']
for char_class in ['Fighter', 'Priest', 'Thief', 'Wizard']:
    allowed = CLASS_WEAPON_RESTRICTIONS[char_class].get('allowed', [])
    if allowed is None:
        allowed = "All"
    else:
        allowed_weapons = [w for w in test_weapons if w in allowed]
        allowed = f"{len(allowed)} weapons: {', '.join(allowed_weapons)}"
    print(f"{char_class:8}: {allowed}")

# Test 3: Armor restrictions
print("\nTest 3: Armor Restrictions by Class")
print("-" * 40)
for char_class in ['Fighter', 'Priest', 'Thief', 'Wizard']:
    config = CLASS_WEAPON_RESTRICTIONS[char_class]
    if config.get('all_armor_allowed'):
        print(f"{char_class:8}: All armor allowed")
    else:
        allowed_armor = config.get('armor_allowed', [])
        if allowed_armor:
            print(f"{char_class:8}: {', '.join(allowed_armor)}")
        else:
            print(f"{char_class:8}: No armor allowed")

# Test 4: Coin arithmetic
print("\nTest 4: Coin Arithmetic")
print("-" * 40)
test_cases = [
    ((10, 0, 0), '5 gp', (5, 0, 0)),
    ((14, 0, 0), '5 cp', (13, 9, 5)),
    ((0, 10, 0), '5 sp', (0, 5, 0)),
    ((1, 5, 0), '5 sp', (1, 0, 0)),
]
for (gp, sp, cp), cost, expected in test_cases:
    result = subtract_cost(gp, sp, cp, cost)
    assert result == expected, f"Failed: {format_coins(gp, sp, cp)} - {cost} = {result}, expected {expected}"
    print(f"✓ {format_coins(gp, sp, cp)} - {cost:8} = {format_coins(*result)}")

# Test 5: Selling items
print("\nTest 5: Item Selling (Half Cost)")
print("-" * 40)
sell_tests = [
    ('5 cp', '2 cp', 'Club'),
    ('3 sp', '1 sp, 5 cp', 'Flask'),
    ('9 gp', '4 gp, 5 sp', 'Longsword'),
]
for cost_str, expected_str, item_name in sell_tests:
    refund_cp = sell_item(cost_str)
    refund_gp, refund_sp, refund_cp_final = cp_to_gp_sp_cp(refund_cp)
    refund_formatted = format_coins(refund_gp, refund_sp, refund_cp_final)
    assert refund_formatted == expected_str, f"Failed: {item_name} sell value {refund_formatted} != {expected_str}"
    print(f"✓ {item_name:12} ({cost_str:8}) sells for {refund_formatted}")

# Test 6: Weapon selection and attack building
print("\nTest 6: Weapon Selection and Attack Building")
print("-" * 40)
random.seed(42)
builder = CharacterBuilder()
char = builder.generate_character()
print(f"Generated {char['ch_class']} with no weapon assigned: {char.get('ch_weapon', 'None')}")
assert char.get('ch_weapon') is None, "Weapon should be None before shop selection"
assert char.get('ch_attacks') == [], "Attacks should be empty before weapon selection"
print(f"✓ No weapon assigned initially")
print(f"✓ Attacks list is empty: {char['ch_attacks']}")

# Simulate weapon selection
char['ch_weapon'] = 'Dagger'
char['equipped_weapon'] = 'Dagger'
builder._regenerate_attacks()
attacks = builder.character_data.get('ch_attacks', [])
assert len(attacks) > 0, "Attacks should be generated after weapon selection"
print(f"✓ After selecting Dagger: {len(attacks)} attack(s)")
for weapon, to_hit, damage, rng in attacks:
    print(f"  - {weapon}: {to_hit:+d} / {damage} / {rng}")

# Test 7: Slot availability
print("\nTest 7: Gear Slots")
print("-" * 40)
random.seed(10)
builder = CharacterBuilder()
char = builder.generate_character()
str_score = char['STR_score']
bonus_slots = 0
if char['ch_class'] == 'Fighter':
    con_mod = char.get('CON_mod', 0)
    if con_mod > 0:
        bonus_slots = con_mod
total_slots = str_score + bonus_slots
print(f"Class: {char['ch_class']}, STR: {str_score}, CON mod: {char.get('CON_mod', 0)}")
print(f"Total slots available: {total_slots}")

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
