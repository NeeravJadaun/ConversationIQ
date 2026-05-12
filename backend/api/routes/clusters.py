from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from api.routes.websocket import broadcast_update
from models import Conversation, FailureCluster
from schemas.cluster import FailureClusterOut
from services.cluster_engine import run_clustering

router = APIRouter(prefix="/api/clusters", tags=["clusters"])


@router.get("", response_model=list[FailureClusterOut])
def list_clusters(db: Session = Depends(get_db)):
    return db.query(FailureCluster).order_by(FailureCluster.size.desc()).all()


@router.post("/recompute", response_model=list[FailureClusterOut])
async def recompute_clusters(op_id: str | None = None, db: Session = Depends(get_db)):
    clusters = run_clustering(op_id, db)
    for cluster in clusters:
        await broadcast_update({"type": "new_cluster", "op_id": cluster.op_id, "cluster_id": cluster.id, "timestamp": cluster.created_at.isoformat()})
    return clusters


@router.get("/{cluster_id}")
def get_cluster(cluster_id: int, db: Session = Depends(get_db)):
    cluster = db.get(FailureCluster, cluster_id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    examples = db.query(Conversation).filter(Conversation.id.in_(cluster.example_conversation_ids)).all()
    return {"cluster": cluster, "example_conversations": examples}
