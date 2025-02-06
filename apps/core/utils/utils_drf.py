from typing import Any

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet


def helper_json_response(param_serializer, param_serializer_data, param_status_code):
    """
    respond with a json renderer

    Args:
        :param param_serializer: the serializer class def
        :param param_serializer_data: the json serializable data to render
        :param param_status_code: the HTTP status code
    Returns:
        :rtype: HttpResponse
    """
    serializer_obj = param_serializer(data=param_serializer_data)
    response_data = JSONRenderer().render(serializer_obj.initial_data)

    return HttpResponse(response_data, "application/json", param_status_code)


class TurboViewset(ModelViewSet):
    turbo_serializer = None

    def get_serializer_class(self):
        if self.action == "list":
            return self.turbo_serializer
        return super().get_serializer_class()
