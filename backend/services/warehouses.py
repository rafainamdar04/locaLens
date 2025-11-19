"""Warehouse locations for delivery optimization."""

# Major warehouse/depot locations in India
# Coordinates obtained from real locations or estimated for major cities
WAREHOUSES = [
    {
        "id": "mumbai_central",
        "name": "Mumbai Central Warehouse",
        "city": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.0760,
        "lon": 72.8777,
        "address": "Central Mumbai, Maharashtra",
        "capacity": "high",
        "services": ["express", "standard", "bulk"]
    },
    {
        "id": "mumbai_andheri",
        "name": "Andheri Logistics Hub",
        "city": "Mumbai",
        "state": "Maharashtra",
        "lat": 19.1136,
        "lon": 72.8697,
        "address": "Andheri East, Mumbai",
        "capacity": "high",
        "services": ["express", "standard"]
    },
    {
        "id": "delhi_connaught",
        "name": "Delhi Central Depot",
        "city": "Delhi",
        "state": "Delhi",
        "lat": 28.6304,
        "lon": 77.2177,
        "address": "Connaught Place, New Delhi",
        "capacity": "high",
        "services": ["express", "standard", "bulk"]
    },
    {
        "id": "delhi_gurgaon",
        "name": "Gurgaon Distribution Center",
        "city": "Gurgaon",
        "state": "Haryana",
        "lat": 28.4595,
        "lon": 77.0266,
        "address": "Sector 18, Gurgaon",
        "capacity": "medium",
        "services": ["express", "standard"]
    },
    {
        "id": "bangalore_whitefield",
        "name": "Bangalore Whitefield Hub",
        "city": "Bangalore",
        "state": "Karnataka",
        "lat": 12.9716,
        "lon": 77.5946,
        "address": "Whitefield, Bangalore",
        "capacity": "high",
        "services": ["express", "standard", "bulk"]
    },
    {
        "id": "bangalore_electronic_city",
        "name": "Electronic City Warehouse",
        "city": "Bangalore",
        "state": "Karnataka",
        "lat": 12.8399,
        "lon": 77.6770,
        "address": "Electronic City, Bangalore",
        "capacity": "medium",
        "services": ["standard", "bulk"]
    },
    {
        "id": "chennai_t_nagar",
        "name": "Chennai T. Nagar Depot",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 13.0827,
        "lon": 80.2707,
        "address": "T. Nagar, Chennai",
        "capacity": "high",
        "services": ["express", "standard"]
    },
    {
        "id": "chennai_maraimalai_nagar",
        "name": "Maraimalai Nagar Logistics Park",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "lat": 12.7777,
        "lon": 80.0222,
        "address": "Maraimalai Nagar, Chennai",
        "capacity": "high",
        "services": ["bulk", "standard"]
    },
    {
        "id": "kolkata_salt_lake",
        "name": "Kolkata Salt Lake Hub",
        "city": "Kolkata",
        "state": "West Bengal",
        "lat": 22.5726,
        "lon": 88.3639,
        "address": "Salt Lake City, Kolkata",
        "capacity": "medium",
        "services": ["standard", "express"]
    },
    {
        "id": "hyderabad_hitech_city",
        "name": "Hyderabad Hi-Tech City Warehouse",
        "city": "Hyderabad",
        "state": "Telangana",
        "lat": 17.3850,
        "lon": 78.4867,
        "address": "Hi-Tech City, Hyderabad",
        "capacity": "high",
        "services": ["express", "standard", "bulk"]
    },
    {
        "id": "pune_hinjewadi",
        "name": "Pune Hinjewadi Distribution Center",
        "city": "Pune",
        "state": "Maharashtra",
        "lat": 18.5913,
        "lon": 73.7389,
        "address": "Hinjewadi, Pune",
        "capacity": "medium",
        "services": ["standard", "express"]
    },
    {
        "id": "ahmedabad_sarkhej",
        "name": "Ahmedabad Sarkhej Logistics Park",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "lat": 22.9870,
        "lon": 72.5090,
        "address": "Sarkhej, Ahmedabad",
        "capacity": "medium",
        "services": ["standard", "bulk"]
    }
]

def find_nearest_warehouse(lat: float, lon: float, service_type: str = "standard") -> dict:
    """Find the nearest warehouse that supports the requested service type.

    Args:
        lat, lon: Delivery destination coordinates
        service_type: 'express', 'standard', or 'bulk'

    Returns:
        Nearest warehouse dict with distance info
    """
    from utils.helpers import haversine

    nearest = None
    min_distance = float('inf')

    for warehouse in WAREHOUSES:
        if service_type not in warehouse["services"]:
            continue

        distance = haversine(lat, lon, warehouse["lat"], warehouse["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest = warehouse.copy()
            nearest["distance_km"] = round(distance, 1)

    return nearest

def get_warehouses_by_city(city: str) -> list:
    """Get all warehouses in a specific city."""
    return [w for w in WAREHOUSES if w["city"].lower() == city.lower()]

def get_all_warehouses() -> list:
    """Get all warehouse locations."""
    return WAREHOUSES