#!/usr/bin/env python3
"""Test duplicate Javelin coloring"""

def test_javelin_duplicates():
    """Test that duplicate Javelins are colored correctly"""
    print("=" * 60)
    print("Testing Javelin Duplicate Coloring")
    print("=" * 60)
    
    # Simulate the item counting logic
    items = [
        "Javelin (1 slot)",
        "Javelin (1 slot)",
        "Javelin (1 slot)"
    ]
    
    print(f"\nInventory: {len(items)} Javelins")
    
    # Count items (corrected logic)
    item_counts = {}
    for item in items:
        # Extract item name
        item_name = item
        if '(' in item:
            item_name = item.split('(')[0].strip()
        elif ' x ' in item:
            item_name = item.split(' x ')[0].strip()
        
        item_counts[item_name] = item_counts.get(item_name, 0) + 1
    
    print(f"Item counts: {item_counts}")
    
    # Verify
    assert "Javelin" in item_counts, "Javelin should be in counts"
    assert item_counts["Javelin"] == 3, f"Expected 3 Javelins, got {item_counts['Javelin']}"
    
    print(f"\n✓ Javelin count: {item_counts['Javelin']}")
    
    # Test coloring logic
    is_duplicate = item_counts.get("Javelin", 0) > 1
    equipped_weapon = "Javelin"
    
    print(f"✓ Is duplicate: {is_duplicate}")
    print(f"✓ Equipped: {equipped_weapon}")
    
    # Apply color logic
    if is_duplicate and equipped_weapon != "Javelin":
        color = "GRAY"
    elif not is_duplicate:
        color = "BLACK" if equipped_weapon == "Javelin" else "GRAY"
    else:
        color = "BLACK"  # duplicate and equipped
    
    print(f"✓ Color: {color}")
    assert color == "BLACK", "Equipped duplicate should be black"
    
    # Test when not equipped
    equipped_weapon = "Longsword"
    if is_duplicate and equipped_weapon != "Javelin":
        color = "GRAY"
    elif not is_duplicate:
        color = "BLACK" if equipped_weapon == "Javelin" else "GRAY"
    else:
        color = "BLACK"
    
    print(f"\nWhen Longsword equipped instead:")
    print(f"  Equipped: {equipped_weapon}")
    print(f"  Javelin color: {color}")
    assert color == "GRAY", "Unequipped duplicate should be gray"
    
    print("\n" + "=" * 60)
    print("✓ ALL JAVELIN TESTS PASSED!")
    print("=" * 60)

def test_old_vs_new_logic():
    """Compare old (buggy) vs new (fixed) counting logic"""
    print("\n" + "=" * 60)
    print("Comparing Old vs New Counting Logic")
    print("=" * 60)
    
    items = [
        "Javelin (1 slot)",
        "Javelin (1 slot)",
        "Dagger (1 slot)"
    ]
    
    # OLD LOGIC (buggy)
    print("\nOLD LOGIC (buggy):")
    gear_item_lines = {"Javelin": [1, 3], "Dagger": [5]}  # Simulated
    
    item_counts_old = {}
    for item_name in gear_item_lines.keys():
        item_counts_old[item_name] = 0
    
    for item in items:
        item_name = item.split('(')[0].strip()
        if item_name in item_counts_old:
            item_counts_old[item_name] += 1
    
    print(f"  Item counts: {item_counts_old}")
    print(f"  Javelin is duplicate: {item_counts_old.get('Javelin', 0) > 1}")
    
    # NEW LOGIC (fixed)
    print("\nNEW LOGIC (fixed):")
    item_counts_new = {}
    for item in items:
        item_name = item.split('(')[0].strip()
        item_counts_new[item_name] = item_counts_new.get(item_name, 0) + 1
    
    print(f"  Item counts: {item_counts_new}")
    print(f"  Javelin is duplicate: {item_counts_new.get('Javelin', 0) > 1}")
    
    # Verify
    assert item_counts_new["Javelin"] == 2, "Should count 2 Javelins"
    assert item_counts_new["Dagger"] == 1, "Should count 1 Dagger"
    
    print("\n✓ New logic counts correctly!")
    print("=" * 60)

if __name__ == "__main__":
    test_javelin_duplicates()
    test_old_vs_new_logic()
