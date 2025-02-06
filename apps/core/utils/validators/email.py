from rest_framework import serializers


def validate_e4email_net(value: str):
    if not value.endswith("@e4email.net"):
        raise serializers.ValidationError("Email must be from the e4email.net domain.")
