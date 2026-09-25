from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from westquant_core import Representation, RepresentationKind

@dataclass(frozen=True)
class BridgeStatus:
    framework: str
    status: str
    native_runtime_verified: bool
    capabilities: tuple[str, ...]
    notes: str=""


def representation(framework: str, kind: RepresentationKind, payload: dict[str,Any], *, representation_id: str, metadata: dict[str,Any]|None=None) -> Representation:
    return Representation(id=representation_id,kind=kind,framework=framework,payload=payload,metadata=metadata or {})
