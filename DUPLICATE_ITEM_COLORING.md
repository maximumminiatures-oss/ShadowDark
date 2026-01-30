# Duplicate Item Coloring Feature

## Overview
When a character has multiple copies of the same weapon or armor, and one of them is equipped, all other copies are now grayed out to show they are duplicates of the equipped item.

## Behavior

### Weapons
- **Single weapon equipped**: Item displayed in black
- **Single weapon not equipped**: Item displayed in gray
- **Multiple weapons (duplicates), one equipped**: Equipped copy is black, all other copies are gray
- **Multiple weapons (duplicates), none equipped**: All copies are gray

### Armor/Shields
- Same behavior as weapons
- If a duplicate is equipped (either as armor or shield), it displays in black
- All other copies of that armor/shield display in gray

## Examples

### Example 1: Two Greataxes, one equipped
```
Character inventory:
• Greataxe:           [BLACK]
•   greataxe is heavy [BLACK]
• Greataxe:           [GRAY]
•   greataxe is heavy [GRAY]
```
The first Greataxe is equipped (black), the second is grayed out as a duplicate.

### Example 2: Two Shields, one equipped
```
• Shield              [BLACK]  (equipped)
• Shield              [GRAY]   (duplicate, not equipped)
```

### Example 3: Multiple items with duplicates
```
• Longsword           [GRAY]   (single, not equipped)
• Greataxe:           [BLACK]  (duplicate, equipped)
•   greataxe is heavy [BLACK]
• Greataxe:           [GRAY]   (duplicate, not equipped)
•   greataxe is heavy [GRAY]
• Shield              [BLACK]  (duplicate, equipped)
• Shield              [GRAY]   (duplicate, not equipped)
• Dagger              [GRAY]   (single, not equipped)
```

## Implementation Details

### Location
File: `character_sheet.py`, lines 595-660

### Logic
1. **Count items**: Iterate through all gear items and count occurrences of each item name
2. **Determine duplicates**: If an item appears 2+ times, it's a duplicate
3. **Apply coloring**:
   - For weapons: If duplicate and not equipped → gray; if not duplicate → check if equipped
   - For armor/shields: Same logic as weapons
   - For other items: Default color (black)
4. **Apply tags**: Color tags are applied to all line numbers for each item

### Key Code
```python
# Count item occurrences
item_counts = {}
for item in items:
    item_name = item.split('(')[0].strip() or item.split(' x ')[0].strip()
    item_counts[item_name] = item_counts.get(item_name, 0) + 1

# Apply colors
for item_name in items:
    is_duplicate = item_counts[item_name] > 1
    is_equipped = item_name == equipped_weapon  # or armor/shield
    
    if is_duplicate and not is_equipped:
        color = gray_color
    elif not is_duplicate:
        color = black if is_equipped else gray_color
    else:
        color = black  # duplicate and equipped
```

## Testing
All scenarios tested and verified:
- ✓ Single duplicate, equipped
- ✓ Multiple duplicates, none equipped
- ✓ Mixed items with various duplicates
- ✓ Multiple weapons with different duplicate counts
- ✓ Armor and shield duplicates
- ✓ Multi-slot items (Greataxe with sub-bullets)

## Behavior Notes

1. **Count is global**: All copies of an item count together
   - If you have 3 Greataxes, and equip one, all 3 show as duplicate (1 black, 2 gray)

2. **Applies to weapons and armor only**: Other items like ropes, rations, etc. stay black

3. **Multi-slot items work correctly**: The sub-bullets ("is heavy") are also colored with the main item

4. **Works with both formats**:
   - Item format: "Greataxe (2 slots)"
   - Stackable format: "Rations x 3"

## Future Enhancements
- Could add a UI indicator (e.g., "[+1]") showing how many duplicates of that item exist
- Could allow swapping which duplicate is equipped via click
