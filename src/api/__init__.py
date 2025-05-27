from api.admin.comments import CommentViewSet
from api.admin.likes import LikeViewSet
from api.admin.places import PlaceViewSet
from api.admin.routes import RouteViewSet
from api.admin.surveys import SurveyViewSet
from api.admin.users import router as user_router
from api.public.auth import router as auth_router
from api.public.comments import PublicCommentViewSet
from api.public.health import router as health_router
from api.public.likes import PublicLikeViewSet
from api.public.places import PublicPlaceViewSet
from api.public.profile import router as profile_router
from api.public.routes import PublicRouteViewSet
from api.public.surveys import router as survey_router

place_viewset = PlaceViewSet()
route_viewset = RouteViewSet()
survey_viewset = SurveyViewSet()
comment_viewset = CommentViewSet()
like_viewset = LikeViewSet()


public_place_viewset = PublicPlaceViewSet()
public_route_viewset = PublicRouteViewSet()
public_comment_viewset = PublicCommentViewSet()
public_like_viewset = PublicLikeViewSet()
admin_routers = [
    user_router,
    place_viewset.router,
    route_viewset.router,
    survey_viewset.router,
    comment_viewset.router,
    like_viewset.router,
]

public_routers = [
    health_router,
    auth_router,
    profile_router,
    survey_router,
    public_place_viewset.router,
    public_route_viewset.router,
    public_comment_viewset.router,
    public_like_viewset.router,
]
