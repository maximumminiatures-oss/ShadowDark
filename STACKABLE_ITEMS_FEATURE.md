# Stackable Items Feature Implementation

## Summary
Successfully implemented a stackable items system for the ShadowDark character generator. Items like arrows, crossbow bolts, and rations now stack intelligently in inventory slots.

## How It Works

### Stackable Items
Items with `slots_per` property automatically stack:
- **Arrow**: 20 per slot
- **Crossbow bolts**: 20 per slot  
- **Rations**: 3 per slot
- **Coins**: 100 per slot
- **Iron spikes**: 10 per slot

### Stacking Behavior
1. **First Purchase**: Displays as "Arrow x 1"
2. **Subsequent Purchases**: Count increases (e.g., "Arrow x 2", "Arrow x 3", etc.)
3. **At Maximum**: When reaching the max (e.g., "Arrow x 20"), the item is marked as heavy with indentation: "  Arrow x 20 are heavy!"
4. **Overflow to New Slot**: Next purchase creates a new slot with "Arrow x 1"
5. **Multiple Full Slots**: Each full slot shows the "are heavy!" message with indentation

### Display Format
- Normal stacking: `Arrow x 5` (uses 1 slot)
- Full slot (heavy): `  Arrow x 20 are heavy!` (uses 1 slot, indented)
- Multiple full slots: Each appears as a separate line with indentation

### Slot Usage
Each stackable item line (whether counting 1-19 items or 20+ marked as heavy) counts as 1 inventory slot in terms of STR-based carrying capacity.

## Code Changes

### character_builder.py
Added new method `add_stackable_item()`:
- Manages stacking logic
- Tracks item counts
- Handles overflow to new slots
- Applies "are heavy!" formatting when slots are full

### shop_ui.py
Modified `buy_item()` method:
- Detects stackable items (those with `slots_per`)
- Routes to special stackable handling
- Uses new `_can_add_stackable_item()` helper

Added new method `_can_add_stackable_item()`:
- Checks if item can be added to existing stack
- Verifies slot availability for new stacks
- Returns True/False for purchase eligibility

Updated `calculate_used_slots()`:
- Now recognizes stackable format "ItemName x N"
- Properly counts all gear types

## Testing
Test script demonstrates:
- Arrow stacking up to 20, then overflow to new slot
- Ration stacking with smaller limit (3 per slot)
- Proper "are heavy!" message formatting
- Multiple full slots with indentation

Example output:
```
[0] Leather Armor (1 slot)
[1]   Arrow x 20 are heavy!
[2] Arrow x 4
[3]   Ration, per day x 3 are heavy!
[4]   Ration, per day x 3 are heavy!
[5] Ration, per day x 3
```

## Integration
The feature integrates seamlessly with:
- Character generation (items with `slots_per` automatically use this system)
- Shop UI (buy button handles stackable items correctly)
- Character sheet display (shows proper formatting)
- Coin management (cost subtraction works normally)
- Inventory slot limits (respects STR-based carrying capacity)
