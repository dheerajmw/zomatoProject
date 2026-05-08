"""Phase 2 — user preferences validation (see doc/phase-wise-architecture.md)."""

from app.phase2.preferences import (
    ALLOWED_OPTIONAL_TAGS,
    PreferencesValidationError,
    validate_and_normalize_preferences,
)

__all__ = [
    "ALLOWED_OPTIONAL_TAGS",
    "PreferencesValidationError",
    "validate_and_normalize_preferences",
]
