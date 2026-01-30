"""Centralized data tables."""

WEAPONS = {
    'Bastard Sword': { 'cost':'10 gp', 'type':'M',   'range':'C',   'damage':'1d8/1d10', 'properties':['V','2H'],  'slots':2, 'usable_by':['Fighter'] },
    'Club':          { 'cost':'5 cp',  'type':'M',   'range':'C',   'damage':'1d4',       'properties':[],          'slots':1, 'usable_by':['Fighter','Priest','Thief'] },
    'Crossbow':      { 'cost':'8 gp',  'type':'R',   'range':'F',   'damage':'1d6',       'properties':['2H','L'],  'slots':1, 'usable_by':['Fighter','Priest','Thief'] },
    'Dagger':        { 'cost':'1 gp',  'type':'M/R', 'range':'C/N', 'damage':'1d4',       'properties':['F','Th'],  'slots':1, 'usable_by':['Fighter','Priest','Thief','Wizard'] },
    'Greataxe':      { 'cost':'10 gp', 'type':'M',   'range':'C',   'damage':'1d8/1d10',  'properties':['V','2H'],  'slots':2, 'usable_by':['Fighter'] },
    'Greatsword':    { 'cost':'12 gp', 'type':'M',   'range':'C',   'damage':'1d12',      'properties':['2H'],      'slots':2, 'usable_by':['Fighter'] },
    'Javelin':       { 'cost':'5 sp',  'type':'M/R', 'range':'C/F', 'damage':'1d4',       'properties':['Th'],      'slots':1, 'usable_by':['Fighter'] },
    'Longbow':       { 'cost':'8 gp',  'type':'R',   'range':'F',   'damage':'1d8',       'properties':['2H'],      'slots':1, 'usable_by':['Fighter'] },
    'Longsword':     { 'cost':'9 gp',  'type':'M',   'range':'C',   'damage':'1d8',       'properties':[],          'slots':1, 'usable_by':['Fighter'] },
    'Mace':          { 'cost':'5 gp',  'type':'M',   'range':'C',   'damage':'1d6',       'properties':[],          'slots':1, 'usable_by':['Fighter','Priest'] },
    'Shortbow':      { 'cost':'6 gp',  'type':'R',   'range':'F',   'damage':'1d4',       'properties':['2H'],      'slots':1, 'usable_by':['Fighter','Thief'] },
    'Shortsword':    { 'cost':'7 gp',  'type':'M',   'range':'C',   'damage':'1d6',       'properties':[],          'slots':1, 'usable_by':['Fighter','Thief'] },
    'Spear':         { 'cost':'5 sp',  'type':'M/R', 'range':'C/N', 'damage':'1d6',       'properties':['Th'],      'slots':1, 'usable_by':['Fighter'] },
    'Staff':         { 'cost':'5 sp',  'type':'M',   'range':'C',   'damage':'1d4',       'properties':['2H'],      'slots':1, 'usable_by':['Fighter','Priest','Wizard'] },
    'Warhammer':     { 'cost':'10 gp', 'type':'M',   'range':'C',   'damage':'1d10',      'properties':['2H'],      'slots':1, 'usable_by':['Fighter','Priest'] },
}

ARMORS = {
    'Textile Armor': { 'cost':'10 gp', 'slots':1, 'ac_type':'base_plus_dex', 'base':11, 'properties':['disadvantage on stealth'] },
    'Leather Armor': { 'cost':'10 gp', 'slots':1, 'ac_type':'base_plus_dex', 'base':11, 'properties':[] },
    'Brigadine':     { 'cost':'35 gp', 'slots':1, 'ac_type':'base_plus_dex', 'base':12, 'properties':[] },
    'Hide':          { 'cost':'10 gp', 'slots':1, 'ac_type':'base_plus_dex', 'base':11, 'properties':['disadvantage on swim'] },
    'Scalemail':     { 'cost':'45 gp', 'slots':1, 'ac_type':'base_plus_dex', 'base':12, 'properties':['disadvantage on stealth','disadvantage on swim'] },
    'Chainmail':     { 'cost':'60 gp', 'slots':2, 'ac_type':'base_plus_dex', 'base':13, 'properties':['disadvantage on stealth','disadvantage on swim'] },
    'Lamellar':      { 'cost':'45 gp', 'slots':3, 'ac_type':'base_plus_dex', 'base':13, 'properties':['no swim','disadvantage on stealth'] },
    'Insect Chitin': { 'cost':'80 gp', 'slots':2, 'ac_type':'flat',          'base':14, 'properties':['-2 to CHA_mod'] },
    'Plate mail':    { 'cost':'130 gp','slots':3, 'ac_type':'flat',          'base':15, 'properties':['no swim','disadvantage on stealth'] },
    'Shield':        { 'cost':'10 gp', 'slots':1, 'ac_type':'shield',        'base':2,  'properties':['shield'] },
}

EQUIPMENT = {
    'Arrow': { 'cost': '5 cp', 'slots_per': 20, 'base_slots': 1 },
    'Backpack': { 'cost': '2 gp', 'first_free': True },
    'Caltrops': { 'cost': '5 sp', 'slots': 1 },
    'Crossbow bolts': { 'cost': '5 cp', 'slots_per': 20, 'base_slots': 1 },
    'Crowbar': { 'cost': '5 sp', 'slots': 1 },
    'Flask or bottle': { 'cost': '3 sp', 'slots': 1 },
    'Flint and steel': { 'cost': '5 sp', 'slots': 1 },
    'Grappling hook': { 'cost': '1 gp', 'slots': 1 },
    'Iron spike': { 'cost': '1 sp', 'slots_per': 10, 'base_slots': 1 },
    'Lantern': { 'cost': '5 gp', 'slots': 1 },
    'Mirror': { 'cost': '10 gp', 'slots': 1 },
    'Oil, flask': { 'cost': '5 sp', 'slots': 1 },
    'Pole': { 'cost': '5 sp', 'slots': 1 },
    'Ration, per day': { 'cost': '2 sp', 'slots_per': 3, 'base_slots': 1 },
    "Rope, 60'": { 'cost': '1 gp', 'slots': 1 },
    'Torch': { 'cost': '5 sp', 'slots': 1 },
}

# Name tables by ancestry
NAME_TABLES = {
    'Dwarf': ['Hilde', 'Torbin', 'Marga', 'Bruno', 'Karina', 'Naugrim', 'Brenna', 'Darvin', 
              'Elga', 'Alric', 'Isolde', 'Gendry', 'Bruga', 'Junnor', 'Vidrid', 'Torson', 
              'Brielle', 'Ulfgar', 'Sarna', 'Grimm'],
    'Elf': ['Eliara', 'Ryarn', 'Sariel', 'Tirolas', 'Galira', 'Varos', 'Daeniel', 'Axidor', 
            'Hiralia', 'Cyrwin', 'Lothiel', 'Zaphiel', 'Nayra', 'Ithior', 'Amriel', 'Elyon', 
            'Jirwyn', 'Natinel', 'Fiora', 'Ruhiel'],
    'Goblin': ['Iggs', 'Tark', 'Nix', 'Lenk', 'Roke', 'Fitz', 'Tila', 'Riggs', 'Prim', 'Zeb', 
               'Finn', 'Borg', 'Yark', 'Deeg', 'Nibs', 'Brak', 'Fink', 'Rizzo', 'Squib', 'Grix'],
    'Halfling': ['Willow', 'Benny', 'Annie', 'Tucker', 'Marie', 'Hobb', 'Cora', 'Gordie', 
                 'Rose', 'Ardo', 'Alma', 'Norbert', 'Jennie', 'Barvin', 'Tilly', 'Pike', 
                 'Lydia', 'Marlow', 'Astrid', 'Jasper'],
    'Half Orc': ['Vara', 'Gralk', 'Ranna', 'Korv', 'Zasha', 'Hrogar', 'Klara', 'Tragan', 
                 'Brolga', 'Drago', 'Yelena', 'Krull', 'Ulara', 'Tulk', 'Shiraal', 'Wulf', 
                 'Ivara', 'Hirok', 'Aja', 'Zoraan'],
    'Human': ['Zali', 'Bram', 'Clara', 'Nattias', 'Rina', 'Denton', 'Mirena', 'Aran', 
              'Morgan', 'Giralt', 'Tamra', 'Oscar', 'Ishana', 'Rogar', 'Jasmin', 'Tarin', 
              'Yuri', 'Malchor', 'Lienna', 'Godfrey']
}

# Background table
BACKGROUNDS = [
    "Urchin. {character_name} grew up in the merciless streets of a large city",
    "Outlaw. There's a price on {character_name}'s head, but {character_name} has allies",
    "Cult Initiate. {character_name} knows blasphemous secrets and rituals",
    "Thieves' Guildmember. {character_name} has connections, contacts, and debts",
    "Exile. {character_name}'s people cast {character_name} out for supposed crimes",
    "Orphan. An unusual guardian rescued and raised {character_name}",
    "Wizard's Apprentice. {character_name} has a knack and eye for magic",
    "Jeweler. {character_name} can easily appraise value and authenticity",
    "Herbalist. {character_name} knows plants, medicines, and poisons",
    "Barbarian. {character_name} left the horde, but it never quite left {character_name}",
    "Mercenary. {character_name} fought friend and foe alike for coin",
    "Sailor. Pirate, privateer, or merchant — the seas are {character_name}'s",
    "Acolyte. {character_name} is well trained in religious rites and doctrines",
    "Soldier. {character_name} served as a fighter in an organized army",
    "Ranger. The woods and wilds are {character_name}'s true home",
    "Scout. {character_name} survived on stealth, observation, and speed",
    "Minstrel. {character_name} has traveled far with {character_name}'s charm and talent",
    "Scholar. {character_name} knows much about ancient history and lore",
    "Noble. A famous name has opened many doors for {character_name}",
    "Chirurgeon. {character_name} knows anatomy, surgery, and first aid",
]

# Deity table
DEITIES = [
    "Saint Terragnis",
    "Saint Terragnis",
    "Madeera the Covenant",
    "Gede",
    "Ord",
    "Memnon",
    "Shune the Vile",
    "Ramlaat"
]

# Deity to alignment mapping
DEITY_ALIGNMENTS = {
    "Saint Terragnis": "Lawful",
    "Madeera the Covenant": "Lawful",
    "Gede": "Neutral",
    "Ord": "Neutral",
    "Memnon": "Chaotic",
    "Shune the Vile": "Chaotic",
    "Ramlaat": "Chaotic"
}

# Language tables
WIZARD_D4_LANGUAGES = ["Celestial", "Diabolic", "Draconic", "Primordial"]
WIZARD_D10_LANGUAGES = ["Dwarvish", "Elvish", "Giant", "Goblin", "Merran", "Orcish", 
                        "Reptilian", "Sylvan", "Thanian", "Reroll"]

# Spell tables
PRIEST_SPELLS = ["Light", "Cure Wounds", "Holy Weapon", "Protection from Evil", "Shield of Faith"]
WIZARD_SPELLS = ["Alarm", "Burning Hands", "Charm Person", "Detect Magic", "Feather Fall",
                 "Floating Disk", "Hold Portal", "Light", "Mage Armor", "Magic Missile",
                 "Protection from Evil", "Sleep"]

# Deity descriptions for tooltips
DEITY_DESCRIPTIONS = {
    "Saint Terragnis": "A legendary knight who is the patron of most lawful humans.\nShe ascended to godhood long ago and is the embodiment of righteousness and justice.",
    "Madeera the Covenant": "Madeera was the first manifestation of Law.\nShe is Memnon's twin.\nShe carries every law of reality, a dictate called the Covenant,\nwritten on her skin in precise symbols.",
    "Gede": "The god of feasts, mirth, and the wilds.\nGede is usually peaceful, but primal storms rage when her anger rises.\nMany elves and halflings worship her.",
    "Ord": "Ord the Unbending, the Wise, the Secret Keeper.\nHe is the god of magic, knowledge, secrets, and equilibrium.",
    "Memnon": "Memnon was the first manifestation of Chaos.\nHe is Madeera's twin, a red maned, leonine being.\nHis ultimate ambition is to rend the cosmic laws of the Covenant from his sister's skin.",
    "Shune the Vile": "Shune whispers arcane secrets to sorcerers and witches who call to her in the dark hours.\nShe schemes to displace Ord so she can control the vast flow of magic herself.",
    "Ramlaat": "Ramlaat is the Pillager, the Barbaric, the Horde.\nMany orcs worship him and live by the Blood Rite,\na prophecy that says only the strongest will survive a coming doom."
}

# Ancestry names for display
ANCESTRY_NAMES = {
    'Dwarf': 'Dwarven',
    'Elf': 'Elven',
    'Goblin': 'Goblin',
    'Halfling': 'Halfling',
    'Half-Orc': 'Orcish',
    'Human': 'Human'
}

# Alignment descriptions (templates with {ancestry} and {background} placeholders)
ALIGNMENT_DESCRIPTIONS = {
    'Chaotic': 'This {ancestry} {background} aligns with destruction, ambition, and wickedness.\n"Survival of the fittest."',
    'Lawful': 'This {ancestry} {background} believes in fairness, order, and virtue.\n"For the good of the whole."',
    'Neutral': 'This {ancestry} {background} finds balance between Law and Chaos.\nThey accept the cycle of growth and decline.\n"Nature must take its course."'
}
