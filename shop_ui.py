"""
Shop UI for selecting and buying gear after character generation
"""

import tkinter as tk
from tkinter import messagebox
from coin_utils import cost_to_cp, cp_to_gp_sp_cp, format_coins, subtract_cost, add_coins


# Class-specific availability (grayed out weapons that are NOT available)
CLASS_WEAPON_RESTRICTIONS = {
    'Priest': {
        'allowed': ['Club', 'Crossbow', 'Dagger', 'Mace', 'Staff', 'Warhammer'],
        'all_armor_allowed': True
    },
    'Thief': {
        'allowed': ['Club', 'Crossbow', 'Dagger', 'Shortbow', 'Shortsword'],
        'armor_allowed': ['Leather Armor', 'Brigadine', 'Scalemail']
    },
    'Wizard': {
        'allowed': ['Dagger', 'Staff'],
        'armor_allowed': []
    },
    'Fighter': {
        'allowed': None,  # All weapons allowed
        'all_armor_allowed': True
    }
}


class ShopUI:
    """Shop UI for gear selection and purchasing"""
    
    def __init__(self, root, character_data, builder, character_sheet=None):
        self.root = root
        self.character_data = character_data
        self.builder = builder
        self.character_sheet = character_sheet
        self.phase = 'weapon_selection'  # 'weapon_selection' or 'buy_gear'
        self.selected_weapon = None
        
        # Weapon/armor/equipment tables
        self.weapons = self.builder.WEAPONS
        self.armors = self.builder.ARMORS
        self.equipment = self.builder.EQUIPMENT
        
        # Store references to canvas/scrollable frames for later updates (to preserve scroll position)
        self.canvas_w = None
        self.scrollable_w = None
        self.canvas_a = None
        self.scrollable_a = None
        self.canvas_e = None
        self.scrollable_e = None
        self.coin_label = None
        
        # Character info
        self.char_class = character_data['ch_class']
        self.title = character_data['ch_title']
        self.gp = character_data['gp_coin']
        self.sp = character_data['sp_coin']
        self.cp = character_data['cp_coin']
        
        # Check if this is a fighter who needs to select weapon masteries
        self.weapon_mastery_count = character_data.get('weapon_mastery_count', 0)
        self.selected_masteries = []
        self.is_mastery_selection = self.weapon_mastery_count > 0
        
        # Create the window once
        self.main_window = tk.Toplevel(self.root)
        self.main_window.title("Shop - Pick Your Gear")
        self.main_window.configure(bg='#D2B48C')  # Light brown
        self.main_window.geometry('500x700')
        
        # Position shop window to the right of the main window
        self.root.update_idletasks()  # Ensure root window is updated
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        shop_x = root_x + root_width + 20  # Position to the right with 20px gap
        shop_y = root_y
        self.main_window.geometry(f'500x700+{shop_x}+{shop_y}')
        
        # Create main frame that will be reused and updated
        self.main_frame = tk.Frame(self.main_window, bg='#D2B48C')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show initial phase
        self.update_ui()
    
    def update_ui(self):
        """Update the shop UI content based on current phase"""
        # Clear existing widgets in main_frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        if self.phase == 'weapon_selection':
            self.show_weapon_selection()
        else:
            self.show_buy_gear()
    
    def show_weapon_selection(self):
        """Phase 1: Pick a weapon or select weapon masteries for fighter"""
        # Title message - different for mastery selection
        if self.is_mastery_selection:
            mastery_num = len(self.selected_masteries) + 1
            title_text = f"Choose Weapon Mastery {mastery_num} of {self.weapon_mastery_count}, {self.title.lower()}."
        else:
            title_text = f"Pick a weapon, {self.title.lower()}."
        
        title_label = tk.Label(
            self.main_frame,
            text=title_text,
            font=('Times New Roman', 14, 'bold'),
            bg='#D2B48C'
        )
        title_label.pack(pady=10)
        
        # Weapons frame
        weapons_frame = tk.LabelFrame(
            self.main_frame,
            text="Weapons",
            font=('Times New Roman', 12, 'bold'),
            bg='#D2B48C',
            fg='black'
        )
        weapons_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollable canvas for weapons
        canvas = tk.Canvas(weapons_frame, bg='#D2B48C', highlightthickness=0)
        scrollbar = tk.Scrollbar(weapons_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#D2B48C')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for weapon_name, weapon_data in self.weapons.items():
            is_allowed = self.is_weapon_allowed(weapon_name)
            # If doing weapon mastery selection, gray out already selected masteries
            if self.is_mastery_selection and weapon_name in self.selected_masteries:
                is_allowed = False  # Gray out
            self.create_weapon_row(scrollable_frame, weapon_name, weapon_data, is_allowed, phase='selection')
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_buy_gear(self):
        """Phase 2: Buy gear"""
        # Coin display
        coin_frame = tk.Frame(self.main_frame, bg='#D2B48C')
        coin_frame.pack(fill=tk.X, padx=5, pady=5)
        
        coin_text = format_coins(self.gp, self.sp, self.cp)
        self.coin_label = tk.Label(
            coin_frame,
            text=f"Coins: {coin_text}",
            font=('Times New Roman', 12),
            bg='#D2B48C'
        )
        self.coin_label.pack(anchor='w')
        
        # Title message
        title_label = tk.Label(
            self.main_frame,
            text=f"Do you want to buy anything?",
            font=('Times New Roman', 14, 'bold'),
            bg='#D2B48C'
        )
        title_label.pack(pady=10)
        
        # Create notebook-style tabs for weapons, armor, equipment
        tabs_frame = tk.Frame(self.main_frame, bg='#D2B48C')
        tabs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Weapons tab
        weapons_frame = tk.LabelFrame(tabs_frame, text="Weapons", font=('Times New Roman', 12, 'bold'), bg='#D2B48C')
        weapons_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas_w = tk.Canvas(weapons_frame, bg='#D2B48C', highlightthickness=0, height=150)
        scrollbar_w = tk.Scrollbar(weapons_frame, orient=tk.VERTICAL, command=self.canvas_w.yview)
        self.scrollable_w = tk.Frame(self.canvas_w, bg='#D2B48C')
        
        self.scrollable_w.bind("<Configure>", lambda e: self.canvas_w.configure(scrollregion=self.canvas_w.bbox("all")))
        self.canvas_w.create_window((0, 0), window=self.scrollable_w, anchor="nw")
        self.canvas_w.configure(yscrollcommand=scrollbar_w.set)
        
        for weapon_name, weapon_data in self.weapons.items():
            is_allowed = self.is_weapon_allowed(weapon_name)
            self.create_weapon_row(self.scrollable_w, weapon_name, weapon_data, is_allowed, phase='buy')
        
        self.canvas_w.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_w.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Armor tab
        armor_frame = tk.LabelFrame(tabs_frame, text="Armor & Shields", font=('Times New Roman', 12, 'bold'), bg='#D2B48C')
        armor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas_a = tk.Canvas(armor_frame, bg='#D2B48C', highlightthickness=0, height=150)
        scrollbar_a = tk.Scrollbar(armor_frame, orient=tk.VERTICAL, command=self.canvas_a.yview)
        self.scrollable_a = tk.Frame(self.canvas_a, bg='#D2B48C')
        
        self.scrollable_a.bind("<Configure>", lambda e: self.canvas_a.configure(scrollregion=self.canvas_a.bbox("all")))
        self.canvas_a.create_window((0, 0), window=self.scrollable_a, anchor="nw")
        self.canvas_a.configure(yscrollcommand=scrollbar_a.set)
        
        for armor_name, armor_data in self.armors.items():
            is_allowed = self.is_armor_allowed(armor_name)
            self.create_armor_row(self.scrollable_a, armor_name, armor_data, is_allowed)
        
        self.canvas_a.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_a.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Equipment tab
        equipment_frame = tk.LabelFrame(tabs_frame, text="Equipment & Items", font=('Times New Roman', 12, 'bold'), bg='#D2B48C')
        equipment_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas_e = tk.Canvas(equipment_frame, bg='#D2B48C', highlightthickness=0, height=150)
        scrollbar_e = tk.Scrollbar(equipment_frame, orient=tk.VERTICAL, command=self.canvas_e.yview)
        self.scrollable_e = tk.Frame(self.canvas_e, bg='#D2B48C')
        
        self.scrollable_e.bind("<Configure>", lambda e: self.canvas_e.configure(scrollregion=self.canvas_e.bbox("all")))
        self.canvas_e.create_window((0, 0), window=self.scrollable_e, anchor="nw")
        self.canvas_e.configure(yscrollcommand=scrollbar_e.set)
        
        for item_name, item_data in self.equipment.items():
            self.create_equipment_row(self.scrollable_e, item_name, item_data)
        
        self.canvas_e.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_e.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Done button
        done_button = tk.Button(
            self.main_frame,
            text="Done Shopping",
            font=('Times New Roman', 11, 'bold'),
            bg='#8B7355',
            fg='white',
            activebackground='#6B5B3D',
            command=self.finish_shopping
        )
        done_button.pack(pady=10)
    
    def create_weapon_row(self, parent, weapon_name, weapon_data, is_allowed, phase):
        """Create a row for a weapon"""
        row = tk.Frame(parent, bg='#D2B48C')
        row.pack(fill=tk.X, padx=5, pady=2)
        
        # Determine if grayed out
        fg_color = 'black' if is_allowed else '#999999'
        
        # Get button
        if phase == 'selection':
            btn_text = "Get" if is_allowed else "X"
            btn_cmd = lambda: self.select_weapon(weapon_name) if is_allowed else None
            btn = tk.Button(
                row,
                text=btn_text,
                width=5,
                font=('Times New Roman', 9),
                bg='#8B7355' if is_allowed else '#CCCCCC',
                fg='white' if is_allowed else '#999999',
                state=tk.NORMAL if is_allowed else tk.DISABLED,
                command=btn_cmd
            )
        else:  # phase == 'buy'
            cost_cp = cost_to_cp(weapon_data['cost'])
            total_cp = self.gp * 100 + self.sp * 10 + self.cp
            can_afford = total_cp >= cost_cp and is_allowed
            btn_text = "Buy"
            btn_cmd = lambda: self.buy_item('weapon', weapon_name, weapon_data['cost']) if can_afford else None
            btn = tk.Button(
                row,
                text=btn_text,
                width=5,
                font=('Times New Roman', 9),
                bg='#8B7355' if can_afford else '#CCCCCC',
                fg='white' if can_afford else '#999999',
                state=tk.NORMAL if can_afford else tk.DISABLED,
                command=btn_cmd
            )
        
        btn.pack(side=tk.LEFT, padx=2)
        
        # Weapon info
        cost_text = weapon_data['cost'] if phase == 'buy' else ''
        info_text = f"{weapon_name}: {weapon_data['damage']} dmg, {weapon_data['range']} range, {weapon_data['slots']} slot(s), {weapon_data['type']} type, {', '.join(weapon_data['properties']) if weapon_data['properties'] else 'no properties'}"
        if cost_text:
            info_text += f"  [{cost_text}]"
        
        info = tk.Label(
            row,
            text=info_text,
            font=('Times New Roman', 9),
            bg='#D2B48C',
            fg=fg_color,
            justify=tk.LEFT
        )
        info.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_armor_row(self, parent, armor_name, armor_data, is_allowed):
        """Create a row for armor"""
        row = tk.Frame(parent, bg='#D2B48C')
        row.pack(fill=tk.X, padx=5, pady=2)
        
        fg_color = 'black' if is_allowed else '#999999'
        
        # Buy button
        cost_cp = cost_to_cp(armor_data['cost'])
        total_cp = self.gp * 100 + self.sp * 10 + self.cp
        can_afford = total_cp >= cost_cp and is_allowed
        
        btn = tk.Button(
            row,
            text="Buy",
            width=5,
            font=('Times New Roman', 9),
            bg='#8B7355' if can_afford else '#CCCCCC',
            fg='white' if can_afford else '#999999',
            state=tk.NORMAL if can_afford else tk.DISABLED,
            command=lambda: self.buy_item('armor', armor_name, armor_data['cost']) if can_afford else None
        )
        btn.pack(side=tk.LEFT, padx=2)
        
        # Armor info
        ac_info = f"AC: {armor_data['base']}" if armor_data['ac_type'] == 'flat' else f"AC: {armor_data['base']} + DEX"
        props_text = ', '.join(armor_data['properties']) if armor_data['properties'] else 'no penalties'
        info_text = f"{armor_name}: {ac_info}, {armor_data['slots']} slot(s), {props_text}  [{armor_data['cost']}]"
        
        info = tk.Label(
            row,
            text=info_text,
            font=('Times New Roman', 9),
            bg='#D2B48C',
            fg=fg_color,
            justify=tk.LEFT
        )
        info.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_equipment_row(self, parent, item_name, item_data):
        """Create a row for equipment/items"""
        row = tk.Frame(parent, bg='#D2B48C')
        row.pack(fill=tk.X, padx=5, pady=2)
        
        # Buy button
        cost_cp = cost_to_cp(item_data['cost'])
        total_cp = self.gp * 100 + self.sp * 10 + self.cp
        can_afford = total_cp >= cost_cp
        
        btn = tk.Button(
            row,
            text="Buy",
            width=5,
            font=('Times New Roman', 9),
            bg='#8B7355' if can_afford else '#CCCCCC',
            fg='white' if can_afford else '#999999',
            state=tk.NORMAL if can_afford else tk.DISABLED,
            command=lambda: self.buy_item('equipment', item_name, item_data['cost']) if can_afford else None
        )
        btn.pack(side=tk.LEFT, padx=2)
        
        # Item info
        info_text = f"{item_name}: {item_data['cost']}"
        
        info = tk.Label(
            row,
            text=info_text,
            font=('Times New Roman', 9),
            bg='#D2B48C',
            justify=tk.LEFT
        )
        info.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def is_weapon_allowed(self, weapon_name):
        """Check if weapon is allowed for this character class"""
        restrictions = CLASS_WEAPON_RESTRICTIONS.get(self.char_class, {})
        allowed = restrictions.get('allowed')
        if allowed is None:  # Fighter: all allowed
            return True
        return weapon_name in allowed
    
    def is_armor_allowed(self, armor_name):
        """Check if armor is allowed for this character class"""
        restrictions = CLASS_WEAPON_RESTRICTIONS.get(self.char_class, {})
        if restrictions.get('all_armor_allowed'):
            return True
        allowed_armor = restrictions.get('armor_allowed', [])
        return armor_name in allowed_armor
    
    def select_weapon(self, weapon_name):
        """Player selected a weapon in phase 1 or for weapon mastery"""
        self.selected_weapon = weapon_name
        
        # If this is weapon mastery selection, add to mastery list
        if self.is_mastery_selection:
            self.selected_masteries.append(weapon_name)
            
            # Check if we need more masteries
            if len(self.selected_masteries) < self.weapon_mastery_count:
                # More masteries to select - refresh the display
                self.update_ui()
            else:
                # All masteries selected - store them and move to weapon selection
                for idx, mastery_weapon in enumerate(self.selected_masteries, 1):
                    self.character_data[f'weapon_mastery_{idx}'] = mastery_weapon
                
                self.character_data['weapon_masteries'] = self.selected_masteries
                
                # Update talent display with masteries
                self.builder._update_talent_display_with_masteries()
                
                self.is_mastery_selection = False
                
                # Now show normal weapon selection (starting weapon choice)
                self.update_ui()
            return
        
        # Regular weapon selection
        # Add weapon to character and gear (NOT auto-equipped - user must click to equip)
        self.character_data['ch_weapon'] = weapon_name  # Keep for backwards compatibility
        # Don't set equipped_weapon or equipped_weapon_instance - user must click to equip
        
        weapon_slots = self.weapons[weapon_name]['slots']
        suffix = 'slot' if weapon_slots == 1 else 'slots'
        gear = self.character_data.setdefault('ch_gear_items', [])
        gear.append(f"{weapon_name} ({weapon_slots} {suffix})")
        
        # Rebuild attacks
        self.builder._regenerate_attacks()
        self.character_data['ch_attacks'] = self.builder.character_data['ch_attacks']
        
        # Update character sheet if available
        if self.character_sheet:
            self.character_sheet.update_character_data(self.character_data)
        
        # Move to phase 2
        self.phase = 'buy_gear'
        self.update_ui()
    
    def buy_item(self, item_type, item_name, cost_str):
        """Player clicked buy on an item"""
        result = subtract_cost(self.gp, self.sp, self.cp, cost_str)
        if result is None:
            messagebox.showerror("Insufficient Funds", f"You cannot afford {item_name}.")
            return
        
        # Check slot availability
        new_gp, new_sp, new_cp = result
        gear = self.character_data.get('ch_gear_items', [])
        
        # Calculate used slots
        str_score = self.character_data.get('STR_score', 10)
        char_class = self.character_data['ch_class']
        con_mod = self.character_data.get('CON_mod', 0)
        max_slots = str_score + (con_mod if char_class == 'Fighter' and con_mod > 0 else 0)
        
        # For stackable items, check if we can fit in existing slot
        if item_type == 'equipment' and item_name in self.equipment:
            item_data = self.equipment[item_name]
            if 'slots_per' in item_data:
                # This is a stackable item
                can_add = self._can_add_stackable_item(gear, item_name, item_data, str_score, char_class, con_mod)
                if not can_add:
                    messagebox.showerror("Too Heavy", f"No slot available for {item_name}.")
                    return
                
                # Add stackable item with special formatting
                self._add_stackable_item_formatted(gear, item_name, item_data)
                
                # Update coins
                self.character_data['gp_coin'] = new_gp
                self.character_data['sp_coin'] = new_sp
                self.character_data['cp_coin'] = new_cp
                self.gp, self.sp, self.cp = new_gp, new_sp, new_cp
                
                # Update character sheet if available
                if self.character_sheet:
                    self.character_sheet.update_character_data(self.character_data)
                
                # Only refresh the affected widgets
                self._refresh_coins_and_buttons()
                return
        
        # Non-stackable items (weapons, armor, regular equipment)
        used_slots = self.calculate_used_slots(gear, item_type, item_name)
        if used_slots >= max_slots:
            messagebox.showerror("Too Heavy", "No slot available for this item.")
            return
        
        # Add item to gear
        if item_type == 'weapon':
            # Can only have one equipped weapon, but can own multiple
            slots = self.weapons[item_name]['slots']
        elif item_type == 'armor':
            slots = self.armors[item_name]['slots']
        else:  # equipment
            slots = self.calculate_item_slots(item_name)
        
        suffix = 'slot' if slots == 1 else 'slots'
        gear.append(f"{item_name} ({slots} {suffix})")
        
        # Update coins
        self.character_data['gp_coin'] = new_gp
        self.character_data['sp_coin'] = new_sp
        self.character_data['cp_coin'] = new_cp
        self.gp, self.sp, self.cp = new_gp, new_sp, new_cp
        
        # Update character sheet if available
        if self.character_sheet:
            self.character_sheet.update_character_data(self.character_data)
        
        # Only refresh the affected widgets
        self._refresh_coins_and_buttons()
    
    def calculate_used_slots(self, gear, item_type, item_name):
        """Calculate number of slots used by current gear"""
        used = 0
        for item_str in gear:
            # Parse "ItemName (X slots)" or "ItemName (X slot)" or stackable format "ItemName x N"
            if '(' in item_str and ')' in item_str:
                slots_part = item_str.split('(')[1].split(')')[0]
                try:
                    slots = int(slots_part.split()[0])
                    used += slots
                except:
                    used += 1
            elif ' x ' in item_str:
                # Stackable item already counted as 1 slot per line
                used += 1
            else:
                used += 1
        return used
    
    def _can_add_stackable_item(self, gear, item_name, item_data, str_score, char_class, con_mod):
        """Check if a stackable item can be added (either to existing stack or new slot)"""
        slots_per = item_data.get('slots_per', 1)
        
        # Find existing stack
        existing_count = 0
        for item_str in gear:
            if item_str.startswith(item_name):
                if ' x ' in item_str:
                    try:
                        count_str = item_str.split(' x ')[1].strip()
                        count_str = count_str.replace(' are heavy!', '')
                        existing_count = int(count_str)
                    except:
                        existing_count = 1
                else:
                    existing_count = 1
                break
        
        # If there's an existing stack and it's not full, we can add to it
        if existing_count > 0 and existing_count < slots_per:
            return True
        
        # If existing stack is full or no stack exists, check if we have a free slot
        max_slots = str_score + (con_mod if char_class == 'Fighter' and con_mod > 0 else 0)
        used_slots = self.calculate_used_slots(gear, 'equipment', item_name)
        
        # If existing stack is at max, we need a new slot
        if existing_count >= slots_per:
            return used_slots < max_slots
        
        # No existing stack, need one slot
        return used_slots < max_slots
    
    def calculate_item_slots(self, item_name):
        """Calculate slots for an equipment item"""
        if item_name not in self.equipment:
            return 1
        
        item_data = self.equipment[item_name]
        
        # Fixed slots
        if 'slots' in item_data:
            return item_data['slots']
        
        # Dynamic calculation based on quantity
        # For simplicity, assume 1 slot per item for now
        return 1
    
    def _refresh_coins_and_buttons(self):
        """Update coins display and button states without resetting scroll position"""
        # Update coin display
        if self.coin_label:
            coin_text = format_coins(self.gp, self.sp, self.cp)
            self.coin_label.config(text=f"Coins: {coin_text}")
        
        # Recreate weapon buttons only
        if self.scrollable_w:
            for widget in self.scrollable_w.winfo_children():
                widget.destroy()
            for weapon_name, weapon_data in self.weapons.items():
                is_allowed = self.is_weapon_allowed(weapon_name)
                self.create_weapon_row(self.scrollable_w, weapon_name, weapon_data, is_allowed, phase='buy')
        
        # Recreate armor buttons only
        if self.scrollable_a:
            for widget in self.scrollable_a.winfo_children():
                widget.destroy()
            for armor_name, armor_data in self.armors.items():
                is_allowed = self.is_armor_allowed(armor_name)
                self.create_armor_row(self.scrollable_a, armor_name, armor_data, is_allowed)
        
        # Recreate equipment buttons only
        if self.scrollable_e:
            for widget in self.scrollable_e.winfo_children():
                widget.destroy()
            for item_name, item_data in self.equipment.items():
                self.create_equipment_row(self.scrollable_e, item_name, item_data)
    
    def _add_stackable_item_formatted(self, gear, item_name, item_data):
        """Add a stackable item to gear with proper formatting
        
        Stackable items display as:
        • ration x 1
        • rations x 7
        •   rations are heavy
        •   rations are heavy
        
        Where each "are heavy" line represents one full slot beyond the first.
        Uses singular form for count=1, plural form for count>1.
        """
        slots_per = item_data.get('slots_per', 1)
        plural_name = self._pluralize(item_name)
        
        # Find and update existing stack
        existing_index = -1
        existing_count = 0
        
        for i, item_str in enumerate(gear):
            # Check for both singular and plural forms in the main line
            if item_str.startswith(f"{item_name} x ") or item_str.startswith(f"{plural_name} x "):
                existing_index = i
                # Extract count from "rations x 7" or "ration x 1" format
                try:
                    x_pos = item_str.rfind(' x ')
                    if x_pos > 0:
                        count_str = item_str[x_pos + 3:].strip()
                        existing_count = int(count_str)
                except:
                    existing_count = 1
                break
        
        # Add one more item
        new_count = existing_count + 1
        total_slots = (new_count + slots_per - 1) // slots_per  # ceil division
        
        # Use singular or plural form based on count
        display_name = item_name if new_count == 1 else plural_name
        
        # Build the gear entry with main line + heavy lines
        gear_entries = [f"{display_name} x {new_count}"]
        
        # Add "are heavy" lines using plural form
        for _ in range(total_slots - 1):
            gear_entries.append(f"  {plural_name} are heavy")
        
        # Remove old entry if it exists and add new formatted entries
        if existing_index >= 0:
            # Remove old main entry and all its "heavy" lines
            j = existing_index + 1
            while j < len(gear) and "are heavy" in gear[j]:
                j += 1
            # Remove from existing_index to j-1
            del gear[existing_index:j]
            # Insert new entries at that position
            for idx, entry in enumerate(gear_entries):
                gear.insert(existing_index + idx, entry)
        else:
            # New stackable item, add all entries
            gear.extend(gear_entries)
    
    def _pluralize(self, word):
        """Convert word to plural form (simple rule: add 's')"""
        return f"{word}s"
    
    
    def finish_shopping(self):
        """Close shop and return to main app"""
        self.main_window.destroy()


