from api.public.health import router as health_router
from api.admin.users import router as user_router
from api.public.auth import router as auth_router
from api.public.profile import router as profile_router

from api.admin.places import PlaceViewSet
place_viewset = PlaceViewSet()

routers = [
    health_router,
    user_router,
    auth_router,
    profile_router,
    place_viewset.router,
]
