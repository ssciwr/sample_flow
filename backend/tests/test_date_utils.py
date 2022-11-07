import datetime
from circuit_seq_server.date_utils import get_start_of_week


def test_get_start_of_week():
    assert get_start_of_week().weekday() == 0
    assert get_start_of_week().month == datetime.date.today().month
    assert get_start_of_week().year == datetime.date.today().year
    for d in range(1, 6):
        # first week of november
        current_date = datetime.date(2022, 11, d)
        start_of_week = get_start_of_week(current_date)
        assert start_of_week.weekday() == 0
        assert start_of_week.month == 10
        assert start_of_week.year == 2022
        year, week, day = start_of_week.isocalendar()
        assert year == 2022
        assert week == 44
        assert day == 1
    for d in range(7, 13):
        # second week of november
        current_date = datetime.date(2022, 11, d)
        start_of_week = get_start_of_week(current_date)
        assert start_of_week.weekday() == 0
        assert start_of_week.month == 11
        assert start_of_week.year == 2022
        year, week, day = start_of_week.isocalendar()
        assert year == 2022
        assert week == 45
        assert day == 1
