import json
from pathlib import Path
from typing import Dict
from enum import Enum

def load_settings() -> Dict:
    settings_path = Path(__file__).parent.parent / "utils" / "settings.json"
    # NOTE: Pozor, zde by mohl být problém, pokud bych měl komplikovanější strukturu adresáře.
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Could not find the settings.json file.")
        return {}

def update_settings(settings: Dict) -> None:
    settings_path = Path(__file__).parent.parent / "utils" / "settings.json"
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

class Day(Enum):
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
    SCHEDULE_DRAWN = 0
    SCHEDULE_LIST_SHOWN = 1
