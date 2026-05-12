import json

from openai import OpenAI
from sqlalchemy.orm import Session

from core.config import get_settings
from models import Conversation, FailureCluster, OperatingProcedure, Recommendation, RecommendationPriority


def _priority(op: OperatingProcedure) -> RecommendationPriority:
    if op.health_score < 60 or op.escalation_rate > 0.4:
        return RecommendationPriority.high
    if op.health_score <= 75:
        return RecommendationPriority.medium
    return RecommendationPriority.low


def _mock_text(op: OperatingProcedure, cluster: FailureCluster | None) -> str:
    gap = cluster.gap_description if cluster else "the lowest-performing customer paths for this operating procedure"
    return (
        "Mock recommendation - add OPENAI_API_KEY for AI-generated suggestions. "
        f"For {op.name}, add an explicit procedure branch for {gap} Include intent examples, a confirmation response, clear limits, and a specialist escalation path when the customer rejects the standard flow."
    )


def generate_recommendation(op_id: str, cluster_id: int | None, db: Session) -> Recommendation:
    op = db.get(OperatingProcedure, op_id)
    if op is None:
        raise ValueError(f"Unknown operating procedure: {op_id}")
    cluster = db.get(FailureCluster, cluster_id) if cluster_id else None
    text = _mock_text(op, cluster)
    settings = get_settings()
    api_key = settings.normalized_openai_api_key
    if api_key is not None:
        client = OpenAI(api_key=api_key)
        examples = []
        if cluster:
            examples = [
                row.intent_detected
                for row in db.query(Conversation).filter(Conversation.id.in_(cluster.example_conversation_ids)).all()
            ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior conversational AI designer specializing in banking Operating Procedures. Generate a specific, actionable recommendation to fix a gap in a banking AI agent's Operating Procedure. Write for a non-technical bank operations manager. Be concrete - describe exactly what new intent handling, response logic, or escalation path should be added.",
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "operating_procedure": op.name,
                            "health_score": op.health_score,
                            "resolution_rate": op.resolution_rate,
                            "identified_gap": cluster.gap_description if cluster else None,
                            "example_failed_customer_phrases": examples,
                        }
                    ),
                },
            ],
        )
        text = response.choices[0].message.content or text

    recommendation = Recommendation(
        op_id=op_id,
        cluster_id=cluster_id,
        recommendation_text=text,
        priority=_priority(op),
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation
