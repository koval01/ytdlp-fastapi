"""
Init module for middleware
"""

from functools import partial
from typing import Coroutine, Any

from . import process_time

process_time_middleware: partial[Coroutine[Any, Any, Any]] \
    = partial(process_time.process_time_middleware)
