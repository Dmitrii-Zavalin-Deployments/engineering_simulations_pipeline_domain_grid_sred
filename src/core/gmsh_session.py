# src/core/gmsh_session.py

"""
gmsh_session.py

Encapsulated Gmsh lifecycle management module.

Usage:
    from src.core.gmsh_session import GmshSession

    with GmshSession():
        # Your Gmsh logic here
"""

import gmsh
import logging

logger = logging.getLogger(__name__)


class GmshSession:
    """Context-managed Gmsh lifecycle wrapper."""

    def __init__(self, auto_finalize: bool = True):
        """
        Initialize the wrapper.
        :param auto_finalize: Whether to automatically finalize at context exit.
        """
        self.auto_finalize = auto_finalize
        self._initialized_by_self = False

    def __enter__(self):
        if not gmsh.isInitialized():
            gmsh.initialize()
            self._initialized_by_self = True
            logger.debug("Gmsh initialized by GmshSession context manager.")
        else:
            logger.debug("Gmsh already initialized; using existing session.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._initialized_by_self and self.auto_finalize:
            try:
                gmsh.finalize()
                logger.debug("Gmsh finalized by GmshSession context manager.")
            except Exception as e:
                logger.warning(f"Error finalizing Gmsh: {e}")
        else:
            logger.debug("GmshSession did not finalize Gmsh (external session).")


def ensure_gmsh_active():
    """Helper to initialize Gmsh if not already active."""
    if not gmsh.isInitialized():
        gmsh.initialize()
        logger.info("Gmsh initialized by ensure_gmsh_active()")


def safe_finalize():
    """Helper to finalize Gmsh safely."""
    if gmsh.isInitialized():
        try:
            gmsh.finalize()
            logger.info("Gmsh finalized by safe_finalize()")
        except Exception as e:
            logger.warning(f"Gmsh finalization failed: {e}")
