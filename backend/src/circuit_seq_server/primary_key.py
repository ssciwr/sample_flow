from typing import Optional
import math

def get_primary_key(week: int, count: int) -> Optional[str]:
    n_rows = 8
    n_cols = 12
    max_samples = n_rows * n_cols
    row_labels = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
    ]
    if count >= max_samples:
        return None

    i_row = math.floor(count / n_cols)
    i_col = count % n_cols
    return f"{week}_{row_labels[i_row]}{i_col + 1}"
