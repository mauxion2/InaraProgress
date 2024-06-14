
def check_limit(tab: dict[str, dict[int, int]], data: str, min_tier: int = 5) -> int:
    tab_data = tab[data]
    if min_tier < 5:
        return tab_data.get(min_tier + 1)
    else:
        return tab_data.get(5)


def check_threshold(value: int, tab: dict[str, dict[int, int]], data: str, min_tier: int = 5) -> int:
    tab_data = tab[data]
    if min_tier < 5:
        return tab_data.get(min_tier + 1)
    else:
        if value < tab_data.get(5):
            for tier_poz in tab_data:
                threshold = tab_data.get(tier_poz)
                if value <= threshold:
                    z = threshold
                    return z
        else:
            return tab_data.get(5)


def check_tier(tab: dict[str, dict[int, int]], tab_v: dict[int, int]) -> int:
    if len(tab) == len(tab_v):
        min_value = 6
        licz = 0
        tmp = 0
        for x, obj in tab.items():
            if tab_v[licz] <= obj[5]:
                for y in obj:
                    if tab_v[licz] >= obj[y]:
                        tmp = y
                licz += 1
                if min_value > tmp:
                    min_value = tmp
        if min_value == 6:
            min_value = 5
        return min_value
    else:
        return -1
