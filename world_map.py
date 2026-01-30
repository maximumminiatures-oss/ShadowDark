"""
Hex-based world map system for ShadowDark RPG
Handles terrain generation, rendering, fog of war, and player movement.
"""

import random
import math
import os
from enum import Enum
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
import tkinter as tk
from tkinter import Canvas, messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
from name_generator import generate_forest_name, generate_desert_name, generate_ocean_name, generate_lake_name
from player_controls import PlayerControls
from hex_painter import HexPainter

# Constants
HEX_SIZE = 74  # Radius (center to corner). Width ~= 128px, Height = 148px
HIDDEN_FOG_ALPHA = 255  # Fully opaque
SHROUD_FOG_ALPHA = 150  # Explored but not currently visible (if we implement LoS)

class TerrainType(Enum):
    """Terrain types with associated rules and generation weights"""
    # Normalized weights - all natural terrains now equal chance
    GRASS = ("grass", 1.0, True, 1)      
    FOREST = ("forest", 1.0, True, 2)
    MOUNTAIN = ("mountain", 1.0, True, 3)
    WATER = ("water", 1.0, False, 999)
    SWAMP = ("swamp", 1.0, True, 3)
    HILLS = ("hills", 1.0, True, 2)
    DESERT = ("desert", 1.0, True, 2)
    # Special types remain rare
    TOWN = ("town", 0.02, True, 0)
    DUNGEON = ("dungeon", 0.02, True, 0)
    
    def __init__(self, display_name, base_weight, passable, movement_cost):
        self.display_name = display_name
        self.base_weight = base_weight
        self.passable = passable
        self.movement_cost = movement_cost

@dataclass
class HexTile:
    """Represents a single hex tile with terrain, decorations, and fog state"""
    q: int  # Axial coordinate Q
    r: int  # Axial coordinate R
    terrain: TerrainType
    decorations: List[str]  # Asset names like "tall_tree_nw", "mountain_peak"
    is_explored: bool = False
    is_visible: bool = False
    variant_id: int = 0  # 0-3 for random visual variations
    
    def get_pixel_coords(self, size: int) -> Tuple[float, float]:
        """Convert axial hex coordinates to pixel coordinates (pointy-top orientation)"""
        # x = size * sqrt(3) * (q + r/2)
        # y = size * 3/2 * r
        # NOTE: The formula in the advice was slightly different, using typical pointy-top conversion here
        x = size * (math.sqrt(3) * self.q + math.sqrt(3)/2 * self.r)
        y = size * (3./2 * self.r)
        return (x, y)
    
    @property
    def key(self) -> Tuple[int, int]:
        return (self.q, self.r)

@dataclass
class MapLabel:
    text: str
    x: float
    y: float
    angle: float
    color: str = "white"

class HexMap:
    """Manages hex generation, storage, and queries"""
    
    def __init__(self, radius: int = 10, hex_size: int = HEX_SIZE):
        """
        Args:
            radius: Number of hex rings around center (10 = ~300+ hexes)
            hex_size: Pixel size of each hex (radius)
        """
        self.radius = radius
        self.hex_size = hex_size
        self.hexes: Dict[Tuple[int, int], HexTile] = {}
        self.center = (0, 0)  # Center hex at origin
        self.labels: List[MapLabel] = []
        
        # Terrain adjacency weights - higher = more likely to be adjacent
        self.terrain_affinity = {
            TerrainType.WATER: {
                TerrainType.FOREST: 4,
                TerrainType.MOUNTAIN: 1,
                TerrainType.SWAMP: 5,
                TerrainType.HILLS: 4,
                TerrainType.GRASS: 10,
                TerrainType.DESERT: 2,
            },
            TerrainType.FOREST: {
                TerrainType.WATER: 5,
                TerrainType.MOUNTAIN: 5,
                TerrainType.SWAMP: 7,
                TerrainType.HILLS: 7,
                TerrainType.GRASS: 10,
                TerrainType.DESERT: 2,
            },
            TerrainType.MOUNTAIN: {
                TerrainType.WATER: 1,
                TerrainType.FOREST: 3,
                TerrainType.SWAMP: 1,
                TerrainType.HILLS: 10,
                TerrainType.GRASS: 3,
                TerrainType.DESERT: 3,
            },
            TerrainType.SWAMP: {
                TerrainType.WATER: 10,
                TerrainType.FOREST: 9,
                TerrainType.MOUNTAIN: 1,
                TerrainType.HILLS: 3,
                TerrainType.GRASS: 8,
                TerrainType.DESERT: 1,
            },
            TerrainType.HILLS: {
                TerrainType.WATER: 3,
                TerrainType.FOREST: 7,
                TerrainType.MOUNTAIN: 10,
                TerrainType.SWAMP: 3,
                TerrainType.GRASS: 10,
                TerrainType.DESERT: 7,
            },
            TerrainType.GRASS: {
                TerrainType.WATER: 10,
                TerrainType.FOREST: 10,
                TerrainType.MOUNTAIN: 2,
                TerrainType.SWAMP: 10,
                TerrainType.HILLS: 10,
                TerrainType.DESERT: 10,
            },
            TerrainType.DESERT: {
                TerrainType.WATER: 2,
                TerrainType.FOREST: 4,
                TerrainType.MOUNTAIN: 3,
                TerrainType.SWAMP: 1,
                TerrainType.HILLS: 10,
                TerrainType.GRASS: 10,
            },
            TerrainType.TOWN: {
                TerrainType.WATER: 10,
                TerrainType.FOREST: 3,
                TerrainType.MOUNTAIN: 1,
                TerrainType.SWAMP: 1,
                TerrainType.HILLS: 5,
                TerrainType.GRASS: 10,
                TerrainType.DESERT: 3,
            },
            TerrainType.DUNGEON: {
                TerrainType.WATER: 3,
                TerrainType.FOREST: 5,
                TerrainType.MOUNTAIN: 10,
                TerrainType.SWAMP: 10,
                TerrainType.HILLS: 6,
                TerrainType.GRASS: 3,
                TerrainType.DESERT: 10,
            },
        }
    
    def generate_map(self):
        """Generate all hexes with terrain using coherent clustering"""
        # Ensure spiral order so neighbors exist when we generate
        hexes_to_gen = self._get_spiral_coords(self.radius)
        
        for q, r in hexes_to_gen:
            if q == 0 and r == 0:
                # Center is always Town or safe Grass
                terrain = TerrainType.TOWN
                decorations = []
                self.hexes[(q, r)] = HexTile(q, r, terrain, decorations, is_explored=True, is_visible=True)
            else:
                self.hexes[(q, r)] = self._generate_hex_tile(q, r)
        
        self._analyze_clusters()

    def _analyze_clusters(self):
        """Identify clusters of terrain and generate labels"""
        print("Analyzing map clusters...")
        
        # Find forest clusters
        visited_forest = set()
        forest_count = 0
        for coord, tile in self.hexes.items():
            if tile.terrain == TerrainType.FOREST and coord not in visited_forest:
                cluster = self._flood_fill_terrain(coord, visited_forest, TerrainType.FOREST)
                if len(cluster) >= 5:  # Increased threshold to avoid clutter
                    self._generate_cluster_label(cluster, generate_forest_name)
                    forest_count += 1
        print(f"Generated {forest_count} forest labels.")
        
        # Find desert clusters
        visited_desert = set()
        desert_count = 0
        for coord, tile in self.hexes.items():
            if tile.terrain == TerrainType.DESERT and coord not in visited_desert:
                cluster = self._flood_fill_terrain(coord, visited_desert, TerrainType.DESERT)
                if len(cluster) >= 5:  # Same threshold
                    self._generate_cluster_label(cluster, generate_desert_name)
                    desert_count += 1
        print(f"Generated {desert_count} desert labels.")
        
        # Find water clusters
        visited_water = set()
        water_count = 0
        for coord, tile in self.hexes.items():
            if tile.terrain == TerrainType.WATER and coord not in visited_water:
                cluster = self._flood_fill_terrain(coord, visited_water, TerrainType.WATER)
                if len(cluster) >= 3:  # Smaller threshold for water
                    # Determine if ocean or lake/inland sea
                    touches_boundary = self._cluster_touches_boundary(cluster)
                    cluster_width = self._measure_cluster_width(cluster)
                    
                    if touches_boundary or cluster_width >= 10:
                        # Ocean - can have multiple labels
                        self._generate_water_labels(cluster, generate_ocean_name, cluster_width >= 10)
                        water_count += 1
                    else:
                        # Lake/Inland Sea - single label
                        self._generate_cluster_label(cluster, generate_lake_name)
                        water_count += 1
        print(f"Generated {water_count} water labels.")

    def _flood_fill_terrain(self, start_coord, visited, terrain_type: TerrainType) -> List[HexTile]:
        """Flood fill to find all connected hexes of a specific terrain type"""
        cluster = []
        queue = [start_coord]
        visited.add(start_coord)
        
        while queue:
            curr = queue.pop(0)
            if curr in self.hexes:
                cluster.append(self.hexes[curr])
            
            for nq, nr in self._get_neighbors(*curr):
                if (nq, nr) not in visited and (nq, nr) in self.hexes:
                    if self.hexes[(nq, nr)].terrain == terrain_type:
                        visited.add((nq, nr))
                        queue.append((nq, nr))
                        
        return cluster

    def _flood_fill_forest(self, start_coord, visited) -> List[HexTile]:
        """Legacy method - delegates to _flood_fill_terrain"""
        return self._flood_fill_terrain(start_coord, visited, TerrainType.FOREST)

    def _cluster_touches_boundary(self, cluster: List[HexTile]) -> bool:
        """Check if a cluster touches the edge of the generated map"""
        for tile in cluster:
            # Check if any neighbor is outside our hex map
            for nq, nr in self._get_neighbors(tile.q, tile.r):
                if (nq, nr) not in self.hexes:
                    return True
        return False
    
    def _measure_cluster_width(self, cluster: List[HexTile]) -> int:
        """Measure the maximum width of a cluster (max distance between any two points)"""
        if len(cluster) < 2:
            return 1
        
        points = [(h.q, h.r) for h in cluster]
        max_dist = 0
        
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                q1, r1 = points[i]
                q2, r2 = points[j]
                # Axial distance = (|q1-q2| + |r1-r2| + |q1+r1-q2-r2|) / 2
                dist = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2
                max_dist = max(max_dist, dist)
        
        return max_dist
    
    def _generate_water_labels(self, cluster: List[HexTile], name_gen_func, is_large: bool):
        """Generate water labels. For large oceans, place multiple labels at least 3 hexes apart."""
        if not is_large:
            # Single label for small water bodies
            self._generate_cluster_label(cluster, name_gen_func)
            return
        
        # For large oceans, find boundary water tiles (adjacent to non-water)
        boundary_tiles = []
        for tile in cluster:
            is_boundary = False
            for nq, nr in self._get_neighbors(tile.q, tile.r):
                if (nq, nr) not in self.hexes or self.hexes[(nq, nr)].terrain != TerrainType.WATER:
                    is_boundary = True
                    break
            if is_boundary:
                boundary_tiles.append(tile)
        
        if not boundary_tiles:
            # Fallback if no boundary found
            self._generate_cluster_label(cluster, name_gen_func)
            return
        
        # Place labels on boundary tiles, at least 3 hexes apart
        placed_labels = []
        for tile in boundary_tiles:
            # Check if this tile is at least 3 hexes away from all already placed labels
            can_place = True
            for placed_tile in placed_labels:
                q1, r1 = tile.q, tile.r
                q2, r2 = placed_tile.q, placed_tile.r
                dist = (abs(q1 - q2) + abs(r1 - r2) + abs(q1 + r1 - q2 - r2)) // 2
                if dist < 3:
                    can_place = False
                    break
            
            if can_place:
                px, py = tile.get_pixel_coords(self.hex_size)
                # Calculate angle for this label (simple approach: use cluster center direction)
                center_q = sum(t.q for t in cluster) / len(cluster)
                center_r = sum(t.r for t in cluster) / len(cluster)
                dy = center_r - tile.r
                dx = center_q - tile.q
                angle = math.degrees(math.atan2(dy, dx))
                
                if angle > 90:
                    angle -= 180
                elif angle < -90:
                    angle += 180
                
                name = name_gen_func()
                self.labels.append(MapLabel(name, px, py, angle))
                placed_labels.append(tile)

    def _generate_cluster_label(self, cluster: List[HexTile], name_generator_func):
        # Calculate centroids and fit a line
        if not cluster: return
        
        # Get pixel coordinates for all hexes
        points = []
        for h in cluster:
            px, py = h.get_pixel_coords(self.hex_size)
            points.append((px, py))
            
        # Find the two most distant points to define length and angle
        max_dist = 0
        p1_best, p2_best = points[0], points[0]
        
        # Simple N^2 search for diameter (N is usually small < 20 for forests)
        # If N is large, we might want a convex hull, but this is fine only running once
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                p1 = points[i]
                p2 = points[j]
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                dist = dx*dx + dy*dy
                if dist > max_dist:
                    max_dist = dist
                    p1_best = p1
                    p2_best = p2
        
        # Midpoint
        mx = (p1_best[0] + p2_best[0]) / 2
        my = (p1_best[1] + p2_best[1]) / 2
        
        # Angle in degrees
        dy = p2_best[1] - p1_best[1]
        dx = p2_best[0] - p1_best[0]
        angle = math.degrees(math.atan2(dy, dx))
        
        # Ensure text is upright (-90 to 90 degrees preference)
        if angle > 90:
            angle -= 180
        elif angle < -90:
            angle += 180
            
        name = name_generator_func()
        
        self.labels.append(MapLabel(name, mx, my, angle))

    def _get_spiral_coords(self, radius: int) -> List[Tuple[int, int]]:
        """Get hex coordinates in spiral from center outward"""
        results = [(0, 0)]
        for k in range(1, radius + 1):
            q, r = 0, -k
            for _ in range(k):
                q += 1; results.append((q, r))
            for _ in range(k):
                r += 1; results.append((q, r))
            for _ in range(k):
                q -= 1; r += 1; results.append((q, r))
            for _ in range(k):
                q -= 1; results.append((q, r))
            for _ in range(k):
                r -= 1; results.append((q, r))
            for _ in range(k):
                q += 1; r -= 1; results.append((q, r))
        return results
    
    def _generate_hex_tile(self, q: int, r: int) -> HexTile:
        """Generate a single hex with terrain using weighted adjacency"""
        terrain = self._pick_terrain(q, r)
        decorations = self._generate_decorations(terrain)
        variant_id = random.randint(0, 3) 
        return HexTile(q, r, terrain, decorations, variant_id=variant_id)

    def _get_noise_val(self, q: int, r: int, scale: float) -> float:
        """Deterministic noise helper. Returns roughly -1.0 to 1.0"""
        # Simple coordinate hashing for randomness consistency
        # Using primes to avoid repeating patterns on integer grids
        val = math.sin(q * scale) + math.cos(r * scale * 1.1) 
        val += 0.5 * math.sin((q + r) * scale * 1.7)
        return val / 2.5  # Normalize roughly to [-1, 1]
    
    def _pick_terrain(self, q: int, r: int) -> TerrainType:
        """
        Pick terrain using a noise-based approach to ensure proper clump sizes.
        - Primary biomes uses medium-freq noise (scale ~0.35) for ~5-hex blobs.
        - Mountains use high-freq ridged noise (scale ~0.4) for narrow bands.
        """
        
        # 1. MOUNTAINS (Narrow Bands)
        # Use a "ridge" function: 1.0 - abs(noise). High values = center of ridge.
        # Scale 0.45 creates bands. Thresholding creates width.
        m_noise = self._get_noise_val(q + 123, r - 456, 0.45) # Offset coordinates
        ridge_val = 1.0 - abs(m_noise)
        # Threshold > 0.85 keeps it narrow (top 15% of the wave)
        # This averages roughly 2 hexes wide
        if ridge_val > 0.88:
            return TerrainType.MOUNTAIN
            
        # 2. MAIN BIOMES (Broad Clumps)
        # Use smoother noise for main terrain blobs
        b_noise = self._get_noise_val(q, r, 0.35) 
        
        # Add slight local randomness to blur edges (irregularity)
        b_noise += random.uniform(-0.15, 0.15)
        
        # Map noise range (-1.2 to 1.2) to terrain gradient
        # Order aims for logical adjacency: Water <-> Swamp <-> Forest <-> Grass <-> Hills <-> Desert
        # This naturally groups them.
        
        # Normalize roughly to 0..1
        val = (b_noise + 1.0) / 2.0
        val = max(0.0, min(1.0, val))
        
        if val < 0.18: return TerrainType.WATER
        if val < 0.28: return TerrainType.SWAMP
        if val < 0.50: return TerrainType.FOREST
        if val < 0.72: return TerrainType.GRASS
        if val < 0.88: return TerrainType.HILLS
        return TerrainType.DESERT

        # Step 3: Rare Features (Town/Dungeon) - applied as random overrides
        if random.random() < 0.005: return TerrainType.TOWN
        if random.random() < 0.005: return TerrainType.DUNGEON
        
        return TerrainType.GRASS # Fallback
    
    def _get_neighbors(self, q: int, r: int) -> List[Tuple[int, int]]:
        """Get 6 neighboring hex coordinates (axial)"""
        # Pointy-top hex neighbors in axial coordinates:
        # (+1, 0), (+1, -1), (0, -1), (-1, 0), (-1, +1), (0, +1)
        vectors = [
            (1, 0), (1, -1), (0, -1), 
            (-1, 0), (-1, 1), (0, 1)
        ]
        return [(q + dq, r + dr) for dq, dr in vectors]
    
    def _generate_decorations(self, terrain: TerrainType) -> List[str]:
        """Generate random decorations/assets for a hex"""
        decorations = []
        
        decoration_pools = {
            TerrainType.FOREST: ["tree_1", "tree_2", "tree_group", "tree_tall_nw"],
            TerrainType.MOUNTAIN: ["mountain_1", "mountain_peak_nw", "mountain_small"],
            TerrainType.GRASS: ["grass_tuft_1", "flower_1", "rock_small"],
            TerrainType.WATER: ["waves_1", "lilypad"],
            TerrainType.SWAMP: ["dead_tree", "swamp_grass"],
            TerrainType.HILLS: ["hill_1", "hill_2"],
            TerrainType.DESERT: ["cactus", "rocks", "dune"],
            TerrainType.TOWN: ["house_1", "tower"],
            TerrainType.DUNGEON: ["ruins", "cave_entrance"]
        }
        
        if terrain in decoration_pools:
            if random.random() < 0.4: # 40% chance of decoration
                count = random.randint(1, 2)
                pool = decoration_pools[terrain]
                decorations = random.choices(pool, k=count)
        
        return decorations
    
    def get_hex_at(self, q: int, r: int) -> Optional[HexTile]:
        return self.hexes.get((q, r))
    
    def reveal_hex(self, q: int, r: int, radius: int = 1):
        """Reveal hex and neighbors (fog of war removal)"""
        # Simple BFS / flooding for range
        seen = set()
        queue = [(q, r, 0)]
        seen.add((q, r))
        
        while queue:
            curr_q, curr_r, dist = queue.pop(0)
            
            # Mark as explored
            if (curr_q, curr_r) in self.hexes:
                self.hexes[(curr_q, curr_r)].is_explored = True
                # In this simple implementation, explored = visible
                # A proper LoS system would separate known-but-dark from visible
                self.hexes[(curr_q, curr_r)].is_visible = True
            
            if dist < radius:
                for nq, nr in self._get_neighbors(curr_q, curr_r):
                    if (nq, nr) not in seen:
                        seen.add((nq, nr))
                        queue.append((nq, nr, dist + 1))


class HexMapRenderer:
    """Handles rendering of hex map with layers using PIL and Tkinter"""
    
    def __init__(self, world_map: HexMap, canvas: Canvas):
        self.world_map = world_map
        self.canvas = canvas
        self.hex_size = world_map.hex_size
        
        # Caches
        self.asset_cache: Dict[str, Image.Image] = {} # Key: "TerrainName_vX"
        self.tk_asset_cache: Dict[str, ImageTk.PhotoImage] = {} 
        self.shoreline_cache: Dict[int, ImageTk.PhotoImage] = {} # Key: edge_index 0-5
        self.tk_images: Dict[str, ImageTk.PhotoImage] = {} # Per-frame unique items if needed
        self.label_cache: Dict[str, ImageTk.PhotoImage] = {} # Cache for label images
        self.unique_hex_cache: Dict[Tuple[int, int], ImageTk.PhotoImage] = {} # Key: (q, r) for unique tiles
        self.forest_base_cache: Dict[int, Image.Image] = {} # Key: base index 1-6
        
        self._init_assets()
    
    def _init_assets(self):
        """Load or generate assets"""
        asset_dir = "assets/hex_tiles"
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)
            
        # Ensure we have base images for all terrains with variants
        for terrain in TerrainType:
            for v in range(4): # 0 to 3 variants
                filename = f"{terrain.display_name}_v{v}.png"
                path = os.path.join(asset_dir, filename)
                
                # key e.g. "mountain_v0"
                key = f"{terrain.display_name}_v{v}"
                
                if not os.path.exists(path):
                    self._generate_procedural_hex(terrain, path, v)
                
                img = Image.open(path).convert("RGBA")
                self.asset_cache[key] = img
                self.tk_asset_cache[key] = ImageTk.PhotoImage(img)
            
        # Generate Shoreline Overlays (RAM only, fast enough)
        for i in range(6):
            self._generate_shoreline_overlay(i)
            
        # Decorations placeholder generation (simplified)
        # In a real scenario, these would be separate files
        # We can simulate them by drawing on top of copies or new images
        
        # Fog
        fog_path = os.path.join(asset_dir, "fog.png")
        if not os.path.exists(fog_path):
            self._generate_fog_placeholder(fog_path)
        
        fog_img = Image.open(fog_path).convert("RGBA")
        self.asset_cache["fog"] = fog_img
        self.tk_asset_cache["fog"] = ImageTk.PhotoImage(fog_img)

    def _generate_shoreline_overlay(self, edge_index: int):
        """Generate a transparent overlay with a shoreline on one edge"""
        width = int(math.sqrt(3) * self.hex_size)
        height = int(2 * self.hex_size)
        padding = 80  # Match hex tile padding
        img_w, img_h = width + padding, height + padding
        
        img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        # draw = ImageDraw.Draw(img) # No longer needed for sprite pasting
        
        cx, cy = img_w / 2, img_h / 2
        HexPainter.draw_shoreline_overlay(img, cx, cy, self.hex_size, edge_index)
        
        self.shoreline_cache[edge_index] = ImageTk.PhotoImage(img)

    def _generate_procedural_hex(self, terrain: TerrainType, path: str, variant_id: int):
        """Generate a procedurally painted hex tile"""
        width = int(math.sqrt(3) * self.hex_size)
        height = int(2 * self.hex_size)
        # Increased padding to prevent trees/mountains from being cut off
        padding = 80  # Large enough for rotated/scaled sprites
        img_w, img_h = width + padding, height + padding
        
        img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        cx, cy = img_w / 2, img_h / 2
        
        # Base Colors
        colors = {
            TerrainType.GRASS: (100, 200, 100, 255),
            TerrainType.FOREST: (34, 100, 34, 255), # Darker green base
            TerrainType.MOUNTAIN: (140, 140, 140, 255),
            TerrainType.WATER: (65, 105, 225, 255),
            TerrainType.SWAMP: (85, 107, 47, 255),
            TerrainType.HILLS: (218, 165, 32, 255),
            TerrainType.DESERT: (237, 201, 175, 255),
            TerrainType.TOWN: (205, 92, 92, 255),
            TerrainType.DUNGEON: (75, 0, 130, 255),
        }
        fill_col = colors.get(terrain, (255, 255, 255, 255))
        
        # 1. Draw Base Hex
        HexPainter.draw_hex_base(draw, cx, cy, self.hex_size, fill_col)
        
        # 2. Draw Features based on terrain
        seed = f"{terrain.name}_{variant_id}" # Consistent seed for this variant asset
        
        if terrain == TerrainType.MOUNTAIN:
            # Passes 'img' now, not 'draw'
            HexPainter.draw_mountain_variant(img, cx, cy, self.hex_size, seed)
        
        elif terrain == TerrainType.FOREST:
            # For cached variants, we now only draw the base if we want unique trees later.
            # But _init_assets generates generic variants v0-v3.
            # If we switch to unique on-the-fly generation for FOREST, 
            # we should still generate these as fallbacks or just regular full tiles?
            # User wants UNIQUE.
            # Let's keep this as is for fallback, but _draw_hex will ignore it.
            HexPainter.draw_forest_variant(img, cx, cy, self.hex_size, seed)
            
        elif terrain == TerrainType.GRASS:
            HexPainter.draw_grass_variant(img, cx, cy, self.hex_size, seed)
            
        elif terrain == TerrainType.HILLS:
            # We can reuse mountain painter but fewer/smaller? 
            # Or just leave hills as flat colored for now
            pass
            
        # Draw Text Label (debug or style)
        # try:
        #    draw.text((cx - 20, cy - 10), f"{terrain.display_name[:3]}", fill=(0,0,0,128))
        # except:
        #    pass
            
        img.save(path)

    def _load_forest_base_image(self, index: int) -> Image.Image:
        if index in self.forest_base_cache:
            return self.forest_base_cache[index]

        asset_dir = "assets/hex_tiles"
        path = os.path.join(asset_dir, f"forest_base_{index}.png")

        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
        else:
            # Fallback: generate a simple green base if the file is missing
            width = int(math.sqrt(3) * self.hex_size)
            height = int(2 * self.hex_size)
            padding = 80
            img_w, img_h = width + padding, height + padding
            img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            cx, cy = img_w / 2, img_h / 2
            HexPainter.draw_hex_base(draw, cx, cy, self.hex_size, (34, 100, 34, 255))

        self.forest_base_cache[index] = img
        return img

    def _generate_unique_forest_tile(self, hex_tile: HexTile) -> ImageTk.PhotoImage:
        """Generate a unique forest tile on the fly"""
        width = int(math.sqrt(3) * self.hex_size)
        height = int(2 * self.hex_size)
        padding = 80
        img_w, img_h = width + padding, height + padding

        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
        cx, cy = img_w / 2, img_h / 2

        # Deterministic seed unique to this hex
        seed = (hex_tile.q * 73856093) ^ (hex_tile.r * 19349663)
        rng = random.Random(seed)

        # 1. Choose a random forest base (1-6) and rotate it
        base_index = rng.randint(1, 6)
        base_img = self._load_forest_base_image(base_index).copy()
        rotation = rng.choice([0, 60, 120, 180, 240, 300])
        if rotation:
            base_img = base_img.rotate(rotation, expand=True, resample=Image.BICUBIC)

        bw, bh = base_img.size
        left = int(cx - bw / 2)
        top = int(cy - bh / 2)
        img.paste(base_img, (left, top), base_img)

        # 2. Draw Unique Trees seeded by coordinates
        tree_seed = seed ^ 0xA5A5A5A5
        HexPainter.draw_forest_variant(img, cx, cy, self.hex_size, tree_seed)

        return ImageTk.PhotoImage(img)

    def _generate_fog_placeholder(self, path: str):
        width = int(math.sqrt(3) * self.hex_size)
        height = int(2 * self.hex_size)
        padding = 80  # Match the hex tile padding
        img = Image.new('RGBA', (width + padding, height + padding), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        cx, cy = (width + padding) / 2, (height + padding) / 2
        
        # Draw hex with same radius as terrain, filled completely with fog
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = cx + self.hex_size * math.cos(angle_rad)
            y = cy + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
            
        draw.polygon(points, fill=(20, 20, 20, 255), outline=(0, 0, 0, 255))
        img.save(path)

    def render_all(self, offset_x=0, offset_y=0):
        """Render the map to the canvas with viewport culling"""
        self.canvas.delete("all")
        self.tk_images.clear() # Clear reference cache
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        canvas_center_x = canvas_width / 2
        canvas_center_y = canvas_height / 2
        
        # Calculate viewing rectangle in world pixel coordinates relative to map center
        # padding of 200px to ensure huge assets overlap correctly
        view_min_x = -canvas_center_x - offset_x - 200
        view_max_x = canvas_center_x - offset_x + canvas_width + 200
        view_min_y = -canvas_center_y - offset_y - 200
        view_max_y = canvas_center_y - offset_y + canvas_height + 200
        
        # Convert bounding box corners to axial coordinates to find Q/R range
        # Corners: (min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)
        corners = [
            (view_min_x, view_min_y),
            (view_max_x, view_min_y),
            (view_max_x, view_max_y),
            (view_min_x, view_max_y)
        ]
        
        qs = []
        rs = []
        
        for x, y in corners:
            # Axial conversion:
            # q = (sqrt(3)/3 * x - 1/3 * y) / size
            # r = (2/3 * y) / size
            q = (math.sqrt(3)/3 * x - 1.0/3 * y) / self.hex_size
            r = (2.0/3 * y) / self.hex_size
            qs.append(q)
            rs.append(r)
            
        q_start = int(min(qs)) - 1
        q_end = int(max(qs)) + 1
        r_start = int(min(rs)) - 1
        r_end = int(max(rs)) + 1
        
        # Collect visible hexes
        visible_hexes = []
        
        for r in range(r_start, r_end + 1):
            for q in range(q_start, q_end + 1):
                hex_tile = self.world_map.get_hex_at(q, r)
                if hex_tile:
                    visible_hexes.append(hex_tile)
        
        # Sort by depth (r, then -q) to handle occlusion correctly
        # We process rows top-to-bottom (increasing r)
        # But within a row, we draw Right-to-Left (decreasing q) so that
        # the Left tile (drawn last) overlaps the Right tile.
        # This prevents the Right tile's base from cutting off the Left tile's trees.
        sorted_hexes = sorted(visible_hexes, key=lambda h: (h.r, -h.q))
        
        for hex_tile in sorted_hexes:
            px, py = hex_tile.get_pixel_coords(self.hex_size)
            screen_x = canvas_center_x + px + offset_x
            screen_y = canvas_center_y + py + offset_y
            
            self._draw_hex(hex_tile, screen_x, screen_y)
            
        # 4. Render Labels (Overlays)
        self._render_labels(offset_x, offset_y, canvas_width, canvas_height)

    def _pixel_to_axial(self, x: float, y: float) -> Tuple[int, int]:
        """Convert pixel coordinates to axial hex coordinates"""
        q = (math.sqrt(3)/3 * x - 1/3 * y) / self.hex_size
        r = (2/3 * y) / self.hex_size
        return self._round_axial(q, r)
    
    def _round_axial(self, q: float, r: float) -> Tuple[int, int]:
        """Round fractional axial coordinates to nearest hex"""
        xgrid = q
        zgrid = r
        ygrid = -q - r
        
        rx = round(xgrid)
        ry = round(ygrid)
        rz = round(zgrid)
        
        x_diff = abs(rx - xgrid)
        y_diff = abs(ry - ygrid)
        z_diff = abs(rz - zgrid)
        
        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
            
        return int(rx), int(rz)

    def _render_labels(self, offset_x, offset_y, width, height):
        canvas_center_x = width / 2
        canvas_center_y = height / 2
        
        # Simple bounds check for labels
        # Labels are centered at mx, my (world coords)
        # Screen x = center_x + mx + offset_x
        
        for label in self.world_map.labels:
            screen_x = canvas_center_x + label.x + offset_x
            screen_y = canvas_center_y + label.y + offset_y
            
            # Loose culling
            if -200 < screen_x < width + 200 and -200 < screen_y < height + 200:
                # Check if the hex at label's world position is visible (fog of war)
                hex_q, hex_r = self._pixel_to_axial(label.x, label.y)
                hex_tile = self.world_map.get_hex_at(hex_q, hex_r)
                
                # Only render label if the hex is visible (not hidden by fog)
                if hex_tile and hex_tile.is_visible:
                    self._draw_label_text(label, screen_x, screen_y)

    def _draw_label_text(self, label: MapLabel, x: float, y: float):
        # We need to draw rotated text. Canvas doesn't support it natively well.
        # We use PIL to create a text image, rotate it, and stamp it.
        
        # Check cache
        cache_key = f"{label.text}_{label.angle}"
        if cache_key in self.label_cache:
            tk_img = self.label_cache[cache_key]
        else:
            # Create image for text
            # Guess size
            font_size = 24
            # We don't have a reliable way to get text size without a font object context, 
            # but we can overestimate.
            # 20 chars * 15px width ~= 300px
            w, h = 600, 100
            
            # Create transparent image
            txt_img = Image.new('RGBA', (w, h), (0,0,0,0))
            draw = ImageDraw.Draw(txt_img)
            
            # Load font if available, else default
            try:
                # Try strict path for Windows or generic name
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\Arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Draw text in center
            # New Pillow versions use specific text bbox
            try:
                bbox = draw.textbbox((0, 0), label.text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
            except:
                # Fallback for old Pillow
                try:
                    text_w, text_h = draw.textsize(label.text, font=font)
                except:
                     text_w, text_h = 200, 30 # absolute fallback
            
            # High contrast text for visibility
            # Stroke: Black, Fill: White/Gold
            draw.text(((w - text_w)/2, (h - text_h)/2), label.text, font=font, fill=(255, 255, 240, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
            
            # Rotate
            # PIL rotates counter-clockwise. Our angle is math atan2 (standard math).
            # If angle is 30 deg (pointing SE), we want text to follow that line.
            # rotate takes degrees.
            rot_img = txt_img.rotate(-label.angle, expand=True, resample=Image.BICUBIC)
            
            tk_img = ImageTk.PhotoImage(rot_img)
            self.label_cache[cache_key] = tk_img
            
        self.tk_images[f"lbl_{x}_{y}"] = tk_img # Keep reference
        # Ensure label is drawn on top of everything
        self.canvas.create_image(x, y, image=tk_img, tags="label")
        self.canvas.tag_raise("label")

    def _draw_hex(self, hex_tile: HexTile, x: float, y: float):
        # 3. Fog
        # If the tile is not explored, ONLY draw the fog and return
        if not hex_tile.is_explored:
            tk_fog = self.tk_asset_cache.get("fog")
            if tk_fog:
                self.canvas.create_image(x, y, image=tk_fog, tags="fog")
            return

        # 1. Terrain Base
        tk_img = None
        
        # If FOREST, use unique generated tile
        if hex_tile.terrain == TerrainType.FOREST:
            tile_key = (hex_tile.q, hex_tile.r)
            if tile_key in self.unique_hex_cache:
                tk_img = self.unique_hex_cache[tile_key]
            else:
                # Generate on the fly
                tk_img = self._generate_unique_forest_tile(hex_tile)
                # Simple cache management - loose limit
                if len(self.unique_hex_cache) > 2000:
                    self.unique_hex_cache.clear()
                self.unique_hex_cache[tile_key] = tk_img
        
        # Standard variant lookup for other terrains (or fallback)
        if not tk_img:
            # Use variant ID
            key = f"{hex_tile.terrain.display_name}_v{hex_tile.variant_id}"
            tk_img = self.tk_asset_cache.get(key)
            
            # Fallback to v0 if specific variant missing (safety)
            if not tk_img:
                tk_img = self.tk_asset_cache.get(f"{hex_tile.terrain.display_name}_v0")
            
        if tk_img:
            self.canvas.create_image(x, y, image=tk_img, tags=f"hex_{hex_tile.q}_{hex_tile.r}")

        # 1.5 Shoreline Overlays
        # If this tile is WATER, check neighbors for Land
        if hex_tile.terrain == TerrainType.WATER:
            neighbors = self.world_map._get_neighbors(hex_tile.q, hex_tile.r)
            # We need strictly ordered directions 0..5
            # _get_neighbors returns list, but directions are fixed order in the method:
            # [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
            # 0: (+1, 0) -> Right (0 deg? No.)
            #
            # Let's re-verify angles. 
            # Flat top vs Pointy top.
            # HexPainter assumes: 60*i - 30.
            # i=0: -30 (Top Right).
            # i=1: 30 (Bottom Right).
            # i=2: 90 (Bottom).
            # i=3: 150 (Bottom Left).
            # i=4: 210 (Top Left).
            # i=5: 270 (Top).
            
            # Axial Neighbors (Pointy Top):
            # (+1, -1): Top Right
            # (+1, 0): Right (Wait, +1 q means move right-ish)
            
            # Let's trust logic mapping:
            # i=0 (Top Right): q+1, r-1
            # i=1 (Right): q+1, r (Actually this is 30deg?)
            # 
            # Standard Pointy Top Axial directions starting from 0 deg (Right) going clockwise?
            # Convention usually:
            # Direction 0: (+1, 0)
            # Direction 1: (+1, -1) --- Wait, +1, -1 is Top Right
            # Direction 2: (0, -1) --- Top Left
            # Direction 3: (-1, 0) --- Left
            # Direction 4: (-1, 1) --- Bottom Left
            # Direction 5: (0, 1) --- Bottom Right
            
            # _get_neighbors lists them as:
            # (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
            # If HexPainter expects i=0 to be Top Right (-30 deg)...
            # Top Right in axial is (+1, -1). That is index 1 in _get_neighbors.
            
            # Let's map explicitly to be safe.
            # HexPainter Vertices:
            # 0: -30 deg (Top Right)
            # 1: 30 deg (Bottom Right)
            # 2: 90 deg (Bottom)
            # 3: 150 deg (Bottom Left)
            # 4: 210 deg (Top Left)
            # 5: 270 deg (Top)
            
            # Axial Neighbors for those directions:
            # Top Right: (+1, -1)
            # Bottom Right: (0, +1)
            # Bottom: ... wait. Pointy top hexes don't have a "Bottom" neighbor directly below?
            # Yes, Pointy top has neighbors at 30, 90, 150...
            # Wait. Pointy top means the "point" is at the top. Vertices are at -90 (top), -30...
            # My HexPainter says `angle_deg = 60 * i - 30`.
            # i=0: -30 (Top Right Vertex). Edge 0 connects Vertex 0 (-30) and Vertex 1 (30).
            # So Edge 0 is the Right-hand vertical-ish edge?
            # Vertex 0 (-30) to Vertex 1 (30). The edge is at 0 degrees (Right).
            # So Edge 0 corresponds to neighbor at (+1, 0).
            
            # i=1: Edge between V1 (30) and V2 (90). Edge is at 60 deg (Bottom Right).
            # Neighbor at (0, +1)?
            
            # Let's assume standard sequence:
            # Edge 0: Right (+1, 0)
            # Edge 1: Bottom Right (0, +1)
            # Edge 2: Bottom Left (-1, +1)
            # Edge 3: Left (-1, 0)
            # Edge 4: Top Left (-1, -1) -- wait (-1, -1)? No.
            # Edge 5: Top Right (+1, -1)
            
            neighbor_deltas = [
                (1, 0),   # Edge 0 (Right)
                (0, 1),   # Edge 1 (Bottom Right)
                (-1, 1),  # Edge 2 (Bottom Left)
                (-1, 0),  # Edge 3 (Left)
                (0, -1),  # Edge 4 (Top Left)
                (1, -1)   # Edge 5 (Top Right)
            ]
            
            for i, (dq, dr) in enumerate(neighbor_deltas):
                nq, nr = hex_tile.q + dq, hex_tile.r + dr
                neighbor = self.world_map.get_hex_at(nq, nr)
                
                # If neighbor is LAND (or at least NOT water), draw shoreline
                # Also treat 'None' (void) as water? No, void is void.
                if neighbor and neighbor.terrain != TerrainType.WATER:
                     tk_overlay = self.shoreline_cache.get(i)
                     if tk_overlay:
                         self.canvas.create_image(x, y, image=tk_overlay, tags=f"shore_{hex_tile.q}_{hex_tile.r}_{i}")

        # 2. Decoration (Pseudo-implementation)
        # In a real version, we'd lookup `hex_tile.decorations` and draw respective images
        # offset by y to create the "pop up" effect.
        if hex_tile.decorations:
            # Just draw a simple indicator for now or use the logic from advice
            # For this MVP, we rely on the base tile text.
            pass
        
        # 3. Fog - Handled at start of method now
        if not hex_tile.is_visible:
            # Shroud (explored but not current) - semi transparent fog
            pass # Implement later


class WorldMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowDark World Map")
        self.root.geometry("1024x768")
        
        # Frame for UI
        self.toolbar = tk.Frame(root, bg="#333", height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self.toolbar, text="Use Arrows to Move | Click to Select", fg="white", bg="#333").pack()
        
        self.canvas = Canvas(root, bg="#1a1a1a")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize Logic
        self.map_data = HexMap(radius=100)
        self.map_data.generate_map()
        
        # Reveal center
        self.map_data.reveal_hex(0, 0, radius=2)
        
        self.renderer = HexMapRenderer(self.map_data, self.canvas)
        
        # Player State
        self.player_pos = (0, 0) # q, r
        self.camera_offset = (0, 0)
        
        # Minimap cache
        self.minimap_image = None
        self.minimap_tk_image = None
        
        # Initialize player controls
        self.player_controls = PlayerControls()
        self.player_controls.set_movement_callback(self._handle_player_move)
        self.player_controls.set_click_callback(self._handle_map_click)
        
        # Bindings
        self.canvas.bind("<Configure>", lambda e: self.on_canvas_resize())
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        
        # Keyboard bindings - arrows (no N/S moves)
        self.root.bind("<Left>", lambda e: self.player_controls.handle_keyboard("Left"))
        self.root.bind("<Right>", lambda e: self.player_controls.handle_keyboard("Right"))
        
        # Keyboard bindings - numpad (no N/S moves)
        self.root.bind("<KP_7>", lambda e: self.player_controls.handle_keyboard("KP_7"))
        self.root.bind("<KP_9>", lambda e: self.player_controls.handle_keyboard("KP_9"))
        self.root.bind("<KP_4>", lambda e: self.player_controls.handle_keyboard("KP_4"))
        self.root.bind("<KP_6>", lambda e: self.player_controls.handle_keyboard("KP_6"))
        self.root.bind("<KP_1>", lambda e: self.player_controls.handle_keyboard("KP_1"))
        self.root.bind("<KP_3>", lambda e: self.player_controls.handle_keyboard("KP_3"))

        # Numpad without NumLock (Home/PgUp/End/PgDn)
        self.root.bind("<Home>", lambda e: self.player_controls.handle_keyboard("KP_7"))
        self.root.bind("<Prior>", lambda e: self.player_controls.handle_keyboard("KP_9"))
        self.root.bind("<End>", lambda e: self.player_controls.handle_keyboard("KP_3"))
        self.root.bind("<Next>", lambda e: self.player_controls.handle_keyboard("KP_1"))
        
        # Initial Render
        self.root.after(100, self.center_camera_on_player)

    def on_canvas_resize(self):
        """Handle canvas resize events"""
        self.renderer.render_all(self.camera_offset[0], self.camera_offset[1])
        self.update_player_token()
        self.render_minimap()
    
    def center_camera_on_player(self):
        """Update camera offset to center the player token"""
        hex_tile = self.map_data.get_hex_at(*self.player_pos)
        if hex_tile:
            # We want player pixel coords (px, py) to be at canvas center (0,0 offset relative to center)
            # screen_x = center_x + px + offset_x
            # We want screen_x = center_x, so: px + offset_x = 0 => offset_x = -px
            px, py = hex_tile.get_pixel_coords(self.map_data.hex_size)
            self.camera_offset = (-px, -py)
            
            self.renderer.render_all(self.camera_offset[0], self.camera_offset[1])
            self.update_player_token()
            self.render_minimap()

    def move_player(self, dq, dr):
        nq = self.player_pos[0] + dq
        nr = self.player_pos[1] + dr
        
        target_hex = self.map_data.get_hex_at(nq, nr)
        if target_hex and target_hex.terrain.passable:
            self.player_pos = (nq, nr)
            self.map_data.reveal_hex(nq, nr, radius=2)
            self.center_camera_on_player()
        else:
            print("Blocked or Void")
    
    def _handle_player_move(self, dq: int, dr: int):
        """Internal handler for player movement from controls"""
        self.move_player(dq, dr)
    
    def _handle_map_click(self, hex_coords: Tuple[int, int]):
        """Internal handler for mouse click movement"""
        target_q, target_r = hex_coords
        target_hex = self.map_data.get_hex_at(target_q, target_r)
        if target_hex and target_hex.terrain.passable:
            self.player_pos = (target_q, target_r)
            self.map_data.reveal_hex(target_q, target_r, radius=2)
            self.center_camera_on_player()
    
    def _on_canvas_click(self, event):
        """Handle canvas mouse click"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        canvas_center = (canvas_width / 2, canvas_height / 2)
        
        self.player_controls.handle_mouse_click(
            (event.x, event.y),
            canvas_center,
            self.camera_offset,
            HEX_SIZE
        )

    def update_player_token(self):
        self.canvas.delete("player_token")
        
        # Calculate screen position
        hex_tile = self.map_data.get_hex_at(*self.player_pos)
        if not hex_tile: return
        
        canvas_center_x = self.canvas.winfo_width() / 2
        canvas_center_y = self.canvas.winfo_height() / 2
        
        px, py = hex_tile.get_pixel_coords(HEX_SIZE)
        screen_x = canvas_center_x + px + self.camera_offset[0]
        screen_y = canvas_center_y + py + self.camera_offset[1]
        
        # Draw Token
        r = 15
        self.canvas.create_oval(screen_x - r, screen_y - r, screen_x + r, screen_y + r, 
                                fill="red", outline="white", width=2, tags="player_token")
    
    def render_minimap(self):
        """Render a hexagonal minimap in the top-right corner"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 100 or canvas_height < 100:
            return  # Canvas not ready
        
        # Minimap dimensions
        minimap_size = 200  # Size of the hexagonal container
        hex_radius = minimap_size // 2
        padding = 20
        
        # Position in top-right
        minimap_x = canvas_width - minimap_size - padding
        minimap_y = padding
        
        # Create PIL image for minimap
        minimap_img = Image.new('RGBA', (minimap_size, minimap_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(minimap_img)
        
        # Calculate pixel size per hex on minimap
        world_radius = self.map_data.radius
        pixels_per_hex = hex_radius / (world_radius * 1.8)  # Scale down more to fit all hexes
        
        # Terrain color mapping
        terrain_colors = {
            TerrainType.GRASS: (100, 200, 100),
            TerrainType.FOREST: (34, 139, 34),
            TerrainType.MOUNTAIN: (169, 169, 169),
            TerrainType.WATER: (65, 105, 225),
            TerrainType.SWAMP: (85, 107, 47),
            TerrainType.HILLS: (218, 165, 32),
            TerrainType.DESERT: (237, 201, 175),
            TerrainType.TOWN: (205, 92, 92),
            TerrainType.DUNGEON: (75, 0, 130),
        }
        
        # Draw hexes
        center_x = minimap_size / 2
        center_y = minimap_size / 2
        
        for (q, r), hex_tile in self.map_data.hexes.items():
            if hex_tile.is_explored:
                # Calculate minimap position
                x = pixels_per_hex * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
                y = pixels_per_hex * (3./2 * r)
                
                screen_x = center_x + x
                screen_y = center_y + y
                
                # Draw small filled circle for each hex
                color = terrain_colors.get(hex_tile.terrain, (128, 128, 128))
                dot_size = max(1, int(pixels_per_hex * 0.8))
                draw.ellipse(
                    (screen_x - dot_size, screen_y - dot_size,
                     screen_x + dot_size, screen_y + dot_size),
                    fill=color
                )
        
        # Draw player position
        player_hex = self.map_data.get_hex_at(*self.player_pos)
        if player_hex:
            px = pixels_per_hex * (math.sqrt(3) * self.player_pos[0] + math.sqrt(3)/2 * self.player_pos[1])
            py = pixels_per_hex * (3./2 * self.player_pos[1])
            p_screen_x = center_x + px
            p_screen_y = center_y + py
            
            # Draw player as red dot
            player_size = max(2, int(pixels_per_hex * 1.2))
            draw.ellipse(
                (p_screen_x - player_size, p_screen_y - player_size,
                 p_screen_x + player_size, p_screen_y + player_size),
                fill=(255, 50, 50),
                outline=(255, 255, 255),
                width=1
            )
        
        # Create hexagonal mask
        mask = Image.new('L', (minimap_size, minimap_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw hexagon mask (flat-top orientation to contain pointy-top hex grid)
        # Rotate by 30 degrees from pointy-top (start at 0 instead of -30)
        hex_points = []
        for i in range(6):
            angle_deg = 60 * i  # Flat-top: starts at 0 degrees
            angle_rad = math.radians(angle_deg)
            x = center_x + hex_radius * math.cos(angle_rad)
            y = center_y + hex_radius * math.sin(angle_rad)
            hex_points.append((x, y))
        
        mask_draw.polygon(hex_points, fill=255)
        
        # Apply mask to minimap
        minimap_img.putalpha(mask)
        
        # Draw border hexagon on the minimap itself
        border_draw = ImageDraw.Draw(minimap_img)
        border_draw.polygon(hex_points, outline=(255, 255, 255, 200), width=3)
        
        # Convert to PhotoImage and display
        self.minimap_image = minimap_img
        self.minimap_tk_image = ImageTk.PhotoImage(minimap_img)
        
        # Delete old minimap and draw new one
        self.canvas.delete("minimap")
        self.canvas.create_image(
            minimap_x + minimap_size // 2,
            minimap_y + minimap_size // 2,
            image=self.minimap_tk_image,
            tags="minimap"
        )
        self.canvas.tag_raise("minimap")

    def on_click(self, event):
        # Convert pixel to hex
        cx = self.canvas.winfo_width() / 2 + self.camera_offset[0]
        cy = self.canvas.winfo_height() / 2 + self.camera_offset[1]
        
        x = event.x - cx
        y = event.y - cy
        
        # Pixel to Axial
        # q = (sqrt(3)/3 * x  -  1/3 * y) / size ??? 
        # Pointy Top matrix:
        # q = (sqrt(3)/3 * x - 1/3 * y) / size
        # r = (2/3 * y) / size
        
        q = (math.sqrt(3)/3 * x - 1/3 * y) / HEX_SIZE
        r = (2./3 * y) / HEX_SIZE
        
        clicked_hex = self.axial_round(q, r)
        
        tile = self.map_data.get_hex_at(clicked_hex[0], clicked_hex[1])
        if tile:
            print(f"Clicked: {clicked_hex} - {tile.terrain.name}")
            if tile.terrain in [TerrainType.DUNGEON, TerrainType.TOWN]:
                messagebox.showinfo("Enter Location", f"Enter {tile.terrain.value[0]}?")
        else:
            print(f"Clicked void: {clicked_hex}")

    def axial_round(self, x, y):
        # Convert axial to cube
        xgrid = x
        zgrid = y
        ygrid = -x - y
        
        rx = round(xgrid)
        ry = round(ygrid)
        rz = round(zgrid)
        
        x_diff = abs(rx - xgrid)
        y_diff = abs(ry - ygrid)
        z_diff = abs(rz - zgrid)
        
        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry
            
        return int(rx), int(rz)

if __name__ == "__main__":
    root = tk.Tk()
    app = WorldMapApp(root)
    root.mainloop()
