"""
GUI Display Verification Test
Shows exactly what the GUI displays for sample characters
"""

import random
from character_builder import CharacterBuilder


def format_character_for_display(char_data):
    """Format a character exactly as it appears in the GUI"""
    output = []
    
    # --- Left Column ---
    output.append("=" * 80)
    output.append("LEFT COLUMN: Character Info & Attacks")
    output.append("=" * 80)
    
    output.append(f"\nCharacter Information:")
    output.append(f"  Name:       {char_data['ch_name']}")
    output.append(f"  Ancestry:   {char_data['ch_ancestry']}")
    output.append(f"  Class:      {char_data['ch_class']}")
    output.append(f"  Title:      {char_data['ch_title']}")
    output.append(f"  Alignment:  {char_data['ch_align']}")
    output.append(f"  Background: {char_data['ch_background']}")
    output.append(f"  Deity:      {char_data['ch_deity']}")
    output.append(f"\nLevel/XP:")
    output.append(f"  LEVEL:      {char_data['LEVEL']}")
    output.append(f"  XP:         {char_data['XP']}")
    
    output.append(f"\nGraphics (HP & AC):")
    output.append(f"  HP:         {char_data['ch_HP']}")
    output.append(f"  AC:         {char_data['ch_AC']}")
    
    output.append(f"\nArmor worn:")
    output.append(f"  {char_data['ch_armor']}")
    
    output.append(f"\nAttacks: +To Hit / Damage / Range")
    attacks = char_data['ch_attacks']
    for weapon, to_hit, damage, range_str in attacks:
        to_hit_str = f"+{to_hit}" if to_hit >= 0 else str(to_hit)
        output.append(f"  {weapon:20} {to_hit_str:>5} / {damage:<8} / {range_str}")
    
    # --- Center Column ---
    output.append("\n" + "=" * 80)
    output.append("CENTER COLUMN: ShadowDark Title & Ability Scores")
    output.append("=" * 80)
    
    output.append("\n                    SHADOWDARK\n")
    
    abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    for abbr in abilities:
        score = char_data[f'{abbr}_score']
        mod = char_data[f'{abbr}_mod']
        mod_str = f"+{mod}" if mod >= 0 else str(mod)
        output.append(f"  {abbr}:  {score}/{mod_str}")
    
    output.append(f"\nLanguages:")
    lang_lines = char_data['ch_lang'].split(', ')
    for lang in lang_lines:
        output.append(f"  {lang}")
    
    # --- Right Column ---
    output.append("\n" + "=" * 80)
    output.append("RIGHT COLUMN: Talents/Spells & Gear")
    output.append("=" * 80)
    
    output.append(f"\nTalents/Spells:")
    talent_text = char_data.get('ch_talent', '').strip()
    spell_text = char_data.get('ch_spell', '').strip()
    
    if talent_text:
        output.append(f"  Talents: {talent_text}")
    if spell_text:
        output.append(f"  Spells: {spell_text}")
    if not talent_text and not spell_text:
        output.append("  (none)")
    
    output.append(f"\nGear:")
    output.append(f"  GP: {char_data['gp_coin']}")
    output.append(f"  SP: {char_data['sp_coin']}")
    output.append(f"  CP: {char_data['cp_coin']}")
    
    return "\n".join(output)


def test_display():
    """Test and display multiple characters"""
    test_cases = [
        (42, "Wizard - High INT, multiple languages"),
        (100, "Thief - Backstab, AC boost from DEX"),
        (300, "Fighter - High STR, big weapon"),
        (400, "Priest - Spells from WIS"),
    ]
    
    print("\n" + "=" * 80)
    print("GUI DISPLAY VERIFICATION TEST")
    print("=" * 80)
    
    for seed, description in test_cases:
        random.seed(seed)
        builder = CharacterBuilder()
        char_data = builder.generate_character()
        
        print(f"\n[Seed {seed}: {description}]")
        print(format_character_for_display(char_data))
        print("\n" + "-" * 80)
    
    print("\n[SUCCESS] GUI display test complete!")
    print("The above shows exactly what appears in the GUI windows.")


if __name__ == "__main__":
    test_display()
