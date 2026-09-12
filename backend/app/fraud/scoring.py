from dataclasses import dataclass

from app.core.config import RuleConfig
from app.core.enums import FraudType
from app.fraud.types import Signal


@dataclass(frozen=True)
class RiskScore:
    total: int
    contributions: dict[str, int]
    primary_category: FraudType | None


def score_signals(signals: list[Signal], config: RuleConfig) -> RiskScore:
    categories = sorted({signal.fraud_type for signal in signals}, key=str)
    contributions = {category.value: config.weights[category] for category in categories}
    primary = max(categories, key=lambda category: config.weights[category]) if categories else None
    return RiskScore(min(100, sum(contributions.values())), contributions, primary)
