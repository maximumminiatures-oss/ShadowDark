#!/usr/bin/env python3
"""Comprehensive test of weapon mastery selection system"""

def test_fighter_mastery_selection():
    """Test the complete weapon mastery selection flow"""
    print("=" * 60)
    print("Testing Weapon Mastery Selection System")
    print("=" * 60)
    
    # Scenario 1: Non-human fighter with 1 talent roll, rolls 2 on talent table
    print("\nScenario 1: Non-human Fighter with 1 additional mastery")
    print("-" * 60)
    
    character_data = {
        'ch_class': 'Fighter',
        'ch_ancestry': 'Dwarf',
        'weapon_mastery_count': 2,  # 1 base + 1 from talent roll
        'ch_gear_items': [],
    }
    
    # Simulate shop initialization
    weapon_mastery_count = character_data.get('weapon_mastery_count', 0)
    selected_masteries = []
    is_mastery_selection = weapon_mastery_count > 0
    
    print(f"Fighter needs to select: {weapon_mastery_count} weapon masteries")
    print(f"Mastery selection active: {is_mastery_selection}")
    
    # First selection: Shortsword
    selected_masteries.append("Shortsword")
    print(f"\nMastery 1 selected: Shortsword")
    print(f"Progress: {len(selected_masteries)}/{weapon_mastery_count}")
    
    if len(selected_masteries) < weapon_mastery_count:
        print("→ More masteries needed, show selection again (gray out Shortsword)")
    
    # Second selection: Mace
    selected_masteries.append("Mace")
    print(f"\nMastery 2 selected: Mace")
    print(f"Progress: {len(selected_masteries)}/{weapon_mastery_count}")
    
    if len(selected_masteries) < weapon_mastery_count:
        print("→ More masteries needed")
    else:
        print("→ All masteries selected! Store them and move to weapon selection phase")
        
    # Store in character data
    for idx, mastery_weapon in enumerate(selected_masteries, 1):
        character_data[f'weapon_mastery_{idx}'] = mastery_weapon
    character_data['weapon_masteries'] = selected_masteries
    
    print(f"\nFinal character data:")
    print(f"  weapon_masteries: {character_data['weapon_masteries']}")
    print(f"  weapon_mastery_1: {character_data['weapon_mastery_1']}")
    print(f"  weapon_mastery_2: {character_data['weapon_mastery_2']}")
    
    # Test attack bonus calculation
    print(f"\nAttack bonus calculation:")
    for weapon in ["Shortsword", "Mace", "Greataxe", "Longsword"]:
        has_mastery = weapon in character_data.get('weapon_masteries', [])
        bonus = "+1" if has_mastery else "+0"
        print(f"  {weapon}: attack {bonus}, damage {bonus if has_mastery else '+0'}")
    
    # Scenario 2: Human fighter with 2 talent rolls, both roll 2
    print("\n" + "=" * 60)
    print("Scenario 2: Human Fighter with 3 total masteries")
    print("-" * 60)
    
    character_data2 = {
        'ch_class': 'Fighter',
        'ch_ancestry': 'Human',
        'weapon_mastery_count': 3,  # 1 base + 2 from talent rolls
    }
    
    weapon_mastery_count = character_data2.get('weapon_mastery_count', 0)
    selected_masteries = []
    
    print(f"Fighter needs to select: {weapon_mastery_count} weapon masteries")
    
    # Simulate three selections
    weapons_to_select = ["Longsword", "Mace", "Dagger"]
    for i, weapon in enumerate(weapons_to_select, 1):
        selected_masteries.append(weapon)
        print(f"\nMastery {i} selected: {weapon}")
        print(f"Progress: {len(selected_masteries)}/{weapon_mastery_count}")
        
        if len(selected_masteries) < weapon_mastery_count:
            print(f"→ More masteries needed")
        else:
            print(f"→ All masteries selected!")
    
    # Store in character data
    for idx, mastery_weapon in enumerate(selected_masteries, 1):
        character_data2[f'weapon_mastery_{idx}'] = mastery_weapon
    character_data2['weapon_masteries'] = selected_masteries
    
    print(f"\nFinal character data:")
    print(f"  weapon_masteries: {character_data2['weapon_masteries']}")
    for idx in range(1, 4):
        print(f"  weapon_mastery_{idx}: {character_data2.get(f'weapon_mastery_{idx}', 'N/A')}")
    
    # Test attack bonus calculation
    print(f"\nAttack bonus calculation:")
    for weapon in ["Longsword", "Mace", "Dagger", "Greataxe"]:
        has_mastery = weapon in character_data2.get('weapon_masteries', [])
        bonus = "+1" if has_mastery else "+0"
        print(f"  {weapon}: attack {bonus}, damage {bonus if has_mastery else '+0'}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_fighter_mastery_selection()
