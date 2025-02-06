import logging
import uuid

from rest_framework import serializers
from django.contrib.auth.models import Group

from apps.core.utils.helpers import unique_number_generator
from apps.users.models import AgentSettings, PartnerSettings, User
from apps.core.utils.constants import DATETIME_FORMAT
from apps.core.utils.enums import GenderEnum, UserGroupEnum, UserTypeEnum
from apps.core.utils.validators.validate_user_type import validate_user_type
from config import settings


logger = logging.getLogger("users")


def generate_uuid(model, column):
    unique = str(uuid.uuid4())
    kwargs = {column: unique}
    qs_exists = model.objects.filter(**kwargs).exists()
    if qs_exists:
        return generate_uuid(model, column)
    return unique

class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format=DATETIME_FORMAT, read_only=True)
    group = serializers.CharField(read_only=True)
    avatar = serializers.SerializerMethodField("get_avatar")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "group",
            "phone_number",
            "email",
            "country",
            "state",
            "local_govt",
            "city",
            "town",
            "address",
            "gender",
            "is_confirmed",
            "avatar",
            "created_at",
        ]

    @staticmethod
    def get_avatar(obj: User):
        if obj.avatar:
            return f"{settings.BASE_BE_URL}{obj.avatar.url}"
        return None
   
    
class UserFormSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=True)
    email = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    local_govt = serializers.CharField(required=False)
    address = serializers.CharField(required=False)


    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    def validate(self, attrs):
        if User.objects.filter(email=attrs.get("email")).exists():
            raise Exception("User with this email already exist")
        if User.objects.filter(phone_number=attrs.get("phone_number")).exists():
            raise Exception("User with this phone number already exist")
        return attrs


class PartnerRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)
    phone_number = serializers.CharField(required=True)
    gender = serializers.CharField(required=True, choices=GenderEnum.choices())
    is_accept_terms_and_condition = serializers.BooleanField()

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            instance.__setattr__(k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        payload = {
            "username": generate_uuid(User, "username"),
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name"),
            "phone_number": validated_data.get("mobile"),
            "type": UserTypeEnum.PARTNER,
            "is_accept_terms_and_condition": validated_data.get("is_accept_terms_and_condition"),
        }
        instance = User.objects.create(**payload)
        instance.set_password(validated_data.get("password"))
        instance.save()
        group, _ = Group.objects.get_or_create(name=UserGroupEnum.PARTNER)
        _ = PartnerSettings.objects.create(
            **{"user": instance, 'reg_no': unique_number_generator(PartnerSettings, 'reg_no', 8), 'is_current': True})
        instance.groups.add(group)
        instance.save()
        return instance
    
    
class PartnerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    reg_no = serializers.CharField(read_only=True)
    class Meta:
        model = PartnerSettings
        fields = (
            "id", 
            "user", 
            "address", 
            "location", 
            "business_type", 
            "organization", 
            "service", 
            "reg_no", 
            "created_at", 
            "updated_at"
            )
    
        
class PartnerFormSerializer(serializers.Serializer):
    pass
    
    
class AgentRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    """

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8)
    phone_number = serializers.CharField(required=True)
    gender = serializers.CharField(required=True, choices=GenderEnum.choices())

    def create(self, validated_data):
        payload = {
            "username": generate_uuid(User, "username"),
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name"),
            "phone_number": validated_data.get("mobile"),
            "type": UserTypeEnum.AGENT,
            "is_accept_terms_and_condition": validated_data.get("is_accept_terms_and_condition"),
        }
        instance = User.objects.create(**payload)
        instance.set_password(validated_data.get("password"))
        instance.save()
        group, _ = Group.objects.get_or_create(name=UserGroupEnum.AGENT)
        _ = AgentSettings.objects.create(
            **{"user": instance, 'reg_no': unique_number_generator(AgentSettings, 'reg_no', 8), 'is_current': True})
        instance.groups.add(group)
        instance.save()
        return instance


class AgentFormSerializers(serializers.Serializer):
    pass