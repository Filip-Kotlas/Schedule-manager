"""Tests for Lesson class."""
from datetime import time
from app.src.lesson import Lesson
from app.utils.utilities import Day

def test_get_hex_color():
    """Test get_hex_color function from Lesson class."""
    lesson1 = Lesson("", "", "", Day.MON, time(8, 0), time(9, 0), (0, 0, 0))
    lesson2 = Lesson("", "", "", Day.MON, time(8, 0), time(9, 0), (255, 255, 255))
    lesson3 = Lesson("", "", "", Day.MON, time(8, 0), time(9, 0), (160, 185, 12))

    assert lesson1.get_hex_color() == "#000000"
    assert lesson2.get_hex_color() == "#FFFFFF"
    assert lesson3.get_hex_color() == "#A0B90C"

def test_set_hex_color():
    """Test set_hex_color function from Lesson class."""
    lesson = Lesson("", "", "", Day.MON, time(8, 0), time(9, 0), (0, 0, 0))

    lesson.set_hex_color("#000000")
    assert lesson.color == (0, 0, 0)

    lesson.set_hex_color("#FFFFFF")
    assert lesson.color == (255, 255, 255)

    lesson.set_hex_color("#2DA0D4")
    assert lesson.color == (45, 160, 212)
