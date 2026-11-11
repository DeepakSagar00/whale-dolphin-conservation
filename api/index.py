"""Serverless entry point for the Whale & Dolphin Conservation API.

Vercel runs this file as a Python function; it simply re-exports the
FastAPI application from the bundled package.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from app.main import app  # noqa: E402,F401

__all__ = ['app']
