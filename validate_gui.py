"""
Validation Test for Character Generation and Display Logic
Tests that all data structures are correct for GUI display
"""

import random
from character_builder import CharacterBuilder


def validate_character(char_data):
    """Validate that a character has all required fields for GUI display"""
    errors = []
    warnings = []
    
    # Required fields
    required_fields = [
        'ch_name', 'ch_ancestry', 'ch_class', 'ch_title', 'ch_align',
        'ch_background', 'ch_deity', 'ch_lang', 'ch_armor',
        'STR_score', 'STR_mod', 'DEX_score', 'DEX_mod',
        'CON_score', 'CON_mod', 'INT_score', 'INT_mod',
        'WIS_score', 'WIS_mod', 'CHA_score', 'CHA_mod',
        'ch_HP', 'ch_AC', 'ch_attacks', 'ch_talent', 'ch_spell',
        'gp_coin', 'sp_coin', 'cp_coin', 'LEVEL', 'XP'
    ]
    
    for field in required_fields:
        if field not in char_data:
            errors.append(f"Missing field: {field}")
    
    # Validate attacks structure
    if 'ch_attacks' in char_data:
        attacks = char_data['ch_attacks']
        if not isinstance(attacks, list):
            errors.append(f"ch_attacks must be list, got {type(attacks)}")
        else:
            for i, attack in enumerate(attacks):
                if not isinstance(attack, tuple) or len(attack) != 4:
                    errors.append(f"Attack {i} invalid: must be 4-tuple, got {attack}")
                else:
                    weapon, to_hit, damage, range_str = attack
                    if not isinstance(to_hit, int):
                        errors.append(f"Attack {i} to_hit must be int, got {type(to_hit)}")
    
    # Validate ability scores
    for abbr in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
        score = char_data.get(f'{abbr}_score', 0)
        mod = char_data.get(f'{abbr}_mod', 0)
        expected_mod = (score - 10) // 2
        if mod != expected_mod:
            errors.append(f"{abbr} modifier mismatch: expected {expected_mod}, got {mod}")
        if score < 3 or score > 18:
            warnings.append(f"{abbr} score {score} outside typical range 3-18")
    
    # Validate HP
    hp = char_data.get('ch_HP', 0)
    if hp < 1:
        errors.append(f"HP must be >= 1, got {hp}")
    
    # Validate AC
    ac = char_data.get('ch_AC', 0)
    if ac < 8 or ac > 18:
        warnings.append(f"AC {ac} outside typical range 8-18")
    
    # Validate class-specific AC
    char_class = char_data.get('ch_class')
    armor = char_data.get('ch_armor', '')
    if char_class in ['Fighter', 'Priest', 'Thief']:
        if 'Leather armor' not in armor:
            warnings.append(f"{char_class} should have Leather armor, got {armor}")
    elif char_class == 'Wizard':
        if 'None' not in armor:
            warnings.append(f"Wizard should have no armor, got {armor}")
    
    return errors, warnings


def test_seed(seed):
    """Test a single seed"""
    random.seed(seed)
    builder = CharacterBuilder()
    char_data = builder.generate_character()
    
    errors, warnings = validate_character(char_data)
    
    print(f"\nSeed {seed}: {char_data['ch_class']} {char_data['ch_ancestry']}")
    
    if errors:
        print(f"  [ERROR]:")
        for error in errors:
            print(f"    - {error}")
        return False
    else:
        print(f"  [PASS]")
    
    if warnings:
        print(f"  [WARNING]:")
        for warning in warnings:
            print(f"    - {warning}")
    
    return True


def main():
    """Run validation tests"""
    print("="*70)
    print("Character Generation & Display Validation Tests")
    print("="*70)
    
    test_seeds = [10, 42, 100, 200, 300, 400, 500, 777, 999]
    passed = 0
    failed = 0
    
    for seed in test_seeds:
        if test_seed(seed):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "="*70)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("[SUCCESS] All validation tests passed!")
    else:
        print(f"[FAILED] {failed} test(s) failed")
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
