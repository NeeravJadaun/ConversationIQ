from __future__ import annotations

from collections import defaultdict
import warnings

import numpy as np
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.exceptions import ConvergenceWarning
from sqlalchemy.orm import Session

from models import Conversation, FailureCluster, Recommendation
from services.embedder import embed_conversation


FAILURE_STATUSES = {"failed", "escalated", "looped"}


def _gap_description(items: list[Conversation]) -> str:
    labels = [item.suggested_intent_label or item.intent_detected for item in items[:5]]
    reason = items[0].failure_reason or "procedure gap"
    return f"The procedure is missing a clear path for {', '.join(labels[:3])}. Add explicit detection, customer-facing wording, and an escalation rule for this case because the current flow ends in {reason}."


def _fit_kmeans(matrix: np.ndarray, n_clusters: int) -> np.ndarray:
    if n_clusters <= 1:
        return np.zeros(len(matrix), dtype=int)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning, module=r"sklearn\.utils\.extmath")
        return KMeans(n_clusters=n_clusters, random_state=7, n_init="auto").fit_predict(matrix)


def _fit_hdbscan(matrix: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning, module=r"sklearn\.utils\.extmath")
        return HDBSCAN(min_cluster_size=5, min_samples=3).fit_predict(matrix)


def _cluster_labels(matrix: np.ndarray, op_id: str | None) -> np.ndarray:
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
    unique_vectors = len(np.unique(matrix, axis=0))
    if unique_vectors <= 1:
        return np.zeros(len(matrix), dtype=int)

    minimum_clusters = 2 if op_id else 5
    if len(matrix) < 10 or unique_vectors < 5:
        return _fit_kmeans(matrix, min(minimum_clusters, unique_vectors, len(matrix)))

    labels = _fit_hdbscan(matrix)
    usable_clusters = {int(label) for label in labels if label >= 0}
    if len(usable_clusters) < minimum_clusters:
        return _fit_kmeans(matrix, min(minimum_clusters, unique_vectors, len(matrix)))
    return labels


def run_clustering(op_id: str | None, db: Session) -> list[FailureCluster]:
    query = db.query(Conversation).filter(Conversation.resolution_status.in_(FAILURE_STATUSES))
    if op_id:
        query = query.filter(Conversation.op_id == op_id)
    conversations = query.all()
    if not conversations:
        return []

    for conversation in conversations:
        if not conversation.embedding:
            conversation.embedding = embed_conversation(
                {
                    "conversation_id": conversation.id,
                    "turns": conversation.turns,
                }
            )
    db.flush()

    old_cluster_query = db.query(FailureCluster)
    if op_id:
        old_cluster_query = old_cluster_query.filter(FailureCluster.op_id == op_id)
    old_cluster_ids = [cluster_id for (cluster_id,) in old_cluster_query.with_entities(FailureCluster.id).all()]
    if old_cluster_ids:
        db.query(Recommendation).filter(Recommendation.cluster_id.in_(old_cluster_ids)).update(
            {Recommendation.cluster_id: None},
            synchronize_session=False,
        )
        db.query(FailureCluster).filter(FailureCluster.id.in_(old_cluster_ids)).delete(synchronize_session=False)
    matrix = np.array([row.embedding for row in conversations], dtype=float)
    labels = _cluster_labels(matrix, op_id)

    grouped: dict[tuple[str, int], list[Conversation]] = defaultdict(list)
    for conversation, label in zip(conversations, labels, strict=True):
        clean_label = int(label if label >= 0 else 999)
        conversation.cluster_id = clean_label
        grouped[(conversation.op_id, clean_label)].append(conversation)

    created: list[FailureCluster] = []
    for (group_op_id, label), rows in grouped.items():
        vectors = np.array([row.embedding for row in rows], dtype=float)
        centroid = vectors.mean(axis=0)
        distances = np.linalg.norm(vectors - centroid, axis=1)
        examples = [rows[i] for i in np.argsort(distances)[:3]]
        summary = "; ".join(f"{row.intent_detected}: {row.failure_reason or 'failed'}" for row in examples)
        cluster = FailureCluster(
            op_id=group_op_id,
            cluster_label=label,
            size=len(rows),
            centroid_summary=summary,
            example_conversation_ids=[row.id for row in examples],
            gap_description=_gap_description(examples),
        )
        db.add(cluster)
        db.flush()
        for row in rows:
            row.cluster_id = cluster.id
        created.append(cluster)
    db.commit()
    return created
