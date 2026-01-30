import random
from character_builder import CharacterBuilder

# Test wizard with spell advantage talent
for seed in [777, 1700]:
    random.seed(seed)
    builder = CharacterBuilder()
    char = builder.generate_character()
    talents = char.get('ch_talent', '').strip()
    spells = char.get('ch_spell', '').strip()
    print(f'\nSeed {seed}: {char["ch_class"]} ({char["ch_ancestry"]})')
    print(f'Talent: {talents}')
    print(f'Spells:')
    for spell in spells.split('\n'):
        if spell.strip():
            print(f'  - {spell.strip()}')
