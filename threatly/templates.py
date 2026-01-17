"""
Legacy compatibility shim.

Threatly templates have been refactored into the `threatly.templates` package
(directory). This file remains to avoid breaking old imports during transition.
"""

from threatly.templates import *  # re-export package symbols
