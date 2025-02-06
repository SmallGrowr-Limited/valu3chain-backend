from typing import Union
from django.core.cache import cache


def validate_values(key: str, value: Union[str, dict] = None):
    if not key:
        raise Exception("Key can not be empty")

    if isinstance(value, str) and len(value.strip()) == 0:
        raise Exception("value can not be empty")

    if isinstance(value, dict) and not value:
        raise Exception("value is required")


def set_value_in_redis(key: str, value: Union[str, dict], expiration: int) -> None:
    validate_values(key, value)
    cache.set(key, value, timeout=expiration)


def get_value_in_redis(key: str):
    validate_values(key)
    return cache.get(key)


def delete_value_in_redis(key: str):
    validate_values(key)
    cache.delete(key)
