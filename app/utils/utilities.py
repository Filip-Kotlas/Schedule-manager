import json
from pathlib import Path
from typing import Dict

def load_settings() -> Dict:
    settings_path = Path(__file__).parent.parent / "utils" / "settings.json"
    # NOTE: Pozor, zde by mohl být problém, pokud bych měl komplikovanější strukturu adresáře.
    try:
        with open(settings_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Could not find the settings.json file.")
        return {}

def update_settings(settings: Dict) -> None:
    settings_path = Path(__file__).parent.parent / "utils" / "settings.json"
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=4)
