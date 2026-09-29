"""Hypothesis profiles: HYPOTHESIS_PROFILE=dev|full (D34)."""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "dev",
    max_examples=100,
    deadline=None,
    suppress_health_check=(HealthCheck.too_slow,),
)
settings.register_profile(
    "full",
    max_examples=1000,
    deadline=None,
    suppress_health_check=(HealthCheck.too_slow,),
)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "dev"))
