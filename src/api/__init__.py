from api.admin.places import PlaceViewSet
from api.admin.routes import RouteViewSet
from api.admin.surveys import SurveyViewSet
from api.admin.users import router as user_router
from api.public.auth import router as auth_router
from api.public.health import router as health_router
from api.public.places import PublicPlaceViewSet
from api.public.profile import router as profile_router
from api.public.surveys import router as survey_router
from src.api.public.routes import PublicRouteViewSet

place_viewset = PlaceViewSet()
route_viewset = RouteViewSet()
survey_viewset = SurveyViewSet()


public_place_viewset = PublicPlaceViewSet()
public_route_viewset = PublicRouteViewSet()
admin_routers = [
    user_router,
    place_viewset.router,
    route_viewset.router,
    survey_viewset.router,
]

public_routers = [
    health_router,
    auth_router,
    profile_router,
    survey_router,
    public_place_viewset.router,
    public_route_viewset.router,
]
