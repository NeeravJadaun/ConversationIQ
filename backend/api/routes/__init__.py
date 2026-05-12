from api.routes.clusters import router as clusters_router
from api.routes.conversations import router as conversations_router
from api.routes.procedures import router as procedures_router
from api.routes.recommendations import router as recommendations_router
from api.routes.websocket import router as websocket_router

__all__ = [
    "clusters_router",
    "conversations_router",
    "procedures_router",
    "recommendations_router",
    "websocket_router",
]
