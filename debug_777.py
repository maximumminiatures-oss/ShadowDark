import random
from character_builder import CharacterBuilder, WIZARD_SPELLS

# Test wizard with spell advantage talent (seed 777)
random.seed(777)
builder = CharacterBuilder()

# Manually trace through generation to see what happens
builder._generate_ability_scores()
builder._generate_ancestry()
builder._determine_class()
builder._generate_deity()
builder._determine_alignment()
builder._generate_background()
builder._determine_title()
builder._generate_languages()
builder._generate_name()
builder._calculate_hp()
builder._calculate_ac()
builder._generate_attacks()

# Now check talents generation
print(f"Class: {builder.character_data['ch_class']}")
print(f"INT_mod: {builder.character_data['INT_mod']}")

# Roll wizard spells
char_class = builder.character_data['ch_class']
int_mod = builder.character_data.get('INT_mod', 0)
num_spells = max(1, 2 + max(0, int_mod // 2))
spells = []
spells_available = WIZARD_SPELLS.copy()
for _ in range(min(num_spells, len(spells_available))):
    spell = random.choice(spells_available)
    spells.append(spell)
    spells_available.remove(spell)

print(f"\nInitial spells ({num_spells} needed): {spells}")

# Set ch_spell
spell_display = "\n".join(spells) if spells else ""
builder.character_data['ch_spell'] = spell_display
print(f"ch_spell before talent: {repr(builder.character_data['ch_spell'])}")

# Roll talent
from character_builder import roll_2d6
talent_roll = roll_2d6()
print(f"Talent roll: {talent_roll}")
print(f"Before talent - ch_spell: {repr(builder.character_data.get('ch_spell', 'NOT SET'))}")
talent_text = builder._process_wizard_talent(talent_roll, builder.character_data['ch_ancestry'])
print(f"Talent text: {talent_text}")
print(f"After talent - ch_spell: {repr(builder.character_data.get('ch_spell', 'NOT SET'))}")

# Check if Charm person is in spells
ch_spell = builder.character_data['ch_spell']
spells_in_char = [s.strip() for s in ch_spell.split('\n') if s.strip()]
print(f"\nSpells in character: {spells_in_char}")
print(f"'Charm person' in spells: {'Charm person' in spells_in_char}")
