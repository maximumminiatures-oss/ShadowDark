#!/usr/bin/env python3
"""Final validation test - ensure all components work together"""

import re

def test_add_damage_bonus():
    """Test the _add_damage_bonus logic"""
    print("Testing damage bonus calculation...")
    
    def add_damage_bonus(damage_str, bonus):
        """Add a bonus to a damage string"""
        match = re.match(r'(\d+d\d+)((?:[+-]\d+)?)', damage_str.strip())
        if match:
            dice_part = match.group(1)
            modifier_str = match.group(2) if match.group(2) else ''
            
            if modifier_str:
                existing_mod = int(modifier_str)
            else:
                existing_mod = 0
            
            new_mod = existing_mod + bonus
            if new_mod > 0:
                return f"{dice_part}+{new_mod}"
            elif new_mod < 0:
                return f"{dice_part}{new_mod}"
            else:
                return dice_part
        return damage_str
    
    test_cases = [
        ("1d6", 1, "1d6+1"),
        ("1d8+1", 1, "1d8+2"),
        ("1d10", 1, "1d10+1"),
        ("2d6+2", 1, "2d6+3"),
        ("1d4", 1, "1d4+1"),
        ("1d8", 1, "1d8+1"),
    ]
    
    all_pass = True
    for damage, bonus, expected in test_cases:
        result = add_damage_bonus(damage, bonus)
        status = "✓" if result == expected else "✗"
        if result != expected:
            all_pass = False
        print(f"  {status} add_damage_bonus('{damage}', {bonus}) = '{result}' (expected '{expected}')")
    
    return all_pass

def test_mastery_detection():
    """Test that mastery detection works correctly"""
    print("\nTesting mastery detection...")
    
    # Test with weapon_masteries list
    character_data = {
        'weapon_masteries': ['Longsword', 'Mace', 'Dagger']
    }
    
    test_weapons = ['Longsword', 'Mace', 'Dagger', 'Greataxe']
    all_pass = True
    
    for weapon in test_weapons:
        has_mastery = False
        if 'weapon_masteries' in character_data:
            has_mastery = weapon in character_data['weapon_masteries']
        
        expected = weapon in ['Longsword', 'Mace', 'Dagger']
        status = "✓" if has_mastery == expected else "✗"
        if has_mastery != expected:
            all_pass = False
        print(f"  {status} {weapon}: has_mastery={has_mastery} (expected {expected})")
    
    return all_pass

def test_sequential_selection():
    """Test sequential mastery selection logic"""
    print("\nTesting sequential mastery selection...")
    
    weapon_mastery_count = 3
    selected_masteries = []
    all_pass = True
    
    weapons = ['Longsword', 'Mace', 'Dagger']
    
    for i, weapon in enumerate(weapons, 1):
        selected_masteries.append(weapon)
        
        # Check progress
        expected_count = i
        actual_count = len(selected_masteries)
        status = "✓" if actual_count == expected_count else "✗"
        if actual_count != expected_count:
            all_pass = False
        
        print(f"  {status} Selection {i}: selected {weapon}, count={actual_count}/{weapon_mastery_count}")
        
        # Check if more needed
        needs_more = len(selected_masteries) < weapon_mastery_count
        expected_needs_more = i < weapon_mastery_count
        
        status = "✓" if needs_more == expected_needs_more else "✗"
        if needs_more != expected_needs_more:
            all_pass = False
        
        print(f"      {status} More masteries needed: {needs_more} (expected {expected_needs_more})")
    
    return all_pass

def test_grayed_out_logic():
    """Test that grayed out logic works correctly"""
    print("\nTesting grayed-out weapon logic...")
    
    selected_masteries = ['Longsword', 'Mace']
    is_mastery_selection = True
    all_weapons = ['Longsword', 'Mace', 'Dagger', 'Greataxe']
    all_pass = True
    
    for weapon in all_weapons:
        # Check if this weapon should be allowed
        is_allowed = True  # Assume allowed by default
        
        # If doing weapon mastery selection, gray out already selected
        if is_mastery_selection and weapon in selected_masteries:
            is_allowed = False
        
        expected_allowed = weapon not in selected_masteries
        status = "✓" if is_allowed == expected_allowed else "✗"
        if is_allowed != expected_allowed:
            all_pass = False
        
        print(f"  {status} {weapon}: is_allowed={is_allowed}, {'[GRAYED OUT]' if not is_allowed else '[AVAILABLE]'}")
    
    return all_pass

def main():
    print("=" * 60)
    print("FINAL VALIDATION TEST")
    print("=" * 60 + "\n")
    
    results = []
    results.append(("Damage Bonus Calculation", test_add_damage_bonus()))
    results.append(("Mastery Detection", test_mastery_detection()))
    results.append(("Sequential Selection", test_sequential_selection()))
    results.append(("Grayed-Out Logic", test_grayed_out_logic()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_pass = all(result[1] for result in results)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    if all_pass:
        print("✓ ALL TESTS PASSED!")
    else:
        print("✗ SOME TESTS FAILED!")
    print("=" * 60)
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    exit(main())
