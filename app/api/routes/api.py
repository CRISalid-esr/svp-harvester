"""
API redirection router
"""

from fastapi import APIRouter

from app.api.routes import references, retrieval, metrics, reference_events

router = APIRouter()
router.include_router(references.router, tags=["references"], prefix="/references")
router.include_router(
    reference_events.router, tags=["reference_events"], prefix="/reference_events"
)
router.include_router(retrieval.router, tags=["retrievals"], prefix="/retrievals")
router.include_router(metrics.router, tags=["metrics"], prefix="/metrics")
