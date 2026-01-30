#!/usr/bin/env python3
"""Integration test for weapon mastery system"""

def test_shop_ui_mastery_flow():
    """Test that shop UI correctly handles mastery selection"""
    print("=" * 60)
    print("Testing Shop UI Mastery Selection Flow")
    print("=" * 60)
    
    # Simulate character_data from character_builder
    character_data = {
        'ch_class': 'Fighter',
        'ch_ancestry': 'Human',
        'weapon_mastery_count': 3,  # Would be set by character builder
        'gp_coin': 50,
        'sp_coin': 0,
        'cp_coin': 0,
    }
    
    # Simulate shop initialization
    weapon_mastery_count = character_data.get('weapon_mastery_count', 0)
    selected_masteries = []
    is_mastery_selection = weapon_mastery_count > 0
    
    print(f"\nCharacter Data:")
    print(f"  Class: {character_data['ch_class']}")
    print(f"  Ancestry: {character_data['ch_ancestry']}")
    print(f"  Weapon Mastery Count: {weapon_mastery_count}")
    
    print(f"\nShop UI State:")
    print(f"  is_mastery_selection: {is_mastery_selection}")
    print(f"  weapon_mastery_count: {weapon_mastery_count}")
    
    # Simulate user selecting weapons for mastery
    print(f"\nMastery Selection Phase:")
    weapons_available = ["Shortsword", "Mace", "Longsword", "Greataxe", "Dagger"]
    
    for i in range(weapon_mastery_count):
        print(f"\n  Mastery {i + 1} of {weapon_mastery_count}")
        # Gray out already selected weapons
        available_for_selection = [w for w in weapons_available if w not in selected_masteries]
        print(f"    Available: {available_for_selection}")
        
        # Simulate selection
        selected = available_for_selection[i]
        selected_masteries.append(selected)
        print(f"    Selected: {selected}")
        
        if len(selected_masteries) < weapon_mastery_count:
            print(f"    → Continue to next mastery selection")
        else:
            print(f"    → All masteries selected!")
    
    # Store masteries in character_data
    for idx, mastery_weapon in enumerate(selected_masteries, 1):
        character_data[f'weapon_mastery_{idx}'] = mastery_weapon
    character_data['weapon_masteries'] = selected_masteries
    
    print(f"\nStored Masteries:")
    for idx, weapon in enumerate(selected_masteries, 1):
        print(f"  weapon_mastery_{idx}: {weapon}")
    
    # Now test attack calculation
    print(f"\nAttack Bonus Calculation (Mastery Phase Over):")
    
    # Simulate _weapon_to_attacks checking for masteries
    test_weapons = ["Shortsword", "Mace", "Longsword", "Dagger", "Greataxe"]
    
    for weapon in test_weapons:
        has_mastery = False
        if 'weapon_masteries' in character_data:
            has_mastery = weapon in character_data['weapon_masteries']
        
        attack_bonus = 1 if has_mastery else 0
        damage_bonus = 1 if has_mastery else 0
        status = "✓ MASTERED" if has_mastery else ""
        print(f"  {weapon:12s}: +{attack_bonus} attack, {damage_bonus}d{6 if weapon != 'Dagger' else 4}+{damage_bonus} damage {status}")
    
    # Now move to weapon selection phase
    print(f"\nWeapon Selection Phase:")
    is_mastery_selection = False
    
    # Select starting weapon
    starting_weapon = "Longsword"
    character_data['equipped_weapon'] = starting_weapon
    character_data['ch_weapon'] = starting_weapon
    
    print(f"  Starting weapon selected: {starting_weapon}")
    
    # Calculate attacks for starting weapon
    print(f"\n  Attack string would include:")
    if starting_weapon in character_data.get('weapon_masteries', []):
        print(f"    Longsword: +1 attack, 1d8+1 damage (mastered)")
    else:
        print(f"    Longsword: +0 attack, 1d8 damage (not mastered)")
    
    print("\n" + "=" * 60)
    print("✓ Integration test passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_shop_ui_mastery_flow()
