from __future__ import annotations
from typing import Optional
import datetime


def get_start_of_week(current_date: Optional[datetime.date] = None) -> datetime.date:
    if current_date is None:
        current_date = datetime.date.today()
    year, week, day = current_date.isocalendar()
    return datetime.date.fromisocalendar(year, week, 1)
