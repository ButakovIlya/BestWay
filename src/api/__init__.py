from api.admin.places import PlaceViewSet
from api.admin.routes import RouteViewSet
from api.admin.users import router as user_router
from api.public.auth import router as auth_router
from api.public.health import router as health_router
from api.public.profile import router as profile_router

place_viewset = PlaceViewSet()
route_viewset = RouteViewSet()

admin_routers = [
    user_router,
    place_viewset.router,
    route_viewset.router,
]

public_routers = [
    health_router,
    auth_router,
    profile_router,
]
