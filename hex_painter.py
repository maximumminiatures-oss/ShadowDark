import math
import random
import os
from PIL import Image, ImageDraw

class HexPainter:
    """
    Utility class for painting hexagonal tiles and terrain features using PIL.
    Aligns with the 'Pointy Top' convention where:
    angle_deg = 60 * i - 30.
    """
    
    # Static sprite cache
    _sprites = {}
    
    @classmethod
    def load_sprite(cls, name):
        if name in cls._sprites:
            return cls._sprites[name]
        
        # Try finding in assets/sprites/
        try:
            path = f"assets/sprites/{name}.png"
            if os.path.exists(path):
                img = Image.open(path).convert("RGBA")
                cls._sprites[name] = img
                return img
        except Exception as e:
            print(f"Failed to load sprite {name}: {e}")
            
        cls._sprites[name] = None
        return None

    @staticmethod
    def _get_hex_vertex(cx, cy, size, index):
        """
        Calculates the vertex coordinates for a given index (0-5).
        Vertex 0 is Top-Right (-30 deg), Vertex 1 is Bottom-Right (30 deg), etc.
        """
        angle_deg = 60 * index - 30
        angle_rad = math.radians(angle_deg)
        x = cx + size * math.cos(angle_rad)
        y = cy + size * math.sin(angle_rad)
        return x, y

    @staticmethod
    def draw_hex_base(draw, center_x, center_y, size, color):
        """
        Draws the filled hexagon with a default outline.
        """
        points = []
        for i in range(6):
            points.append(HexPainter._get_hex_vertex(center_x, center_y, size, i))
        
        # Uses a dark gray outline consistent with typical map styles
        draw.polygon(points, fill=color, outline=(50, 50, 50))

    @staticmethod
    def draw_mountain_variant(image, cx, cy, size, seed):
        """
        Draws randomized mountain peaks using sprites.
        """
        rng = random.Random(seed)
        num_peaks = rng.randint(1, 3)
        
        peaks = []
        for _ in range(num_peaks):
            ox = rng.uniform(-size * 0.35, size * 0.35)
            oy = rng.uniform(-size * 0.35, size * 0.35)
            peaks.append((cx + ox, cy + oy))
            
        peaks.sort(key=lambda p: p[1])
        
        # Load sprites
        sprites = []
        for i in range(1, 3):
            s = HexPainter.load_sprite(f"mountain_{i}")
            if s: sprites.append(s)
            
        if not sprites:
             return
        
        for px, py in peaks:
            # Pick random sprite
            sprite = rng.choice(sprites)
            # Scale
            s_scale = rng.uniform(0.8, 1.2) * (size / 60.0) 
            w, h = sprite.size
            nw, nh = int(w * s_scale), int(h * s_scale)
            
            s_resized = sprite.resize((nw, nh), Image.Resampling.LANCZOS)
            
            # Position: Center bottom-ish
            left = int(px - nw / 2)
            top = int(py - nh * 0.8) # Move up slightly so base isn't lowest point
            
            image.paste(s_resized, (left, top), s_resized)

    @staticmethod
    def draw_forest_variant(image, cx, cy, size, seed):
        """
        Draws randomized tree clumps using sprites with variations.
        """
        rng = random.Random(seed)
        num_trees = rng.randint(5, 8)
        
        trees = []
        for _ in range(num_trees):
            # Base distribution in hex
            ox = rng.uniform(-size * 0.5, size * 0.5)
            oy = rng.uniform(-size * 0.5, size * 0.5)
            
            # User requested extra offset capability +/- 20px
            # Applying it here or during paste? 
            # Applying here affects Z-sorting (which is good).
            offset_x = rng.uniform(-20, 20)
            offset_y = rng.uniform(-20, 20)
            
            trees.append((cx + ox + offset_x, cy + oy + offset_y))
            
        trees.sort(key=lambda p: p[1])
        
        sprites = []
        for i in range(1, 19): # Trees 1-18
            s = HexPainter.load_sprite(f"tree_{i}")
            if s: sprites.append(s)
            
        if not sprites: return
        
        for tx, ty in trees:
            sprite = rng.choice(sprites)
            
            # 1. Flip Horizontal
            if rng.choice([True, False]):
                sprite = sprite.transpose(Image.FLIP_LEFT_RIGHT)
                
            # 2. Rotate +/- 30 degrees
            angle = rng.uniform(-30, 30)
            # Expand=True changes size, but we need to keep anchor at bottom center
            sprite = sprite.rotate(angle, expand=True, resample=Image.BICUBIC)
            
            # Scale
            s_scale = rng.uniform(0.6, 0.9) * (size / 40.0)
            w, h = sprite.size
            nw, nh = int(w * s_scale), int(h * s_scale)
            
            s_resized = sprite.resize((nw, nh), Image.Resampling.LANCZOS)
            
            # Position: anchor at bottom center
            left = int(tx - nw / 2)
            top = int(ty - nh * 0.9)
            
            # Paste with alpha
            image.paste(s_resized, (left, top), s_resized)
            
    @staticmethod
    def draw_grass_variant(image, cx, cy, size, seed):
        """
        Draws randomized grass using sprites.
        """
        rng = random.Random(seed)
        num_tufts = rng.randint(4, 7)
        
        sprite = HexPainter.load_sprite("grass_1")
        if not sprite: return
        
        for _ in range(num_tufts):
            gx = cx + rng.uniform(-size * 0.6, size * 0.6)
            gy = cy + rng.uniform(-size * 0.6, size * 0.6)
            
            s_scale = rng.uniform(0.6, 1.0) * (size / 40.0)
            w, h = sprite.size
            nw, nh = int(w * s_scale), int(h * s_scale)
            
            s_resized = sprite.resize((nw, nh), Image.Resampling.LANCZOS)
            left = int(gx - nw / 2)
            top = int(gy - nh / 2)
            
            image.paste(s_resized, (left, top), s_resized)



    @staticmethod
    def draw_shoreline_overlay(image, cx, cy, size, edge_index):
        """
        Draws a shoreline sprite along ONE specific edge (0 to 5).
        """
        sprite = HexPainter.load_sprite("shoreline")
        if not sprite: return

        # 1. Calculate Edge Midpoint and Angle
        # Vertex 0: -30 deg. Vertex 1: 30 deg.
        # Edge 0 connects V0 and V1. 
        # Midpoint angle is 0 deg (Right).
        # Edge index i midpoint is (i * 60) degrees.
        
        edge_angle_deg = edge_index * 60
        mid_angle_rad = math.radians(edge_angle_deg)
        
        # Distance to midpoint of edge is size * sqrt(3)/2
        edge_dist = size * math.sqrt(3) / 2
        
        mx = cx + edge_dist * math.cos(mid_angle_rad)
        my = cy + edge_dist * math.sin(mid_angle_rad)
        
        # 2. Resize Sprite to match edge length?
        # Edge length is 'size'.
        sw, sh = sprite.size
        target_w = int(size * 1.2) # Slightly larger to cover corners
        scale = target_w / sw
        target_h = int(sh * scale)
        
        s_resized = sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # 3. Rotate Sprite
        # Sprite is horizontal. 
        # Edge 0 (Right) angle is 0 deg? No, the edge is vertical-ish.
        # Let's trace:
        # V0 (-30 deg) to V1 (30 deg). 
        # The vector V1 - V0 is pointing downwards-right?
        # V0=(cos -30, sin -30) = (0.866, -0.5)
        # V1=(cos 30, sin 30) = (0.866, 0.5)
        # Vec = (0, 1). So Edge 0 is perfectly vertical pointing DOWN.
        # So rotation for Edge 0 should be 90 degrees (if 0 is horizontal right).
        
        # Generalize:
        # Edge i vector angle is (60 * i) + 90 degrees.
        rotation = (edge_index * 60) + 90
        
        # PIL rotate is Counter Clockwise.
        # We want to rotate the image so it aligns with the edge.
        # Start sprite is Horizontal (pointing right).
        # We want it Vertical (pointing down). So -90 degrees? Or 270.
        
        # Let's try: s_rotated = s_resized.rotate(-rotation, expand=True)
        # expand=True changes dimensions, which makes centering harder.
        # Better to rotate without resize if we handle transparent background well, 
        # OR calculate new center.
        s_rotated = s_resized.rotate(-rotation, expand=True, resample=Image.BICUBIC)
        
        # 4. Paste at Midpoint
        rw, rh = s_rotated.size
        left = int(mx - rw / 2)
        top = int(my - rh / 2)
        
        # Calculate normal to push it slightly inward?
        # "Inward" is towards (cx, cy).
        # Normal vector is opposite to mid_angle?
        # Edge midpoint vector is (cos(A), sin(A)).
        # Inward is (-cos(A), -sin(A)).
        
        push_in = size * 0.1
        left -= int(push_in * math.cos(mid_angle_rad))
        top -= int(push_in * math.sin(mid_angle_rad))
        
        image.paste(s_rotated, (left, top), s_rotated)
