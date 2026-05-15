from __future__ import annotations as _annotations

from copy import deepcopy

from .context import AirlineAgentContext

MOCK_ITINERARIES = {
    "disrupted": {
        "name": "Paris to New York to Austin",
        "passenger_name": "Morgan Lee",
        "confirmation_number": "IR-D204",
        "seat_number": "14C",
        "baggage_tag": "BG20488",
        "segments": [
            {
                "flight_number": "PA441",
                "origin": "Paris (CDG)",
                "destination": "New York (JFK)",
                "departure": "2024-12-09 14:10",
                "arrival": "2024-12-09 17:40",
                "status": "Delayed 5 hours due to weather, expected departure 19:55",
                "gate": "B18",
            },
            {
                "flight_number": "NY802",
                "origin": "New York (JFK)",
                "destination": "Austin (AUS)",
                "departure": "2024-12-09 19:10",
                "arrival": "2024-12-09 22:35",
                "status": "Connection missed because of first leg delay",
                "gate": "C7",
            },
        ],
        "rebook_options": [
            {
                "flight_number": "NY950",
                "origin": "New York (JFK)",
                "destination": "Austin (AUS)",
                "departure": "2024-12-10 09:45",
                "arrival": "2024-12-10 12:30",
                "seat": "2A (front row)",
                "note": "Partner flight secured with auto-reaccommodation for disrupted travelers",
            },
            {
                "flight_number": "NY982",
                "origin": "New York (JFK)",
                "destination": "Austin (AUS)",
                "departure": "2024-12-10 13:20",
                "arrival": "2024-12-10 16:05",
                "seat": "3C",
                "note": "Backup option if the morning flight is full",
            },
        ],
        "vouchers": {
            "hotel": "Overnight hotel covered up to $180 near JFK Terminal 5 partner hotel",
            "meal": "$60 meal credit for the delay",
            "ground": "$40 ground transport credit to the hotel",
        },
    },
    "on_time": {
        "name": "On-time commuter flight",
        "passenger_name": "Taylor Lee",
        "confirmation_number": "LL0EZ6",
        "seat_number": "23A",
        "baggage_tag": "BG55678",
        "segments": [
            {
                "flight_number": "FLT-123",
                "origin": "San Francisco (SFO)",
                "destination": "Los Angeles (LAX)",
                "departure": "2024-12-09 16:10",
                "arrival": "2024-12-09 17:35",
                "status": "On time and operating as scheduled",
                "gate": "A10",
            }
        ],
        "rebook_options": [],
        "vouchers": {},
    },
}

# Default scenario to load when no confirmation number is provided by the user.
# Swap to "on_time" to demo the happy-path flow instead of the disruption flow.
DEFAULT_SCENARIO = "disrupted"


def apply_itinerary_defaults(ctx: AirlineAgentContext, scenario_key: str | None = None) -> None:
    """Populate the context with a demo itinerary if missing.

    Uses DEFAULT_SCENARIO when no scenario_key is supplied.
    """
    if scenario_key is None:
        scenario_key = DEFAULT_SCENARIO

    if ctx.itinerary is None and scenario_key in MOCK_ITINERARIES:
        ctx.itinerary = deepcopy(MOCK_ITINERARIES[scenario_key])
