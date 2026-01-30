import random
from character_builder import CharacterBuilder

# Test wizard with spell advantage talent (seed 777)
random.seed(777)
builder = CharacterBuilder()
char = builder.generate_character()
talents = char.get('ch_talent', '').strip()
spells = char.get('ch_spell', '').strip()

print(f'Seed 777: {char["ch_class"]} ({char["ch_ancestry"]})')
print(f'\nTalent: {talents}')
print(f'\nSpells ({len(spells.split(chr(10)))} total):')
for spell in spells.split('\n'):
    if spell.strip():
        print(f'  - {spell.strip()}')
