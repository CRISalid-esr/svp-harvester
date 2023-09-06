"""
API redirection router
"""
from fastapi import APIRouter

from app.gui.routes import admin

router = APIRouter()
router.include_router(admin.router, tags=["admin"], prefix="/admin")
