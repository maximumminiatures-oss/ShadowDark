import random
from character_builder import CharacterBuilder

# Test with seed that should give talents with ability increases
for seed in range(100, 2000, 50):
    random.seed(seed)
    builder = CharacterBuilder()
    char = builder.generate_character()
    talents = char.get('ch_talent', '').strip()
    if 'increase' in talents.lower():
        print(f'\nSeed {seed}: {char["ch_class"]} ({char["ch_ancestry"]})')
        print(f'  STR: {char["STR_score"]}, DEX: {char["DEX_score"]}, CON: {char["CON_score"]}, INT: {char["INT_score"]}, WIS: {char["WIS_score"]}, CHA: {char["CHA_score"]}')
        print(f'  Talent: {talents}')
        print(f'  Spells: {char.get("ch_spell", "").strip()}')
