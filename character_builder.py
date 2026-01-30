"""
Character Builder for ShadowDark RPG
Generates random characters and displays them in the character sheet GUI
"""

import random
import tkinter as tk
from tkinter import messagebox
import sys
import os
from character_sheet import CharacterSheet
from coin_utils import cost_to_cp, cp_to_gp_sp_cp, format_coins, subtract_cost, add_coins, sell_item
from data_tables import (WEAPONS, ARMORS, EQUIPMENT, DEITY_DESCRIPTIONS,
                         NAME_TABLES, BACKGROUNDS, DEITIES, DEITY_ALIGNMENTS,
                         WIZARD_D4_LANGUAGES, WIZARD_D10_LANGUAGES,
                         PRIEST_SPELLS, WIZARD_SPELLS)
from inventory_utils import add_stackable_item as inv_add_stackable_item, coin_count


SOUND_ENABLED = False
ATTACK_BONUS_ALL = "+1 to melee and ranged attacks"


def roll(sides: int) -> int:
    """Roll a die with the given number of sides."""
    return random.randint(1, sides)


def roll_d4():
    return roll(4)


def roll_d6():
    return roll(6)


def roll_d8():
    return roll(8)


def roll_d10():
    return roll(10)


def roll_d12():
    return roll(12)


def roll_d20():
    return roll(20)


def roll_d100():
    return roll(100)


def roll_2d6():
    return roll_d6() + roll_d6()


def roll_3d6():
    return roll_d6() + roll_d6() + roll_d6()


# Ability modifier calculation function
def get_ability_modifier(score):
    """Get ability modifier from score using the formula (score - 10) // 2
    Works for any ability score, including those above 18 or below 3"""
    return (score - 10) // 2


class CharacterBuilder:
    """Generates random ShadowDark characters"""
    
    def __init__(self):
        self.character_data = {}
        # Shared data tables
        self.WEAPONS = WEAPONS
        self.ARMORS = ARMORS
        self.EQUIPMENT = EQUIPMENT
    
    def generate_character(self):
        """Phase 1: Generate initial character attributes"""
        self._generate_ability_scores()
        self._generate_ancestry()
        self._determine_class()
        self._generate_deity()
        self._determine_alignment()
        self._generate_background()
        self._determine_title()
        self._generate_int_modifier_languages()  # Generate INT mod languages once
        self._generate_languages()
        self._generate_name()
        self._calculate_hp()
        self._calculate_ac()
        self._generate_attacks()
        
        # Set defaults
        self.character_data['LEVEL'] = 1
        self.character_data['XP'] = 0
        
        # Generate starting coins: 2d6 x 5 gp
        total_gp = (roll_d6() + roll_d6()) * 5
        self.character_data['gp_coin'] = total_gp
        self.character_data['sp_coin'] = 0
        self.character_data['cp_coin'] = 0
        
        return self.character_data
    
    def finalize_character(self):
        """Phase 2: Generate talents, spells and finalize character"""
        self._generate_talents()
        self._regenerate_attacks()
        self._calculate_ac()
        return self.character_data
    
    def update_from_selection(self, key, value):
        """Update character data based on a manual dropdown selection"""
        if not self.character_data:
            return
            
        old_class = self.character_data.get('ch_class')
        old_ancestry = self.character_data.get('ch_ancestry')
        self.character_data[key] = value
        
        # Recalculate dependencies
        if key == 'ch_class' or key == 'ch_align':
            self._determine_title()
        
        if key == 'ch_class':
            self._calculate_hp()
            # Regenerate languages if class changed (wizards get more)
            self._generate_languages()
            
            # If changing TO a class that doesn't use leather armor, remove it
            if value == 'Wizard':
                gear = self.character_data.get('ch_gear_items', [])
                self.character_data['ch_gear_items'] = [item for item in gear if 'Leather Armor' not in str(item)]
                self.character_data['equipped_armor'] = None
                self.character_data['equipped_armor_instance'] = None
        
        # If ancestry changed, handle language changes
        if key == 'ch_ancestry':
            # If changing TO human and we don't have a stored random language yet, generate it
            if value == "Human":
                if not self.character_data.get('_human_random_lang'):
                    self._generate_human_random_language()
            # Regenerate languages for any ancestry change
            self._generate_languages()
        
        # If deity changed, update alignment based on deity
        if key == 'ch_deity':
            if value in DEITY_ALIGNMENTS:
                self.character_data['ch_align'] = DEITY_ALIGNMENTS[value]
                self._determine_title()  # Title may change with alignment
            
        # Recalculate AC and attacks as they might depend on class
        self._calculate_ac()
        self._generate_attacks()
        
        return self.character_data
    
    def _generate_ability_scores(self):
        """Generate ability scores using 3d6 for each"""
        abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
        for abbr in abilities:
            score = roll_3d6()
            mod = get_ability_modifier(score)
            self.character_data[f'{abbr}_score'] = score
            self.character_data[f'{abbr}_mod'] = mod
    
    def _generate_ancestry(self):
        """Generate ancestry using d12"""
        roll = roll_d12()
        if roll <= 4:
            ancestry = "Human"
        elif roll <= 6:
            ancestry = "Elf"
        elif roll <= 8:
            ancestry = "Dwarf"
        elif roll <= 10:
            ancestry = "Halfling"
        elif roll == 11:
            ancestry = "Half Orc"
        else:
            ancestry = "Goblin"
        self.character_data['ch_ancestry'] = ancestry
        
        # For humans, generate and store a random language on the side
        # This will be used when the character is human
        if ancestry == "Human":
            self._generate_human_random_language()
    
    def _determine_class(self):
        """Determine class based on highest ability score with tie-breaking"""
        scores = {
            'STR': self.character_data['STR_score'],
            'DEX': self.character_data['DEX_score'],
            'INT': self.character_data['INT_score'],
            'WIS': self.character_data['WIS_score']
        }
        # Ignore CHA, use CON for tie-breaking
        
        # Find highest score
        max_score = max(scores.values())
        highest_abilities = [abbr for abbr, score in scores.items() if score == max_score]
        
        if len(highest_abilities) == 1:
            # Single highest
            ability = highest_abilities[0]
            if ability == 'STR':
                self.character_data['ch_class'] = 'Fighter'
            elif ability == 'DEX':
                self.character_data['ch_class'] = 'Thief'
            elif ability == 'INT':
                self.character_data['ch_class'] = 'Wizard'
            else:  # WIS
                self.character_data['ch_class'] = 'Priest'
        else:
            # Tie - use tie-breaking rules
            con_score = self.character_data['CON_score']
            class_name = self._resolve_class_tie(highest_abilities, con_score)
            self.character_data['ch_class'] = class_name
    
    def _resolve_class_tie(self, tied_abilities, con_score):
        """Resolve class determination when abilities are tied"""
        if len(tied_abilities) == 2:
            ab1, ab2 = tied_abilities
            
            # STR + DEX
            if 'STR' in tied_abilities and 'DEX' in tied_abilities:
                return 'Fighter' if con_score > 10 else 'Thief'
            
            # STR + INT
            if 'STR' in tied_abilities and 'INT' in tied_abilities:
                return 'Fighter' if con_score > 10 else 'Wizard'
            
            # STR + WIS
            if 'STR' in tied_abilities and 'WIS' in tied_abilities:
                return 'Fighter' if con_score > 10 else 'Priest'
            
            # DEX + INT
            if 'DEX' in tied_abilities and 'INT' in tied_abilities:
                return 'Thief' if con_score > 10 else 'Wizard'
            
            # DEX + WIS
            if 'DEX' in tied_abilities and 'WIS' in tied_abilities:
                return 'Thief' if con_score > 10 else 'Priest'
            
            # INT + WIS
            if 'INT' in tied_abilities and 'WIS' in tied_abilities:
                return 'Priest' if con_score > 10 else 'Wizard'
        
        # If CON is also tied or 3+ abilities tied, random selection
        class_map = {
            'STR': 'Fighter',
            'DEX': 'Thief',
            'INT': 'Wizard',
            'WIS': 'Priest'
        }
        selected = random.choice(tied_abilities)
        return class_map[selected]
    
    def _generate_deity(self):
        """Generate deity using d8"""
        roll = roll_d8()
        self.character_data['ch_deity'] = DEITIES[roll - 1]
        self.character_data['_deity_roll'] = roll  # Store for alignment
    
    def _determine_alignment(self):
        """Determine alignment based on deity and class"""
        deity_roll = self.character_data.get('_deity_roll', 1)
        char_class = self.character_data['ch_class']
        alignment = self._alignment_from_roll(deity_roll, char_class)
        self.character_data['ch_align'] = alignment

    def _alignment_from_roll(self, deity_roll, char_class):
        if char_class == 'Priest':
            if deity_roll <= 3:
                return "Lawful"
            if deity_roll <= 5:
                return "Neutral"
            return "Chaotic"

        modifier = random.randint(-2, 2)
        adjusted_roll = max(1, min(10, deity_roll + modifier))
        if adjusted_roll <= 4:
            return "Lawful"
        if adjusted_roll <= 6:
            return "Neutral"
        return "Chaotic"
    
    def _generate_background(self):
        """Generate background using d20"""
        roll = roll_d20()
        self.character_data['ch_background'] = BACKGROUNDS[roll - 1]
    
    def _determine_title(self):
        """Determine title based on class and alignment"""
        char_class = self.character_data['ch_class']
        alignment = self.character_data['ch_align']
        
        if char_class == 'Fighter':
            if alignment == 'Lawful':
                title = "Squire"
            elif alignment == 'Chaotic':
                title = "Knave"
            else:
                title = "Warrior"
        elif char_class == 'Thief':
            if alignment == 'Lawful':
                title = "Footpad"
            elif alignment == 'Chaotic':
                title = "Thug"
            else:
                title = "Robber"
        elif char_class == 'Priest':
            if alignment == 'Lawful':
                title = "Acolyte"
            elif alignment == 'Chaotic':
                title = "Initiate"
            else:
                title = "Seeker"
        else:  # Wizard
            if alignment == 'Lawful':
                title = "Apprentice"
            elif alignment == 'Chaotic':
                title = "Adept"
            else:
                title = "Shaman"
        
        self.character_data['ch_title'] = title
    
    def _generate_human_random_language(self):
        """Generate and store the random bonus language for humans"""
        # Humans get a single random language as their ancestry bonus
        # This is always assigned, independent of INT modifier
        random_lang = None
        while True:
            roll = roll_d10()
            if roll == 10:
                continue  # Reroll on 10
            lang = WIZARD_D10_LANGUAGES[roll - 1]
            if lang not in ["Common"]:
                random_lang = lang
                break
        
        self.character_data['_human_random_lang'] = random_lang
    
    def _generate_int_modifier_languages(self):
        """Generate and store bonus languages from INT modifier"""
        int_mod = self.character_data['INT_mod']
        int_langs = []
        
        if int_mod > 0:
            # Don't add Common since it's always known
            for _ in range(int_mod):
                while True:
                    roll = roll_d10()
                    if roll == 10:
                        continue  # Reroll on 10
                    lang = WIZARD_D10_LANGUAGES[roll - 1]
                    if lang not in int_langs and lang != "Common":
                        int_langs.append(lang)
                        break
        
        self.character_data['_int_modifier_langs'] = int_langs
    
    def _generate_languages(self):
        """Generate languages"""
        languages = ["Common"]
        ancestry = self.character_data['ch_ancestry']
        char_class = self.character_data['ch_class']
        int_mod = self.character_data['INT_mod']
        deity_roll = self.character_data.get('_deity_roll', 1)
        
        # Ancestry language
        ancestry_langs = {
            'Dwarf': 'Dwarvish',
            'Elf': 'Elvish',
            'Goblin': 'Goblin',
            'Half Orc': 'Orcish'
        }
        
        # For humans, use the stored random bonus language
        if ancestry == "Human":
            stored_lang = self.character_data.get('_human_random_lang')
            if stored_lang:
                languages.append(stored_lang)
        elif ancestry in ancestry_langs:
            languages.append(ancestry_langs[ancestry])
        
        # Wizard languages - use stored if available, otherwise generate and store
        if char_class == 'Wizard':
            wizard_langs = self.character_data.get('_wizard_langs')
            if wizard_langs is None:
                # First time: generate and store
                wizard_langs = {'d4': [], 'd10': []}
                
                # 2 from d4 table
                d4_selected = []
                while len(d4_selected) < 2:
                    roll = roll_d4()
                    lang = WIZARD_D4_LANGUAGES[roll - 1]
                    if lang not in languages and lang not in d4_selected:
                        d4_selected.append(lang)
                wizard_langs['d4'] = d4_selected
                
                # 2 from d10 table
                d10_selected = []
                while len(d10_selected) < 2:
                    roll = roll_d10()
                    if roll == 10:
                        continue
                    lang = WIZARD_D10_LANGUAGES[roll - 1]
                    if lang not in languages and lang not in d10_selected:
                        d10_selected.append(lang)
                wizard_langs['d10'] = d10_selected
                
                self.character_data['_wizard_langs'] = wizard_langs
            
            # Add stored wizard languages
            for lang in wizard_langs.get('d4', []):
                if lang not in languages:
                    languages.append(lang)
            for lang in wizard_langs.get('d10', []):
                if lang not in languages:
                    languages.append(lang)
        
        # Priest language
        if char_class == 'Priest':
            if deity_roll <= 3:
                languages.append("Celestial")
            elif deity_roll <= 5:
                languages.append("Primordial")
            else:
                languages.append("Diabolic")
        
        # Add stored INT modifier languages (computed once and reused)
        int_langs = self.character_data.get('_int_modifier_langs', [])
        for lang in int_langs:
            if lang not in languages:
                languages.append(lang)
        
        self.character_data['ch_lang'] = ", ".join(languages)
    
    def _generate_name(self):
        """Generate name based on ancestry"""
        ancestry = self.character_data['ch_ancestry']
        roll = roll_d20()
        name = NAME_TABLES[ancestry][roll - 1]
        self.character_data['ch_name'] = name
    
    def _calculate_hp(self):
        """Calculate hit points based on class and CON modifier"""
        char_class = self.character_data['ch_class']
        con_mod = self.character_data['CON_mod']
        ancestry = self.character_data.get('ch_ancestry', '')
        
        # Base HP by class
        die_type = ''
        if char_class == 'Fighter':
            base_hp = roll_d8()
            die_type = '1d8'
        elif char_class == 'Thief':
            base_hp = roll_d4()
            die_type = '1d4'
        elif char_class == 'Priest':
            base_hp = roll_d6()
            die_type = '1d6'
        elif char_class == 'Wizard':
            base_hp = roll_d4()
            die_type = '1d4'
        else:
            base_hp = roll_d6()  # Fallback
            die_type = '1d6'
        
        # Build breakdown for tooltip
        breakdown_parts = [f"{die_type}: rolled {base_hp}"]
        
        # Add CON modifier, but HP cannot go below 1
        hp_before_min = base_hp + con_mod
        if con_mod != 0:
            breakdown_parts.append(f"CON {con_mod:+d}")
        
        # Dwarf ancestry bonus: +2 HP
        if ancestry == 'Dwarf':
            breakdown_parts.append("Dwarf +2")
            hp_before_min += 2
        
        hp = max(1, hp_before_min)
        
        # Store breakdown for tooltip
        breakdown = ", ".join(breakdown_parts) + f" = {hp}"
        self.character_data['hp_breakdown'] = breakdown
        self.character_data['ch_HP'] = hp
    
    def _calculate_ac(self):
        """Calculate armor class
        Base AC = 10 + DEX_mod for all characters
        Starting armor: Leather Armor for Fighter/Priest/Thief added to inventory (NOT equipped).
        User must click to equip armor.
        """
        char_class = self.character_data['ch_class']
        dex_mod = self.character_data['DEX_mod']

        # Add default starting armor to gear if none (but don't auto-equip)
        gear = self.character_data.setdefault('ch_gear_items', [])
        if self.character_data.get('equipped_armor') is None:
            if char_class in ['Fighter', 'Priest', 'Thief']:
                if not any('Leather Armor' in str(it) for it in gear):
                    gear.append('Leather Armor (1 slot)')
                # Don't auto-equip - user must click to equip
                self.character_data['equipped_armor'] = None
                self.character_data['equipped_armor_instance'] = None
            else:
                self.character_data['equipped_armor'] = None
                self.character_data['equipped_armor_instance'] = None

        # Calculate AC from equipped armor
        base_ac = 10 + dex_mod
        armor_name = self.character_data.get('equipped_armor')
        ac = base_ac
        
        # Build breakdown for tooltip
        breakdown_parts = ["base 10"]
        armor_bonus_to_base = 0
        
        if armor_name and armor_name in getattr(self, 'ARMORS', {}):
            a = self.ARMORS[armor_name]
            if a['ac_type'] == 'base_plus_dex':
                # Armor has a base that replaces 10
                armor_bonus_to_base = a['base'] - 10
                ac = a['base'] + dex_mod
                if armor_bonus_to_base > 0:
                    breakdown_parts.append(f"{armor_name} +{armor_bonus_to_base}")
            elif a['ac_type'] == 'flat':
                # Flat AC, no DEX
                ac = a['base']
                breakdown_parts = [f"{armor_name} (flat {a['base']})"]
            # shield handled separately
            self.character_data['ch_armor'] = armor_name
        else:
            self.character_data['ch_armor'] = 'None'
        
        # Add DEX modifier to breakdown (if armor allows it)
        if armor_name and armor_name in getattr(self, 'ARMORS', {}):
            a = self.ARMORS[armor_name]
            if a['ac_type'] != 'flat' and dex_mod != 0:
                breakdown_parts.append(f"DEX {dex_mod:+d}")
        elif dex_mod != 0:
            breakdown_parts.append(f"DEX {dex_mod:+d}")

        # Shield bonus
        shield_bonus = 0
        shield_name = self.character_data.get('equipped_shield')
        if shield_name == 'Shield' and shield_name in getattr(self, 'ARMORS', {}):
            shield_bonus += self.ARMORS[shield_name]['base']
            breakdown_parts.append(f"Shield +{shield_bonus}")
            # If shield equipped, unequip 2H weapon (unless it's versatile)
            eq_weap_instance = self.character_data.get('equipped_weapon_instance')
            if eq_weap_instance:
                # Extract base weapon name from instance key
                eq_weap = eq_weap_instance.split('__instance_')[0] if '__instance_' in eq_weap_instance else eq_weap_instance
                weapon_props = self.WEAPONS.get(eq_weap, {}).get('properties', [])
                # Only unequip if 2H and NOT versatile
                if '2H' in weapon_props and 'V' not in weapon_props:
                    self.character_data['equipped_weapon_instance'] = None
                    self.character_data['equipped_weapon'] = None
        ac += shield_bonus
        
        # Check for Fighter +1 AC talent
        talent_ac_bonus = 0
        talents = self.character_data.get('ch_talent', '')
        if '+1 to AC' in talents:
            talent_ac_bonus = 1
            ac += talent_ac_bonus
            breakdown_parts.append("Fighter talent +1")
        
        # Store breakdown for tooltip
        breakdown = ", ".join(breakdown_parts) + f" = {ac}"
        self.character_data['ac_breakdown'] = breakdown
        self.character_data['ch_AC'] = ac
    
    def _generate_attacks(self):
        self.character_data['ch_attacks'] = self._build_attacks(apply_talent_bonuses=False)
    
    def _generate_talents(self):
        """Generate talents and spells for the character based on class"""
        char_class = self.character_data['ch_class']
        ancestry = self.character_data['ch_ancestry']
        
        talents = []
        spells = []
        
        # Add ancestry talent first
        ancestry_talent = self._generate_ancestry_talent()
        if ancestry_talent:
            talents.append(ancestry_talent)
        
        # Determine number of talents by ancestry: Humans roll 2, others roll 1
        num_talents = 2 if ancestry == 'Human' else 1
        
        # All fighters get at least 1 weapon mastery
        weapon_mastery_count = 1 if char_class == 'Fighter' else 0

        # Talent tables by class
        if char_class == 'Fighter':
            for _ in range(num_talents):
                talent_roll = roll_2d6()
                talent_text = self._process_fighter_talent(talent_roll)
                if talent_text:
                    # Check if this is an additional mastery
                    if talent_text == "ADDITIONAL_MASTERY":
                        weapon_mastery_count += 1
                        talents.append("additional weapon mastery (select in shop)")
                    else:
                        talents.append(talent_text)
        
        elif char_class == 'Thief':
            # Thief has specific talent table
            for _ in range(num_talents):
                talent_roll = roll_2d6()
                talent_text = self._process_thief_talent(talent_roll)
                if talent_text:
                    talents.append(talent_text)
        
        elif char_class == 'Priest':
            # Priest: always gains exactly 2 spells
            num_spells = 2
            spells_available = PRIEST_SPELLS.copy()
            for _ in range(min(num_spells, len(spells_available))):
                spell = random.choice(spells_available)
                spells.append(spell)
                spells_available.remove(spell)
            
            # Initialize priest spellcasting modifier
            self.character_data.setdefault('priest_spell_mod', 0)
            
            # Roll talents for priest
            for _ in range(num_talents):
                talent_roll = roll_2d6()
                talent_text = self._process_priest_talent(talent_roll, spells)
                if talent_text:
                    talents.append(talent_text)
        
        elif char_class == 'Wizard':
            # Wizard: starts with exactly 3 spells and talents (based on ancestry)
            num_spells = 3
            spells_available = WIZARD_SPELLS.copy()
            for _ in range(min(num_spells, len(spells_available))):
                spell = random.choice(spells_available)
                spells.append(spell)
                spells_available.remove(spell)

            # Store initial spells for talent to pick from
            self.character_data['_initial_spells'] = spells.copy()

            # Initialize wizard spellcasting modifier
            self.character_data.setdefault('wizard_spell_mod', 0)

            # Pre-set spell list for downstream usage
            self.character_data['ch_spell'] = "\n".join(spells) if spells else ""

            # Roll talents for wizard
            for _ in range(num_talents):
                talent_roll = roll_2d6()
                talent_text = self._process_wizard_talent(talent_roll, ancestry)
                if talent_text:
                    talents.append(talent_text)
        
        # Combine talents and spells for display
        talent_display = "\n".join(talents) if talents else ""
        if char_class != 'Wizard':
            # For non-wizards, set ch_spell now (wizards already set it above)
            spell_display = "\n".join(spells) if spells else ""
            self.character_data['ch_spell'] = spell_display

        # Store weapon mastery count for fighters
        if char_class == 'Fighter':
            self.character_data['weapon_mastery_count'] = weapon_mastery_count

        # Append casting bonus below spells for Priests and Wizards
        if char_class in ['Priest', 'Wizard']:
            if char_class == 'Priest':
                x = self.character_data.get('WIS_mod', 0) + self.character_data.get('priest_spell_mod', 0)
                bonus_text = f"+ {x} to cast Priest spells"
            else:
                x = self.character_data.get('INT_mod', 0) + self.character_data.get('wizard_spell_mod', 0)
                bonus_text = f"+ {x} to cast Wizard spells"
            existing_spells = self.character_data.get('ch_spell', '')
            if existing_spells:
                self.character_data['ch_spell'] = f"{existing_spells}\n{bonus_text}"
            else:
                self.character_data['ch_spell'] = bonus_text

        self.character_data['ch_talent'] = talent_display
    
    def _update_talent_display_with_masteries(self):
        """Update talent display to include weapon masteries"""
        char_class = self.character_data.get('ch_class', '')
        if char_class != 'Fighter':
            return
        
        masteries = self.character_data.get('weapon_masteries', [])
        if not masteries:
            return
        
        # Get current talents
        current_talents = self.character_data.get('ch_talent', '')
        talent_lines = [line for line in current_talents.split('\n') if line.strip() and 'select in shop' not in line]
        
        # Add mastery lines
        for mastery_weapon in masteries:
            talent_lines.append(f"Mastery in {mastery_weapon}")
        
        # Update talent display
        self.character_data['ch_talent'] = '\n'.join(talent_lines)
    
    def _generate_ancestry_talent(self):
        """Generate ancestry-specific talent and apply mechanical bonuses"""
        ancestry = self.character_data.get('ch_ancestry')
        char_class = self.character_data.get('ch_class')
        
        if ancestry == 'Dwarf':
            # HP bonus already applied in _calculate_hp
            return "Stout: gain +2 HP at level 1. Advantage on HP rolls when levelling up."
        
        elif ancestry == 'Elf':
            if char_class in ['Wizard', 'Priest']:
                # Add +1 to spellcasting
                if char_class == 'Wizard':
                    current = self.character_data.get('wizard_spell_mod', 0)
                    self.character_data['wizard_spell_mod'] = current + 1
                else:  # Priest
                    current = self.character_data.get('priest_spell_mod', 0)
                    self.character_data['priest_spell_mod'] = current + 1
                return "Fey Ancestry: +1 to spellcasting checks."
            else:
                # +1 to ranged attacks (applied in _build_attacks)
                return "Farsight: +1 to ranged attacks."
        
        elif ancestry == 'Goblin':
            return "You can't be surprised."
        
        elif ancestry == 'Half Orc':
            # Attack and damage bonuses applied in _build_attacks and _weapon_to_attacks
            return "Mighty: +1 to hit and damage with melee weapons."
        
        elif ancestry == 'Halfling':
            return "Stealthy: Once per day, you can become invisible for 3 rounds."
        
        elif ancestry == 'Human':
            # Humans already get 2 talents instead of 1
            return "Ambitious: you gain an additional talent at 1st level."
        
        return ""
    
    def _regenerate_attacks(self):
        self.character_data['ch_attacks'] = self._build_attacks(apply_talent_bonuses=True)

    def _build_attacks(self, apply_talent_bonuses):
        """Rebuild attack list, optionally applying talent bonuses."""
        char_class = self.character_data['ch_class']
        ancestry = self.character_data['ch_ancestry']
        dex_mod = self.character_data['DEX_mod']
        str_mod = self.character_data['STR_mod']
        wis_mod = self.character_data['WIS_mod']

        attack_bonus_melee = 0
        attack_bonus_ranged = 0
        if apply_talent_bonuses:
            talent_text = self.character_data.get('ch_talent', '')
            if '+1 to melee or ranged attacks' in talent_text or ATTACK_BONUS_ALL in talent_text:
                attack_bonus_melee = 1
                attack_bonus_ranged = 1
            
            # Half Orc ancestry bonus: +1 to melee attacks
            if ancestry == 'Half Orc':
                attack_bonus_melee += 1
            
            # Elf ancestry bonus: +1 to ranged attacks (if not wizard/priest)
            if ancestry == 'Elf' and char_class not in ['Wizard', 'Priest']:
                attack_bonus_ranged += 1

        # Use equipped_weapon if available, otherwise ch_weapon for backwards compatibility
        weapon_name = self.character_data.get('equipped_weapon') or self.character_data.get('ch_weapon')
        if weapon_name is None:
            # No weapon selected yet; return unarmed attack
            self.character_data['ch_weapon'] = None
            self.character_data['equipped_weapon'] = None
            # Unarmed attack: STR modifier, 1 damage, close range
            unarmed_to_hit = str_mod + attack_bonus_melee
            unarmed_breakdown = f"To hit: STR {str_mod:+d}"
            if attack_bonus_melee > 0:
                unarmed_breakdown += f", bonus +{attack_bonus_melee}"
            unarmed_breakdown += f" = {unarmed_to_hit:+d}"
            return [("Unarmed", unarmed_to_hit, "1", "C", unarmed_breakdown)]
        
        # Build attacks for the currently equipped weapon
        gear = self.character_data.setdefault('ch_gear_items', [])
        weapon_slots = self.WEAPONS.get(weapon_name, {}).get('slots', 1)
        # Avoid duplicate entry if rebuilt
        if not any(weapon_name in str(it) for it in gear):
            suffix = 'slot' if weapon_slots == 1 else 'slots'
            gear.append(f"{weapon_name} ({weapon_slots} {suffix})")
        # Default equip weapon if not already set
        if self.character_data.get('equipped_weapon') is None:
            self.character_data['equipped_weapon'] = weapon_name
        attacks = self._weapon_to_attacks(
            weapon_name,
            str_mod,
            dex_mod,
            attack_bonus_melee,
            attack_bonus_ranged
        )

        if apply_talent_bonuses and char_class == 'Thief' and 'backstab' in self.character_data:
            backstab = self.character_data['backstab']
            updated_attacks = []
            for attack in attacks:
                if len(attack) == 5:
                    weapon, to_hit, damage, rng, breakdown = attack
                    if 'shortsword' in weapon.lower():
                        updated_attacks.append((weapon, to_hit, f"{damage} (backstab +{backstab}d6)", rng, breakdown + f"\nBackstab: +{backstab}d6"))
                    else:
                        updated_attacks.append(attack)
                elif len(attack) == 4:
                    weapon, to_hit, damage, rng = attack
                    if 'shortsword' in weapon.lower():
                        updated_attacks.append((weapon, to_hit, f"{damage} (backstab +{backstab}d6)", rng, f"Backstab: +{backstab}d6"))
                    else:
                        updated_attacks.append(attack)
            attacks = updated_attacks

        # Remove spell attack from attacks; casting bonus will be shown under spells
        # (Priests and Wizards will have a separate display for casting bonus)

        return attacks
    
    def add_stackable_item(self, gear_list, item_name, item_data):
        """Add a stackable item to gear, stacking in the same slot until full.
        
        For items with 'slots_per' property:
        - Stack items in the same slot until reaching slots_per max
        - When full, move to next slot
        - Format as "ItemName (X qty)" or indent as "ItemName x N are heavy!"
        
        Args:
            gear_list: The ch_gear_items list
            item_name: Name of the item to add
            item_data: The equipment data dict for the item
            
        Returns:
            The updated gear_list
        """
        if 'slots_per' not in item_data:
            # Not a stackable item, add normally
            return gear_list
        
        slots_per = item_data['slots_per']
        return inv_add_stackable_item(gear_list, item_name, slots_per)

    def _weapon_to_attacks(self, weapon_name, str_mod, dex_mod, attack_bonus_melee, attack_bonus_ranged):
        """Convert a weapon into one or two attack entries including range.
        Handles finesse, thrown dual entries, and versatile (damage choice depends on shield).
        Applies weapon mastery bonuses if applicable.
        
        Args:
            weapon_name: Name of the weapon
            str_mod: Base STR modifier
            dex_mod: Base DEX modifier
            attack_bonus_melee: Additional melee attack bonus (from talents, ancestry)
            attack_bonus_ranged: Additional ranged attack bonus (from talents, ancestry)
        """
        w = self.WEAPONS[weapon_name]
        entries = []
        # Check if shield is equipped (support both instance-based and legacy systems)
        shield = (self.character_data.get('equipped_shield_instance') is not None or 
                  self.character_data.get('equipped_shield') is not None)
        
        # Check for weapon mastery bonus (check all stored masteries)
        has_mastery = False
        if 'weapon_masteries' in self.character_data:
            has_mastery = weapon_name in self.character_data['weapon_masteries']
        else:
            # Legacy support for old weapon_mastery key
            mastery_weapon = self.character_data.get('weapon_mastery')
            has_mastery = mastery_weapon == weapon_name
        
        mastery_atk_bonus = 1 if has_mastery else 0
        ancestry = self.character_data.get('ch_ancestry', '')

        # Determine which ability mod to use
        use_mod = str_mod
        base_ability = 'STR'
        if 'F' in w['properties']:
            if dex_mod > str_mod:
                use_mod = dex_mod
                base_ability = 'DEX'

        # Handle damage (versatile)
        dmg = w['damage']
        base_dmg = dmg
        if '/' in dmg:  # versatile two values
            low, high = dmg.split('/')
            dmg_to_use = low.strip() if shield else high.strip()
            base_dmg = dmg_to_use
        else:
            dmg_to_use = dmg
            base_dmg = dmg
        
        # Track damage bonuses for breakdown
        dmg_bonus_parts = []
        
        # Add weapon mastery damage bonus if applicable
        if has_mastery:
            dmg_to_use = self._add_damage_bonus(dmg_to_use, 1)
            dmg_bonus_parts.append("mastery +1")
        
        # Half Orc ancestry bonus: +1 damage to melee weapons
        if ancestry == 'Half Orc' and 'M' in w['type']:
            dmg_to_use = self._add_damage_bonus(dmg_to_use, 1)
            dmg_bonus_parts.append("Half Orc +1")

        # Ranges
        rng = w['range']  # e.g., 'C', 'F', 'C/N'

        # Add mastery prefix if applicable
        mastery_prefix = "(Mastery) " if has_mastery else ""
        
        if 'Th' in w['properties'] and 'R' in w['type']:
            # Produce two entries: melee and ranged
            # Melee entry uses STR (or finesse), range C
            melee_mod = use_mod + attack_bonus_melee + mastery_atk_bonus
            melee_range = 'C'
            
            # Build melee to-hit breakdown
            melee_parts = [f"{base_ability} {use_mod:+d}"]
            if ancestry == 'Half Orc':
                melee_parts.append("Half Orc +1")
            if attack_bonus_melee > 1 or (attack_bonus_melee == 1 and ancestry != 'Half Orc'):
                # Additional talent bonuses beyond Half Orc
                talent_bonus = attack_bonus_melee - (1 if ancestry == 'Half Orc' else 0)
                if talent_bonus > 0:
                    melee_parts.append(f"talent +{talent_bonus}")
            if has_mastery:
                melee_parts.append("mastery +1")
            melee_breakdown = "To hit: " + ", ".join(melee_parts) + f" = {melee_mod:+d}"
            if dmg_bonus_parts:
                melee_breakdown += "\nDamage: " + ", ".join(dmg_bonus_parts)
            
            # Ranged uses DEX
            ranged_mod = dex_mod + attack_bonus_ranged + mastery_atk_bonus
            # Pick ranged part from range declaration
            ranged_range = 'N'
            if '/' in rng:
                parts = rng.split('/')
                if len(parts) == 2:
                    ranged_range = parts[1]
            
            # Build ranged to-hit breakdown
            char_class = self.character_data.get('ch_class', '')
            ranged_parts = [f"DEX {dex_mod:+d}"]
            if ancestry == 'Elf' and char_class not in ['Wizard', 'Priest']:
                ranged_parts.append("Elf +1")
            if attack_bonus_ranged > 1 or (attack_bonus_ranged == 1 and not (ancestry == 'Elf' and char_class not in ['Wizard', 'Priest'])):
                talent_bonus = attack_bonus_ranged - (1 if ancestry == 'Elf' and char_class not in ['Wizard', 'Priest'] else 0)
                if talent_bonus > 0:
                    ranged_parts.append(f"talent +{talent_bonus}")
            if has_mastery:
                ranged_parts.append("mastery +1")
            ranged_breakdown = "To hit: " + ", ".join(ranged_parts) + f" = {ranged_mod:+d}"
            # Ranged damage doesn't get Half Orc bonus
            if has_mastery:
                ranged_breakdown += "\nDamage: mastery +1"
            
            entries.append((f"{mastery_prefix}{weapon_name} (melee)", melee_mod, dmg_to_use, melee_range, melee_breakdown))
            entries.append((f"{mastery_prefix}{weapon_name} (ranged)", ranged_mod, dmg_to_use, ranged_range, ranged_breakdown))
        else:
            # Single entry
            is_melee = 'M' in w['type']
            char_class = self.character_data.get('ch_class', '')
            
            # Build to-hit breakdown
            to_hit_parts = []
            if is_melee:
                final_mod = use_mod + attack_bonus_melee + mastery_atk_bonus
                to_hit_parts.append(f"{base_ability} {use_mod:+d}")
                if ancestry == 'Half Orc':
                    to_hit_parts.append("Half Orc +1")
                # Additional talent bonuses beyond Half Orc
                if attack_bonus_melee > 1 or (attack_bonus_melee == 1 and ancestry != 'Half Orc'):
                    talent_bonus = attack_bonus_melee - (1 if ancestry == 'Half Orc' else 0)
                    if talent_bonus > 0:
                        to_hit_parts.append(f"talent +{talent_bonus}")
            else:
                final_mod = dex_mod + attack_bonus_ranged + mastery_atk_bonus
                to_hit_parts.append(f"DEX {dex_mod:+d}")
                # Check for Elf ancestry ranged bonus
                if ancestry == 'Elf' and char_class not in ['Wizard', 'Priest']:
                    to_hit_parts.append("Elf +1")
                # Additional talent bonuses beyond Elf
                if attack_bonus_ranged > 1 or (attack_bonus_ranged == 1 and not (ancestry == 'Elf' and char_class not in ['Wizard', 'Priest'])):
                    talent_bonus = attack_bonus_ranged - (1 if ancestry == 'Elf' and char_class not in ['Wizard', 'Priest'] else 0)
                    if talent_bonus > 0:
                        to_hit_parts.append(f"talent +{talent_bonus}")
            
            if has_mastery:
                to_hit_parts.append("mastery +1")
            
            breakdown = "To hit: " + ", ".join(to_hit_parts) + f" = {final_mod:+d}"
            if dmg_bonus_parts:
                breakdown += "\nDamage: " + ", ".join(dmg_bonus_parts)
            
            entries.append((f"{mastery_prefix}{weapon_name}", final_mod, dmg_to_use, rng if isinstance(rng, str) else '', breakdown))

        return entries
    
    def _add_damage_bonus(self, damage_str, bonus):
        """Add a bonus to a damage string (e.g., '1d4+1' -> '1d4+2')"""
        import re
        # Match pattern like "1d6", "1d8+1", "1d10", etc.
        match = re.match(r'(\d+d\d+)((?:[+-]\d+)?)', damage_str.strip())
        if match:
            dice_part = match.group(1)
            modifier_str = match.group(2) if match.group(2) else ''
            
            # Parse existing modifier
            if modifier_str:
                existing_mod = int(modifier_str)
            else:
                existing_mod = 0
            
            new_mod = existing_mod + bonus
            if new_mod > 0:
                return f"{dice_part}+{new_mod}"
            elif new_mod < 0:
                return f"{dice_part}{new_mod}"
            else:
                return dice_part
        return damage_str

    def _process_fighter_talent(self, roll):
        """Process fighter talent roll"""
        if roll == 2:
            # Additional weapon mastery for this fighter
            return "ADDITIONAL_MASTERY"
        if roll in [3, 4, 5, 6]:
            return ATTACK_BONUS_ALL
        if roll in [7, 8, 9]:
            selected = random.choice(['STR', 'DEX', 'CON'])
            old_score = self.character_data[f'{selected}_score']
            self._adjust_score(selected, 2)
            new_score = self.character_data[f'{selected}_score']
            stat_name = {'STR': 'Strength', 'DEX': 'Dexterity', 'CON': 'Constitution'}[selected]
            return f"{stat_name} increase of {old_score} to {new_score}."
        if roll in [10, 11]:
            self.character_data['ch_AC'] += 1
            return "+1 to AC"
        if roll == 12:
            return self._boost_odd_scores_or_stat('STR')
        return ""
    
    def _process_thief_talent(self, roll):
        """Process thief talent roll"""
        if roll == 2:
            return "Gain advantage on initiative rolls"
        if roll in [3, 4, 5]:
            backstab = self.character_data.get('backstab', 0) + 1
            self.character_data['backstab'] = backstab
            return f"your backstab deals +{backstab} dice of damage"
        if roll in [6, 7, 8, 9]:
            selected = random.choice(['STR', 'DEX', 'CHA'])
            old_score = self.character_data[f'{selected}_score']
            self._adjust_score(selected, 2)
            new_score = self.character_data[f'{selected}_score']
            stat_name = {'STR': 'Strength', 'DEX': 'Dexterity', 'CHA': 'Charisma'}[selected]
            return f"{stat_name} increase of {old_score} to {new_score}."
        if roll in [10, 11]:
            return ATTACK_BONUS_ALL
        if roll == 12:
            return self._boost_odd_scores_or_stat('DEX')
        return ""
    
    def _process_priest_talent(self, roll, spells):
        """Process priest talent roll"""
        if roll == 2:
            # Gain advantage on casting one spell you know
            if spells:
                spell = random.choice(spells)
                return f"Gain advantage when casting: {spell}"
            return ""
        if roll in [3, 4, 5, 6]:
            return ATTACK_BONUS_ALL
        if roll in [7, 8, 9]:
            current = self.character_data.get('priest_spell_mod', 0)
            self.character_data['priest_spell_mod'] = current + 1
            return "+1 to Spellcasting"
        if roll in [10, 11]:
            selected = random.choice(['STR', 'WIS'])
            old_score = self.character_data[f'{selected}_score']
            self._adjust_score(selected, 2)
            new_score = self.character_data[f'{selected}_score']
            stat_name = {'STR': 'Strength', 'WIS': 'Wisdom'}[selected]
            return f"{stat_name} increase of {old_score} to {new_score}."
        if roll == 12:
            return self._boost_odd_scores_or_stat('WIS')
        return ""
    
    def _process_wizard_talent(self, roll, ancestry):
        """Process wizard talent roll"""
        if roll == 2:
            # Add Magic jar to gear; consumes 1 slot
            gear = self.character_data.get('ch_gear_items', [])
            gear.append('Magic jar (1 slot)')
            self.character_data['ch_gear_items'] = gear
            return "magic jar"
        if roll in [3, 4, 5, 6, 7]:
            # 50%: +2 INT, 50%: +1 wizard spellcasting modifier
            if random.choice([True, False]):
                old_score = self.character_data['INT_score']
                self._adjust_score('INT', 2)
                new_score = self.character_data['INT_score']
                return f"Intelligence increase of {old_score} to {new_score}."
            else:
                current = self.character_data.get('wizard_spell_mod', 0)
                self.character_data['wizard_spell_mod'] = current + 1
                return "+1 to Spellcasting"
        if roll in [8, 9]:
            # Pick advantage spell from the wizard's initial spells
            initial_spells = self.character_data.get('_initial_spells', [])
            if initial_spells:
                spell = random.choice(initial_spells)
                if spell == "Magic missile":
                    # Reroll if we land on Magic missile
                    return self._process_wizard_talent(roll_2d6(), ancestry)
            else:
                # Fallback if no initial spells (shouldn't happen)
                spell = random.choice(WIZARD_SPELLS)
                if spell == "Magic missile":
                    return self._process_wizard_talent(roll_2d6(), ancestry)
            
            return f"Gain advantage when casting: {spell}"
        if roll in [10, 11]:
            current_langs = self.character_data.get('ch_lang', '').split(', ')
            available = [lang for lang in WIZARD_D10_LANGUAGES if lang not in current_langs and lang != 'Reroll']
            if available:
                new_lang = random.choice(available)
                current_langs.append(new_lang)
                self.character_data['ch_lang'] = ", ".join(current_langs)
                return f"new language: {new_lang}"
        if roll == 12:
            return self._boost_odd_scores_or_stat('INT')
        return ""

    def _adjust_score(self, abbr, amount):
        self.character_data[f'{abbr}_score'] += amount
        self.character_data[f'{abbr}_mod'] = get_ability_modifier(self.character_data[f'{abbr}_score'])

    def _boost_odd_scores_or_stat(self, primary_stat):
        odd_scores = [abbr for abbr in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
                     if self.character_data[f'{abbr}_score'] % 2 == 1]
        stat_names = {'STR': 'Strength', 'DEX': 'Dexterity', 'CON': 'Constitution', 
                      'INT': 'Intelligence', 'WIS': 'Wisdom', 'CHA': 'Charisma'}
        if len(odd_scores) >= 2:
            selected = random.sample(odd_scores, 2)
            increases = []
            for abbr in selected:
                old_score = self.character_data[f'{abbr}_score']
                self._adjust_score(abbr, 1)
                new_score = self.character_data[f'{abbr}_score']
                increases.append(f"{stat_names[abbr]} increase of {old_score} to {new_score}")
            return ", ".join(increases) + "."
        old_score = self.character_data[f'{primary_stat}_score']
        self._adjust_score(primary_stat, 2)
        new_score = self.character_data[f'{primary_stat}_score']
        return f"{stat_names[primary_stat]} increase of {old_score} to {new_score}."


class CharacterGeneratorApp:
    """Main application window with buttons and character sheet"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ShadowDark Character Generator")
        self.root.configure(bg='#F5F5DC')
        self.sound_enabled = False
        
        # Create medieval font for buttons (same as CharacterSheet uses)
        self.medieval_button_font = self._get_medieval_font(13, bold=True)  # 11 * 1.2
        
        # Store current character builder for callbacks
        self.builder = None
        self.current_character = None
        self.shop_window = None  # Store reference to shop window
        
        # Create character sheet with callbacks
        self.character_sheet = CharacterSheet(root, 
                                             on_equipment_changed=self._on_equipment_toggled,
                                             on_info_changed=self._on_info_updated)
        self.character_sheet.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create button frame
        button_frame = tk.Frame(root, bg='#F5F5DC')
        button_frame.pack(pady=10)
        
        # Roll button
        self.roll_button = tk.Button(button_frame, text="Roll a Character", 
                                     font=self.medieval_button_font,
                                     bg='#8B7355', fg='white', 
                                     activebackground='#6B5B3D',
                                     command=self.roll_character,
                                     width=20, height=1)
        self.roll_button.pack(side=tk.LEFT, padx=5)
        
        # Worthy button (Phase 2)
        self.worthy_button = tk.Button(button_frame, text="They look worthy.", 
                                     font=self.medieval_button_font,
                                     bg='#CCCCCC', fg='white',
                                     activebackground='#6B5B3D',
                                     command=self.finalize_character,
                                     state=tk.DISABLED,
                                     width=20, height=1)
        self.worthy_button.pack(side=tk.LEFT, padx=5)
        
        # Quest button
        self.quest_button = tk.Button(button_frame, text="Thy quest begins!", 
                                     font=self.medieval_button_font,
                                     bg='#CCCCCC', fg='white',
                                     activebackground='#6B5B3D',
                                     command=self.take_character,
                                     state=tk.DISABLED,
                                     width=20, height=1)
        self.quest_button.pack(side=tk.LEFT, padx=5)
        
        # Initialize sound system
        self._init_sounds()
    
    def _get_medieval_font(self, size, bold=False):
        """Create a medieval font with fallback to Times New Roman"""
        import tkinter.font as tkfont
        try:
            return tkfont.Font(family='MedievalSD', size=size, weight='bold' if bold else 'normal')
        except:
            return tkfont.Font(family='Times New Roman', size=size, weight='bold' if bold else 'normal')
    
    def _init_sounds(self):
        """Initialize sound effects"""
        self.click_sound = None
        self.dice_sound = None
        self.dice_sounds = []
        
        try:
            import pygame as pg
            pg.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self._pygame = pg
            self.sound_enabled = True
            global SOUND_ENABLED
            SOUND_ENABLED = True
        except Exception:
            self.sound_enabled = False
            return
        
        # Generate simple click sound using pygame
        try:
            import array
            sample_rate = 22050
            duration = 0.1
            frequency = 800
            samples = int(sample_rate * duration)
            click_wave = array.array('h')
            for i in range(samples):
                sample = int(32767 * 0.3 * (1 - i / samples) * 
                           (1 if (i * frequency // sample_rate) % 2 == 0 else -1))
                click_wave.append(sample)
                click_wave.append(sample)  # Stereo
            self.click_sound = self._pygame.sndarray.make_sound(click_wave)
        except Exception:
            # Fallback: will use system beep
            pass
        
        # Generate dice rolling sound (multiple clicks)
        try:
            import array
            sample_rate = 22050
            duration = 0.05
            self.dice_sounds = []
            for i in range(5):
                frequency = 400 + random.randint(-50, 50)
                samples = int(sample_rate * duration)
                wave = array.array('h')
                for j in range(samples):
                    volume = 0.2 - (i * 0.02)
                    sample = int(32767 * volume * 
                               (1 if (j * frequency // sample_rate) % 2 == 0 else -1))
                    wave.append(sample)
                    wave.append(sample)  # Stereo
                self.dice_sounds.append(self._pygame.sndarray.make_sound(wave))
        except Exception:
            self.dice_sounds = []
    
    def _play_click_sound(self):
        """Play button click sound"""
        if self.click_sound:
            self.click_sound.play()
        elif SOUND_ENABLED:
            try:
                import winsound
                winsound.Beep(800, 100)
            except:
                pass
    
    def _play_dice_sound(self):
        """Play dice rolling sound"""
        if self.dice_sounds:
            for sound in self.dice_sounds:
                sound.play()
                self.root.update()
                self._pygame.time.wait(50)
        elif self.sound_enabled:
            try:
                import winsound
                for _ in range(5):
                    winsound.Beep(400 + random.randint(-50, 50), 50)
                    self.root.update()
                    self._pygame.time.wait(50)
            except Exception:
                pass
    
    def roll_character(self):
        """Roll a new character"""
        # Disable and gray out button
        self.roll_button.config(state=tk.DISABLED, bg='#CCCCCC')
        self.root.update()
        
        # Play click sound
        self._play_click_sound()
        
        # Wait a moment
        self.root.after(100, self._continue_roll)
    
    def _continue_roll(self):
        """Continue character roll after button click"""
        # Play dice rolling sound
        self._play_dice_sound()
        
        # Close shop window if it exists (only the shop Toplevel, not the main window)
        if self.shop_window and hasattr(self.shop_window, 'main_window'):
            try:
                self.shop_window.main_window.destroy()
            except:
                pass
            self.shop_window = None
        
        # Clear previous character
        self.character_sheet.clear_fields()
        
        # Unlock dropdowns for new character selection
        self.character_sheet.unlock_dropdowns()
        
        # Generate new character (Phase 1: Base attributes)
        builder = CharacterBuilder()
        character_data = builder.generate_character()
        
        # Store for callbacks
        self.builder = builder
        self.current_character = character_data
        
        # Update sheet
        self.character_sheet.update_character_data(character_data)
        
        # Update buttons
        self.roll_button.config(text="Roll Another?", state=tk.NORMAL, bg='#8B7355')
        self.worthy_button.config(state=tk.NORMAL, bg='#8B7355')
        self.quest_button.config(state=tk.DISABLED, bg='#CCCCCC')

    def _on_info_updated(self, key, value):
        """Handle manual updates from character sheet dropdowns"""
        if not self.builder:
            return
            
        # Update builder's data
        updated_data = self.builder.update_from_selection(key, value)
        self.current_character = updated_data
        
        # Refresh character sheet with dependent changes (title, HP, AC, attacks)
        self.character_sheet.update_character_data(updated_data)

    def finalize_character(self):
        """Phase 2: Generate talents, spells and open shop"""
        if not self.builder or not self.current_character:
            return
            
        # Play click sound
        self._play_click_sound()
        
        # Generate talents and spells
        finalized_data = self.builder.finalize_character()
        self.current_character = finalized_data
        
        # Update sheet (talents and spells are now visible)
        self.character_sheet.update_character_data(finalized_data)
        
        # Lock dropdowns to prevent further changes
        self.character_sheet.lock_dropdowns()
        
        # Update title in case class changed
        self.builder._update_talent_display_with_masteries()
        
        # Open Shop UI for gear selection
        from shop_ui import ShopUI
        self.shop_window = ShopUI(self.root, finalized_data, self.builder, self.character_sheet)
        
        # Update buttons
        self.worthy_button.config(state=tk.DISABLED, bg='#CCCCCC')
        self.quest_button.config(state=tk.NORMAL, bg='#8B7355')
    
    def _on_equipment_toggled(self, instance_key, base_item_name):
        """Handle equipment toggle from character sheet gear click"""
        if not self.builder or not self.current_character:
            return
        
        from data_tables import WEAPONS, ARMORS
        
        # Clean base item name (remove stackable count info if present)
        clean_item = base_item_name.strip()
        if ' x ' in clean_item:
            clean_item = clean_item.split(' x ')[0].strip()
        
        char_class = self.current_character.get('ch_class', 'Fighter')
        dex_mod = self.current_character.get('DEX_mod', 0)
        str_mod = self.current_character.get('STR_mod', 0)
        
        # Determine what type of equipment this is
        is_weapon = clean_item in WEAPONS
        is_armor = clean_item in ARMORS
        
        if is_weapon:
            # Handle weapon toggling - track by instance
            currently_equipped = self.current_character.get('equipped_weapon_instance') == instance_key
            
            if currently_equipped:
                # Unequip this weapon instance
                self.current_character['equipped_weapon_instance'] = None
                self.current_character['equipped_weapon'] = None  # Keep for compatibility
            else:
                # Equip this weapon instance
                weapon = WEAPONS[clean_item]
                is_2h = '2H' in weapon.get('properties', [])
                is_versatile = 'V' in weapon.get('properties', [])
                is_ranged = 'R' in weapon.get('type', '')
                
                # If equipping a 2H weapon, unequip shield (unless it's versatile)
                if is_2h and not is_versatile and self.current_character.get('equipped_shield_instance'):
                    self.current_character['equipped_shield_instance'] = None
                    self.current_character['equipped_shield'] = None
                
                # If equipping a ranged weapon, unequip any melee weapons
                if is_ranged:
                    # Unequip shield since ranged can't use shield
                    if self.current_character.get('equipped_shield_instance'):
                        self.current_character['equipped_shield_instance'] = None
                        self.current_character['equipped_shield'] = None
                
                # Set the new weapon instance as equipped
                self.current_character['equipped_weapon_instance'] = instance_key
                self.current_character['equipped_weapon'] = clean_item  # Keep for compatibility
        
        elif is_armor:
            # Handle armor/shield toggling - track by instance
            if clean_item == 'Shield':
                currently_equipped = self.current_character.get('equipped_shield_instance') == instance_key
                if currently_equipped:
                    self.current_character['equipped_shield_instance'] = None
                    self.current_character['equipped_shield'] = None
                else:
                    # Equip shield, unequip only true 2H weapons (not versatile)
                    weapon_instance = self.current_character.get('equipped_weapon_instance')
                    if weapon_instance:
                        # Extract base weapon name from instance key
                        weapon_name = weapon_instance.split('__instance_')[0] if '__instance_' in weapon_instance else weapon_instance
                        if weapon_name in WEAPONS:
                            props = WEAPONS[weapon_name].get('properties', [])
                            # Only unequip if it's 2H AND not versatile
                            if '2H' in props and 'V' not in props:
                                self.current_character['equipped_weapon_instance'] = None
                                self.current_character['equipped_weapon'] = None
                    self.current_character['equipped_shield_instance'] = instance_key
                    self.current_character['equipped_shield'] = clean_item
            else:
                # Regular armor - track by instance
                currently_equipped = self.current_character.get('equipped_armor_instance') == instance_key
                if currently_equipped:
                    self.current_character['equipped_armor_instance'] = None
                    self.current_character['equipped_armor'] = None
                else:
                    self.current_character['equipped_armor_instance'] = instance_key
                    self.current_character['equipped_armor'] = clean_item
        
        # Recalculate AC
        self.builder.character_data = self.current_character
        self.builder._calculate_ac()
        self.current_character['ch_AC'] = self.builder.character_data['ch_AC']
        self.current_character['ch_armor'] = self.builder.character_data.get('ch_armor', 'None')
        
        # Rebuild attacks using equipped weapon instance
        equipped_weapon_instance = self.current_character.get('equipped_weapon_instance')
        if equipped_weapon_instance:
            # Extract base weapon name from instance key
            weapon_name = equipped_weapon_instance.split('__instance_')[0] if '__instance_' in equipped_weapon_instance else equipped_weapon_instance
            if weapon_name in WEAPONS:
                attacks = self.builder._build_attacks(apply_talent_bonuses=True)
            else:
                attacks = []
        else:
            attacks = []
        self.current_character['ch_attacks'] = attacks
        
        # Refresh display
        self.character_sheet.update_character_data(self.current_character)
    
    def take_character(self):
        """Handle quest button click"""
        # Disable and gray out button
        self.quest_button.config(state=tk.DISABLED, bg='#CCCCCC')
        self.root.update()
        
        # Play click sound
        self._play_click_sound()
        
        # Re-enable after 1 second
        self.root.after(1000, lambda: self.quest_button.config(state=tk.NORMAL, bg='#8B7355'))


def main():
    """Main entry point"""
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode: generate character and print data
        seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
        if seed:
            random.seed(seed)
        builder = CharacterBuilder()
        char_data = builder.generate_character()
        print(f"Class: {char_data['ch_class']} / Ancestry: {char_data['ch_ancestry']}")
        print(f"HP: {char_data['ch_HP']} / AC: {char_data['ch_AC']} / Armor: {char_data.get('ch_armor', 'None')}")
        print(f"HP Breakdown: {char_data.get('hp_breakdown', 'N/A')}")
        print(f"AC Breakdown: {char_data.get('ac_breakdown', 'N/A')}")
        print(f"STR: {char_data['STR_score']} ({char_data['STR_mod']:+d})")
        print(f"DEX: {char_data['DEX_score']} ({char_data['DEX_mod']:+d})")
        print("Attacks:")
        for attack in char_data['ch_attacks']:
            if len(attack) == 5:
                weapon, to_hit, damage, range_str, breakdown = attack
                print(f"  {weapon}: {to_hit:+d} / {damage} / {range_str}")
                print(f"    Breakdown: {breakdown}")
            elif len(attack) == 4:
                weapon, to_hit, damage, range_str = attack
                print(f"  {weapon}: {to_hit:+d} / {damage} / {range_str}")
            else:
                print(f"  {attack}")
        langs = char_data.get('ch_lang', [])
        if isinstance(langs, str):
            print(f"Languages: {langs}")
        else:
            print(f"Languages: {', '.join(str(l) for l in langs)}")
        talent_text = char_data.get('ch_talent', '').strip()
        spell_text = char_data.get('ch_spell', '').strip()
        if talent_text or spell_text:
            print("Talents/Spells:")
            if talent_text:
                print(f"  Talents: {talent_text}")
            if spell_text:
                print(f"  Spells: {spell_text}")
    else:
        root = tk.Tk()
        app = CharacterGeneratorApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()
