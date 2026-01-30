"""
GUI Test Script for ShadowDark Character Generator
Tests character generation and display without manual interaction
"""

import random
import tkinter as tk
from character_builder import CharacterBuilder
from character_sheet import CharacterSheet


def test_character_display(seed, duration_ms=3000):
    """Generate and display a character for testing"""
    random.seed(seed)
    
    # Create window
    root = tk.Tk()
    root.title(f"Test: Character {seed}")
    root.geometry("1200x800")
    
    # Create character sheet
    sheet = CharacterSheet(root)
    sheet.pack(fill=tk.BOTH, expand=True)
    
    # Generate character
    builder = CharacterBuilder()
    char_data = builder.generate_character()
    
    # Display character
    sheet.update_character_data(char_data)
    
    print(f"\n{'='*60}")
    print(f"Test {seed}: {char_data['ch_class']} {char_data['ch_ancestry']}")
    print(f"{'='*60}")
    print(f"  Name: {char_data['ch_name']}")
    print(f"  HP: {char_data['ch_HP']} | AC: {char_data['ch_AC']} | Armor: {char_data['ch_armor']}")
    print(f"  Attacks: {len(char_data['ch_attacks'])} entries")
    for attack in char_data['ch_attacks']:
        weapon, to_hit, damage, rng = attack
        print(f"    - {weapon}: {to_hit:+d} / {damage} / {rng}")
    print(f"  Languages: {char_data['ch_lang']}")
    talent_text = char_data.get('ch_talent', '').strip()
    spell_text = char_data.get('ch_spell', '').strip()
    if talent_text:
        print(f"  Talents: {talent_text}")
    if spell_text:
        print(f"  Spells: {spell_text}")
    
    # Show window for a moment
    root.update()
    print(f"  [Display: {duration_ms}ms]")
    root.after(duration_ms, root.destroy)
    
    try:
        root.mainloop()
    except:
        pass


def run_gui_tests():
    """Run multiple character tests"""
    print("\n" + "="*60)
    print("ShadowDark Character Generator - GUI Test Suite")
    print("="*60)
    
    test_seeds = [42, 100, 200, 300, 400]
    
    for seed in test_seeds:
        test_character_display(seed, duration_ms=2000)
    
    print("\n" + "="*60)
    print("✓ All GUI tests completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_gui_tests()
