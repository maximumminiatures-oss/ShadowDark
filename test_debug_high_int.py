"""Debug test to find and test a high-INT character"""

from character_builder import CharacterBuilder

def test_high_int():
    print("Finding a character with high INT modifier...")
    for attempt in range(20):
        builder = CharacterBuilder()
        builder.generate_character()
        
        int_mod = builder.character_data['INT_mod']
        int_langs = builder.character_data.get('_int_modifier_langs', [])
        
        if int_mod > 0 and len(int_langs) > 0:
            print(f"\nAttempt {attempt + 1}: Found character with INT mod {int_mod}!")
            print(f"  Ancestry: {builder.character_data['ch_ancestry']}")
            print(f"  Languages: {builder.character_data['ch_lang']}")
            print(f"  Stored INT langs: {int_langs}")
            
            # Make sure character is human
            builder.update_from_selection('ch_ancestry', 'Human')
            print(f"\nAfter changing to Human:")
            print(f"  Languages: {builder.character_data['ch_lang']}")
            print(f"  Stored human lang: {builder.character_data.get('_human_random_lang')}")
            
            initial_lang = builder.character_data['ch_lang']
            initial_int = builder.character_data.get('_int_modifier_langs', [])
            
            # Change to Elf
            builder.update_from_selection('ch_ancestry', 'Elf')
            print(f"\nAfter changing to Elf:")
            print(f"  Languages: {builder.character_data['ch_lang']}")
            print(f"  INT langs in data: {builder.character_data.get('_int_modifier_langs', [])}")
            
            # Change back to Human
            builder.update_from_selection('ch_ancestry', 'Human')
            print(f"\nAfter changing back to Human:")
            print(f"  Languages: {builder.character_data['ch_lang']}")
            final_lang = builder.character_data['ch_lang']
            final_int = builder.character_data.get('_int_modifier_langs', [])
            
            print(f"\n--- RESULT ---")
            print(f"Initial: {initial_lang}")
            print(f"Final:   {final_lang}")
            if initial_lang == final_lang:
                print("✓ SUCCESS!")
            else:
                print("✗ FAILED!")
            break
    else:
        print("\nNo high-INT character found in 20 attempts (unlucky!)")

if __name__ == "__main__":
    test_high_int()
