"""
Test script for stackable items feature
"""

import sys
sys.path.insert(0, 'c:\\SD_game')

from character_builder import CharacterBuilder


def test_stackable_items():
    """Test stackable item addition"""
    builder = CharacterBuilder()
    
    # Create a test character
    char_data = builder.generate_character()
    gear = char_data.setdefault('ch_gear_items', [])
    
    # Get arrow item data
    arrows = builder.EQUIPMENT['Arrow']
    print(f"Arrow data: {arrows}")
    print(f"  - Cost: {arrows['cost']}")
    print(f"  - slots_per: {arrows['slots_per']}")
    print()
    
    # Simulate buying arrows multiple times
    print("Buying arrows one at a time:")
    for i in range(1, 25):
        builder.add_stackable_item(gear, 'Arrow', arrows)
        print(f"  After purchase {i}: {gear[-1] if i <= 1 or ' x 1' in gear[-1] else gear[len(gear)-1]}")
        # Show the relevant gear items
        arrow_items = [g for g in gear if 'Arrow' in g]
        print(f"    Current Arrow slots: {arrow_items}")
    
    print("\n" + "="*60)
    print("Final gear list:")
    for idx, item in enumerate(gear):
        print(f"  [{idx}] {item}")
    
    print("\n" + "="*60)
    print("Test stackable items with rations:")
    rations = builder.EQUIPMENT['Ration, per day']
    print(f"Ration data: {rations}")
    print(f"  - Cost: {rations['cost']}")
    print(f"  - slots_per: {rations['slots_per']}")
    
    gear2 = []
    for i in range(1, 10):
        builder.add_stackable_item(gear2, 'Ration, per day', rations)
        ration_items = [g for g in gear2 if 'Ration' in g]
        print(f"  After purchase {i}: {ration_items}")
    
    print("\n" + "="*60)
    print("Final ration gear list:")
    for item in gear2:
        print(f"  - {item}")


if __name__ == '__main__':
    test_stackable_items()
