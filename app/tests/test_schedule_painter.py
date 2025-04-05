"""Tests for SchedulePainter class."""
from pathlib import Path
from datetime import time

from PIL import Image
import pytest

from app.utils import utilities
from app.src.lesson import Lesson
from app.src.schedule import Schedule
from app.gui.schedule_painter import SchedulePainter
from app.utils.utilities import Day

def test_change_schedule():
    """Test change_schedule function from SchedulePainter class."""
    painter = SchedulePainter()
    schedule = Schedule("Rozvrh")
    painter.change_schedule(schedule)
    assert painter.active_schedule == schedule

@pytest.fixture(params=["schedule_0.png", "schedule_01.png", "schedule_012.png"])
def load_test_image(request):
    """Loads an image from a file."""
    directory_path = Path(__file__).parent / "test_pictures"
    return (request.param, Image.open(directory_path / request.param))

def test_draw(load_test_image):
    """Test draw function from SchedulePainter class."""
    painter = SchedulePainter()
    directory_path = Path(__file__).parent
    painter.settings = utilities.load_settings(directory_path / "test_settings.json")
    painter.update_image()

    test_file_name, test_image = load_test_image
    schedule = Schedule("Rozvrh")
    if "1" in test_file_name:
        lesson1 = Lesson("Matematika",
                         "T-105",
                         "Novák",
                         Day.MON,
                         time(12, 0),
                         time(16, 30),
                         (255, 255, 0))
        schedule.add_lesson(lesson1)
    if "2" in test_file_name:
        lesson2 = Lesson("Čeština",
                         "T-205",
                         "Petrtýl",
                         Day.THU,
                         time(9, 45),
                         time(12, 30),
                         (0, 0, 255))
        schedule.add_lesson(lesson2)

    painter.change_schedule(schedule)
    painter.draw()
    assert test_image.size == painter.image.size
    assert list(painter.image.getdata()) == list(test_image.getdata())
