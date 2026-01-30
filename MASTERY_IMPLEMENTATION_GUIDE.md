# Weapon Mastery System - Implementation Guide

## Quick Summary
The weapon mastery system has been refactored to allow fighters to select multiple weapon masteries:
- **1 mandatory mastery** for all fighters
- **Additional masteries** (0-2 more) based on talent rolls of 2

## How It Works in the App

### Step 1: Character Generation
When a fighter is created:
1. `weapon_mastery_count` is initialized to 1 (all fighters)
2. Each talent roll of 2 increments `weapon_mastery_count`
3. Example: Human fighter rolls 2, 2 on talents → 3 total masteries

### Step 2: Shop UI - Mastery Selection Phase
When the shop opens for a fighter with masteries to select:
1. Title displays: "Choose Weapon Mastery 1 of 3"
2. User clicks "Get" on a weapon to select it as a mastery
3. Already-selected weapons are grayed out (disabled)
4. After each selection, if more masteries are needed, show selection screen again
5. Once all masteries selected, move to normal weapon selection

### Step 3: Shop UI - Weapon Selection Phase
After masteries are selected:
1. Title displays: "Pick a weapon"
2. User selects starting weapon as normal
3. Weapon bonuses already calculated with mastery bonuses

### Step 4: Character Display
In the character sheet:
- Any weapon in the mastery list gets +1 attack and +1 damage
- Example: "Longsword +1 attack, 1d8+1 damage" (if mastered)

## Code Integration Points

### character_builder.py
```python
# In _generate_talents():
weapon_mastery_count = 1 if char_class == 'Fighter' else 0
for talent_roll in talent_rolls:
    if talent_roll == 2:
        weapon_mastery_count += 1
self.character_data['weapon_mastery_count'] = weapon_mastery_count

# In _weapon_to_attacks():
has_mastery = weapon_name in character_data.get('weapon_masteries', [])
if has_mastery:
    attack_bonus += 1
    damage = _add_damage_bonus(damage, 1)
```

### shop_ui.py
```python
# In __init__():
self.weapon_mastery_count = character_data.get('weapon_mastery_count', 0)
self.selected_masteries = []
self.is_mastery_selection = self.weapon_mastery_count > 0

# In show_weapon_selection():
if self.is_mastery_selection:
    title = f"Choose Weapon Mastery {len(selected) + 1} of {total}"
    # Gray out already-selected weapons
    if weapon in self.selected_masteries:
        is_allowed = False

# In select_weapon():
if self.is_mastery_selection:
    selected_masteries.append(weapon)
    if len(selected_masteries) < weapon_mastery_count:
        # Show selection again
        self.update_ui()
    else:
        # Store all masteries and continue
        character_data['weapon_masteries'] = selected_masteries
        self.is_mastery_selection = False
        self.update_ui()
```

## Data Structure

### In character_data:
```python
{
    'weapon_mastery_count': 2,           # How many to select (or 0 for non-fighters)
    'weapon_masteries': ['Longsword', 'Mace'],  # Quick lookup list
    'weapon_mastery_1': 'Longsword',     # Individual entries for reference
    'weapon_mastery_2': 'Mace',
}
```

## Testing the System

### Quick Tests
Run these test files to verify functionality:

```bash
python test_final_validation.py       # Tests core logic
python test_complete_flow.py          # Tests end-to-end flow
python test_fighter_generation.py     # Tests character generation
```

### Manual Testing
1. Generate a fighter with the app
2. Check that shop shows "Choose Weapon Mastery 1 of N" for fighters
3. Click on a weapon to select it
4. Verify already-selected weapons are grayed out
5. Select all masteries
6. Choose a starting weapon
7. Check character sheet shows +1 bonuses for mastered weapons

## Edge Cases Handled

1. **Non-fighters**: Skip mastery selection entirely
2. **Fighters with 1 mastery**: Select 1 weapon, move to weapon selection
3. **Fighters with 3 masteries**: Must select 3 weapons sequentially
4. **Already-selected weapons**: Grayed out in subsequent selections
5. **Backward compatibility**: Old code using single `weapon_mastery` key still works

## Modifying Weapon Mastery Behavior

### To change mastery bonus values:
Edit `_add_damage_bonus(dmg_to_use, 1)` in `_weapon_to_attacks()`:
- Change `1` to `2` for +2 damage bonus
- Change mastery_atk_bonus calculation for attack bonuses

### To allow non-fighters to get masteries:
Edit line 529 in `_generate_talents()`:
```python
# Current:
weapon_mastery_count = 1 if char_class == 'Fighter' else 0

# To allow Thieves 1 mastery:
weapon_mastery_count = 1 if char_class in ['Fighter', 'Thief'] else 0
```

### To change how many masteries humans get:
Adjust talent roll logic in `_generate_talents()` to check different values or add more rolls.

## Known Limitations

1. Masteries must be selected before starting weapon
2. Cannot change masteries after shop closes
3. UI shows masteries as "weapon_mastery_X" in debug (cosmetic only)

## Backward Compatibility Notes

- Old code checking `character_data.get('weapon_mastery')` still works
- New code checks `character_data.get('weapon_masteries')` first for scalability
- Both approaches can coexist in same codebase
