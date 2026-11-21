
from functools import lru_cache


@lru_cache(maxsize=100)
def get_cached_response(question: str, prompt_version: int):
    return None


def cache_response(question: str, prompt_version: int, response: dict):
    _response_cache[(question, prompt_version)] = response


_response_cache = {}


def get_response(question: str, prompt_version: int):
    return _response_cache.get((question, prompt_version))


def clear_cache():
    _response_cache.clear()
