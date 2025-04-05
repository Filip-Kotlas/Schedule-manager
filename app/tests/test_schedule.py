"""Test for Schedule class."""
from datetime import time
import os
import pickle
from pathlib import Path
import pytest
from app.src.schedule import Schedule
from app.src.lesson import Lesson
from app.utils.utilities import Day

def test_add_lesson():
    """Tests add_lesson function from Schedule class."""
    example_lesson = Lesson("Matematika",
                            "T-105",
                            "Novak",
                            Day.MON,
                            time(9, 0),
                            time(12, 0),
                            (165, 120, 13))
    schedule = Schedule("Rozvrh")
    schedule.add_lesson(example_lesson)
    assert schedule.lessons[0] == example_lesson

def test_edit_lesson():
    """Tests edit_lesson function from Schedule class."""
    schedule = Schedule("Rozvrh")
    i = 0
    while i < 10:
        schedule.add_lesson(Lesson())
        i += 1
    new_lesson = Lesson("Matematika",
                        "T-105",
                        "Novak",
                        Day.MON,
                        time(9, 0),
                        time(12, 0),
                        (165, 120, 13))

    schedule.edit_lesson(0, new_lesson)
    schedule.edit_lesson(8, new_lesson)
    schedule.edit_lesson(5, new_lesson)
    assert schedule.lessons[0] == new_lesson
    assert schedule.lessons[8] == new_lesson
    assert schedule.lessons[5] == new_lesson

def test_remove_lesson():
    """Tests remove_lesson function from Schedule class."""
    schedule = Schedule("Rozvrh")
    i = 0
    while i < 10:
        schedule.add_lesson(Lesson())
        i += 1

    i = 9
    while i >= 0:
        schedule.remove_lesson(i)
        assert len(schedule.lessons) == i
        i -= 1

@pytest.mark.parametrize('index', (0, 1))
def test_save_and_load_to_json_file(index):
    """Tests save_to_json_file function from Schedule class."""
    schedule = Schedule("Rozvrh")
    lesson1 = Lesson("Čeština",
                        "B-203",
                        "Zavařil",
                        Day.TUE,
                        time(14, 0),
                        time(14, 45),
                        (255, 0, 0))
    lesson2 = Lesson("Čeština",
                        "B-203",
                        "Zavařil",
                        Day.TUE,
                        time(14, 0),
                        time(14, 45),
                        (255, 0, 0))

    schedule.add_lesson(lesson1)
    schedule.add_lesson(lesson2)
    file_path = Path(__file__).parent / "rozvrh.json"
    schedule.save_to_txt_file(file_path)

    assert os.path.exists(file_path)

    with open(file_path, 'rb') as file:
        loaded_schedule = pickle.load(file)

    assert loaded_schedule.name == schedule.name
    assert loaded_schedule.lessons[index].name == schedule.lessons[index].name
    assert loaded_schedule.lessons[index].place == schedule.lessons[index].place
    assert loaded_schedule.lessons[index].instructor == schedule.lessons[index].instructor
    assert loaded_schedule.lessons[index].day == schedule.lessons[index].day
    assert loaded_schedule.lessons[index].start_time == schedule.lessons[index].start_time
    assert loaded_schedule.lessons[index].end_time == schedule.lessons[index].end_time
    assert loaded_schedule.lessons[index].color == schedule.lessons[index].color

def test_rename():
    """Tests save_to_json_file function from Schedule class."""
    schedule = Schedule("Rozvrh")
    schedule.rename("New name")
    assert schedule.name == "New name"
