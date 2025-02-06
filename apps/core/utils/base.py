from abc import abstractmethod

from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import response, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from .pagination import CustomPaginator


class Addons:
    def unique_alpha_numeric_generator(
        self,
        model,
        field,
        length=9,
        allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        prefix=None,
        year=None,
    ):
        unique = get_random_string(length=length, allowed_chars=allowed_chars)
        if prefix:
            unique = f"{prefix}_{unique}_{year}"
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_alpha_numeric_generator(model, field)
        return unique

    def unique_number_generator(
        self, model, field, length=6, allowed_chars="0123456789"
    ):
        unique = get_random_string(length=length, allowed_chars=allowed_chars)
        kwargs = {field: unique}
        qs_exists = model.objects.filter(**kwargs).exists()
        if qs_exists:
            return self.unique_number_generator(model, field, length)
        return unique


class CustomFilter(DjangoFilterBackend):
    def get_filterset_kwargs(self, request, queryset, view):
        kwargs = super().get_filterset_kwargs(request, queryset, view)
        # merge filterset kwargs provided by view class
        if hasattr(view, "get_filterset_kwargs"):
            kwargs.update(view.get_filterset_kwargs())

        return kwargs


class AbstractBaseViewSet:
    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    filter_backends = [SearchFilter, DjangoFilterBackend]
    paginator_class = CustomPaginator()

    def __init__(self):
        pass

    @staticmethod
    def filter_by_year_range(request, queryset):
        year_from = request.GET.get("year_from")
        year_to = request.GET.get("year_to")

        if year_from and year_to:
            try:
                queryset = queryset.filter(year__range=[int(year_from), int(year_to)])
            except Exception as ex:
                print(f"error filtering year due to {str(ex)}")
        return queryset

    @staticmethod
    def error_message_formatter(serializer_errors):
        """Formats serializer error messages to dictionary"""
        if isinstance(serializer_errors, list):
            errors = {}
            for error in serializer_errors:
                for name, message in error.items():
                    errors.update({f"{name}": f"{message[0]}"})
            return errors
        return {
            f"{name}": f"{message[0]}" for name, message in serializer_errors.items()
        }


class BaseViewSet(ViewSet, AbstractBaseViewSet, Addons):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_data(request) -> dict:
        """Returns a dictionary from the request"""
        return request.data if isinstance(request.data, dict) else request.data.dict()

    @staticmethod
    def get_data_as_list(request) -> list:
        """Returns a list from the request"""
        return request.data if isinstance(request.data, list) else [request.data]

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            if type(query_set) == list:
                query_set = query_set
                return query_set
            query_set = query_set.order_by("-pk")
        return query_set

    def get_paginated_data(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data


class BaseModelViewSet(ModelViewSet, AbstractBaseViewSet):
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = query_set.order_by("-pk")  # was originally 'pk'
        return query_set

    def get_paginated_data(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data


class BaseNoAuthViewSet(ViewSet):
    """
    This class inherit from django ViewSet class
    """

    custom_filter_class = CustomFilter()
    search_backends = SearchFilter()
    order_backend = OrderingFilter()
    paginator_class = CustomPaginator()
    serializer_class = None

    @staticmethod
    def error_message_formatter(serializer_errors):
        """Formats serializer error messages to dictionary"""
        return {
            f"{name}": f"{message[0]}" for name, message in serializer_errors.items()
        }

    @staticmethod
    def get_data(request) -> dict:
        return request.data if isinstance(request.data, dict) else request.data.dict()

    @abstractmethod
    def get_queryset(self):
        pass

    @abstractmethod
    def get_object(self):
        pass

    def get_list(self, queryset):
        if "search" in self.request.query_params:
            query_set = self.search_backends.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        elif self.request.query_params:
            query_set = self.custom_filter_class.filter_queryset(
                request=self.request, queryset=queryset, view=self
            )
        else:
            query_set = queryset
        if "ordering" in self.request.query_params:
            query_set = self.order_backend.filter_queryset(
                query_set, self.request, self
            )
        else:
            query_set = query_set.order_by("-pk")
        return query_set

    def paginator(self, queryset, serializer_class):
        paginated_data = self.paginator_class.generate_response(
            queryset, serializer_class, self.request
        )
        return paginated_data

    @swagger_auto_schema(
        operation_description="List all entries available",
        operation_summary="List all entries available ",
    )
    def list(self, request, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            paginate = self.paginator(
                queryset=self.get_list(self.get_queryset()),
                serializer_class=self.serializer_class,
            )
            context.update(
                {
                    "status": status.HTTP_200_OK,
                    "message": "OK",
                    "data": paginate,
                }
            )
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return response.Response(context, status=context["status"])

    @swagger_auto_schema(
        operation_description="Retrieve entry details",
        operation_summary="Retrieve entry details",
    )
    def retrieve(self, requests, *args, **kwargs):
        context = {"status": status.HTTP_200_OK}
        try:
            context.update({"data": self.serializer_class(self.get_object()).data})
        except Exception as ex:
            context.update({"status": status.HTTP_400_BAD_REQUEST, "message": str(ex)})
        return response.Response(context, status=context["status"])
