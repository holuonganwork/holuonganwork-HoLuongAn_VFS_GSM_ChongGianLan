"""Replaceable detection and assessment boundaries; only rules are implemented today."""

from typing import Protocol

from app.core.config import RuleConfig
from app.fraud import device_detector, gps_detector, promotion_detector, repeated_trip_detector
from app.fraud.contracts import AlertCandidate, Assessment
from app.fraud.scoring import score_signals
from app.fraud.types import DriverObservation, Signal


class Detector(Protocol):
    def detect(self, observation: DriverObservation, config: RuleConfig) -> list[Signal]: ...


class RiskAssessor(Protocol):
    def assess(self, alert: AlertCandidate, config: RuleConfig) -> Assessment: ...


class RuleDetectorAdapter:
    def detect(self, observation: DriverObservation, config: RuleConfig) -> list[Signal]:
        detectors = (
            gps_detector.detect,
            repeated_trip_detector.detect,
            device_detector.detect,
            promotion_detector.detect,
        )
        return [signal for detector in detectors for signal in detector(observation, config)]


class RuleRiskAssessor:
    def assess(self, alert: AlertCandidate, config: RuleConfig) -> Assessment:
        # Category weights are not calibrated probabilities or prediction confidence.
        return Assessment(
            risk_score=score_signals(alert.signals, config).total,
            model_version=f"rules:{config.version}",
        )
