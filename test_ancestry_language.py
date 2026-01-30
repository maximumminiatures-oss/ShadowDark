"""Test script to verify ancestry language persistence feature"""

from character_builder import CharacterBuilder

def test_human_language_persistence():
    """Test that human languages persist when switching back"""
    print("Test: Human Language Persistence")
    print("=" * 50)
    
    builder = CharacterBuilder()
    builder.generate_character()
    
    # Check if character is human
    ancestry = builder.character_data['ch_ancestry']
    initial_lang = builder.character_data['ch_lang']
    
    print(f"Initial Ancestry: {ancestry}")
    print(f"Initial Languages: {initial_lang}")
    
    if ancestry == "Human":
        stored_human_lang = builder.character_data.get('_human_random_lang')
        print(f"Stored Human Random Language: {stored_human_lang}")
        
        # Change to Elf
        print("\nChanging to Elf...")
        builder.update_from_selection('ch_ancestry', 'Elf')
        elf_ancestry = builder.character_data['ch_ancestry']
        elf_lang = builder.character_data['ch_lang']
        print(f"After change - Ancestry: {elf_ancestry}")
        print(f"After change - Languages: {elf_lang}")
        print(f"  (Elf gets Elvish instead of Human's {stored_human_lang})")
        
        # Change back to Human
        print("\nChanging back to Human...")
        builder.update_from_selection('ch_ancestry', 'Human')
        final_ancestry = builder.character_data['ch_ancestry']
        final_lang = builder.character_data['ch_lang']
        print(f"After change back - Ancestry: {final_ancestry}")
        print(f"After change back - Languages: {final_lang}")
        
        # Verify we got the same languages back
        if initial_lang == final_lang:
            print("\n✓ SUCCESS: Languages match after switching back to Human!")
        else:
            print(f"\n✗ FAILED: Languages don't match!")
            print(f"  Initial: {initial_lang}")
            print(f"  Final:   {final_lang}")
    else:
        print(f"\nCharacter is {ancestry}, not Human. Skipping test.")
        print("Trying to force change to Human...")
        builder.update_from_selection('ch_ancestry', 'Human')
        human_lang_1 = builder.character_data['ch_lang']
        stored = builder.character_data.get('_human_random_lang')
        print(f"New Human Languages: {human_lang_1}")
        print(f"Stored random language: {stored}")
        
        # Now try the sequence
        print("\nChanging to Elf...")
        builder.update_from_selection('ch_ancestry', 'Elf')
        elf_lang = builder.character_data['ch_lang']
        print(f"Elf Languages: {elf_lang}")
        print(f"  (Now has Elvish instead of {stored})")
        
        print("\nChanging back to Human...")
        builder.update_from_selection('ch_ancestry', 'Human')
        human_lang_2 = builder.character_data['ch_lang']
        print(f"Human Languages (back): {human_lang_2}")
        
        if human_lang_1 == human_lang_2:
            print("\n✓ SUCCESS: Human languages restored after switching back!")
        else:
            print(f"\n✗ FAILED: Human languages don't match!")


def test_exact_user_scenario():
    """Test the exact scenario the user described"""
    print("\n\nTest: User's Exact Scenario")
    print("=" * 50)
    print("Scenario: Roll human with Common + Reptilian")
    print("Switch to Elf -> should have Common + Elvish")
    print("Switch back to Human -> should have Common + Reptilian")
    
    # Create multiple builders until we get one with the desired languages
    found = False
    attempts = 0
    while not found and attempts < 20:
        attempts += 1
        builder = CharacterBuilder()
        builder.generate_character()
        
        if builder.character_data['ch_ancestry'] == 'Human':
            human_langs = builder.character_data['ch_lang']
            stored = builder.character_data.get('_human_random_lang')
            print(f"\nAttempt {attempts}: Human with languages: {human_langs}")
            
            if stored and 'Reptilian' in stored:
                print(f"✓ Found Human with Reptilian!")
                found = True
                
                # Now do the test
                print(f"\nInitial (Human): {human_langs}")
                
                builder.update_from_selection('ch_ancestry', 'Elf')
                elf_langs = builder.character_data['ch_lang']
                print(f"After Elf change: {elf_langs}")
                
                builder.update_from_selection('ch_ancestry', 'Human')
                human_langs_back = builder.character_data['ch_lang']
                print(f"After switch back: {human_langs_back}")
                
                if human_langs == human_langs_back:
                    print("\n✓ SUCCESS: Human languages match!")
                else:
                    print(f"\n✗ FAILED: Languages don't match!")
                
                break
    
    if not found:
        print(f"\nCould not find Human with Reptilian in {attempts} attempts.")
        print("(This is expected - languages are random!)")


def test_multiple_ancestry_changes():
    """Test multiple ancestry switches"""
    print("\n\nTest: Multiple Ancestry Changes")
    print("=" * 50)
    
    builder = CharacterBuilder()
    builder.generate_character()
    
    # Force to Human
    builder.update_from_selection('ch_ancestry', 'Human')
    human_lang_1 = builder.character_data['ch_lang']
    print(f"Human (1st): {human_lang_1}")
    
    # Switch through multiple
    for ancestry in ['Elf', 'Dwarf', 'Halfling', 'Human']:
        builder.update_from_selection('ch_ancestry', ancestry)
        lang = builder.character_data['ch_lang']
        print(f"{ancestry}: {lang}")
    
    # We should still have the same human languages at the end
    human_lang_final = builder.character_data['ch_lang']
    if human_lang_1 == human_lang_final:
        print(f"\n✓ SUCCESS: Human languages consistent after multiple switches!")
    else:
        print(f"\n✗ FAILED: Human languages changed!")


if __name__ == "__main__":
    test_human_language_persistence()
    test_exact_user_scenario()
    test_multiple_ancestry_changes()
