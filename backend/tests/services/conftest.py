"""
Conftest for services tests.

Minimal configuration for testing services in isolation.
"""

import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

