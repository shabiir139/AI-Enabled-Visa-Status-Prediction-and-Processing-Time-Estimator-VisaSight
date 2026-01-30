"""
Quick Model Test - Single Command Testing
Run this to quickly test all models
"""

import requests
import json

API_BASE = "http://127.0.0.1:8000"


def quick_test():
    """Quick test of all models"""
    print("\n" + "="*60)
    print("QUICK MODEL TEST")
    print("="*60)
    
    # Get available models
    response = requests.get(f"{API_BASE}/api/models")
    models = response.json()
    
    print("\nAvailable Models:")
    for m in models:
        active = "[ACTIVE]" if m['is_active'] else ""
        print(f"  - {m['name']} {m['version']} {active}")
    
    # Test current model
    print("\nTesting Current Model:")
    pred_response = requests.post(
        f"{API_BASE}/api/predict/status",
        json={"case_id": "quick_test"}
    )
    pred = pred_response.json()
    
    print(f"  Status: {pred['predicted_status']}")
    print(f"  Days: {pred['estimated_days_remaining']}")
    print(f"  Model: {pred['model_version']}")
    
    # Active model info
    active_response = requests.get(f"{API_BASE}/api/models/active")
    active = active_response.json()
    
    print(f"\nActive Model: {active['model_type']} ({active['version']})")
    print("\n[OK] Quick test complete!")


if __name__ == "__main__":
    try:
        quick_test()
    except Exception as e:
        print(f"\n[ERROR] {e}")
