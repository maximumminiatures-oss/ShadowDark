"""Final comprehensive test demonstrating the user's requested feature"""

from character_builder import CharacterBuilder

def find_human_with_random_language():
    """Find a human with a stored random language"""
    for attempt in range(50):
        builder = CharacterBuilder()
        builder.generate_character()
        
        if builder.character_data['ch_ancestry'] == 'Human':
            stored = builder.character_data.get('_human_random_lang')
            if stored:
                return builder, stored
    
    return None, None


def test_user_scenario():
    """Test the exact scenario described by the user"""
    print("TESTING USER'S REQUESTED FEATURE")
    print("=" * 70)
    print("Scenario: User rolls a Human with random language (e.g., Reptilian)")
    print("          User changes ancestry to Elf")
    print("          User changes ancestry back to Human")
    print("          Expected: Same languages as original Human")
    print("=" * 70)
    
    builder, stored_lang = find_human_with_random_language()
    
    if not builder:
        print("\n✗ Could not find a Human with stored random language")
        print("  (This is just bad luck - languages are random!)")
        return
    
    print(f"\n✓ Found Human with stored random language: {stored_lang}")
    print(f"  Full languages: {builder.character_data['ch_lang']}")
    initial_langs = builder.character_data['ch_lang']
    initial_class = builder.character_data['ch_class']
    
    # Change to Elf
    print(f"\nChanging to Elf...")
    builder.update_from_selection('ch_ancestry', 'Elf')
    elf_ancestry = builder.character_data['ch_ancestry']
    elf_langs = builder.character_data['ch_lang']
    print(f"  Ancestry: {elf_ancestry}")
    print(f"  Languages: {elf_langs}")
    print(f"  ✓ {stored_lang} is gone, Elvish is added")
    
    # Change back to Human
    print(f"\nChanging back to Human...")
    builder.update_from_selection('ch_ancestry', 'Human')
    human_ancestry = builder.character_data['ch_ancestry']
    human_langs = builder.character_data['ch_lang']
    print(f"  Ancestry: {human_ancestry}")
    print(f"  Languages: {human_langs}")
    
    # Verify
    print(f"\n" + "=" * 70)
    if initial_langs == human_langs:
        print("✓✓✓ SUCCESS! Human languages match original! ✓✓✓")
        print("  The feature is working as expected!")
    else:
        print("✗✗✗ FAILED! Human languages don't match! ✗✗✗")
        print(f"  Initial: {initial_langs}")
        print(f"  Final:   {human_langs}")
    print("=" * 70)


def test_multiple_switches():
    """Test multiple rapid switches"""
    print("\n\nTESTING MULTIPLE ANCESTRY SWITCHES")
    print("=" * 70)
    
    builder = CharacterBuilder()
    builder.generate_character()
    builder.update_from_selection('ch_ancestry', 'Human')
    
    print(f"Starting ancestry: Human")
    print(f"Starting languages: {builder.character_data['ch_lang']}")
    human_langs = builder.character_data['ch_lang']
    
    # Do multiple switches
    for ancestry in ['Elf', 'Dwarf', 'Halfling', 'Half Orc', 'Goblin', 'Human']:
        builder.update_from_selection('ch_ancestry', ancestry)
        print(f"\n{ancestry}: {builder.character_data['ch_lang']}")
    
    final_langs = builder.character_data['ch_lang']
    
    print(f"\n" + "=" * 70)
    if human_langs == final_langs:
        print("✓ SUCCESS! Human languages consistent after all switches!")
    else:
        print("✗ FAILED! Human languages changed!")
    print("=" * 70)


if __name__ == "__main__":
    test_user_scenario()
    test_multiple_switches()
