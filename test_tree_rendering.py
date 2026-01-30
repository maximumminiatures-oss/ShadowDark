"""Test tree sprite rendering"""
from PIL import Image
from hex_painter import HexPainter

# Test loading tree sprites
print("Testing tree sprite loading:")
for i in range(1, 19):
    sprite = HexPainter.load_sprite(f"tree_{i}")
    if sprite:
        print(f"✓ tree_{i}.png loaded: {sprite.size}")
    else:
        print(f"✗ tree_{i}.png FAILED to load")

# Test creating a simple forest tile
print("\nCreating test forest tile...")
img = Image.new('RGBA', (200, 200), (34, 100, 34, 255))
HexPainter.draw_forest_variant(img, 100, 100, 74, "test_seed")
img.save("test_forest_tile.png")
print("Saved test_forest_tile.png")
