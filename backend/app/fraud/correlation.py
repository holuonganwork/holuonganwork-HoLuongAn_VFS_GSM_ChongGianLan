"""Initial correlation: connected signals sharing trip/GPS evidence, within one batch.

Driver, device and promotion identities alone do not establish a common incident.
Time-window correlation and cross-batch merging belong to a later implementation.
"""

import hashlib
import json

from app.core.enums import SourceType
from app.fraud.contracts import AlertCandidate
from app.fraud.types import Signal

CORRELATION_VERSION = "source-overlap-v1"


def canonical_signals(signals: list[Signal]) -> list[dict]:
    return sorted(
        [signal.model_dump(mode="json") for signal in signals],
        key=lambda value: json.dumps(value, sort_keys=True),
    )


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def correlate_signals(driver_id: int, signals: list[Signal]) -> list[AlertCandidate]:
    groups: list[tuple[set[tuple[SourceType, int]], list[Signal]]] = []
    seen: set[str] = set()
    for signal in signals:
        signal_key = fingerprint(signal.model_dump(mode="json"))
        if signal_key in seen:
            continue
        seen.add(signal_key)
        refs = {(ref.source_type, ref.source_id) for ref in signal.sources}
        refs.add((signal.source_type, signal.source_id))
        incident_refs = {ref for ref in refs if ref[0] in {SourceType.TRIP, SourceType.GPS_EVENT}}
        connected = [group for group in groups if group[0] & incident_refs]
        members = [signal]
        for group in connected:
            incident_refs |= group[0]
            members.extend(group[1])
            groups.remove(group)
        groups.append((incident_refs, members))
    alerts = [
        AlertCandidate(
            driver_id=driver_id,
            correlation_key=fingerprint(
                {
                    "version": CORRELATION_VERSION,
                    "driver_id": driver_id,
                    "signals": canonical_signals(members),
                }
            ),
            signals=members,
        )
        for _, members in groups
    ]
    return sorted(alerts, key=lambda alert: alert.correlation_key)
