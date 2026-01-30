import random
from character_builder import CharacterBuilder

random.seed(777)
builder = CharacterBuilder()
char_data = builder.generate_character()

print("Final character data:")
print(f"  ch_talent: {repr(char_data.get('ch_talent', ''))}")
print(f"  ch_spell: {repr(char_data.get('ch_spell', ''))}")

spell_text = char_data.get('ch_spell', '').strip()
if spell_text:
    print(f"\nSpells listed:")
    for spell in spell_text.split('\n'):
        print(f"  - {spell}")
