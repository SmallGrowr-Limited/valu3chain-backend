import uuid

from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken


def generate_username(model, column):
    unique = str(uuid.uuid4())
    kwargs = {column: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return generate_username(model, column)
    return unique


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def unique_alpha_numeric_generator(
    length=9,
    allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
):
    unique = get_random_string(length=length, allowed_chars=allowed_chars)
    return unique


def unique_number_generator(length=5, allowed_chars="0123456789"):
    unique = get_random_string(length=length, allowed_chars=allowed_chars)
    return unique
