"""Test that humans always get a random language regardless of INT modifier"""

from character_builder import CharacterBuilder

def test_human_random_language_always_assigned():
    """Test that humans get random language even with low INT"""
    print("Testing Human Random Language Assignment")
    print("=" * 70)
    
    found_low_int_human = False
    
    for attempt in range(100):
        builder = CharacterBuilder()
        builder.generate_character()
        
        if builder.character_data['ch_ancestry'] == 'Human':
            int_mod = builder.character_data['INT_mod']
            random_lang = builder.character_data.get('_human_random_lang')
            full_langs = builder.character_data['ch_lang']
            
            if int_mod <= 0:
                found_low_int_human = True
                print(f"\nAttempt {attempt + 1}: Found Human with INT mod {int_mod}")
                print(f"  Random language assigned: {random_lang}")
                print(f"  Full languages: {full_langs}")
                
                # Verify it has Common + the random language
                langs_list = [l.strip() for l in full_langs.split(',')]
                if 'Common' in langs_list and random_lang in langs_list:
                    print(f"  ✓ SUCCESS: Human has Common + {random_lang}")
                else:
                    print(f"  ✗ FAILED: Expected Common and {random_lang}")
                    print(f"  Got: {langs_list}")
                
                break
    
    if not found_low_int_human:
        print("Could not find a low INT human in 100 attempts")
        print("Testing with forced human generation...")
        
        # Force generation
        for attempt in range(10):
            builder = CharacterBuilder()
            builder.generate_character()
            builder.update_from_selection('ch_ancestry', 'Human')
            
            int_mod = builder.character_data['INT_mod']
            random_lang = builder.character_data.get('_human_random_lang')
            full_langs = builder.character_data['ch_lang']
            
            print(f"\nForced Attempt {attempt + 1}: INT mod {int_mod}")
            print(f"  Random language: {random_lang}")
            print(f"  Full languages: {full_langs}")
            
            if random_lang:
                print(f"  ✓ Has random language: {random_lang}")
            else:
                print(f"  ✗ No random language assigned!")

if __name__ == "__main__":
    test_human_random_language_always_assigned()
