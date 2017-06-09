from opendatabo.cruzero import get_bus_line, get_all_bus_line_ids


def test_get_bus_line():
    line1 = get_bus_line(1)

    assert line1.line_id == 1
    assert line1.name
    assert line1.speed
    assert line1.distance
    assert line1.total_time


def test_get_all_bus_line_ids():
    line_ids = get_all_bus_line_ids()

    assert line_ids

