"""Contains functions for loading and saving of settings and usefull enum types."""
import json
from pathlib import Path
from typing import Dict
from enum import Enum

def load_settings(file_path: str) -> Dict:
    """
    Loads the settings from a file.

    Args:
        file_path (str): Path to the JSON file with settings.
    Returns:
        Dict: Returns dictionary with loaded settings form settings.json file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_settings(settings: Dict) -> None:
    """Updates settings in the settings.json file."""
    settings_path = Path(__file__).parent.parent / "utils" / "settings.json"
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

class Day(Enum):
    """Enum class for days in a week."""
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    def __str__(self):
        string_days = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
        return string_days[self.value]

class ScreenState(Enum):
    """Enum class for posible states of the screen."""
    SCHEDULE_DRAWN = 0
    SCHEDULE_LIST_SHOWN = 1
