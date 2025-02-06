from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()


class CustomAuthBackend(object):
    def authenticate(self, request, username=None, password=None):
        try:
            user = UserModel.objects.using("default").get(
                Q(email=username) | Q(username=username)
            )
            if user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            return None
        except Exception as ex:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
