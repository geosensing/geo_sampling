"""
Test package for geo_sampling.

This module initializes the test package and sets up any required
configurations for testing.
"""

import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out
