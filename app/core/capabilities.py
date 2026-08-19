"""Shared contracts for AMIP environment capabilities."""

from dataclasses import asdict, dataclass
from enum import Enum


class CapabilityStatus(str, Enum):
    """User-facing readiness state for one AMIP capability."""

    READY = "READY"
    CONFIGURATION_REQUIRED = "CONFIGURATION_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True)
class CapabilityResult:
    """Safe result returned by readiness checks without exposing secrets."""

    key: str
    label: str
    status: CapabilityStatus
    message: str
    action: str | None = None
    operator_action: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload
