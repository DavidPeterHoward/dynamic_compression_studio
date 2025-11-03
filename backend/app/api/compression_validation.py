"""
Compression Validation API module wrapper.

Imports and exposes the validation router from the v1 compression API.
"""

from app.api.v1.compression.validation import router

__all__ = ["router"]

