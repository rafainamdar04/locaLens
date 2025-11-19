#!/usr/bin/env python3
"""Demo script for Warehouse-based Delivery & Navigation feature."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.delivery_navigator import get_delivery_navigation

def main():
    print("🚚 Warehouse-Based Delivery & Navigation Demo")
    print("=" * 60)

    # Example: Delivery to a residential area in Bangalore
    destination = {"lat": 12.9352, "lon": 77.6245}  # Koramangala, Bangalore

    print(f"Delivery destination: {destination}")
    print("(Example: Koramangala, Bangalore)")
    print()

    # Test different service types
    service_types = ["express", "standard", "bulk"]

    for service_type in service_types:
        print(f"📦 Service Type: {service_type.upper()}")
        print("-" * 30)

        result = get_delivery_navigation(destination, "car", service_type)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "available_services" in result:
                print(f"Available services: {result['available_services']}")
            print()
            continue

        warehouse = result.get('warehouse', {})
        routes = result.get('routes', [])
        scores = result.get('scores', {})

        # Warehouse Info
        print(f"🏭 Nearest Warehouse: {warehouse.get('name', 'Unknown')}")
        print(f"📍 Location: {warehouse.get('address', 'Unknown')}")
        print(f"📏 Distance: {warehouse.get('distance_km', 0)} km")
        print(f"🚛 Capacity: {warehouse.get('capacity', 'Unknown')}")
        print()

        # Route Info
        if routes:
            route = routes[0]
            print("🛣️  Route Details:")
            print(f"   Distance: {route.get('distance_km', 0)} km")
            print(f"   ETA: {route.get('duration_min', 0)} minutes")
            if route.get('traffic_delay_min', 0) > 0:
                print(f"   Traffic Delay: +{route['traffic_delay_min']} minutes")
            print()

        # Scores
        if scores:
            print("📊 Delivery Scores:")
            print(f"   Efficiency: {scores.get('delivery_efficiency', {}).get('score', 0)}%")
            print(f"   Navigation: {scores.get('navigation_ease', {}).get('score', 0)}%")
            print(f"   Traffic Safety: {scores.get('traffic_safety', {}).get('score', 0)}%")
            print()

        # Sample Instructions
        if routes and routes[0].get('instructions'):
            instructions = routes[0]['instructions'][:3]
            print("🧭 Sample Route Instructions:")
            for i, instr in enumerate(instructions, 1):
                print(f"   {i}. {instr}")
            print()

        print("=" * 60)

    print("💡 Key Benefits:")
    print("• Automatic warehouse selection based on proximity")
    print("• Service type matching (express/standard/bulk)")
    print("• Real delivery logistics from actual warehouse locations")
    print("• Optimized for e-commerce last-mile delivery")

if __name__ == "__main__":
    main()