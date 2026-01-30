import random
from character_builder import CharacterBuilder

for seed in [777, 1350]:
    random.seed(seed)
    c = CharacterBuilder().generate_character()
    print(f'Seed {seed}:')
    print(f'  Talent: {c["ch_talent"]}')
    
    spells = c['ch_spell'].split('\n')
    print(f'  Spells ({len(spells)} total):')
    for spell in spells:
        print(f'    - {spell}')
    
    talent = c['ch_talent']
    for spell_name in ['Charm person', 'Alarm', 'Sleep', 'Protection from evil']:
        if spell_name in talent:
            is_in_spells = spell_name in spells
            print(f'  ✓ {spell_name} in talent, in spells list: {is_in_spells}')
    print()
