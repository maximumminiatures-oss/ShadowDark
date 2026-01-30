#!/usr/bin/env python3
"""Test weapon mastery selection flow for fighters"""

# Test the mastery selection logic
def test_mastery_flow():
    """Test that fighters with multiple masteries can select them sequentially"""
    
    # Simulate a fighter with 2 weapon masteries
    selected_masteries = []
    weapon_mastery_count = 2
    
    # Simulate selecting Shortsword as first mastery
    selected_masteries.append("Shortsword")
    print(f"Selected mastery 1: {selected_masteries[0]}")
    print(f"Masteries selected: {len(selected_masteries)}/{weapon_mastery_count}")
    
    # Check if more needed
    if len(selected_masteries) < weapon_mastery_count:
        print("More masteries needed - showing selection again")
        # In real code, this would call show_weapon_selection() again
        # Gray out already selected weapons
        print(f"Already selected: {selected_masteries}")
    
    # Simulate selecting Mace as second mastery
    selected_masteries.append("Mace")
    print(f"\nSelected mastery 2: {selected_masteries[1]}")
    print(f"Masteries selected: {len(selected_masteries)}/{weapon_mastery_count}")
    
    # Check if more needed
    if len(selected_masteries) < weapon_mastery_count:
        print("More masteries needed - showing selection again")
    else:
        print("All masteries selected!")
        print(f"Final masteries: {selected_masteries}")
    
    # Simulate storing in character_data
    character_data = {}
    for idx, mastery_weapon in enumerate(selected_masteries, 1):
        character_data[f'weapon_mastery_{idx}'] = mastery_weapon
    character_data['weapon_masteries'] = selected_masteries
    
    print(f"\nCharacter data: {character_data}")
    
    # Test that attack calculation checks all masteries
    weapon_name = "Shortsword"
    has_mastery = False
    if 'weapon_masteries' in character_data:
        has_mastery = weapon_name in character_data['weapon_masteries']
    
    print(f"\nShortword has mastery bonus: {has_mastery}")
    
    weapon_name = "Mace"
    has_mastery = False
    if 'weapon_masteries' in character_data:
        has_mastery = weapon_name in character_data['weapon_masteries']
    
    print(f"Mace has mastery bonus: {has_mastery}")
    
    weapon_name = "Greataxe"
    has_mastery = False
    if 'weapon_masteries' in character_data:
        has_mastery = weapon_name in character_data['weapon_masteries']
    
    print(f"Greataxe has mastery bonus: {has_mastery}")

if __name__ == "__main__":
    test_mastery_flow()
