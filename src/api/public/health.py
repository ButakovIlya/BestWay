from fastapi import Request, status
from fastapi.routing import APIRouter

from api.permissions.is_authenticated import is_authenticated
from api.schemas import CheckHealthSchema

router = APIRouter(tags=["Health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def check_health(request: Request) -> CheckHealthSchema:
    return CheckHealthSchema(status="ok")


@router.get("/health-auth", status_code=status.HTTP_200_OK)
@is_authenticated
async def check_health_authenticated(request: Request) -> CheckHealthSchema:
    return CheckHealthSchema(status="ok")
