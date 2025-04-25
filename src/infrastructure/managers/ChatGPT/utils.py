import logging
from functools import wraps
from time import sleep

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)
REQUEST_TEXTS_COUNT = get_settings().request_texts_count or 5


def retry_on_status_code(code: int, max_retries=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    response = func(*args, **kwargs)
                    return response
                except httpx.HTTPStatusError as ex:
                    if ex.response.status_code == code:
                        logger.warning(
                            f"Received {code} response. Retrying {retries + 1}/{max_retries} in {delay} seconds..."
                        )
                        retries += 1
                        sleep(delay)
                    else:
                        raise ex
                except Exception as ex:
                    raise ex
            raise Exception("Max retries exceeded.")

        return wrapper

    return decorator
