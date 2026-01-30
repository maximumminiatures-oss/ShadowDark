import os
from PIL import Image, ImageDraw, ImageFilter

def create_tree_sprite(path, color):
    # 40x40 sprite for a tree
    size = 40
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Draw tree layers
    # Trunk
    draw.rectangle([18, 30, 22, 40], fill=(101, 67, 33))
    
    # Leaves (3 circles)
    draw.ellipse([5, 10, 35, 35], fill=color)
    draw.ellipse([10, 0, 30, 20], fill=color)
    
    # Texture/Shade
    draw.ellipse([8, 12, 32, 32], fill=None, outline=(0,0,0, 30))
    
    img.save(path)

def create_mountain_sprite(path, color):
    # 60x60 sprite
    size = 64
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Triangle
    points = [(32, 5), (5, 55), (59, 55)]
    draw.polygon(points, fill=color)
    
    # Snowcap
    cap_points = [(32, 5), (22, 23), (25, 20), (32, 25), (39, 20), (42, 23)]
    draw.polygon(cap_points, fill=(240, 240, 255))
    
    # Outline
    draw.polygon(points, fill=None, outline=(50, 50, 50), width=1)
    
    img.save(path)

def create_grass_sprite(path):
    size = 20
    img = Image.new('RGBA', (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Tufts
    draw.line([(5, 15), (10, 5)], fill=(50, 150, 50), width=1)
    draw.line([(10, 5), (15, 15)], fill=(50, 150, 50), width=1)
    draw.line([(8, 12), (10, 2)], fill=(80, 180, 80), width=1)
    
    img.save(path)

def create_shoreline_sprite(path):
    # Represents a single edge of water/foam
    # Width ~ hex_edge_length. Height ~ thickness of effect.
    # We'll make it horizontal, then rotate it in code.
    w, h = 100, 30
    img = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # Wavy foam
    # Draw a sine wave or just chunky foam
    points = []
    import math
    for x in range(w):
        y = 15 + math.sin(x * 0.2) * 5
        points.append((x, y))
        
    # Draw thick foam
    draw.line(points, fill=(200, 230, 255, 200), width=4)
    # Highlight
    points_high = [(x, y-2) for x, y in points]
    draw.line(points_high, fill=(255, 255, 255, 255), width=2)
    
    img.save(path)
    
def main():
    if not os.path.exists("assets/sprites"):
        os.makedirs("assets/sprites")
    
    create_tree_sprite("assets/sprites/tree_1.png", (34, 139, 34))
    create_tree_sprite("assets/sprites/tree_2.png", (0, 100, 0))
    create_tree_sprite("assets/sprites/tree_3.png", (46, 139, 87)) # SeaGreen
    create_tree_sprite("assets/sprites/tree_4.png", (85, 107, 47)) # DarkOliveGreen
    create_tree_sprite("assets/sprites/tree_5.png", (107, 142, 35)) # OliveDrab
    create_tree_sprite("assets/sprites/tree_6.png", (100, 110, 30)) # Muddy green
    
    create_mountain_sprite("assets/sprites/mountain_1.png", (120, 120, 120))
    create_mountain_sprite("assets/sprites/mountain_2.png", (100, 100, 100))
    create_grass_sprite("assets/sprites/grass_1.png")
    create_shoreline_sprite("assets/sprites/shoreline.png")
    
    print("Sprites generated.")

if __name__ == "__main__":
    main()
