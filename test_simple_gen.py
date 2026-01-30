"""Simple test to verify character generation works"""

from character_builder import CharacterBuilder

print("Testing character generation...")
builder = CharacterBuilder()
builder.generate_character()
print("✓ Character generation successful")
print(f"Ancestry: {builder.character_data['ch_ancestry']}")
print(f"Languages: {builder.character_data['ch_lang']}")

# Test ancestry change
print("\nTesting ancestry change...")
builder.update_from_selection('ch_ancestry', 'Elf')
print(f"✓ Ancestry changed to Elf")
print(f"Languages: {builder.character_data['ch_lang']}")
