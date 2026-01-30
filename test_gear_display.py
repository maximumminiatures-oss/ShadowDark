#!/usr/bin/env python3
"""Test multi-slot item display formatting"""

def format_gear_items(items):
    """Simulate the gear display logic"""
    output_lines = []
    current_line = 1
    
    for item in items:
        # Extract item name and slot count
        item_name = item
        slots = 1
        
        # Parse item format "ItemName (X slots)" or "ItemName (X slot)"
        if '(' in item and ')' in item:
            item_name = item.split('(')[0].strip()
            try:
                slots_part = item.split('(')[1].split(')')[0]
                slots = int(slots_part.split()[0])
            except:
                slots = 1
        elif ' x ' in item:
            # Stackable format "Item x N"
            item_name = item.split(' x ')[0].strip()
            slots = 1
        
        # For multi-slot items, format as main item with sub-bullets
        if slots > 1:
            # Main bullet with item name and colon
            output_lines.append(f"• {item_name}:")
            current_line += 1
            
            # Add sub-bullets for additional slots (plural form with lowercase)
            item_lower = item_name.lower()
            for _ in range(slots - 1):
                output_lines.append(f"•   {item_lower} is heavy")
                current_line += 1
        else:
            # Single-slot items display normally
            output_lines.append(f"• {item}")
            current_line += 1
    
    return output_lines

def test_single_greataxe():
    """Test single 2-slot greataxe"""
    print("Test 1: Single Greataxe (2 slots)")
    print("-" * 40)
    items = ["Greataxe (2 slots)"]
    output = format_gear_items(items)
    for line in output:
        print(line)
    print()

def test_two_greataxes_and_dagger():
    """Test 2 greataxes and dagger"""
    print("Test 2: Two Greataxes (2 slots each) + Dagger (1 slot)")
    print("-" * 40)
    items = [
        "Greataxe (2 slots)",
        "Greataxe (2 slots)",
        "Dagger (1 slot)"
    ]
    output = format_gear_items(items)
    for line in output:
        print(line)
    print(f"Total lines used: {len(output)}")
    print()

def test_mixed_items():
    """Test various item types"""
    print("Test 3: Mixed Items")
    print("-" * 40)
    items = [
        "Longsword (1 slot)",
        "Greataxe (2 slots)",
        "Shield (1 slot)",
        "Leather Armor (1 slot)",
        "Rope (1 slot)"
    ]
    output = format_gear_items(items)
    for line in output:
        print(line)
    print(f"Total lines used: {len(output)}")
    print()

def test_with_empty_slots():
    """Test with empty slots shown"""
    print("Test 4: Items with Empty Slots")
    print("-" * 40)
    items = [
        "Greataxe (2 slots)",
        "Dagger (1 slot)"
    ]
    output = format_gear_items(items)
    
    # Add empty slots
    for i in range(6):
        output.append("•")
    
    for line in output:
        print(line)
    print(f"Total lines: {len(output)} (items: 3 lines, empty: 6 lines)")
    print()

def test_slot_counting():
    """Test that slot counting works correctly"""
    print("Test 5: Slot Counting")
    print("-" * 40)
    
    def count_slots_from_items(items):
        """Count how many slots are used by items"""
        used = 0
        for item_str in items:
            if '(' in item_str and ')' in item_str:
                try:
                    slots_part = item_str.split('(')[1].split(')')[0]
                    slots = int(slots_part.split()[0])
                    used += slots
                except:
                    used += 1
            elif ' x ' in item_str:
                used += 1
            elif item_str.strip():
                used += 1
        return used
    
    test_cases = [
        (["Greataxe (2 slots)"], 2),
        (["Greataxe (2 slots)", "Dagger (1 slot)"], 3),
        (["Greataxe (2 slots)", "Greataxe (2 slots)", "Dagger (1 slot)"], 5),
        (["Longsword (1 slot)", "Shield (1 slot)", "Rope (1 slot)"], 3),
    ]
    
    for items, expected in test_cases:
        actual = count_slots_from_items(items)
        status = "✓" if actual == expected else "✗"
        print(f"{status} {items}: {actual} slots (expected {expected})")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("MULTI-SLOT ITEM DISPLAY FORMATTING TEST")
    print("=" * 50)
    print()
    
    test_single_greataxe()
    test_two_greataxes_and_dagger()
    test_mixed_items()
    test_with_empty_slots()
    test_slot_counting()
    
    print("=" * 50)
    print("✓ All tests complete!")
    print("=" * 50)
