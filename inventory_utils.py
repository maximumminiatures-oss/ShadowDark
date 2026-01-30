"""Inventory helpers for stackable items and coin slot math."""

import math
from typing import List, Tuple

COIN_FREE = 100
COIN_PER_SLOT = 100


def coin_count(gp: int, sp: int, cp: int) -> int:
    return max(0, gp) + max(0, sp) + max(0, cp)


def coin_slots(total_coins: int, free: int = COIN_FREE, per_slot: int = COIN_PER_SLOT) -> int:
    if total_coins <= free:
        return 0
    return math.ceil((total_coins - free) / per_slot)


def stack_slots(count: int, slots_per: int, free: int = 0) -> int:
    if count <= free:
        return 0
    return math.ceil((count - free) / slots_per)


def parse_stack_count(item_str: str) -> Tuple[str, int]:
    base = item_str.strip().replace('  ', '').replace(' are heavy!', '')
    if ' x ' in base:
        name, rest = base.split(' x ', 1)
        try:
            return name.strip(), int(rest.strip())
        except ValueError:
            return name.strip(), 1
    return base, 1


def add_stackable_item(gear_list: List[str], item_name: str, slots_per: int) -> List[str]:
    existing_index = None
    existing_count = 0
    for idx, gear_item in enumerate(gear_list):
        if gear_item.startswith(item_name):
            existing_index = idx
            if ' x ' in gear_item:
                try:
                    cnt = gear_item.split(' x ')[1].strip().replace(' are heavy!', '')
                    existing_count = int(cnt)
                except ValueError:
                    existing_count = 1
            else:
                existing_count = 1
            break

    new_count = existing_count + 1
    if existing_index is not None:
        if new_count <= slots_per:
            gear_list[existing_index] = f"{item_name} x {new_count}"
        else:
            if existing_count == slots_per:
                gear_list[existing_index] = f"  {item_name} x {existing_count} are heavy!"
            gear_list.append(f"{item_name} x 1")
    else:
        gear_list.append(f"{item_name} x 1")
    return gear_list
