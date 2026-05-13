"""Tools available to airline customer service agents.

Each tool corresponds to an action an agent can take on behalf of a customer,
such as looking up flight status, changing seats, or processing refunds.
"""

from datetime import datetime, timedelta
from typing import Optional

from agents import RunContextWrapper, function_tool

from .context import AirlineAgentContext
from .demo_data import get_itinerary_for_flight, active_itinerary


# ---------------------------------------------------------------------------
# Flight Information Tools
# ---------------------------------------------------------------------------

@function_tool
def get_flight_status(
    context: RunContextWrapper[AirlineAgentContext],
    flight_number: str,
) -> str:
    """Look up the current status of a flight.

    Args:
        flight_number: The flight number to look up (e.g. "AA123").

    Returns:
        A human-readable string describing the flight status.
    """
    itinerary = get_itinerary_for_flight(flight_number)
    if itinerary is None:
        return f"No flight found with number {flight_number}."

    departure_time = itinerary.get("departure_time", "Unknown")
    arrival_time = itinerary.get("arrival_time", "Unknown")
    status = itinerary.get("status", "On Time")
    origin = itinerary.get("origin", "Unknown")
    destination = itinerary.get("destination", "Unknown")

    return (
        f"Flight {flight_number}: {origin} → {destination}\n"
        f"Departure: {departure_time}  |  Arrival: {arrival_time}\n"
        f"Status: {status}"
    )


@function_tool
def get_booking_details(
    context: RunContextWrapper[AirlineAgentContext],
) -> str:
    """Retrieve the current customer's booking details from context.

    Returns:
        A formatted summary of the customer's active itinerary.
    """
    ctx = context.context
    if ctx.itinerary is None:
        return "No active booking found for this customer."

    it = ctx.itinerary
    return (
        f"Booking reference: {it.get('confirmation_number', 'N/A')}\n"
        f"Flight: {it.get('flight_number', 'N/A')}\n"
        f"Route: {it.get('origin', '?')} → {it.get('destination', '?')}\n"
        f"Departure: {it.get('departure_time', 'N/A')}\n"
        f"Seat: {it.get('seat', 'Not assigned')}\n"
        f"Cabin class: {it.get('cabin_class', 'Economy')}"
    )


# ---------------------------------------------------------------------------
# Seat Service Tools
# ---------------------------------------------------------------------------

@function_tool
def change_seat(
    context: RunContextWrapper[AirlineAgentContext],
    new_seat: str,
) -> str:
    """Change the customer's seat assignment.

    Args:
        new_seat: The desired seat (e.g. "14A").

    Returns:
        Confirmation message or an error description.
    """
    ctx = context.context
    if ctx.itinerary is None:
        return "Unable to change seat: no active booking found."

    old_seat = ctx.itinerary.get("seat", "unassigned")
    ctx.itinerary["seat"] = new_seat
    return f"Seat successfully changed from {old_seat} to {new_seat}."


# ---------------------------------------------------------------------------
# Booking / Cancellation Tools
# ---------------------------------------------------------------------------

@function_tool
def cancel_booking(
    context: RunContextWrapper[AirlineAgentContext],
    confirmation_number: str,
) -> str:
    """Cancel a booking by confirmation number.

    Args:
        confirmation_number: The booking confirmation number to cancel.

    Returns:
        Confirmation of cancellation or an error message.
    """
    ctx = context.context
    if ctx.itinerary is None:
        return "No active booking found to cancel."

    if ctx.itinerary.get("confirmation_number") != confirmation_number:
        return (
            f"Confirmation number {confirmation_number} does not match "
            "the customer's active booking."
        )

    ctx.itinerary["status"] = "Cancelled"
    return (
        f"Booking {confirmation_number} has been successfully cancelled. "
        "A cancellation confirmation will be sent to the customer's email."
    )


# ---------------------------------------------------------------------------
# Refunds & Compensation Tools
# ---------------------------------------------------------------------------

@function_tool
def request_refund(
    context: RunContextWrapper[AirlineAgentContext],
    confirmation_number: str,
    reason: str,
) -> str:
    """Submit a refund request for a cancelled or disrupted booking.

    Args:
        confirmation_number: The booking reference number.
        reason: The reason for the refund request.

    Returns:
        A refund reference number and estimated processing time.
    """
    ctx = context.context
    if ctx.itinerary is None:
        return "No booking found to refund."

    if ctx.itinerary.get("confirmation_number") != confirmation_number:
        return "Confirmation number does not match the customer's booking."

    # Generate a deterministic-looking refund reference for the demo
    refund_ref = f"REF-{confirmation_number[-6:]}-{datetime.utcnow().strftime('%m%d')}"
    return (
        f"Refund request submitted successfully.\n"
        f"Refund reference: {refund_ref}\n"
        f"Reason on file: {reason}\n"
        f"Estimated processing time: 5–7 business days."
    )
