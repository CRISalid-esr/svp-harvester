"""
API redirection router
"""
from fastapi import APIRouter
from starlette.responses import RedirectResponse

from app.gui.routes import admin

router = APIRouter()
router.include_router(admin.router, tags=["admin"], prefix="/admin")


@router.get("/")
def redirect_to_admin():
    """
    Redirect users from the root path to the admin path
    :return: RedirectResponse
    """
    return RedirectResponse(url="/admin")
