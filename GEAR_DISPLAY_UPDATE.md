# Multi-Slot Item Display Format - Implementation Summary

## Change Overview
Updated the gear display in the character sheet to format multi-slot items (items taking 2+ slots) with a better visual representation.

## Display Format

### Single-Slot Items
Single-slot items display normally:
```
• Dagger (1 slot)
• Longsword (1 slot)
```

### Multi-Slot Items
Multi-slot items now display as main item with sub-bullets for each additional slot:
```
• Greataxe:
•   greataxe is heavy
• Crossbow:
•   crossbow is heavy
```

### Full Example
Character with 10 STR (5 slots), carrying 2 Greataxes and 1 Dagger:
```
• Greataxe:
•   greataxe is heavy
• Greataxe:
•   greataxe is heavy
• Dagger (1 slot)
•
•
```

## Technical Implementation

### File Modified
**character_sheet.py**

### Changes Made

#### 1. Gear Display Logic (lines 545-590)
- **Before**: All items displayed as-is with slot count
- **After**: 
  - Parse item slot count from "(X slots)" format
  - For multi-slot items (slots > 1):
    - Display item name with colon on first bullet: `• Greataxe:`
    - Add sub-bullets for each additional slot: `•   greataxe is heavy`
  - For single-slot items: Display normally as `• ItemName (1 slot)`

#### 2. Slot Counting Method (lines 662-695)
- Updated docstring to clarify handling of "are heavy" sub-bullets
- No logic change needed - existing code handles both old and new formats

### Key Features

1. **Color Coding Preserved**: Multi-slot items are colored based on equipped status
   - The main item name line (e.g., "Greataxe:") gets the item color
   - All sub-bullet lines automatically inherit the same color
   - Both Greataxe instances in the example above are tracked separately for coloring

2. **Slot Calculation Correct**: Slot counting still works properly
   - "Greataxe (2 slots)" correctly counts as 2 slots
   - "Greataxe:" + "greataxe is heavy" (displayed) still equals 2 slots

3. **Line Mapping Works**: Click handling and item tracking remain functional
   - Each instance of a multi-slot item gets its own entry in the mapping
   - Clicking on any line of a multi-slot item works correctly

## Testing

Created comprehensive tests to verify:
- ✓ Single item display format
- ✓ Multiple items (same weapon type) display correctly
- ✓ Mixed single and multi-slot items
- ✓ Empty slot display
- ✓ Slot counting accuracy
- ✓ Item line mapping for color coding
- ✓ Exact format matches requirements

All tests pass successfully.

## Backward Compatibility

The change is fully backward compatible:
- Old item format "ItemName (X slots)" still works
- Stackable items "Item x N" still work
- Existing color coding and click handling unchanged
- No database or data format changes

## User Impact

✓ Better visual representation of heavy/bulky items
✓ Clearer understanding of how much inventory space items take
✓ More realistic feel for character inventory management
✓ No functional changes - just improved display
