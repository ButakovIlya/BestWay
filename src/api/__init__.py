from api.health import router as health_router
from api.users import router as user_router
from api.auth import router as auth_router
from api.public.profile import router as profile_router


routers = [
    health_router,
    user_router,
    auth_router,
    profile_router,
]
