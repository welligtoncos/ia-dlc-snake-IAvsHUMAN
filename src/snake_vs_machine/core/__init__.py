"""Game core: state, setup, engine, queries, features."""

from snake_vs_machine.core.engine import is_terminal, outcome, step
from snake_vs_machine.core.features import (
    FEATURE_SCHEMA_VERSION,
    extract_features,
    feature_names,
)
from snake_vs_machine.core.queries import (
    body_cells,
    flood_fill_count,
    is_fatal,
    next_occupancy,
    reachable_cells,
)
from snake_vs_machine.core.rng import agent_generator
from snake_vs_machine.core.setup import SetupError, new_match
from snake_vs_machine.core.state import (
    Action,
    Cell,
    CoreConfig,
    DeathCause,
    Direction,
    EndReason,
    Outcome,
    Side,
    Snake,
    SnakeId,
    State,
    copy,
)

__all__ = [
    "Action",
    "Cell",
    "CoreConfig",
    "DeathCause",
    "Direction",
    "EndReason",
    "FEATURE_SCHEMA_VERSION",
    "Outcome",
    "SetupError",
    "Side",
    "Snake",
    "SnakeId",
    "State",
    "agent_generator",
    "body_cells",
    "copy",
    "extract_features",
    "feature_names",
    "flood_fill_count",
    "is_fatal",
    "is_terminal",
    "new_match",
    "next_occupancy",
    "outcome",
    "reachable_cells",
    "step",
]
