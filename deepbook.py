"""
Main entry point for the DeepBook application.

This script starts the Streamlit server and loads the app module.
"""

import streamlit as st

from app import run_app

if __name__ == "__main__":
    run_app()
