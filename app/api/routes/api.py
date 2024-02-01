"""
API redirection router
"""
from fastapi import APIRouter

from app.api.routes import references, retrieval

router = APIRouter()
router.include_router(references.router, tags=["references"], prefix="/references")
router.include_router(retrieval.router, tags=["retrievals"], prefix="/retrievals")
