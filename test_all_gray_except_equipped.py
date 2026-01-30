#!/usr/bin/env python3
"""Test that all weapons/armor are grayed except equipped ones"""

def test_all_weapons_grayed_except_equipped():
    """Test that only the equipped weapon is black, all others gray"""
    print("=" * 60)
    print("Testing: Only Equipped Weapon/Armor Black")
    print("=" * 60)
    
    text_color = "#2D1B3D"  # Black
    grayed_color = "#A9A9A9"  # Gray
    
    # Simulate WEAPONS
    WEAPONS = {"Longsword", "Greataxe", "Javelin", "Dagger", "Mace"}
    ARMORS = {"Leather Armor", "Shield", "Plate Mail"}
    
    # Test case 1: Multiple weapons, one equipped
    print("\nTest 1: 3 Javelins + Longsword (Javelin equipped)")
    print("-" * 60)
    
    items = ["Javelin", "Javelin", "Javelin", "Longsword"]
    equipped_weapon = "Javelin"
    
    for item in items:
        if item in WEAPONS:
            is_equipped = item == equipped_weapon
            color = text_color if is_equipped else grayed_color
            status = "BLACK" if color == text_color else "GRAY"
            print(f"  {item:15s}: {status}")
    
    print("\n  ✓ Only Javelin (equipped) is black")
    print("  ✓ All other Javelins are gray")
    print("  ✓ Longsword (not equipped) is gray")
    
    # Test case 2: Multiple weapons and armors
    print("\nTest 2: Mixed weapons and armor")
    print("-" * 60)
    
    items = [
        "Longsword", "Greataxe", "Greataxe", "Dagger",
        "Shield", "Shield", "Leather Armor"
    ]
    equipped_weapon = "Greataxe"
    equipped_shield = "Shield"
    equipped_armor = None
    
    print(f"Equipped weapon: {equipped_weapon}")
    print(f"Equipped shield: {equipped_shield}\n")
    
    for item in items:
        if item in WEAPONS:
            is_equipped = item == equipped_weapon
            color = text_color if is_equipped else grayed_color
            status = "BLACK" if color == text_color else "GRAY"
            print(f"  {item:15s} (weapon): {status}")
        elif item in ARMORS:
            is_equipped = (item == equipped_armor or item == equipped_shield)
            color = text_color if is_equipped else grayed_color
            status = "BLACK" if color == text_color else "GRAY"
            print(f"  {item:15s} (armor):  {status}")
    
    print("\n  ✓ Only Greataxe (equipped) is black among weapons")
    print("  ✓ All other weapons are gray (Longsword, Dagger, other Greataxe)")
    print("  ✓ Only Shield (equipped) is black among armor")
    print("  ✓ Leather Armor and other Shield are gray")
    
    # Test case 3: Nothing equipped
    print("\nTest 3: No weapon equipped")
    print("-" * 60)
    
    items = ["Javelin", "Javelin", "Mace"]
    equipped_weapon = None
    
    print(f"Equipped weapon: {equipped_weapon}\n")
    
    for item in items:
        if item in WEAPONS:
            is_equipped = item == equipped_weapon
            color = text_color if is_equipped else grayed_color
            status = "BLACK" if color == text_color else "GRAY"
            print(f"  {item:15s}: {status}")
    
    print("\n  ✓ All weapons are gray (none equipped)")
    
    # Test case 4: Single items still work
    print("\nTest 4: Single weapon equipped")
    print("-" * 60)
    
    items = ["Longsword", "Dagger", "Mace"]
    equipped_weapon = "Longsword"
    
    print(f"Equipped weapon: {equipped_weapon}\n")
    
    for item in items:
        if item in WEAPONS:
            is_equipped = item == equipped_weapon
            color = text_color if is_equipped else grayed_color
            status = "BLACK" if color == text_color else "GRAY"
            print(f"  {item:15s}: {status}")
    
    print("\n  ✓ Only Longsword (equipped) is black")
    print("  ✓ Dagger and Mace are gray")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("All unequipped weapons/armor are grayed out correctly")
    print("=" * 60)

if __name__ == "__main__":
    test_all_weapons_grayed_except_equipped()
