from datetime import date, timedelta


FEEDING_RATIOS = {
    "玉米蛇": 0.15,
    "王蛇": 0.15,
    "球蟒": 0.12,
    "豹纹守宫": 0.10,
    "睫角守宫": 0.08,
    "鬃狮蜥": 0.05,
    "绿鬣蜥": 0.03,
    "龟类": 0.02,
}


def calculate_feeding_amount(species: str, weight: float) -> float:
    ratio = FEEDING_RATIOS.get(species, 0.10)
    return round(weight * ratio, 1)


def calculate_feeding_cycle(weight: float) -> int:
    if weight < 100:
        return 5
    if weight < 500:
        return 7
    return 14


def calculate_calcium_cycle(has_uvb: bool = False) -> int:
    return 14 if has_uvb else 7


def calculate_next_feeding_date(last_feeding_date: date | None, feeding_cycle: int) -> date | None:
    if not last_feeding_date:
        return None
    return last_feeding_date + timedelta(days=feeding_cycle)
