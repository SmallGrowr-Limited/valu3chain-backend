import logging
import os
import uuid
from datetime import datetime

import pytz
from django.contrib.auth import authenticate, get_user_model, logout
from django.db.models import Q
from rest_framework.serializers import ValidationError
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.users.serializers import (
    AgentRegistrationSerializer,
    PartnerRegistrationSerializer,
    UserFormSerializer,
    UserSerializer,
)

from apps.core.utils.base import BaseViewSet
from apps.core.utils.enums import  UserGroupEnum, UserTypeEnum
from apps.core.utils.helpers import get_tokens_for_user, unique_number_generator
from apps.core.utils.permissions import has_permission
from apps.core.utils.redis_cache import (
    delete_value_in_redis,
    get_value_in_redis,
    set_value_in_redis,
)

logger = logging.getLogger("users")

class AuthViewSet(ViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @staticmethod
    def get_user(username):
        try:
            user = get_user_model().objects.get(
                Q(email=username) | Q(phone_number=username)
            )
            return user
        except get_user_model().DoesNotExist:
            return None

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="username is phone number or email",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="user password"
                ),
            },
        ),
        operation_description="",
        responses={},
        operation_summary="LOGIN ENDPOINT FOR ALL USERS",
    )
    @action(detail=False, methods=["post"], description="Login authentication")
    def login(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            for key, value in data.items():
                if key not in ["username", "password"]:
                    raise Exception(f"{key} missing from the request")
            user = authenticate(
                request,
                username=data.get("username"),
                password=data.get("password"),
            )
            if user:
                user.last_login = make_aware(
                    datetime.today(),
                    timezone=pytz.timezone("Africa/Lagos"),
                )
                user.save(update_fields=["last_login"])
                context.update(
                    {
                        "data": UserSerializer(user).data,
                        "token": get_tokens_for_user(user),
                    }
                )
            else:
                context["status"] = status.HTTP_400_BAD_REQUEST
                context["message"] = (
                    "Invalid credentials, Kindly supply valid credentials"
                )
            return Response(context, status=context["status"])
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @staticmethod
    def error_message_formatter(serializer_errors):
        """Formats serializer error messages to dictionary"""
        return {
            f"{name}": f"{message[0]}" for name, message in serializer_errors.items()
        }

    @swagger_auto_schema(
        request_body=PartnerRegistrationSerializer,
        operation_description=f"This endpoint handles user onboarding based on account_type {UserGroupEnum.to_list()}",
        responses={},
        operation_summary="USER ONBOARD ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description=f"on boarding user.",
        url_path=r"(?P<account_type>[^/]+)/sign-up",
    )
    def sign_up(self, request, account_type: str):
        context = {"status": status.HTTP_201_CREATED}
        account_type_list = [UserGroupEnum.AGENT, UserGroupEnum.PARTNER]
        
        if account_type not in account_type_list:
            raise Exception("Kindly supply a valid account type")
    
        try:
            data = self.get_data(request)
            if get_user_model().objects.filter(email=data.get("email")).exists():
                raise Exception("User with this email already exist on our system")
            
            if get_user_model().objects.filter(phone_number=data.get("phone_number")).exists():
                raise Exception("User with this phone number already exist on our system")
            
            otp = unique_number_generator()
            
            if account_type == UserGroupEnum.PARTNER:
                self.register_partner(data, otp)
            
            elif account_type == UserGroupEnum.AGENT:
                self.register_agent(data, otp)
            
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])
    

    def register_partner(self, data, otp):
        context = {"status": status.HTTP_201_CREATED}
        try: 
            serializer = PartnerRegistrationSerializer(data=data)
                
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                set_value_in_redis(
                    otp,
                    instance.id,
                    expiration=int(os.environ.get("REDIS_KEY_EXP", 360)),
                )
                
                logger.info(f"Partner Account created successfully")
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(serializer.errors),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )
        
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])
    
    def register_agent(self, data, otp):
        context = {"status": status.HTTP_201_CREATED}
        try:
            serializer = AgentRegistrationSerializer(data=data)
                
            if serializer.is_valid():
                instance = serializer.create(serializer.validated_data)
                # Set the cache with an expiration of 7 days (604800 seconds)
                set_value_in_redis(
                    otp,
                    instance.id,
                    expiration=int(os.environ.get("REDIS_KEY_EXP", 360)),
                )
            else:
                context.update(
                    {
                        "errors": self.error_message_formatter(serializer.errors),
                        "status": status.HTTP_400_BAD_REQUEST,
                    }
                )   
                logger.info(f"Agent Account created successfully")
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="This is the user email",
                ),
            },
        ),
        operation_description="This endpoint handles user request forget password",
        responses={},
        operation_summary="FORGET ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description="Forgot password endpoint",
        url_path="password/forget",
    )
    def forget_password(self, request, *args, **kwargs):
        data = self.get_data(request)
        username = data.get("username")

        if not username:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Kindly supply a valid parameter",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_user_model().objects.filter(Q(email=username) | Q(phone_number=username)).first()

        if not user:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Supplied credential not associated to any user",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        # exp to 6mins
        otp = unique_number_generator()
        set_value_in_redis(
            otp,
            user.id,
            expiration=int(os.environ.get("REDIS_OTP_EXP", 360)),
        )

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "OTP sent successfully",
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "otp": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="OTP generated to reset password",
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New password for the user",
                ),
            },
        ),
        operation_description="This endpoint handles user request to reset password",
        responses={},
        operation_summary="RESET PASSWORD ENDPOINT",
    )
    @action(
        detail=False,
        methods=["post"],
        description="Reset password endpoint",
        url_path="password/reset",
    )
    def reset_password(self, request, *args, **kwargs):
        data = self.get_data(request)
        otp = data.get("otp")
        new_password = data.get("new_password")

        if not otp or not new_password:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "OTP and new password are required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = get_value_in_redis(otp)

        if not user_id:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid OTP",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(get_user_model(), pk=user_id)
        user.set_password(new_password)
        user.save()
        delete_value_in_redis(otp)

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Password updated successfully",
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Resend OTP to user's email",
        responses={200: "OTP sent successfully", 400: "User not found"},
        operation_summary="RESEND OTP ENDPOINT",
    )
    @action(
        detail=False,
        methods=["get"],
        description="Resend OTP endpoint",
        url_path=r"resend-otp/(?P<username>[^/]+)",
    )
    def resend_token(self, request, username):
        """
        Resend OTP to user's email
        """
        context = {
            "status": status.HTTP_200_OK,
            "message": "OTP sent successfully",
        }

        try:
            # Ensure the user exists
            user = get_user_model().objects.filter(Q(phone_number=username) | Q(email=username)).first()
            if not user:
                raise ValidationError(
                    "User with this username does not exist in our system"
                )

            # Generate and store OTP in Redis
            otp = unique_number_generator()
            set_value_in_redis(
                otp,
                user.id,
                expiration=int(os.environ.get("REDIS_OTP_EXP", 360)),
            )

        except ValidationError as e:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
        except Exception as e:
            context.update(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}
            )

        return Response(context, status=context["status"])
    
    
    @swagger_auto_schema(
        operation_description="verify phone number",
        responses={200: "phone number verified successfully", 400: "User not found"},
        operation_summary="Verify phone number ENDPOINT",
    )
    @action(
        detail=False,
        methods=["get"],
        description="Verify phone number endpoint",
        url_path=r"phone-verification/(?P<otp>[^/]+)",
    )
    def phone_verification(self, request, otp):
        """
        verify otp
        """
        context = {
            "status": status.HTTP_200_OK,
            "message": "OTP verified successfully",
        }

        try:
            # Ensure the user exists
            user_id = get_value_in_redis(otp)
            if not user_id:
                raise Exception("Invalid OTP, please request a new one")
            
            user = get_user_model().objects.filter(id=user_id).first()
            
            if not user:
                raise ValidationError(
                    "User does not exist in our system"
                )
            user.is_confirmed = True
            user.is_active = True
            user.save()

            delete_value_in_redis(otp)

        except ValidationError as e:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
        except Exception as e:
            context.update(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}
            )

        return Response(context, status=context["status"])
    
    @swagger_auto_schema(
        operation_description="verify OTP",
        responses={200: "OTP verified successfully", 400: "User not found"},
        operation_summary="Verify OTP ENDPOINT",
    )
    @action(
        detail=False,
        methods=["get"],
        description="Verify OTP endpoint",
        url_path=r"OTP-verification/(?P<otp>[^/]+)",
    )
    def otp_verification(self, request, otp):
        """
        verify otp
        """
        context = {
            "status": status.HTTP_200_OK,
            "message": "OTP verified successfully",
        }

        try:
            # Ensure the user exists
            user_id = get_value_in_redis(otp)
            if not user_id:
                raise Exception("Invalid OTP, please request a new one")
            
            user = get_user_model().objects.filter(id=user_id).first()
            
            if not user:
                raise ValidationError(
                    "User does not exist in our system"
                )
            delete_value_in_redis(otp)

        except ValidationError as e:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})
        except Exception as e:
            context.update(
                {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}
            )

        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Logout",
        responses={},
        operation_summary="logout",
    )
    @action(
        detail=False,
        methods=["get"],
        description="resend token endpoint",
        url_path=r"logout",
    )
    def account_logout(self, request):
        try:
            logout(request)
        except Exception as ex:
            pass
        return redirect("/")


class UserViewSet(BaseViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        return self.queryset

    def get_object(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_description="",
        responses={},
        operation_summary="Retrieve user information",
    )
    @action(
        detail=False,
        methods=["get"],
        description="Get user profile information",
    )
    def me(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update({"data": self.serializer_class(request.user).data})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=UserFormSerializer,
        operation_description="",
        responses={},
        operation_summary="Update user profile endpoint",
    )
    def update(self, request, *args, **kwargs):
        context = {"status": status.HTTP_400_BAD_REQUEST}
        try:
            instance = request.user
            data = self.get_data(request)
            serializer = UserFormSerializer(data=data, instance=instance)
            if serializer.is_valid():

                all_users_exclude_current = (
                    get_user_model().objects.all().exclude(id=request.user.id)
                )

                if (
                    serializer.validated_data.get("phone_number")
                    and all_users_exclude_current.filter(
                        phone_number=serializer.validated_data.get("phone_number")
                    ).exists()
                ):
                    raise Exception("Phone number already being used")

                if serializer.validated_data.get("email"):
                    if all_users_exclude_current.filter(
                        email=serializer.validated_data.get("email")
                    ).exists():
                        raise Exception("Email already being used")
                obj = serializer.update(
                    instance=instance,
                    validated_data=serializer.validated_data,
                )
                context.update(
                    {
                        "data": self.serializer_class(obj).data,
                        "status": status.HTTP_200_OK,
                    }
                )
            else:
                context.update(
                    {"errors": self.error_message_formatter(serializer.errors)}
                )
        except Exception as ex:
            context.update({"message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "old_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="old password"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="new password"
                ),
            },
        ),
        operation_description="This endpoint handles new password reset",
        responses={},
        operation_summary="Update password  endpoint",
    )
    @action(
        detail=False,
        methods=["put"],
        description="Update password endpoint",
        url_path=r"update-password",
    )
    def update_password(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            data = self.get_data(request)
            user = request.user

            for key, value in data.items():
                if value == "" or value is None:
                    raise Exception(f"{key} is required")

            if user.check_password(data.get("old_password")) is True:
                user.set_password(data.get("new_password"))
                user.save()
                context.update(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "ok",
                        "data": self.serializer_class(user).data,
                    }
                )
            else:
                raise Exception(
                    "Password does not match with the old password, kindly try again"
                )
        except Exception as ex:
            context.update(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "BAD REQUEST",
                    "error": str(ex),
                }
            )
        return Response(context, status=context["status"])


class AdminViewSet(BaseViewSet):
    serializer_class = UserSerializer
    queryset = get_user_model().objects.using("default").all()

    def get_queryset(self):
        return self.queryset

    def get_object(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs.get("pk"))

    @action(
        detail=False,
        methods=["get"],
        description=f"get all users",
        url_path=r"users",
    )
    @method_decorator(
        has_permission(UserTypeEnum.ADMIN), name="dispatch"
    )
    def get_users(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            logger.info(f"Fetching all users")
            paginate = self.get_paginated_data(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update({"status": status.HTTP_200_OK, "data": paginate})
        except Exception as ex:
            logger.error(f"Error fetching all user due to {str(ex)}")
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])


    @swagger_auto_schema(
        operation_description="Retrieve user detail",
        operation_summary="Retrieve user detail. Only admins have access to this",
    )
    @method_decorator(
        has_permission(UserTypeEnum.ADMIN), name="dispatch"
    )
    def retrieve(self, requests, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update({"data": self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Delete user account",
        operation_summary="The endpoint handles removing  user account. Only admins have access to this",
    )
    @method_decorator(has_permission(UserTypeEnum.ADMIN), name="dispatch")
    def destroy(self, request, *args, **kwargs):
        context = {"status": status.HTTP_204_NO_CONTENT}
        try:
            instance = self.get_object()
            instance.delete()
            context.update({"message": "Account deleted successfully"})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return Response(context, status=context["status"])

