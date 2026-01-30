"""Test wizard language persistence"""

from character_builder import CharacterBuilder

def test_wizard_language_persistence():
    """Test that wizard languages persist when switching ancestry"""
    print("Test: Wizard Language Persistence")
    print("=" * 50)
    
    # Find a wizard character
    for attempt in range(20):
        builder = CharacterBuilder()
        builder.generate_character()
        
        if builder.character_data['ch_class'] == 'Wizard':
            print(f"\nAttempt {attempt + 1}: Found a Wizard!")
            print(f"  Ancestry: {builder.character_data['ch_ancestry']}")
            print(f"  Languages: {builder.character_data['ch_lang']}")
            
            # Store initial wizard languages
            initial_lang = builder.character_data['ch_lang']
            wizard_langs = builder.character_data.get('_wizard_langs')
            print(f"  Stored wizard langs: {wizard_langs}")
            
            # Change to a different ancestry
            original_ancestry = builder.character_data['ch_ancestry']
            new_ancestry = 'Elf' if original_ancestry != 'Elf' else 'Dwarf'
            
            print(f"\nChanging from {original_ancestry} to {new_ancestry}...")
            builder.update_from_selection('ch_ancestry', new_ancestry)
            elf_lang = builder.character_data['ch_lang']
            print(f"  Languages: {elf_lang}")
            
            # Change back
            print(f"\nChanging back to {original_ancestry}...")
            builder.update_from_selection('ch_ancestry', original_ancestry)
            final_lang = builder.character_data['ch_lang']
            print(f"  Languages: {final_lang}")
            
            # Check if wizard languages are the same
            print(f"\n--- RESULT ---")
            if initial_lang == final_lang:
                print("✓ SUCCESS: Wizard languages preserved!")
            else:
                print("✗ FAILED: Wizard languages changed!")
                print(f"  Initial: {initial_lang}")
                print(f"  Final:   {final_lang}")
            
            break
    else:
        print("No wizard found in 20 attempts")


if __name__ == "__main__":
    test_wizard_language_persistence()
