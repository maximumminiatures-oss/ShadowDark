"""
Player controls module - handles keyboard, mouse, and joystick input
Maps to hexagonal movement directions.
"""

import math
from enum import Enum
from typing import Tuple, Optional, Callable

class HexDirection(Enum):
    """Six cardinal directions on a pointy-top hex grid (in degrees)"""
    DIRECTION_0 = (1, 0)      # 0°: East/Right
    DIRECTION_60 = (1, -1)    # 60°: Northeast
    DIRECTION_120 = (0, -1)   # 120°: Northwest
    DIRECTION_180 = (-1, 0)   # 180°: West/Left
    DIRECTION_240 = (-1, 1)   # 240°: Southwest
    DIRECTION_300 = (0, 1)    # 300°: Southeast

    def get_delta(self) -> Tuple[int, int]:
        """Return (dq, dr) movement vector"""
        return self.value

class PlayerControls:
    """Handles all player input and converts to hex movements"""
    
    # Hex direction mappings
    HEX_DIRECTIONS = {
        0: HexDirection.DIRECTION_0,      # 0° = East
        60: HexDirection.DIRECTION_60,    # 60° = Northeast
        120: HexDirection.DIRECTION_120,  # 120° = Northwest
        180: HexDirection.DIRECTION_180,  # 180° = West
        240: HexDirection.DIRECTION_240,  # 240° = Southwest
        300: HexDirection.DIRECTION_300,  # 300° = Southeast
    }
    
    def __init__(self):
        """Initialize control handlers"""
        self.movement_callback: Optional[Callable[[int, int], None]] = None
        self.click_callback: Optional[Callable[[Tuple[int, int]], None]] = None
    
    def set_movement_callback(self, callback: Callable[[int, int], None]):
        """Set callback for movement: callback(dq, dr)"""
        self.movement_callback = callback
    
    def set_click_callback(self, callback: Callable[[Tuple[int, int]], None]):
        """Set callback for mouse click: callback((q, r))"""
        self.click_callback = callback
    
    def handle_keyboard(self, key: str):
        """
        Handle keyboard input.
        
        Supports:
        - Arrow keys: up/down/left/right
        - Numpad: 0-9 for hex directions
        """
        # Arrow keys (no N/S moves)
        key_map = {
            'Left': (-1, 0),      # West
            'Right': (1, 0),      # East
        }
        
        # Numpad keys with directions (no N/S moves)
        numpad_map = {
            'KP_7': HexDirection.DIRECTION_120,  # NW (num7)
            'KP_9': HexDirection.DIRECTION_60,   # NE (num9)
            'KP_4': HexDirection.DIRECTION_180,  # W (num4)
            'KP_6': HexDirection.DIRECTION_0,    # E (num6)
            'KP_1': HexDirection.DIRECTION_300,  # SE (num1)
            'KP_3': HexDirection.DIRECTION_240,  # SW (num3)
            # Num 8 / 2 intentionally unmapped
        }
        
        # Check arrow keys first
        if key in key_map:
            dq, dr = key_map[key]
            if self.movement_callback:
                self.movement_callback(dq, dr)
            return
        
        # Check numpad keys
        if key in numpad_map:
            direction = numpad_map[key]
            dq, dr = direction.get_delta()
            if self.movement_callback:
                self.movement_callback(dq, dr)
            return
    
    def handle_numpad_direction(self, numpad_key: int):
        """
        Handle numpad input by key number (1-9, 0).
        Maps to hex directions.
        """
        numpad_dir_map = {
            7: HexDirection.DIRECTION_120,  # NW
            9: HexDirection.DIRECTION_60,   # NE
            4: HexDirection.DIRECTION_180,  # W
            6: HexDirection.DIRECTION_0,    # E
            1: HexDirection.DIRECTION_300,  # SE
            3: HexDirection.DIRECTION_240,  # SW
        }
        
        if numpad_key in numpad_dir_map:
            direction = numpad_dir_map[numpad_key]
            dq, dr = direction.get_delta()
            if self.movement_callback:
                self.movement_callback(dq, dr)
    
    def handle_joystick_input(self, x: float, y: float) -> Optional[HexDirection]:
        """
        Convert joystick analog input to hex direction.
        
        Args:
            x, y: Joystick axes (-1.0 to 1.0)
        
        Returns:
            HexDirection or None if input is too close to center
        """
        # Deadzone check
        magnitude = math.sqrt(x*x + y*y)
        if magnitude < 0.3:
            return None
        
        # Calculate angle (in degrees)
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
        
        # Round to nearest hex direction (0, 60, 120, 180, 240, 300)
        nearest_angle = round(angle / 60) * 60
        if nearest_angle >= 360:
            nearest_angle = 0
        
        direction = self.HEX_DIRECTIONS.get(nearest_angle)
        
        if direction and self.movement_callback:
            dq, dr = direction.get_delta()
            self.movement_callback(dq, dr)
        
        return direction
    
    def handle_mouse_click(self, screen_pos: Tuple[int, int], 
                          canvas_center: Tuple[int, int], 
                          camera_offset: Tuple[int, int],
                          hex_size: int) -> Optional[Tuple[int, int]]:
        """
        Convert mouse click screen position to hex coordinate.
        
        Args:
            screen_pos: Mouse click (x, y) in screen space
            canvas_center: Canvas center (cx, cy) in screen space
            camera_offset: Current camera offset
            hex_size: Size of each hex in pixels
        
        Returns:
            Axial hex coordinates (q, r) or None if outside map
        """
        click_x, click_y = screen_pos
        canvas_cx, canvas_cy = canvas_center
        offset_x, offset_y = camera_offset
        
        # Convert to world space
        world_x = click_x - canvas_cx - offset_x
        world_y = click_y - canvas_cy - offset_y
        
        # Convert to axial coordinates
        q = (math.sqrt(3)/3 * world_x - 1/3 * world_y) / hex_size
        r = (2./3 * world_y) / hex_size
        
        # Round to nearest hex
        hex_coords = self._round_axial(q, r)
        
        if self.click_callback:
            self.click_callback(hex_coords)
        
        return hex_coords
    
    @staticmethod
    def _round_axial(q: float, r: float) -> Tuple[int, int]:
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
