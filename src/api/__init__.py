from api.admin.comments import router as comment_router
from api.admin.likes import router as like_router
from api.admin.places import router as place_router
from api.admin.posts import router as post_router
from api.admin.routes import router as route_router
from api.admin.surveys import router as survey_router
from api.admin.users import router as user_router
from api.public.auth import router as auth_router
from api.public.comments import router as public_comment_router
from api.public.health import router as health_router
from api.public.likes import router as public_like_router
from api.public.places import router as public_place_router
from api.public.posts import router as posts_survey_router
from api.public.profile import router as profile_router
from api.public.routes import router as public_route_router
from api.public.surveys import router as public_survey_router

admin_routers = [
    user_router,
    comment_router,
    like_router,
    place_router,
    route_router,
    survey_router,
    post_router,
]

public_routers = [
    health_router,
    auth_router,
    profile_router,
    public_place_router,
    public_route_router,
    public_survey_router,
    public_like_router,
    public_comment_router,
    posts_survey_router,
]
