# Weapon Mastery System Refactor - Summary

## Overview
Refactored the weapon mastery system from a single-selection model (triggered only by talent roll = 2) to a multi-selection model where:
- **ALL fighters** get to pick 1 weapon mastery (mandatory)
- **Additional masteries** are gained by rolling 2 on talent tables:
  - Non-humans (1 talent roll): Up to 2 total masteries (1 base + 1 additional)
  - Humans (2 talent rolls): Up to 3 total masteries (1 base + up to 2 additional)

## Changes Made

### 1. character_builder.py

#### _generate_talents() method (lines 519-595)
- **Before**: Only tracked a `needs_weapon_mastery` flag when talent roll = 2
- **After**: 
  - Initializes `weapon_mastery_count = 1` for ALL fighters (line 529)
  - Detects "ADDITIONAL_MASTERY" return value from talent processor (line 537)
  - Increments `weapon_mastery_count` for each additional mastery earned (line 539)
  - Stores `weapon_mastery_count` in `character_data` after talent generation (line 595)

#### _process_fighter_talent() method (lines 787-790)
- **Before**: Set `needs_weapon_mastery = True` flag for roll = 2
- **After**: Returns "ADDITIONAL_MASTERY" marker string for roll = 2

#### _weapon_to_attacks() method (lines 690-735)
- **Before**: Checked single `character_data['weapon_mastery']` key
- **After**:
  - First checks for `character_data['weapon_masteries']` list (multiple masteries)
  - Falls back to legacy `character_data['weapon_mastery']` for backward compatibility
  - Returns True if weapon_name exists in the masteries list
  - Applies +1 attack and +1 damage bonus to all mastered weapons

### 2. shop_ui.py

#### __init__() method (lines 57-66)
- **Added**: 
  - `self.weapon_mastery_count = character_data.get('weapon_mastery_count', 0)` to detect how many masteries fighter needs
  - `self.selected_masteries = []` to track which weapons user has selected
  - `self.is_mastery_selection = self.weapon_mastery_count > 0` to enter mastery selection mode

#### show_weapon_selection() method (lines 101-149)
- **Updated title display** to show progress: "Choose Weapon Mastery X of Y"
- **Added logic** to gray out already-selected weapons during mastery selection
- Checks `self.is_mastery_selection` flag to determine display mode

#### select_weapon() method (lines 393-438)
- **Enhanced** to handle sequential mastery selection:
  - If `self.is_mastery_selection` is True, adds weapon to `selected_masteries` list
  - Checks if more masteries are needed
  - If more needed: calls `update_ui()` to refresh display (grays out selected weapons)
  - If all selected: stores all masteries in `character_data` as:
    - `character_data['weapon_mastery_1']`, `character_data['weapon_mastery_2']`, etc.
    - `character_data['weapon_masteries']` = full list for quick lookups
  - Sets `is_mastery_selection = False` and continues to normal weapon selection

## Data Structure

### Character Data Keys Added/Modified
```python
character_data = {
    'weapon_mastery_count': 2,              # Number of masteries to select (1-3)
    'weapon_mastery_1': 'Longsword',        # First mastery weapon
    'weapon_mastery_2': 'Mace',             # Second mastery weapon (if applicable)
    'weapon_mastery_3': 'Dagger',           # Third mastery weapon (if applicable)
    'weapon_masteries': ['Longsword', 'Mace', 'Dagger'],  # Quick lookup list
}
```

## Flow Diagram

```
Character Builder
    ↓
Generate Fighter
    ↓
weapon_mastery_count = 1 (all fighters)
    ↓
Roll Talents
    ├─ Roll = 2 → weapon_mastery_count += 1
    └─ Roll ≠ 2 → regular talent
    ↓
Store weapon_mastery_count in character_data
    ↓
Open Shop UI
    ↓
is_mastery_selection = (weapon_mastery_count > 0)
    ↓
IF Mastery Selection Mode:
    ├─ Show "Choose Mastery 1 of N" 
    ├─ Gray out already selected weapons
    ├─ User selects weapon
    ├─ Check if more masteries needed
    ├─ If yes → refresh UI, goto step 2
    └─ If no → store all masteries, continue to weapon selection
    ↓
Normal Weapon Selection
    ├─ Show "Pick a weapon"
    ├─ User selects starting weapon
    └─ Continue to gear shopping
    ↓
Attack Calculation
    └─ Check character_data['weapon_masteries'] for +1/+1 bonuses
```

## Backward Compatibility
- Code checks for `weapon_masteries` list first
- Falls back to legacy single `weapon_mastery` key if needed
- Non-fighters still get `weapon_mastery_count = 0` and skip mastery selection

## Testing
Created comprehensive tests to verify:
1. ✓ Fighter generation with weapon_mastery_count calculation
2. ✓ Mastery selection flow (single and multiple)
3. ✓ Gray-out logic for already-selected weapons
4. ✓ Attack bonus calculation for all mastered weapons
5. ✓ Integration between character builder and shop UI

## Benefits
1. **Better mechanical depth**: Fighters now have meaningful weapon mastery choices
2. **Scalable**: Easily supports 1-3 masteries per fighter based on talent rolls
3. **Intuitive UI**: Shows progress during sequential selection with grayed-out weapons
4. **Consistent bonuses**: All mastered weapons get +1/+1 attack and damage
5. **Backward compatible**: Existing code using old system still works
