from datetime import timedelta, timezone

USERS_MAX_ROUTES_COUNT = 10
USERS_MAX_SURVEYS_COUNT = 5
USERS_MAX_COMMENTS_COUNT = 5
MIN_PLACES_COUNT = 2
MAX_PLACES_COUNT = 10

MAX_FIELD_SIZE = 10_000


TIME_ZONE = timezone(timedelta(hours=5))
EDIT_TIME_LIMIT = timedelta(hours=24)
