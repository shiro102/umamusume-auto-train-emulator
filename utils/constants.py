MOOD_LIST = ["AWFUL", "BAD", "NORMAL", "GOOD", "GREAT", "UNKNOWN"]


def get_regions_for_mode():
    """Get the appropriate regions based on phone mode setting"""
    try:
        import json

        # Load config
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)

        USE_PHONE = config.get("usePhone", True)
        SCENARIO = config.get("scenario", 1)

        # Load constants
        with open("constants.json", "r", encoding="utf-8") as file:
            constants = json.load(file)

        scenario_constants = constants.get(f"scenario{SCENARIO}")
        desktop_constants = scenario_constants.get("desktop")
        phone_constants = scenario_constants.get("phone")

        if USE_PHONE:
            return phone_constants
        else:
            return desktop_constants

    except Exception:
        # Fallback to desktop regions
        return desktop_constants