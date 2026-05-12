from datetime import datetime, timezone

from models import Conversation, FailureCluster
from services.cluster_engine import run_clustering


def _add_failed(db, count=50, op_id="OP-01"):
    for i in range(count):
        db.add(
            Conversation(
                id=f"{op_id}-{i}",
                op_id=op_id,
                op_name="Card Lock / Freeze",
                turns=[{"role": "customer", "text": f"put card on hold {i % 3}", "timestamp": "now"}],
                resolution_status="failed",
                turn_count=5,
                customer_sentiment="negative",
                intent_detected=f"gap intent {i % 3}",
                failure_reason="missing intent path",
                suggested_intent_label=f"gap intent {i % 3}",
                embedding=[float(i % 3)] * 384,
                session_duration_seconds=160,
                created_at=datetime.now(timezone.utc),
            )
        )
    db.commit()


def test_clustering_produces_clusters(db):
    _add_failed(db, 50)
    assert len(run_clustering("OP-01", db)) >= 1


def test_cluster_assigns_conversation_ids(db):
    _add_failed(db, 20)
    run_clustering("OP-01", db)
    assert all(row.cluster_id is not None for row in db.query(Conversation).all())


def test_small_dataset_fallback(db):
    _add_failed(db, 8)
    clusters = run_clustering("OP-01", db)
    assert len(clusters) == 2


def test_cluster_gap_description_generated(db):
    _add_failed(db, 12)
    run_clustering("OP-01", db)
    assert db.query(FailureCluster).first().gap_description
