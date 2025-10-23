#!/usr/bin/env python3
"""
Production WSGI entry point for MyMurid Kiosk
"""

from app import app

if __name__ == "__main__":
    app.run()
