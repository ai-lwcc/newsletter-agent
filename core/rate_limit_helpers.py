import os

from django_ratelimit.decorators import ratelimit


def safe_ratelimit(*args, **kwargs):
    def decorator(view_func):
        if os.getenv("PYTEST_RUNNING") == "True":
            return view_func

        return ratelimit(*args, **kwargs)(view_func)

    return decorator