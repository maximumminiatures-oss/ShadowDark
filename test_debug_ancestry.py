"""Debug test to trace language generation"""

from character_builder import CharacterBuilder

def test_debug():
    builder = CharacterBuilder()
    print("Generating character...")
    builder.generate_character()
    
    print(f"\nAfter initial generation:")
    print(f"  Ancestry: {builder.character_data['ch_ancestry']}")
    print(f"  Languages: {builder.character_data['ch_lang']}")
    print(f"  Stored INT langs: {builder.character_data.get('_int_modifier_langs', [])}")
    
    if builder.character_data['ch_ancestry'] != 'Human':
        builder.update_from_selection('ch_ancestry', 'Human')
        print(f"\nAfter changing to Human:")
        print(f"  Ancestry: {builder.character_data['ch_ancestry']}")
        print(f"  Languages: {builder.character_data['ch_lang']}")
        print(f"  Stored INT langs: {builder.character_data.get('_int_modifier_langs', [])}")
        print(f"  Stored human lang: {builder.character_data.get('_human_random_lang')}")
    
    initial_lang = builder.character_data['ch_lang']
    initial_int = builder.character_data.get('_int_modifier_langs', [])
    
    # Change to Elf
    builder.update_from_selection('ch_ancestry', 'Elf')
    print(f"\nAfter changing to Elf:")
    print(f"  Ancestry: {builder.character_data['ch_ancestry']}")
    print(f"  Languages: {builder.character_data['ch_lang']}")
    print(f"  Stored INT langs: {builder.character_data.get('_int_modifier_langs', [])}")
    
    elf_int = builder.character_data.get('_int_modifier_langs', [])
    
    # Change back to Human
    builder.update_from_selection('ch_ancestry', 'Human')
    print(f"\nAfter changing back to Human:")
    print(f"  Ancestry: {builder.character_data['ch_ancestry']}")
    print(f"  Languages: {builder.character_data['ch_lang']}")
    print(f"  Stored INT langs: {builder.character_data.get('_int_modifier_langs', [])}")
    
    final_lang = builder.character_data['ch_lang']
    final_int = builder.character_data.get('_int_modifier_langs', [])
    
    print(f"\n--- COMPARISON ---")
    print(f"Initial Human INT langs: {initial_int}")
    print(f"Elf INT langs: {elf_int}")
    print(f"Final Human INT langs: {final_int}")
    print(f"\nInitial Human langs: {initial_lang}")
    print(f"Final Human langs: {final_lang}")
    print(f"Match: {initial_lang == final_lang}")

if __name__ == "__main__":
    test_debug()
