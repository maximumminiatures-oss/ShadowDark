"""
Character Sheet GUI for ShadowDark RPG
Displays character information in a medieval-styled interface
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
import math
from inventory_utils import coin_count, coin_slots
from data_tables import DEITY_DESCRIPTIONS, ANCESTRY_NAMES, ALIGNMENT_DESCRIPTIONS


class CharacterSheet(tk.Frame):
    """GUI component for displaying character data"""
    
    def __init__(self, parent, on_equipment_changed=None, on_info_changed=None):
        super().__init__(parent)
        self.configure(bg='#F5F5DC')  # Bone color
        
        # Dark purple color for text and graphics
        self.text_color = '#2D1B3D'
        self.grayed_color = '#A9A9A9'  # Gray for unequipped items
        
        # Store callbacks
        self.on_equipment_changed = on_equipment_changed
        self.on_info_changed = on_info_changed
        
        # Try to load medieval font, fallback to Times New Roman (sizes increased by 20%)
        self.title_font = self._get_medieval_font(29, bold=True)  # 24 * 1.2
        self.body_font = self._get_medieval_font(13)  # 11 * 1.2
        self.small_font = self._get_medieval_font(11)  # 9 * 1.2
        # Numeric font (Arial)
        self.numeric_font = tkfont.Font(family='Arial', size=11)
        self.numeric_small_font = tkfont.Font(family='Arial', size=9)
        # Field value font (Arial)
        self.field_value_font = tkfont.Font(family='Arial', size=11)
        self.field_value_small_font = tkfont.Font(family='Arial', size=9)
        
        # Store widget references
        self.widgets = {}
        
        # Callback for equipment changes
        self.on_equipment_changed = on_equipment_changed
        
        # Store current character data for equipment interactions
        self.character_data = {}
        
        # Gear text widget for clickable items
        self.gear_text = None
        
        # Item name to line mapping for gear display
        self.gear_item_lines = {}
        
        self._create_layout()

    def _attach_tooltip(self, widget, text):
        """Attach a simple tooltip to a widget with provided text"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, bg='#FFFFCC',
                            fg='black', font=self.small_font,
                            relief=tk.SOLID, bd=1, padx=5, pady=3)
            label.pack()
            widget.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def _attach_attacks_tooltips(self, text_widget, attack_breakdowns):
        """Attach tooltips to attack text widget that show breakdown based on line under mouse"""
        def show_attack_tooltip(event):
            # Get the line number under the mouse
            try:
                index = text_widget.index(f"@{event.x},{event.y}")
                line_num = int(index.split('.')[0]) - 1  # Convert to 0-based
                
                if line_num in attack_breakdowns:
                    tooltip = tk.Toplevel()
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                    label = tk.Label(tooltip, text=attack_breakdowns[line_num], 
                                    bg='#FFFFCC', fg='black', font=('Arial', 9),
                                    relief=tk.SOLID, bd=1, padx=5, pady=3, justify=tk.LEFT)
                    label.pack()
                    text_widget.attack_tooltip = tooltip
            except:
                pass
        
        def hide_attack_tooltip(event):
            if hasattr(text_widget, 'attack_tooltip'):
                text_widget.attack_tooltip.destroy()
                del text_widget.attack_tooltip
        
        def update_attack_tooltip(event):
            # Hide old tooltip and show new one for current line
            hide_attack_tooltip(event)
            show_attack_tooltip(event)
        
        text_widget.bind('<Motion>', update_attack_tooltip)
        text_widget.bind('<Leave>', hide_attack_tooltip)
    
    def _attach_deity_tooltip(self, widget):
        """Attach a dynamic tooltip to deity dropdown that shows current deity's description"""
        def show_deity_tooltip(event):
            current_deity = widget.get()
            if current_deity and current_deity in DEITY_DESCRIPTIONS:
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = tk.Label(tooltip, text=DEITY_DESCRIPTIONS[current_deity], 
                                bg='#FFFFCC', fg='black', font=self.small_font,
                                relief=tk.SOLID, bd=1, justify=tk.LEFT, padx=5, pady=3)
                label.pack()
                widget.tooltip = tooltip

        def hide_deity_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', show_deity_tooltip)
        widget.bind('<Leave>', hide_deity_tooltip)
    
    def _attach_alignment_tooltip(self, widget):
        """Attach a dynamic tooltip to alignment dropdown that shows alignment description with ancestry and background"""
        def show_alignment_tooltip(event):
            current_alignment = widget.get()
            if current_alignment and current_alignment in ALIGNMENT_DESCRIPTIONS:
                # Get ancestry and background from character data
                ancestry = self.character_data.get('ch_ancestry', 'Human')
                background_full = self.character_data.get('ch_background', '')
                
                # Extract first word from background (e.g., "Wanted" from "Wanted. There's a price...")
                background_word = background_full.split('.')[0] if background_full else 'Adventurer'
                
                # Convert ancestry to proper form
                ancestry_name = ANCESTRY_NAMES.get(ancestry, ancestry)
                
                # Format the description with ancestry and background
                template = ALIGNMENT_DESCRIPTIONS[current_alignment]
                tooltip_text = template.format(ancestry=ancestry_name, background=background_word)
                
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = tk.Label(tooltip, text=tooltip_text, 
                                bg='#FFFFCC', fg='black', font=self.small_font,
                                relief=tk.SOLID, bd=1, justify=tk.LEFT, padx=5, pady=3)
                label.pack()
                widget.tooltip = tooltip

        def hide_alignment_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind('<Enter>', show_alignment_tooltip)
        widget.bind('<Leave>', hide_alignment_tooltip)
    
    def _get_medieval_font(self, size, bold=False):
        """Try to load medieval font, fallback to system font"""
        try:
            # Try common medieval fonts
            font_names = ['medievalSD', 'MedievalSharp', 'Uncial', 'Old English Text MT', 'Times New Roman']
            for name in font_names:
                try:
                    weight = 'bold' if bold else 'normal'
                    return tkfont.Font(family=name, size=size, weight=weight)
                except:
                    continue
        except:
            pass
        # Fallback
        weight = 'bold' if bold else 'normal'
        return tkfont.Font(family='Times New Roman', size=size, weight=weight)
    
    def _create_layout(self):
        """Create the three-column layout"""
        # Main container with padding
        main_frame = tk.Frame(self, bg='#F5F5DC')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create three columns
        left_col = tk.Frame(main_frame, bg='#F5F5DC')
        center_col = tk.Frame(main_frame, bg='#F5F5DC')
        right_col = tk.Frame(main_frame, bg='#F5F5DC')
        
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        center_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        self._create_left_column(left_col)
        self._create_center_column(center_col)
        self._create_right_column(right_col)
    
    def _create_left_column(self, parent):
        """Create left column with character info, HP, AC, and attacks"""
        # Info box
        info_frame = tk.Frame(parent, bg='#F5F5DC', relief=tk.RAISED, bd=2)
        info_frame.pack(fill=tk.X, pady=5)
        
        fields = [
            ('ch_name', 'Name:'),
            ('ch_ancestry', 'Ancestry:'),
            ('ch_class', 'Class:'),
            ('ch_title', 'Title:'),
            ('ch_align', 'Alignment:'),
            ('ch_background', 'Background:'),
            ('ch_deity', 'Deity:')
        ]
        
        # Define dropdown options
        self.dropdown_options = {
            'ch_ancestry': ["Human", "Elf", "Dwarf", "Halfling", "Half Orc", "Goblin"],
            'ch_class': ["Fighter", "Thief", "Priest", "Wizard"],
            'ch_align': ["Lawful", "Neutral", "Chaotic"],
            'ch_deity': ["Saint Terragnis", "Madeera the Covenant", "Gede", "Ord", "Memnon", "Shune the Vile", "Ramlaat"]
        }
        
        for key, label in fields:
            row = tk.Frame(info_frame, bg='#F5F5DC')
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=self.body_font, bg='#F5F5DC', 
                    fg=self.text_color, anchor='w', width=12).pack(side=tk.LEFT)
            
            if key in self.dropdown_options:
                # Use Combobox for these fields
                widget = ttk.Combobox(row, values=self.dropdown_options[key], 
                                     font=self.body_font, state='readonly', width=18)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                widget.bind("<<ComboboxSelected>>", lambda e, k=key: self._on_dropdown_selected(k))
                widget.config(cursor='arrow')
                
                # Add tooltip for deity dropdown
                if key == 'ch_deity':
                    self._attach_deity_tooltip(widget)
                
                # Add tooltip for alignment dropdown
                if key == 'ch_align':
                    self._attach_alignment_tooltip(widget)
            else:
                # Use Entry for others
                widget = tk.Entry(row, font=self.body_font, fg=self.text_color, 
                               bg='white', width=20, relief=tk.SUNKEN, bd=1)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
                # Only the name should remain editable; everything else is read-only
                if key != 'ch_name':
                    widget.config(state='readonly', cursor='arrow')
                else:
                    widget.config(cursor='xterm')  # Text cursor for name field
            
            self.widgets[key] = widget
    
        # LEVEL and XP boxes
        level_xp_frame = tk.Frame(parent, bg='#F5F5DC')
        level_xp_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(level_xp_frame, text='LEVEL', font=self.field_value_small_font, 
                bg='#F5F5DC', fg=self.text_color).pack(side=tk.LEFT, padx=5)
        level_entry = tk.Entry(level_xp_frame, font=self.field_value_font, 
                              fg=self.text_color, bg='white', width=8, 
                              relief=tk.SUNKEN, bd=1)
        level_entry.pack(side=tk.LEFT, padx=5)
        level_entry.config(state='readonly')
        self.widgets['LEVEL'] = level_entry
        
        tk.Label(level_xp_frame, text='XP', font=self.field_value_small_font, 
                bg='#F5F5DC', fg=self.text_color).pack(side=tk.LEFT, padx=5)
        xp_entry = tk.Entry(level_xp_frame, font=self.field_value_font, 
                           fg=self.text_color, bg='white', width=8, 
                           relief=tk.SUNKEN, bd=1)
        xp_entry.pack(side=tk.LEFT, padx=5)
        xp_entry.config(state='readonly')
        self.widgets['XP'] = xp_entry
        
        # Heart and Shield graphics
        graphics_frame = tk.Frame(parent, bg='#F5F5DC')
        graphics_frame.pack(fill=tk.X, pady=10)
        
        # Heart canvas
        heart_frame = tk.Frame(graphics_frame, bg='#F5F5DC')
        heart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        heart_canvas = tk.Canvas(heart_frame, width=120, height=120, 
                                bg='#F5F5DC', highlightthickness=0)
        heart_canvas.pack()
        self._create_heart_shape(heart_canvas, 60, 60, 50)
        tk.Label(heart_frame, text='HP', font=self.field_value_small_font, 
                bg='#F5F5DC', fg=self.text_color).pack()
        hp_entry = tk.Entry(heart_frame, font=self.field_value_font, 
                           fg=self.text_color, bg='white', width=8, 
                           relief=tk.SUNKEN, bd=1, justify=tk.CENTER)
        hp_entry.pack(pady=2)
        hp_entry.config(state='readonly')
        self.widgets['ch_HP'] = hp_entry
        
        # Shield canvas
        shield_frame = tk.Frame(graphics_frame, bg='#F5F5DC')
        shield_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        shield_canvas = tk.Canvas(shield_frame, width=120, height=120, 
                                 bg='#F5F5DC', highlightthickness=0)
        shield_canvas.pack()
        self._create_shield_shape(shield_canvas, 60, 60, 50)
        tk.Label(shield_frame, text='AC', font=self.field_value_small_font, 
                bg='#F5F5DC', fg=self.text_color).pack()
        ac_entry = tk.Entry(shield_frame, font=self.field_value_font, 
                           fg=self.text_color, bg='white', width=8, 
                           relief=tk.SUNKEN, bd=1, justify=tk.CENTER)
        ac_entry.pack(pady=2)
        ac_entry.config(state='readonly')
        self.widgets['ch_AC'] = ac_entry
        
        # Armor worn display
        armor_label_frame = tk.Frame(parent, bg='#F5F5DC')
        armor_label_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(armor_label_frame, text='Armor worn:', font=self.field_value_small_font, 
                bg='#F5F5DC', fg=self.text_color, anchor='w').pack(side=tk.LEFT, padx=5)
        armor_entry = tk.Entry(armor_label_frame, font=self.field_value_font, 
                              fg=self.text_color, bg='white', 
                              relief=tk.SUNKEN, bd=1)
        armor_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        armor_entry.config(state='readonly')
        self.widgets['ch_armor'] = armor_entry
        
        # Attacks box
        attacks_frame = tk.Frame(parent, bg='#F5F5DC', relief=tk.RAISED, bd=2)
        attacks_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Header with column labels aligned to match data format
        # Create two-part header: "Attacks:" in MedievalSD, column headers in Arial
        header_frame = tk.Frame(attacks_frame, bg='#F5F5DC')
        header_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # "Attacks:" label in MedievalSD
        medieval_font = self._get_medieval_font(13)
        attacks_label = tk.Label(header_frame, text='Attacks:', 
                                font=medieval_font, bg='#F5F5DC', fg=self.text_color)
        attacks_label.pack(side=tk.LEFT)
        
        # Column headers in Arial
        arial_font = tkfont.Font(family='Arial', size=11)
        header_text = " +To Hit / Damage / Range"
        header_columns = tk.Label(header_frame, text=header_text, 
                                 font=arial_font, bg='#F5F5DC', fg=self.text_color,
                                 justify=tk.LEFT)
        header_columns.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Attacks text widget with monospace font for alignment
        mono_font = tkfont.Font(family='Courier New', size=11)
        attacks_text = tk.Text(attacks_frame, font=mono_font, 
                              fg=self.text_color, bg='white', 
                              width=25, height=8, wrap=tk.NONE,
                              relief=tk.SUNKEN, bd=1, cursor='arrow')
        attacks_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        attacks_text.config(state=tk.DISABLED)
        self.widgets['ch_attacks'] = attacks_text
    
    def _on_dropdown_selected(self, key):
        """Callback for dropdown selection change"""
        if self.on_info_changed:
            new_value = self.widgets[key].get()
            self.on_info_changed(key, new_value)
    
    def lock_dropdowns(self):
        """Lock all dropdown menus to prevent further changes"""
        dropdown_fields = ['ch_ancestry', 'ch_class', 'ch_align', 'ch_deity']
        for field in dropdown_fields:
            if field in self.widgets:
                widget = self.widgets[field]
                if isinstance(widget, ttk.Combobox):
                    widget.config(state='disabled')
    
    def unlock_dropdowns(self):
        """Unlock all dropdown menus to allow changes"""
        dropdown_fields = ['ch_ancestry', 'ch_class', 'ch_align', 'ch_deity']
        for field in dropdown_fields:
            if field in self.widgets:
                widget = self.widgets[field]
                if isinstance(widget, ttk.Combobox):
                    widget.config(state='readonly')
    
    def _create_center_column(self, parent):
        """Create center column with ShadowDark title and ability scores"""
        # ShadowDark title
        title_label = tk.Label(parent, text='ShadowDark', 
                              font=self.title_font, bg='#F5F5DC', 
                              fg=self.text_color)
        title_label.pack(pady=10)
        
        # Ability scores
        abilities = [
            ('STR', 'Strength'),
            ('DEX', 'Dexterity'),
            ('CON', 'Constitution'),
            ('INT', 'Intelligence'),
            ('WIS', 'Wisdom'),
            ('CHA', 'Charisma')
        ]
        
        for abbr, full_name in abilities:
            score_frame = tk.Frame(parent, bg='#F5F5DC', relief=tk.RAISED, bd=2)
            score_frame.pack(fill=tk.X, pady=3)
            
            # Label with tooltip
            label = tk.Label(score_frame, text=abbr, font=self.small_font, 
                           bg='#F5F5DC', fg=self.text_color)
            label.pack(pady=2)
            # Tooltip on hover for ability full name
            self._attach_tooltip(label, full_name)
            
            # Score/Mod display
            score_entry = tk.Entry(score_frame, font=self.field_value_font, 
                                  fg=self.text_color, bg='white', 
                                  width=15, relief=tk.SUNKEN, bd=1,
                                  justify=tk.CENTER)
            score_entry.pack(pady=2, padx=5)
            score_entry.config(state='readonly')
            self.widgets[f'{abbr}_score'] = score_entry
            self.widgets[f'{abbr}_mod'] = None  # Will be combined in display
        
        # Languages known field under Charisma
        lang_frame = tk.Frame(parent, bg='#F5F5DC', relief=tk.RAISED, bd=2)
        lang_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        
        tk.Label(lang_frame, text='Languages', font=self.body_font, 
               bg='#F5F5DC', fg=self.text_color).pack(pady=2)
        
        lang_text = tk.Text(lang_frame, font=self.body_font, 
                           fg=self.text_color, bg='white', 
                           width=30, height=7, wrap=tk.WORD,
                           relief=tk.SUNKEN, bd=1, cursor='arrow')
        lang_text.pack(pady=2, padx=5, fill=tk.BOTH, expand=True)
        lang_text.config(state=tk.DISABLED)
        self.widgets['ch_lang'] = lang_text
    
    def _create_right_column(self, parent):
        """Create right column with Talents/Spells"""
        talents_frame = tk.Frame(parent, bg='#F5F5DC', relief=tk.RAISED, bd=2)
        talents_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(talents_frame, text='Talents and Spells', font=self.body_font, 
            bg='#F5F5DC', fg=self.text_color, anchor='w').pack(anchor='w', padx=5, pady=2)
        talents_text = tk.Text(talents_frame, font=self.field_value_font, 
                      fg=self.text_color, bg='white', 
                      width=25, height=10, wrap=tk.WORD,
                      relief=tk.SUNKEN, bd=1, cursor='arrow')
        talents_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        talents_text.config(state=tk.DISABLED)
        self.widgets['ch_talent'] = talents_text
        self.widgets['ch_spell'] = talents_text  # Same widget for both

        # Gear section
        gear_frame = tk.Frame(parent, bg='#F5F5DC', relief=tk.RAISED, bd=2)
        gear_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Header with gear label and slots display
        gear_header = tk.Frame(gear_frame, bg='#F5F5DC')
        gear_header.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(gear_header, text='Gear', font=self.field_value_font,
             bg='#F5F5DC', fg=self.text_color, anchor='w').pack(side=tk.LEFT)
        self.slots_label = tk.Label(gear_header, text='Slots: 0/0', font=self.numeric_small_font,
             bg='#F5F5DC', fg=self.text_color, anchor='e')
        self.slots_label.pack(side=tk.RIGHT, padx=5)
        
        coins_row = tk.Frame(gear_frame, bg='#F5F5DC')
        coins_row.pack(fill=tk.X, padx=5)
        # GP
        tk.Label(coins_row, text='GP:', font=self.field_value_small_font, bg='#F5F5DC', fg=self.text_color).pack(side=tk.LEFT)
        gp_entry = tk.Entry(coins_row, width=6, font=self.field_value_font, fg=self.text_color, bg='white', relief=tk.SUNKEN, bd=1, justify=tk.RIGHT)
        gp_entry.pack(side=tk.LEFT, padx=5)
        gp_entry.config(state='readonly')
        self.widgets['gp_coin'] = gp_entry
        # SP
        tk.Label(coins_row, text='SP:', font=self.field_value_small_font, bg='#F5F5DC', fg=self.text_color).pack(side=tk.LEFT, padx=(10,0))
        sp_entry = tk.Entry(coins_row, width=6, font=self.field_value_font, fg=self.text_color, bg='white', relief=tk.SUNKEN, bd=1, justify=tk.RIGHT)
        sp_entry.pack(side=tk.LEFT, padx=5)
        sp_entry.config(state='readonly')
        self.widgets['sp_coin'] = sp_entry
        # CP
        tk.Label(coins_row, text='CP:', font=self.field_value_small_font, bg='#F5F5DC', fg=self.text_color).pack(side=tk.LEFT, padx=(10,0))
        cp_entry = tk.Entry(coins_row, width=6, font=self.field_value_font, fg=self.text_color, bg='white', relief=tk.SUNKEN, bd=1, justify=tk.RIGHT)
        cp_entry.pack(side=tk.LEFT, padx=5)
        cp_entry.config(state='readonly')
        self.widgets['cp_coin'] = cp_entry

        # Combined Gear display: bullets for slots (filled/empty) with item names
        mono_font = tkfont.Font(family='Courier New', size=11)
        gear_text = tk.Text(gear_frame, font=mono_font,
                     fg=self.text_color, bg='white',
                     width=32, height=12, wrap=tk.NONE,
                     relief=tk.SUNKEN, bd=1, cursor='arrow')
        gear_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        gear_text.config(state=tk.DISABLED)
        self.widgets['ch_gear_items'] = gear_text
    
    def _create_heart_shape(self, canvas, x, y, size):
        """Draw a heart shape on the canvas"""
        # Heart shape using bezier curves and polygons
        points = []
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            if angle < 180:
                # Top curves
                r = size * 0.5
                px = x + r * math.cos(rad)
                py = y - size * 0.3 + r * 0.5 * math.sin(rad)
            else:
                # Bottom point
                r = size * 0.3
                px = x + r * math.cos(rad)
                py = y + size * 0.4 + r * 0.3 * math.sin(rad)
            points.append((px, py))
        
        # Draw heart outline
        if len(points) > 2:
            canvas.create_polygon(points, outline=self.text_color, 
                                fill='', width=2)
        else:
            # Fallback simple heart
            canvas.create_arc(x-size*0.5, y-size*0.5, x, y, 
                            start=0, extent=180, outline=self.text_color, width=2, style=tk.ARC)
            canvas.create_arc(x, y-size*0.5, x+size*0.5, y, 
                            start=0, extent=180, outline=self.text_color, width=2, style=tk.ARC)
            canvas.create_polygon([(x-size*0.5, y), (x, y+size*0.5), (x+size*0.5, y)], 
                                outline=self.text_color, fill='', width=2)
    
    def _create_shield_shape(self, canvas, x, y, size):
        """Draw a shield shape on the canvas"""
        # Medieval shield shape (heater shield)
        points = [
            (x, y - size * 0.6),  # Top point
            (x - size * 0.4, y - size * 0.3),  # Top left
            (x - size * 0.45, y + size * 0.2),  # Mid left
            (x - size * 0.3, y + size * 0.5),  # Bottom left
            (x, y + size * 0.55),  # Bottom point
            (x + size * 0.3, y + size * 0.5),  # Bottom right
            (x + size * 0.45, y + size * 0.2),  # Mid right
            (x + size * 0.4, y - size * 0.3),  # Top right
        ]
        canvas.create_polygon(points, outline=self.text_color, fill='', width=2)

    def _set_entry_value(self, widget: tk.Entry, value: str):
        """Update an Entry widget while preserving its read-only state."""
        previous_state = widget.cget('state')
        if previous_state != 'normal':
            widget.config(state='normal')
        widget.delete(0, tk.END)
        widget.insert(0, value)
        if previous_state != 'normal':
            widget.config(state=previous_state)

    def _set_text_value(self, widget: tk.Text, value: str):
        """Update a Text widget while keeping it non-editable for the user."""
        previous_state = widget.cget('state')
        if previous_state == tk.DISABLED:
            widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, value)
        if previous_state == tk.DISABLED:
            widget.config(state=tk.DISABLED)
    
    def _on_gear_click(self, event):
        """Handle click on gear text widget to toggle equipment"""
        if not self.gear_text:
            return
        
        # Get click position
        index = self.gear_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        
        # Find which item instance this line corresponds to
        instance_key = None
        for key, lines in self.gear_item_lines.items():
            if line_num in lines:
                instance_key = key
                break
        
        if not instance_key or not self.on_equipment_changed:
            return
        
        # Extract base item name from instance key
        if '__instance_' in instance_key:
            base_item_name = instance_key.split('__instance_')[0]
        else:
            base_item_name = instance_key
        
        # Toggle equipment for this specific item instance
        self.on_equipment_changed(instance_key, base_item_name)
    
    def update_character_data(self, data_dict):
        """Update all fields from character data dictionary"""
        # Store character data for equipment selectors
        self.character_data = data_dict
        
        # Lock/unlock alignment dropdown based on class
        char_class = data_dict.get('ch_class', '')
        if 'ch_align' in self.widgets and isinstance(self.widgets['ch_align'], ttk.Combobox):
            if char_class == 'Priest':
                self.widgets['ch_align'].config(state='disabled')
            else:
                self.widgets['ch_align'].config(state='readonly')
        
        # Update text fields
        text_fields = ['ch_name', 'ch_ancestry', 'ch_class', 'ch_title', 
                  'ch_align', 'ch_background', 'ch_deity', 'ch_lang', 'ch_armor',
                  'gp_coin', 'sp_coin', 'cp_coin', 'LEVEL', 'XP']
        for key in text_fields:
            if key in self.widgets and key in data_dict:
                widget = self.widgets[key]
                if isinstance(widget, ttk.Combobox):
                    widget.set(str(data_dict[key]))
                elif isinstance(widget, tk.Entry):
                    # Special handling for background: show name, tooltip description
                    if key == 'ch_background':
                        full_bg = str(data_dict[key])
                        char_name = data_dict.get('ch_name', 'Character')
                        
                        # Format background with character name
                        formatted_bg = full_bg.format(character_name=char_name)
                        
                        name = formatted_bg
                        desc = ''
                        # Prefer split by first '.' to separate name and description
                        if '.' in formatted_bg:
                            parts = formatted_bg.split('.', 1)
                            name = parts[0].strip()
                            desc = parts[1].strip()
                        else:
                            # Fallback to first word vs the rest
                            tokens = formatted_bg.split(' ', 1)
                            name = tokens[0].strip()
                            if len(tokens) > 1:
                                desc = tokens[1].strip()
                        self._set_entry_value(widget, name)
                        if desc:
                            self._attach_tooltip(widget, desc)
                    else:
                        self._set_entry_value(widget, str(data_dict[key]))
                elif isinstance(widget, tk.Text) and key == 'ch_lang':
                    # Format languages in two columns for readability
                    langs = str(data_dict[key]).split(', ')
                    # Create two-column layout
                    half = (len(langs) + 1) // 2
                    col1 = langs[:half]
                    col2 = langs[half:]
                    # Format with columns using tabs for consistent alignment
                    lines = []
                    for i in range(max(len(col1), len(col2))):
                        left = col1[i] if i < len(col1) else ''
                        right = col2[i] if i < len(col2) else ''
                        if left and right:
                            lines.append(f"{left}\t\t{right}")
                        elif left:
                            lines.append(left)
                        elif right:
                            lines.append(f"\t\t{right}")
                    self._set_text_value(widget, '\n'.join(lines))
        
        # Update HP and AC with tooltips
        if 'ch_HP' in self.widgets and 'ch_HP' in data_dict:
            self._set_entry_value(self.widgets['ch_HP'], str(data_dict['ch_HP']))
            # Add HP breakdown tooltip
            if 'hp_breakdown' in data_dict:
                self._attach_tooltip(self.widgets['ch_HP'], data_dict['hp_breakdown'])
        
        if 'ch_AC' in self.widgets and 'ch_AC' in data_dict:
            self._set_entry_value(self.widgets['ch_AC'], str(data_dict['ch_AC']))
            # Add AC breakdown tooltip
            if 'ac_breakdown' in data_dict:
                self._attach_tooltip(self.widgets['ch_AC'], data_dict['ac_breakdown'])
        
        # Update ability scores (format: "score/mod")
        abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        for abbr in abilities:
            score_key = f'{abbr}_score'
            mod_key = f'{abbr}_mod'
            if score_key in self.widgets and score_key in data_dict:
                score = data_dict[score_key]
                mod = data_dict.get(mod_key, 0)
                mod_str = f"+{mod}" if mod >= 0 else str(mod)
                self._set_entry_value(self.widgets[score_key], f"{score}/{mod_str}")
        
        # Update attacks with tooltips
        if 'ch_attacks' in self.widgets and 'ch_attacks' in data_dict:
            attacks_data = data_dict['ch_attacks']
            if isinstance(attacks_data, list):
                # Format structured attacks data including range
                attacks_text = ""
                attack_breakdowns = {}  # Map line number to breakdown text
                line_num = 0
                
                if not attacks_data:
                    attacks_text = "(No weapon selected yet - visit the shop!)"
                else:
                    for item in attacks_data:
                        breakdown = ""
                        if len(item) == 5:
                            weapon, to_hit, damage, rng, breakdown = item
                            to_hit_str = f"+{to_hit}" if to_hit >= 0 else str(to_hit)
                            damage_str = damage if damage else ''
                            range_str = rng if rng else ''
                            attacks_text += f"{weapon:20} {to_hit_str:>5} / {damage_str:<8} / {range_str}\n"
                        elif len(item) == 4:
                            weapon, to_hit, damage, rng = item
                            to_hit_str = f"+{to_hit}" if to_hit >= 0 else str(to_hit)
                            damage_str = damage if damage else ''
                            range_str = rng if rng else ''
                            attacks_text += f"{weapon:20} {to_hit_str:>5} / {damage_str:<8} / {range_str}\n"
                        elif len(item) == 3:
                            weapon, to_hit, damage = item
                            to_hit_str = f"+{to_hit}" if to_hit >= 0 else str(to_hit)
                            attacks_text += f"{weapon:20} {to_hit_str:>5} / {damage}\n"
                        
                        if breakdown:
                            attack_breakdowns[line_num] = breakdown
                        line_num += 1
                
                self._set_text_value(self.widgets['ch_attacks'], attacks_text.rstrip())
                
                # Attach attack tooltips to the text widget
                if attack_breakdowns:
                    self._attach_attacks_tooltips(self.widgets['ch_attacks'], attack_breakdowns)
            else:
                # Fallback for string format
                self._set_text_value(self.widgets['ch_attacks'], str(attacks_data))

        # Update combined Gear display with clickable items and color coding
        if 'ch_gear_items' in self.widgets:
            self.gear_item_lines = {}  # Reset item line mapping
            try:
                from data_tables import WEAPONS, ARMORS
                
                # Calculate available slots
                str_score = int(data_dict.get('STR_score', 0))
                con_mod = int(data_dict.get('CON_mod', 0))
                char_class = data_dict.get('ch_class', 'Fighter')
                
                total_slots = str_score
                if char_class == 'Fighter' and con_mod > 0:
                    total_slots += con_mod
                
                # Update slots display
                if hasattr(self, 'slots_label'):
                    self.slots_label.config(text=f'Slots: 0/{total_slots}')
                
                # Get equipped items
                equipped_weapon = data_dict.get('equipped_weapon')
                equipped_armor = data_dict.get('equipped_armor')
                equipped_shield = data_dict.get('equipped_shield')
                
                # Collect all gear items
                items = data_dict.get('ch_gear_items', [])
                if isinstance(items, str):
                    items = [line.strip() for line in items.split('\n') if line.strip()]
                
                # Build display lines with color coding and bullet points
                output_lines = []
                self.gear_item_lines = {}
                current_line = 1
                
                # Calculate used slots from gear items
                used_slots = self._calculate_used_slots(items)
                available_slots = total_slots - used_slots
                
                # Update slots display with actual used/total
                if hasattr(self, 'slots_label'):
                    self.slots_label.config(text=f'Slots: {used_slots}/{total_slots}')
                
                # Display gear items with bullet points
                # Track each item instance separately with a unique index
                item_instance_index = 0
                for item_idx, item in enumerate(items):
                    # Extract item name and slot count
                    item_name = item
                    slots = 1
                    
                    # Parse item format "ItemName (X slots)" or "ItemName (X slot)"
                    if '(' in item and ')' in item:
                        item_name = item.split('(')[0].strip()
                        try:
                            slots_part = item.split('(')[1].split(')')[0]
                            slots = int(slots_part.split()[0])
                        except:
                            slots = 1
                    elif ' x ' in item:
                        # Stackable format "Item x N"
                        item_name = item.split(' x ')[0].strip()
                        slots = 1
                    
                    # Create unique key for this item instance
                    instance_key = f"{item_name}__instance_{item_instance_index}"
                    
                    # Track this item instance's line for click handling
                    if instance_key not in self.gear_item_lines:
                        self.gear_item_lines[instance_key] = []
                    self.gear_item_lines[instance_key].append(current_line)
                    
                    # For multi-slot items, format as main item with sub-bullets
                    if slots > 1:
                        # Main bullet with item name and colon
                        output_lines.append(f"• {item_name}:")
                        current_line += 1
                        
                        # Add sub-bullets for additional slots (plural form with lowercase)
                        item_lower = item_name.lower()
                        for _ in range(slots - 1):
                            output_lines.append(f"•   {item_lower} is heavy")
                            # Track sub-bullet lines with the same instance_key for coloring
                            self.gear_item_lines[instance_key].append(current_line)
                            current_line += 1
                    else:
                        # Single-slot items display normally
                        output_lines.append(f"• {item}")
                        current_line += 1
                    
                    item_instance_index += 1
                
                # Add empty bullet points for available slots
                for _ in range(available_slots):
                    output_lines.append("•")
                    current_line += 1
                
                # Insert text
                full_text = "\n".join(output_lines)
                self.gear_text = self.widgets['ch_gear_items']
                self._set_text_value(self.gear_text, full_text)
                
                # Apply color tags - enable temporarily
                self.gear_text.config(state=tk.NORMAL)
                
                # Get equipped instance keys (stored as "ItemName__instance_N")
                equipped_weapon_instance = data_dict.get('equipped_weapon_instance', '')
                equipped_armor_instance = data_dict.get('equipped_armor_instance', '')
                equipped_shield_instance = data_dict.get('equipped_shield_instance', '')
                
                # Apply colors
                for instance_key, line_nums in self.gear_item_lines.items():
                    # Extract base item name from instance key
                    if '__instance_' in instance_key:
                        base_item_name = instance_key.split('__instance_')[0]
                    else:
                        base_item_name = instance_key
                    
                    # Determine if this item should be grayed out based on equipment rules
                    color = self.text_color  # Default to black (always equipped)
                    
                    # Check if it's a weapon or armor item
                    if base_item_name in WEAPONS:
                        # Weapons: only the equipped instance is black, all others gray
                        is_equipped = instance_key == equipped_weapon_instance
                        color = self.text_color if is_equipped else self.grayed_color
                    elif base_item_name in ARMORS:
                        # Armor/Shield: only equipped instance is black, all others gray
                        is_equipped = (instance_key == equipped_armor_instance or 
                                     instance_key == equipped_shield_instance)
                        color = self.text_color if is_equipped else self.grayed_color
                    elif base_item_name in ['Crossbow bolts', 'Bolts']:
                        # Crossbow bolts match crossbow equipped status
                        equipped_weapon_base = equipped_weapon_instance.split('__instance_')[0] if '__instance_' in equipped_weapon_instance else equipped_weapon_instance
                        is_equipped = equipped_weapon_base == 'Crossbow'
                        color = self.text_color if is_equipped else self.grayed_color
                    elif base_item_name in ['Arrow', 'Arrows']:
                        # Arrows match shortbow or longbow equipped status
                        equipped_weapon_base = equipped_weapon_instance.split('__instance_')[0] if '__instance_' in equipped_weapon_instance else equipped_weapon_instance
                        is_equipped = equipped_weapon_base in ['Shortbow', 'Longbow']
                        color = self.text_color if is_equipped else self.grayed_color
                    # All other items stay black (never grayed out)
                    
                    # Use instance_key for unique tag name
                    tag_name = f"item_{instance_key.replace(' ', '_')}"
                    
                    for line_num in line_nums:
                        start = f"{line_num}.0"
                        end = f"{line_num}.end"
                        self.gear_text.tag_add(tag_name, start, end)
                    
                    self.gear_text.tag_config(tag_name, foreground=color)
                
                self.gear_text.config(state=tk.DISABLED)
                
                # Bind click handler
                self.gear_text.bind("<Button-1>", self._on_gear_click)
                
            except Exception as e:
                pass
        
        # Update talents/spells
        talent_text = ""
        if 'ch_talent' in data_dict:
            talent_text += str(data_dict['ch_talent'])
        if 'ch_spell' in data_dict:
            if talent_text:
                talent_text += "\n\n"
            talent_text += str(data_dict['ch_spell'])
        
        if 'ch_talent' in self.widgets:
            self._set_text_value(self.widgets['ch_talent'], talent_text)
    
    def clear_fields(self):
        """Clear all displayed data"""
        for key, widget in self.widgets.items():
            if isinstance(widget, tk.Entry):
                self._set_entry_value(widget, '')
            elif isinstance(widget, tk.Text):
                self._set_text_value(widget, '')
    
    def _calculate_used_slots(self, items):
        """Calculate number of slots used by gear items
        
        Parses items in the format:
        - "ItemName (X slots)" or "ItemName (X slot)" → X slots
        - "item x N" (stackable, counts as 1 slot per line) → 1 slot
        - "  item are heavy" (stackable overflow or multi-slot sub-bullet) → 1 slot
        - Other formats count as 1 slot
        """
        used = 0
        for item_str in items:
            # Skip empty lines
            if not item_str.strip():
                continue
            
            # "are heavy" lines count as 1 slot each (from multi-slot items)
            if "are heavy" in item_str:
                used += 1
            # "ItemName (X slots)" or "ItemName (X slot)" format
            elif '(' in item_str and ')' in item_str:
                try:
                    slots_part = item_str.split('(')[1].split(')')[0]
                    slots = int(slots_part.split()[0])
                    used += slots
                except:
                    used += 1
            # "item x N" stackable format (main line counts as 1)
            elif ' x ' in item_str:
                used += 1
            # Regular items count as 1 slot
            elif item_str.strip() and not item_str.strip().startswith('•'):
                used += 1
        
        return used
