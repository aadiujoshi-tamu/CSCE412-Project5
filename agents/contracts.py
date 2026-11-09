from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AgentMessage:
    sequence: int
    timestamp: str
    sender: str
    recipient: str
    kind: str
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
