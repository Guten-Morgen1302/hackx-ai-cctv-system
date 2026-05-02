#!/usr/bin/env python
"""Quick test of app2.py imports"""
try:
    from app2 import app
    print("✓ app2.py imports successfully")
    print(f"✓ Flask app created: {app.name}")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
