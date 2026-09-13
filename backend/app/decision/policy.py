from dataclasses import dataclass

from app.core.config import DecisionPolicyConfig
from app.core.enums import DecisionOutcome, Impact
from app.fraud.contracts import Assessment


@dataclass(frozen=True)
class PolicyDecision:
    outcome: DecisionOutcome
    reason: str


def evaluate(assessment: Assessment, policy: DecisionPolicyConfig) -> PolicyDecision:
    """Example routing policy. Automatic outcomes require independently supplied estimates."""
    review = DecisionOutcome.HUMAN_REVIEW
    if assessment.impact != Impact.LOW:
        return PolicyDecision(review, "Impact is high, critical or unknown")
    if assessment.conflicting_signals:
        return PolicyDecision(review, "Conflicting detection signals")
    if assessment.fraud_probability is None or assessment.confidence is None:
        return PolicyDecision(review, "Probability or confidence is unavailable")
    if assessment.confidence < policy.min_confidence:
        return PolicyDecision(review, "Prediction confidence is below policy threshold")
    if (
        assessment.fraud_probability <= policy.auto_clear_max_probability
        and assessment.risk_score <= policy.auto_clear_max_risk
    ):
        return PolicyDecision(DecisionOutcome.AUTO_CLEAR, "Low probability and low risk")
    if assessment.fraud_probability >= policy.auto_fraud_min_probability:
        return PolicyDecision(DecisionOutcome.AUTO_FRAUD, "High probability with low impact")
    return PolicyDecision(review, "Prediction falls between automatic decision thresholds")
