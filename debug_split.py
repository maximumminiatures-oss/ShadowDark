import random
from character_builder import CharacterBuilder

random.seed(777)
builder = CharacterBuilder()
char_data = builder.generate_character()

spell_text = char_data.get('ch_spell', '').strip()
print(f"spell_text: {repr(spell_text)}")
print(f"spell_text length: {len(spell_text)}")

spells = spell_text.split('\n')
print(f"\nSpells after split: {spells}")
print(f"Number of spells: {len(spells)}")

for i, spell in enumerate(spells):
    print(f"  [{i}]: {repr(spell)}")
