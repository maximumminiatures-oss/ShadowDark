from character_builder import CharacterBuilder

builder = CharacterBuilder()
char_data = builder.generate_character()

# Test stackable item logic
gear = char_data.get('ch_gear_items', [])
print(f'Initial gear: {gear}')
print()

# Get arrow data
arrows = builder.EQUIPMENT.get('Arrow')
print(f'Arrow in EQUIPMENT: {arrows}')
print(f'Has slots_per: {"slots_per" in arrows}')
print()

# Try adding an arrow
builder.add_stackable_item(gear, 'Arrow', arrows)
print(f'After adding arrow: {gear}')
