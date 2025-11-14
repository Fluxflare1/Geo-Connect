import math
from typing import Dict, List, Optional

from django.utils import timezone

from apps.catalog.models import Trip
from .models import PricingRule


def haversine_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Simple haversine formula in km. Good enough until we plug real map APIs.
    """
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def _matches_basic_filters(rule: PricingRule, trip: Trip, mode: Optional[str]) -> bool:
    if not rule.active:
        return False
    if rule.provider is not None and rule.provider_id != trip.provider_id:
        return False
    if rule.mode and mode and rule.mode != mode:
        return False
    return True


def _apply_distance_based(rule: PricingRule, distance_km: float) -> Dict:
    cfg = rule.config or {}
    base = cfg.get("base_fare_amount", 0)
    per_km = cfg.get("per_km_amount", 0)
    min_fare = cfg.get("min_fare_amount", 0)

    fare = base + int(distance_km * per_km)
    if fare < min_fare:
        fare = min_fare

    return {
        "amount": fare,
        "currency": rule.currency,
        "components": [
            {"type": "BASE_FARE", "amount": base},
            {"type": "DISTANCE_COMPONENT", "amount": fare - base},
        ],
    }


def _apply_surcharge(rule: PricingRule, base_amount: int) -> Dict:
    cfg = rule.config or {}
    surcharge_type = cfg.get("surcharge_type", "PERCENTAGE")
    value = cfg.get("value", 0)

    if surcharge_type == "FLAT":
        amount = int(value)
    else:
        # percentage
        amount = int(base_amount * (value / 100.0))

    return {
        "amount": amount,
        "currency": rule.currency,
        "type": "SURCHARGE",
    }


def calculate_fare_for_trip(
    trip: Trip,
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    mode: Optional[str] = None,
) -> Dict:
    """
    Main fare engine entry point for trip search.

    Returns:
    {
      "amount": 150000,
      "currency": "NGN",
      "components": [
        {"type": "BASE_FARE", "amount": ...},
        {"type": "DISTANCE_COMPONENT", "amount": ...},
        {"type": "SURCHARGE", "amount": ...}
      ]
    }
    """
    tenant = trip.tenant

    distance_km = haversine_distance_km(origin_lat, origin_lng, dest_lat, dest_lng)

    rules = (
        PricingRule.objects.filter(tenant=tenant, active=True)
        .order_by("priority")
        .select_related("provider")
    )

    base_pricing: Optional[Dict] = None
    surcharges: List[Dict] = []

    now = timezone.now().time()  # you can later use for time_window conditions

    for rule in rules:
        if not _matches_basic_filters(rule, trip, mode):
            continue

        if rule.type == "DISTANCE_BASED" and base_pricing is None:
            base_pricing = _apply_distance_based(rule, distance_km)

        elif rule.type == "SURCHARGE" and base_pricing is not None:
            sur = _apply_surcharge(rule, base_pricing["amount"])
            surcharges.append(sur)

    # Fallback: if no base rule, simple flat default
    if base_pricing is None:
        default_amount = int(distance_km * 1000)  # simple default
        base_pricing = {
            "amount": default_amount,
            "currency": "NGN",
            "components": [
                {"type": "BASE_FARE", "amount": default_amount},
            ],
        }

    total_amount = base_pricing["amount"]
    components = list(base_pricing["components"])

    for s in surcharges:
        total_amount += s["amount"]
        components.append({"type": s["type"], "amount": s["amount"]})

    return {
        "amount": total_amount,
        "currency": base_pricing["currency"],
        "components": components,
        "distance_km": distance_km,
    }
