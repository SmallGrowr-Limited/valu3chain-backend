from rest_framework import serializers

from apps.utils.enums import UserGroup


def validate_user_type(type: int) -> str:
    """
    Validates user type and returns the corresponding
    user role.
    PARAMS:
        type: int
    RETURN:
        string equivalent of type
    """
    if type == 0:
        return UserGroup.DATA_VIEWER
    elif type == 1:
        return UserGroup.DATA_MANAGER
    elif type == 2:
        return UserGroup.SUPER_ADMIN
    elif type == 3:
        return UserGroup.ADMIN
    else:
        raise serializers.ValidationError("Invalid user type.")
