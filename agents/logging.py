import json
from pathlib import Path
from typing import Any

from .contracts import timestamp


class RunLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, event_type: str, **details: Any) -> None:
        record = {"timestamp": timestamp(), "event": event_type, **details}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
