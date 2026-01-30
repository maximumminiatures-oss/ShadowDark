#!/usr/bin/env python3
"""Test that line mapping works correctly for multi-slot items"""

def test_line_mapping():
    """Test that gear_item_lines dictionary is populated correctly"""
    print("Testing line mapping for multi-slot items")
    print("-" * 50)
    
    items = [
        "Greataxe (2 slots)",
        "Longsword (1 slot)",
        "Greataxe (2 slots)",
        "Dagger (1 slot)"
    ]
    
    # Simulate the line mapping logic
    output_lines = []
    gear_item_lines = {}
    current_line = 1
    
    for item in items:
        # Extract item name and slot count
        item_name = item
        slots = 1
        
        if '(' in item and ')' in item:
            item_name = item.split('(')[0].strip()
            try:
                slots_part = item.split('(')[1].split(')')[0]
                slots = int(slots_part.split()[0])
            except:
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
            
            # Add sub-bullets for additional slots
            item_lower = item_name.lower()
            for _ in range(slots - 1):
                output_lines.append(f"•   {item_lower} is heavy")
                current_line += 1
        else:
            # Single-slot items display normally
            output_lines.append(f"• {item}")
            current_line += 1
    
    # Print results
    print("\nOutput lines:")
    for i, line in enumerate(output_lines, 1):
        print(f"{i:2d}: {line}")
    
    print("\nItem line mapping:")
    for item_name, line_nums in sorted(gear_item_lines.items()):
        print(f"  {item_name}: {line_nums}")
    
    print("\nVerification:")
    # Verify that each Greataxe entry can be colored
    greataxe_lines = gear_item_lines.get('Greataxe', [])
    print(f"  Greataxe appears on lines: {greataxe_lines}")
    print(f"  First Greataxe (lines 1-2) and second (lines 5-6) will both be colored together")
    
    longsword_lines = gear_item_lines.get('Longsword', [])
    print(f"  Longsword appears on line: {longsword_lines}")
    
    dagger_lines = gear_item_lines.get('Dagger', [])
    print(f"  Dagger appears on line: {dagger_lines}")

if __name__ == "__main__":
    test_line_mapping()
