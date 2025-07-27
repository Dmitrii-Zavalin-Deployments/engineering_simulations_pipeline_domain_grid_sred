# src/errors/exceptions.py
# ----------------------------------------------------------------------
# Centralized Exception Definitions for Geometry and Pipeline Modules
# ----------------------------------------------------------------------

class EmptyGeometryException(Exception):
    """Raised when a STEP file contains no solids or valid topological entities."""
    pass


class GeometryParseException(Exception):
    """Raised when the STEP parser encounters malformed or unresolvable structure."""
    pass


class ResolutionFallbackException(Exception):
    """Raised if resolution derivation fails across all fallback paths."""
    pass


class EnrichmentSkippedException(Exception):
    """Raised to indicate metadata enrichment has been intentionally bypassed."""
    pass



