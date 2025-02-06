from functools import wraps
from rest_framework import status
from rest_framework.response import Response

def has_permission(*permissions):
    """
    General decorator to check if a user has any of the specified permissions.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.type not in permissions:
                return Response(
                    {
                        "status": status.HTTP_403_FORBIDDEN,
                        "message": "You currently do not have access to this resource",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
