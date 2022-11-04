from __future__ import annotations
from typing import Optional
import string
import math


def get_primary_key(
    year: int, week: int, current_count: int, n_rows: int, n_cols: int
) -> Optional[str]:
    max_samples = n_rows * n_cols
    row_labels = string.ascii_uppercase
    if current_count >= max_samples:
        return None

    i_row = math.floor(current_count / n_cols)
    i_col = current_count % n_cols
    yy = year % 100
    return f"{yy:02d}_{week:02d}_{row_labels[i_row]}{i_col + 1}"
