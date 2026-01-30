import random
from character_builder import CharacterBuilder

print("Testing Wizards with 3 starting spells and advantage on one of them:\n")

for seed in [200, 350, 550, 750, 1150, 1350, 1700, 777, 888, 999]:
    random.seed(seed)
    c = CharacterBuilder().generate_character()
    
    if c["ch_class"] != "Wizard":
        continue
    
    spells = c['ch_spell'].split('\n')
    talent = c['ch_talent'].strip()
    
    print(f'Seed {seed}:')
    print(f'  Spells ({len(spells)} total):')
    for spell in spells:
        print(f'    - {spell}')
    print(f'  Talent: {talent}')
    
    # Check if advantage spell is from initial spells
    if 'advantage' in talent.lower():
        for spell in spells:
            if spell in talent:
                print(f'  ✓ Advantage spell "{spell}" is in spell list')
                break
    print()
