#!/usr/bin/env python3
"""Comprehensive test of the new multi-slot gear display format"""

def simulate_gear_display(items, total_slots=10):
    """Simulate the complete gear display logic"""
    output_lines = []
    gear_item_lines = {}
    current_line = 1
    
    # Display gear items with bullet points
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
        
        # Track this item's line for click handling
        if item_name not in gear_item_lines:
            gear_item_lines[item_name] = []
        gear_item_lines[item_name].append(current_line)
        
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
    
    # Calculate used slots
    used_slots = 0
    for item in items:
        if '(' in item and ')' in item:
            try:
                slots_part = item.split('(')[1].split(')')[0]
                slots = int(slots_part.split()[0])
                used_slots += slots
            except:
                used_slots += 1
        elif ' x ' in item:
            used_slots += 1
        elif item.strip():
            used_slots += 1
    
    available_slots = total_slots - used_slots
    
    # Add empty bullet points for available slots
    for _ in range(available_slots):
        output_lines.append("•")
        current_line += 1
    
    return output_lines, gear_item_lines, used_slots

def test_scenario_1():
    """Test: Single Greataxe, 10 STR"""
    print("\n" + "=" * 60)
    print("Scenario 1: Single Greataxe with 10 STR (5 slots)")
    print("=" * 60)
    
    items = ["Greataxe (2 slots)"]
    output, mapping, used = simulate_gear_display(items, total_slots=5)
    
    print(f"\nUsed slots: {used}/5\n")
    for i, line in enumerate(output, 1):
        print(f"{i:2d}: {line}")
    
    print("\nItem line mapping:")
    for item, lines in sorted(mapping.items()):
        print(f"  {item}: lines {lines}")
    
    # Verify slot counting
    assert used == 2, f"Expected 2 slots, got {used}"
    assert len(output) == 5, f"Expected 5 lines (2 item + 3 empty), got {len(output)}"
    print("\n✓ Test passed!")

def test_scenario_2():
    """Test: 2 Greataxes and Dagger, 10 STR"""
    print("\n" + "=" * 60)
    print("Scenario 2: Two Greataxes + Dagger with 10 STR (5 slots)")
    print("=" * 60)
    
    items = [
        "Greataxe (2 slots)",
        "Greataxe (2 slots)",
        "Dagger (1 slot)"
    ]
    output, mapping, used = simulate_gear_display(items, total_slots=5)
    
    print(f"\nUsed slots: {used}/5\n")
    for i, line in enumerate(output, 1):
        print(f"{i:2d}: {line}")
    
    print("\nItem line mapping:")
    for item, lines in sorted(mapping.items()):
        print(f"  {item}: lines {lines}")
    
    # Verify
    assert used == 5, f"Expected 5 slots, got {used}"
    assert len(output) == 5, f"Expected 5 lines total (no empty), got {len(output)}"
    assert 'Greataxe' in mapping, "Greataxe should be in mapping"
    assert len(mapping['Greataxe']) == 2, "Should have 2 instances of Greataxe"
    print("\n✓ Test passed!")

def test_scenario_3():
    """Test: Mix of single and multi-slot items"""
    print("\n" + "=" * 60)
    print("Scenario 3: Mixed items with 15 STR (15 slots)")
    print("=" * 60)
    
    items = [
        "Longsword (1 slot)",
        "Greataxe (2 slots)",
        "Shield (1 slot)",
        "Crossbow (2 slots)",
        "Rope (1 slot)",
        "Rations x 3 (1 slot)",
    ]
    output, mapping, used = simulate_gear_display(items, total_slots=15)
    
    print(f"\nUsed slots: {used}/15\n")
    for i, line in enumerate(output, 1):
        print(f"{i:2d}: {line}")
    
    print("\nItem line mapping:")
    for item, lines in sorted(mapping.items()):
        print(f"  {item}: lines {lines}")
    
    # Verify
    assert used == 8, f"Expected 8 slots, got {used}"
    expected_lines = 8 + (15 - 8)  # items + empty slots
    assert len(output) == expected_lines, f"Expected {expected_lines} lines, got {len(output)}"
    print("\n✓ Test passed!")

def test_display_format():
    """Verify the exact format matches requirements"""
    print("\n" + "=" * 60)
    print("Format Verification: Exact display format check")
    print("=" * 60)
    
    items = [
        "Greataxe (2 slots)",
        "Dagger (1 slot)"
    ]
    output, _, _ = simulate_gear_display(items, total_slots=5)
    
    expected = [
        "• Greataxe:",
        "•   greataxe is heavy",
        "• Dagger (1 slot)",
        "•",
        "•"
    ]
    
    print("\nExpected format:")
    for line in expected:
        print(f"  {line}")
    
    print("\nActual format:")
    for line in output:
        print(f"  {line}")
    
    assert output == expected, "Format does not match expected"
    print("\n✓ Format verification passed!")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("COMPREHENSIVE GEAR DISPLAY TEST")
    print("=" * 60)
    
    test_scenario_1()
    test_scenario_2()
    test_scenario_3()
    test_display_format()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
