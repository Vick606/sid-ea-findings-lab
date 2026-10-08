"""Load canonical data files from disk.

The schema module defines shapes; this module populates instances from
YAML. Kept separate so schema/ stays free of I/O.
"""

from pathlib import Path

import yaml

from schema.actors import ActorContext

DEFAULT_ACTORS_PATH = Path(__file__).resolve().parent.parent / "actors.yaml"


def load_actors(path: Path | None = None) -> dict[str, ActorContext]:
    """Load the canonical actor registry keyed by name."""
    source = path or DEFAULT_ACTORS_PATH
    raw = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    entries = raw.get("actors", {})
    return {
        name: ActorContext.model_validate(data)
        for name, data in entries.items()
    }
