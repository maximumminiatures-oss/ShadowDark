import math

# Test the stackable item display logic
stackable_items = {
    'Arrow': 20,
    'Crossbow bolts': 20,
    'Iron spike': 10,
    'Ration, per day': 3,
    'Coin': 100,
}

def show_display(item_name, count, slots_per):
    """Simulate the display logic"""
    lines = []
    
    # Add first line with item name and count
    lines.append(f"● {item_name} x {count}")
    
    # Add middle lines as empty
    num_slots = math.ceil(count / slots_per)
    for _ in range(num_slots - 2):
        lines.append("●")
    
    # Add last line with "these items are heavy" if overflow
    if num_slots > 1:
        lines.append(f"●   these {item_name.lower()} are heavy")
    
    return lines

# Test cases
print("21 arrows (slots_per=20):")
for line in show_display("arrow", 21, 20):
    print(line)
print()

print("61 arrows (slots_per=20):")
for line in show_display("arrow", 61, 20):
    print(line)
print()

print("6 rations (slots_per=3):")
for line in show_display("ration, per day", 6, 3):
    print(line)
print()

print("5 arrows (slots_per=20, no overflow):")
for line in show_display("arrow", 5, 20):
    print(line)
