# src/logger_utils.py

"""
📡 Logger Utils

Lightweight logging helpers for standardized CLI output.
Use to enhance visibility and checkpoint traceability across
FreeCAD pipelines, validation modules, and utility layers.
"""

import datetime
import sys

def log_checkpoint(msg: str, *, emoji="🪵", newline=True) -> None:
    """
    Print a standardized checkpoint log.

    Args:
        msg (str): Message content to display.
        emoji (str, optional): Emoji prefix for log tag. Default: '🪵'.
        newline (bool, optional): Whether to append a newline after. Default: True.
    """
    ts = datetime.datetime.utcnow().strftime("%H:%M:%S")
    print(f"{emoji} [{ts}] {msg}", end="\n" if newline else "")


def log_error(msg: str, *, fatal=False) -> None:
    """
    Print a standardized error message.

    Args:
        msg (str): Error description.
        fatal (bool, optional): Whether to terminate execution. Default: False.
    """
    log_checkpoint(f"❌ ERROR: {msg}", emoji="💥")
    if fatal:
        sys.exit(1)


def log_success(msg: str) -> None:
    """
    Print a standardized success message.

    Args:
        msg (str): Success description.
    """
    log_checkpoint(f"✅ {msg}", emoji="🌟")


def log_info(msg: str) -> None:
    """
    Print a neutral informational message.

    Args:
        msg (str): Info message.
    """
    log_checkpoint(msg, emoji="🧾")


def log_warning(msg: str) -> None:
    """
    Print a standardized warning message.

    Args:
        msg (str): Warning message.
    """
    log_checkpoint(f"⚠️ WARNING: {msg}", emoji="⚠️")

def log_debug(msg: str) -> None:
    """
    Print a standardized debug message.

    Args:
        msg (str): Debug message.
    """
    log_checkpoint(f"🐞 DEBUG: {msg}", emoji="🐞")


