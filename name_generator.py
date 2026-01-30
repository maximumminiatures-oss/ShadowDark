import random

COMMON_ADJECTIVES = [
    "Ancient", "Arcane", "Cursed", "Divine", "Enchanted", "Ethereal", "Forgotten",
    "Haunted", "Hidden", "Holy", "Lost", "Mystical", "Sacred", "Secret", "Silent"
]

FOREST_ADJECTIVES = [
    "Abyssal", "Ashen", "Astral", "Awakened", "Benevolent", "Blighted", "Blood", "Boundless",
    "Broken", "Burning", "Celestial", "Charred", "Clouded", "Crystal", "Dark", "Deep",
    "Dense", "Doomed", "Dreaming", "Emerald", "Eternal", "Evil", "Foul", "Found", "Frozen",
    "Fungal", "Ghostly", "Glimmering", "Glass", "Gloomy", "Golden", "High", "Hollow",
    "Impenetrable", "Infernal", "Infinite", "Iron", "Lightning", "Living", "Low", "Lush",
    "Malevolent", "Misty", "Moonlit", "Mossy", "Murky", "Mystic", "Noxious", "Obsidian",
    "Petrified", "Plagued", "Primal", "Radiant", "Rainy", "Rotting", "Savage", "Screaming",
    "Shadowy", "Shattered", "Shrouded", "Silver", "Singing", "Sleeping", "Snowy", "Starry",
    "Stone", "Stormy", "Sunless", "Thunderous", "Thorny", "Timeless", "Toxic", "Twilight",
    "Twisted", "Undying", "Untamed", "Venomous", "Verdant", "Vile", "Weeping", "Whispering",
    "Wicked", "Wild", "Windy", "Withered"
]

FOREST_SYNONYMS = [
    "Forest", "Woods", "Wood", "Woodland", "Grove", "Thicket", "Copse", "Jungle","Trees", "Growth","Wildwood"
    "Wilds", "Weald", "Wold", "Holt", "Bush", "Scrub", "Stand", "Reserve", "Wildlands", "Rainforest", 
    "Timberland", "Preserve", "Glade", "Arbor", "Timber", "Greenwood", "Wealds", "Cloudforest", 
]

DESERT_ADJECTIVES = [
    "Abandoned", "Abyssal", "Arid", "Ashen", "Barren", "Bleak", "Blazing", "Blessed",
    "Broken", "Burning", "Cracked", "Crimson", "Crimson", "Deadly", "Desolate", "Desolate",
    "Dreary", "Dune-Swept", "Endless", "Fiery", "Fissured", "Forbidden", "Forbidden",
    "Golden", "Harsh", "Hellish", "Infernal", "Lonely", "Magical", "Mirage", "Parched",
    "Perilous", "Quiet", "Ravaged", "Ruined", "Scorched", "Scorching", "Scarred",
    "Shattered", "Shimmering", "Spellbound", "Sunbaked", "Treacherous", "Vast",
    "Withered", "Windswept"
]

DESERT_SYNONYMS = [
    "Desert", "Wastes", "Waste", "Sands", "Dunes", "Wasteland", "Badlands", "Expanse",
    "Reaches", "Wilds", "Tundra", "Void", "Emptiness", "Dunes", "Erg", "Desolation", "Barrens", "Aridia", "Sere", "Draught", 
    "Dustlands", "Sunscorched", "Heatlands", "Drylands", "Sandsea", "Sandscape", "Sandfields", "Wastelands", "Plateau", "Mesa",
    "Butte", "Canyon", "Ravine", "Gorge", "Outback"
]

OCEAN_ADJECTIVES = [
    "Azure", "Bitter", "Blighted", "Boundless", "Calm", "Churning", "Cold", "Crystalline",
    "Dangerous", "Dark", "Deep", "Endless", "Eternal", "Foaming", "Fog-Laden", "Frozen",
    "Glittering", "Gloomy", "Hostile", "Icy", "Infinite", "Merciless", "Mist-Shrouded",
    "Moonlit", "Murky", "Mysterious", "Perilous", "Primordial", "Raging", "Roaring",
    "Savage", "Sapphire", "Serene", "Shadowed", "Shadowy", "Shimmering", "Starlit",
    "Storm-Wracked", "Stormy", "Sunlit", "Tempestuous", "Treacherous", "Tranquil",
    "Turbulent", "Untamed", "Vast", "Wild", "Twilight"
]

OCEAN_SYNONYMS = [
    "Ocean", "Sea", "Waters", "Waves", "Deeps", "Depths", "Expanse", "Gulf",
    "Strait", "Channel", "Current", "Tide", "Abyss", "Brine", "Salt", "Fathoms"
]

LAKE_ADJECTIVES = [
    "Azure", "Blue", "Calm", "Clear", "Cold", "Cool", "Crystal", "Dark", "Deep",
    "Dreaming", "Fresh", "Gentle", "Glittering", "Icy", "Mirror", "Peaceful",
    "Pristine", "Pure", "Quiet", "Refreshing", "Sapphire", "Serene", "Shimmering",
    "Silvery", "Sparkling", "Still", "Tranquil"
]

LAKE_SYNONYMS = [
    "Lake", "Mere", "Pool", "Pond", "Loch", "Tarn", "Lagoon", "Mere",
    "Waters", "Inland Sea", "Freshwater", "Basin", "Depression", "Reservoir", "Haven", "Refuge"
]

NOUNS = {
    "Agony": "Agony",
    "Air": "Air",
    "Angels": "Angel",
    "Arcane": "Arcane",
    "Ashes": "Ash",
    "Bandits": "Bandit",
    "Bears": "Bear",
    "Beasts": "Beast",
    "Bones": "Bone",
    "Centipedes": "Centipede",
    "Claws": "Claw",
    "Champions": "Champion",
    "Chaos": "Chaos",
    "Courage": "Courage",
    "Crows": "Crow",
    "Cyclops": "Cyclops",
    "Darkness": "Darkness",
    "Day": "Day",
    "Death": "Death",
    "Demons": "Demon",
    "Despair": "Despair",
    "Destiny": "Destiny",
    "Devils": "Devil",
    "Doom": "Doom",
    "Dragons": "Dragon",
    "Dreams": "Dream",
    "Druids": "Druid",
    "Dunes": "Dune",
    "Dwarves": "Dwarf",
    "Earth": "Earth",
    "Elves": "Elf",
    "Elms": "Elm",
    "Embers": "Ember",
    "Ennui": "Ennui",
    "Fae": "Fae",
    "Fate": "Fate",
    "Fear": "Fear",
    "Fire": "Fire",
    "Flames": "Flame",
    "Frosts": "Frost",
    "Ghosts": "Ghost",
    "Goblins": "Goblin",
    "Gods": "God",
    "Giants": "Giant",
    "Gladiators": "Gladiator",
    "Glory": "Glory",
    "Griffons": "Griffon",
    "Heroes": "Hero",
    "Honor": "Honor",
    "Hopes": "Hope",
    "Hydras": "Hydra",
    "Ices": "Ice",
    "Jackals": "Jackal",
    "Joy": "Joy",
    "Kings": "King",
    "Knights": "Knight",
    "Life": "Life",
    "Lights": "Light",
    "Lightning": "Lightning",
    "Loss": "Loss",
    "Magics": "Magic",
    "Memories": "Memory",
    "Moon": "Moon",
    "Monsters": "Monster",
    "Night": "Night",
    "Nightmares": "Nightmare",
    "Ninjas": "Ninja",
    "Oaks": "Oak",
    "Order": "Order",
    "Orcs": "Orc",
    "Owls": "Owl",
    "Pines": "Pine",
    "Princes": "Prince",
    "Princesses": "Princess",
    "Queens": "Queen",
    "Ravens": "Raven",
    "Robbers": "Robber",
    "Rocks": "Rock",
    "Roses": "Rose",
    "Sands": "Sand",
    "Scorpions": "Scorpion",
    "Serpents": "Serpent",
    "Shadows": "Shadow",
    "Silence": "Silence",
    "Skulls": "Skull",
    "Slimes": "Slime",
    "Sorrows": "Sorrow",
    "Spiders": "Spider",
    "Spirits": "Spirit",
    "Stags": "Stag",
    "Stars": "Star",
    "Stingbats": "Stingbat",
    "Stones": "Stone",
    "Storms": "Storm",
    "Sun": "Sun",
    "Thieves": "Thief",
    "Thorns": "Thorn",
    "Thunder": "Thunder",
    "Time": "Time",
    "Trolls": "Troll",
    "Undead": "Undead",
    "Valor": "Valor",
    "Villains": "Villain",
    "Vipers": "Viper",
    "Vultures": "Vulture",
    "Warriors": "Warrior",
    "Waters": "Water",
    "Whispers": "Whisper",
    "Witches": "Witch",
    "Wizards": "Wizard",
    "Willows": "Willow",
    "Winds": "Wind",
    "Wolves": "Wolf",
    "Wraiths": "Wraith",
    "Wrath": "Wrath",
}

PATTERNS = [
    "Adjective Synonym",
    "The Adjective Synonym",
    "Synonym of Noun",
    "The Synonym of Adjective Noun",
    "Noun-Synonym",
    "Adjective-Synonym",
]
PATTERN_WEIGHTS = [30, 20, 30, 10, 5, 5]


def _generate_place_name(adjectives, synonyms, common_adjectives):
    pattern = random.choices(PATTERNS, weights=PATTERN_WEIGHTS, k=1)[0]
    adjective_pool = random.choice([adjectives, common_adjectives])
    adj = random.choice(adjective_pool)
    syn = random.choice(synonyms)
    noun = random.choice(list(NOUNS.keys()))
    noun_singular = NOUNS[noun]

    if pattern == "Adjective Synonym":
        return f"{adj} {syn}"
    if pattern == "The Adjective Synonym":
        return f"The {adj} {syn}"
    if pattern == "Synonym of Noun":
        return f"{syn} of the {noun_singular}"
    if pattern == "The Synonym of Adjective Noun":
        return f"The {syn} of the {adj} {noun_singular}"
    if pattern == "Noun-Synonym":
        return f"{noun_singular}-{syn.lower()}"
    if pattern == "Adjective-Synonym":
        return f"{adj}-{syn.lower()}"

    return f"The {adj} {syn}"


def generate_forest_name():
    """Generates a random fantasy name for a forest."""
    return _generate_place_name(FOREST_ADJECTIVES, FOREST_SYNONYMS, COMMON_ADJECTIVES)

def generate_desert_name():
    """Generates a random fantasy name for a desert."""
    return _generate_place_name(DESERT_ADJECTIVES, DESERT_SYNONYMS, COMMON_ADJECTIVES)

def generate_ocean_name():
    """Generates a random fantasy name for an ocean."""
    return _generate_place_name(OCEAN_ADJECTIVES, OCEAN_SYNONYMS, COMMON_ADJECTIVES)

def generate_lake_name():
    """Generates a random fantasy name for a lake or inland sea."""
    return _generate_place_name(LAKE_ADJECTIVES, LAKE_SYNONYMS, COMMON_ADJECTIVES)


