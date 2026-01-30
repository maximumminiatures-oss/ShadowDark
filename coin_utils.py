"""Shared coin utilities for cost parsing and arithmetic."""

def cost_to_cp(cost_str: str) -> int:
    parts = cost_str.strip().split()
    if len(parts) != 2:
        return 0
    amount, unit = int(parts[0]), parts[1].lower()
    if unit == 'gp':
        return amount * 100
    if unit == 'sp':
        return amount * 10
    if unit == 'cp':
        return amount
    return 0


def cp_to_gp_sp_cp(total_cp: int) -> tuple[int, int, int]:
    gp = total_cp // 100
    remainder = total_cp % 100
    sp = remainder // 10
    cp = remainder % 10
    return (gp, sp, cp)


def format_coins(gp: int, sp: int, cp: int) -> str:
    parts = []
    if gp > 0:
        parts.append(f"{gp} gp")
    if sp > 0:
        parts.append(f"{sp} sp")
    if cp > 0:
        parts.append(f"{cp} cp")
    if not parts:
        return "0 cp"
    return ", ".join(parts)


def subtract_cost(gp: int, sp: int, cp: int, cost_str: str) -> tuple[int, int, int] | None:
    total_cp = gp * 100 + sp * 10 + cp
    cost_cp = cost_to_cp(cost_str)
    if cost_cp > total_cp:
        return None
    new_total_cp = total_cp - cost_cp
    return cp_to_gp_sp_cp(new_total_cp)


def add_coins(gp: int, sp: int, cp: int, amount_cp: int) -> tuple[int, int, int]:
    total_cp = gp * 100 + sp * 10 + cp + amount_cp
    return cp_to_gp_sp_cp(total_cp)


def sell_item(cost_str: str) -> int:
    cost_cp = cost_to_cp(cost_str)
    return cost_cp // 2
