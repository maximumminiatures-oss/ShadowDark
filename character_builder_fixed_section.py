    def _regenerate_attacks(self):
        """Regenerate attacks after talents may have modified stats"""
        char_class = self.character_data['ch_class']
        ancestry = self.character_data['ch_ancestry']
        dex_mod = self.character_data['DEX_mod']
        str_mod = self.character_data['STR_mod']
        wis_mod = self.character_data['WIS_mod']

        attacks = []  # List of tuples: (weapon_name, to_hit_bonus, damage_str, range_str)

        # Check for talent bonuses to attacks
        attack_bonus_melee = 0
        attack_bonus_ranged = 0
        talent_text = self.character_data.get('ch_talent', '')
        if '+1 to melee or ranged attacks' in talent_text or '+1 to melee and ranged attacks' in talent_text:
            attack_bonus_melee = 1
            attack_bonus_ranged = 1

        # Ensure weapons data exists
        self._ensure_weapons_data()

        # Choose a default weapon again and rebuild entries
        weapon_name = self._choose_default_weapon(char_class, ancestry)
        weapon_attacks = self._weapon_to_attacks(weapon_name, str_mod + attack_bonus_melee, dex_mod + attack_bonus_ranged)
        attacks.extend(weapon_attacks)

        # Add backstab for thieves
        if char_class == 'Thief' and 'backstab' in self.character_data:
            backstab = self.character_data['backstab']
            # Modify the melee attack with backstab info
            for i, (weapon, to_hit, damage, rng) in enumerate(attacks):
                if 'shortsword' in weapon.lower():
                    attacks[i] = (weapon, to_hit, f"{damage} (backstab +{backstab}d6)", rng)

        # Add spell attack for priests
        if char_class == 'Priest':
            priest_spell_mod = self.character_data.get('priest_spell_mod', 0)
            spell_atk = wis_mod + priest_spell_mod
            attacks.append(('spell attack', spell_atk, '', ''))

        # Store attacks in structured format for display
        self.character_data['ch_attacks'] = attacks

