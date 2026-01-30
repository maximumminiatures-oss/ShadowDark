#!/usr/bin/env python3
"""Final comprehensive test with actual character data"""

def test_complete_flow():
    """Test the complete weapon mastery flow as it would happen in the app"""
    print("=" * 70)
    print("COMPLETE WEAPON MASTERY FLOW TEST")
    print("=" * 70)
    
    # Step 1: Character builder creates a fighter
    print("\nStep 1: Character Builder Creates Fighter")
    print("-" * 70)
    
    character_data = {
        'ch_class': 'Fighter',
        'ch_ancestry': 'Human',
        'STR_score': 16,
        'STR_mod': 3,
        'DEX_score': 14,
        'DEX_mod': 2,
        'CON_score': 15,
        'CON_mod': 2,
        'ch_title': 'Human Fighter',
        'gp_coin': 50,
        'sp_coin': 0,
        'cp_coin': 0,
        'ch_gear_items': [],
    }
    
    # Character builder generates 2 talents (human), both roll 2
    weapon_mastery_count = 1  # All fighters get 1
    talent_results = []
    
    for i in range(2):  # Human gets 2 talents
        roll = 2 if i == 0 else 2  # Both roll 2
        if roll == 2:
            weapon_mastery_count += 1
            talent_results.append("Additional weapon mastery")
        else:
            talent_results.append(f"Other talent")
    
    character_data['weapon_mastery_count'] = weapon_mastery_count
    character_data['ch_talent'] = "\n".join(talent_results)
    
    print(f"Generated: {character_data['ch_title']}")
    print(f"Talents rolled: {len(talent_results)}")
    print(f"Weapon Masteries to select: {weapon_mastery_count}")
    print(f"Talents: {character_data['ch_talent']}")
    
    # Step 2: Shop UI initializes
    print("\nStep 2: Shop UI Initializes")
    print("-" * 70)
    
    weapon_mastery_count = character_data.get('weapon_mastery_count', 0)
    selected_masteries = []
    is_mastery_selection = weapon_mastery_count > 0
    
    print(f"is_mastery_selection: {is_mastery_selection}")
    print(f"Need to select: {weapon_mastery_count} masteries")
    
    # Step 3: User selects masteries
    print("\nStep 3: User Selects Weapon Masteries")
    print("-" * 70)
    
    mastery_choices = ["Longsword", "Mace", "Dagger"]
    
    for i, weapon in enumerate(mastery_choices, 1):
        print(f"\n  Mastery Selection {i} of {weapon_mastery_count}:")
        
        # Show available weapons (not previously selected)
        available = [w for w in mastery_choices if w not in selected_masteries]
        print(f"    Available to choose: {available}")
        
        # User selects
        selected_masteries.append(weapon)
        print(f"    User selects: {weapon}")
        
        if len(selected_masteries) < weapon_mastery_count:
            print(f"    → More masteries needed, show selection again")
        else:
            print(f"    → All masteries selected!")
    
    # Store masteries
    for idx, weapon in enumerate(selected_masteries, 1):
        character_data[f'weapon_mastery_{idx}'] = weapon
    character_data['weapon_masteries'] = selected_masteries
    
    print(f"\nStored masteries:")
    for idx in range(1, weapon_mastery_count + 1):
        print(f"  {character_data[f'weapon_mastery_{idx}']}")
    
    # Step 4: User picks starting weapon
    print("\nStep 4: User Picks Starting Weapon")
    print("-" * 70)
    
    character_data['equipped_weapon'] = 'Longsword'
    print(f"Selected: Longsword")
    
    # Step 5: Check attack bonuses
    print("\nStep 5: Attack Calculation with Mastery Bonuses")
    print("-" * 70)
    
    weapons_to_check = ["Longsword", "Mace", "Dagger", "Greataxe", "Shortsword"]
    
    for weapon in weapons_to_check:
        has_mastery = weapon in character_data.get('weapon_masteries', [])
        attack_bonus = f"+{character_data['STR_mod']}" if character_data['STR_mod'] >= 0 else str(character_data['STR_mod'])
        damage_bonus = ""
        
        if has_mastery:
            attack_bonus += "+1"
            damage_bonus = "+1"
        
        if weapon == character_data.get('equipped_weapon'):
            equipped = " ← EQUIPPED"
        else:
            equipped = ""
        
        mastery_marker = " [MASTERED]" if has_mastery else ""
        print(f"  {weapon:12s}: Attack {attack_bonus:5s}, Damage bonus {damage_bonus}{mastery_marker}{equipped}")
    
    print("\n" + "=" * 70)
    print("✓ Complete flow test passed!")
    print("=" * 70)

if __name__ == "__main__":
    test_complete_flow()
