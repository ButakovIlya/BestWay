from redis import Redis, from_url  # type: ignore


def init_redis_pool(host: str, password: str) -> Redis:
    session = from_url(host, password=password, encoding="utf-8", decode_responses=False)
    return session
