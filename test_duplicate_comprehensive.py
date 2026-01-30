#!/usr/bin/env python3
"""Comprehensive test of duplicate item coloring in character sheet context"""

def simulate_character_sheet_coloring(items, equipped_weapon=None, equipped_armor=None, equipped_shield=None):
    """Simulate the exact coloring logic from character_sheet.py"""
    
    text_color = "#2D1B3D"  # Black
    grayed_color = "#A9A9A9"  # Gray
    
    # Simulate WEAPONS and ARMORS dictionaries
    WEAPONS = {
        "Longsword", "Greataxe", "Mace", "Dagger", "Shortsword",
        "Shortbow", "Longbow", "Crossbow", "Spear", "Halberd"
    }
    ARMORS = {
        "Leather Armor", "Shield", "Plate Mail", "Chain Mail", "Helm"
    }
    
    # Count item occurrences
    item_counts = {}
    for item in items:
        item_name = item
        if '(' in item:
            item_name = item.split('(')[0].strip()
        elif ' x ' in item:
            item_name = item.split(' x ')[0].strip()
        
        item_counts[item_name] = item_counts.get(item_name, 0) + 1
    
    # Apply colors to each item
    item_colors = {}
    for item in items:
        item_name = item
        if '(' in item:
            item_name = item.split('(')[0].strip()
        elif ' x ' in item:
            item_name = item.split(' x ')[0].strip()
        
        if item_name not in item_colors:
            # Determine color
            color = text_color  # Default
            is_duplicate = item_counts.get(item_name, 0) > 1
            
            if item_name in WEAPONS:
                is_equipped = item_name == equipped_weapon
                if is_duplicate and not is_equipped:
                    color = grayed_color
                elif not is_duplicate:
                    color = text_color if is_equipped else grayed_color
            elif item_name in ARMORS:
                is_equipped = (item_name == equipped_armor or item_name == equipped_shield)
                if is_duplicate and not is_equipped:
                    color = grayed_color
                elif not is_duplicate:
                    color = text_color if is_equipped else grayed_color
            
            item_colors[item_name] = {
                'color': color,
                'is_duplicate': is_duplicate,
                'count': item_counts[item_name]
            }
    
    return item_colors

def test_scenario_1():
    """Test: 2 Greataxes, first one equipped"""
    print("\nScenario 1: Two Greataxes (first one equipped)")
    print("-" * 60)
    
    items = [
        "Greataxe (2 slots)",
        "Greataxe (2 slots)"
    ]
    colors = simulate_character_sheet_coloring(
        items,
        equipped_weapon="Greataxe"
    )
    
    print(f"Items: {items}")
    print(f"Equipped weapon: Greataxe\n")
    
    for item_name, info in colors.items():
        color_name = "BLACK" if info['color'] == "#2D1B3D" else "GRAY"
        print(f"  {item_name}:")
        print(f"    - Count: {info['count']}")
        print(f"    - Is duplicate: {info['is_duplicate']}")
        print(f"    - Color: {color_name}")
    
    # Verify
    assert colors["Greataxe"]['color'] == "#2D1B3D", "Equipped duplicate should be black"
    print("\n  ✓ All Greataxes are black (equipped)")

def test_scenario_2():
    """Test: 2 Greataxes, none equipped"""
    print("\nScenario 2: Two Greataxes (none equipped)")
    print("-" * 60)
    
    items = [
        "Greataxe (2 slots)",
        "Greataxe (2 slots)"
    ]
    colors = simulate_character_sheet_coloring(items)
    
    print(f"Items: {items}")
    print(f"Equipped weapon: None\n")
    
    for item_name, info in colors.items():
        color_name = "BLACK" if info['color'] == "#2D1B3D" else "GRAY"
        print(f"  {item_name}:")
        print(f"    - Count: {info['count']}")
        print(f"    - Is duplicate: {info['is_duplicate']}")
        print(f"    - Color: {color_name}")
    
    # Verify
    assert colors["Greataxe"]['color'] == "#A9A9A9", "Unequipped duplicates should be gray"
    print("\n  ✓ All Greataxes are gray (not equipped)")

def test_scenario_3():
    """Test: Mix of items with duplicates and singles"""
    print("\nScenario 3: Mixed items with duplicates")
    print("-" * 60)
    
    items = [
        "Longsword (1 slot)",      # Single, not equipped
        "Greataxe (2 slots)",       # Duplicate, equipped
        "Greataxe (2 slots)",       # Duplicate, equipped
        "Shield (1 slot)",          # Duplicate, equipped
        "Shield (1 slot)",          # Duplicate, equipped
        "Dagger (1 slot)"           # Single, not equipped
    ]
    colors = simulate_character_sheet_coloring(
        items,
        equipped_weapon="Greataxe",
        equipped_armor="Leather",
        equipped_shield="Shield"
    )
    
    print(f"Equipped weapon: Greataxe")
    print(f"Equipped shield: Shield\n")
    
    for item_name in sorted(colors.keys()):
        info = colors[item_name]
        color_name = "BLACK" if info['color'] == "#2D1B3D" else "GRAY"
        dup_marker = " [DUPLICATE]" if info['is_duplicate'] else ""
        print(f"  {item_name:15s}: {color_name:5s} ({info['count']} in inventory){dup_marker}")
    
    # Verify
    assert colors["Longsword"]['color'] == "#A9A9A9", "Single unequipped weapon should be gray"
    assert colors["Greataxe"]['color'] == "#2D1B3D", "Equipped duplicate should be black"
    assert colors["Shield"]['color'] == "#2D1B3D", "Equipped duplicate should be black"
    assert colors["Dagger"]['color'] == "#A9A9A9", "Single unequipped weapon should be gray"
    print("\n  ✓ All colors correct!")

def test_scenario_4():
    """Test: Multiple different duplicates"""
    print("\nScenario 4: Multiple duplicate weapons")
    print("-" * 60)
    
    items = [
        "Longsword (1 slot)",
        "Longsword (1 slot)",
        "Mace (1 slot)",
        "Mace (1 slot)",
        "Mace (1 slot)",
        "Dagger (1 slot)"
    ]
    colors = simulate_character_sheet_coloring(
        items,
        equipped_weapon="Longsword"
    )
    
    print(f"Equipped weapon: Longsword\n")
    
    for item_name in sorted(colors.keys()):
        info = colors[item_name]
        color_name = "BLACK" if info['color'] == "#2D1B3D" else "GRAY"
        dup_marker = " [DUPLICATE]" if info['is_duplicate'] else ""
        print(f"  {item_name:15s}: {color_name:5s} ({info['count']} in inventory){dup_marker}")
    
    # Verify
    assert colors["Longsword"]['color'] == "#2D1B3D", "Equipped duplicate should be black"
    assert colors["Mace"]['color'] == "#A9A9A9", "Unequipped duplicates should be gray"
    assert colors["Dagger"]['color'] == "#A9A9A9", "Single unequipped weapon should be gray"
    print("\n  ✓ Correct: Longsword black (equipped), Mace gray (duplicates), Dagger gray (single)")

def test_scenario_5():
    """Test: Armor and Shield duplicates"""
    print("\nScenario 5: Duplicate armor and shields")
    print("-" * 60)
    
    items = [
        "Leather Armor (1 slot)",
        "Leather Armor (1 slot)",
        "Shield (1 slot)",
        "Shield (1 slot)",
    ]
    colors = simulate_character_sheet_coloring(
        items,
        equipped_armor="Leather Armor",
        equipped_shield="Shield"
    )
    
    print(f"Equipped armor: Leather Armor")
    print(f"Equipped shield: Shield\n")
    
    for item_name in sorted(colors.keys()):
        info = colors[item_name]
        color_name = "BLACK" if info['color'] == "#2D1B3D" else "GRAY"
        print(f"  {item_name:20s}: {color_name:5s} ({info['count']} in inventory)")
    
    # Verify
    assert colors["Leather Armor"]['color'] == "#2D1B3D", "Equipped armor should be black"
    assert colors["Shield"]['color'] == "#2D1B3D", "Equipped shield should be black"
    print("\n  ✓ All armor and shields colored correctly!")

if __name__ == "__main__":
    print("=" * 60)
    print("COMPREHENSIVE DUPLICATE ITEM COLORING TEST")
    print("=" * 60)
    
    test_scenario_1()
    test_scenario_2()
    test_scenario_3()
    test_scenario_4()
    test_scenario_5()
    
    print("\n" + "=" * 60)
    print("✓ ALL SCENARIOS PASSED!")
    print("=" * 60)
