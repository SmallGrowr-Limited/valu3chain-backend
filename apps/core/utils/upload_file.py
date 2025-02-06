import logging

from django.forms import ValidationError
from django.apps import apps
import pandas as pd

from apps.dmi.models import FileUpload
from apps.utils.validators.data_file import (
    validate_file_extension,
    validate_file_size,
    validate_headers,
)


logger = logging.getLogger("data")


class UploadFile:

    @staticmethod
    def validate_file(file):
        """
        Validate file extension and size.
        """
        try:
            ext = validate_file_extension(file)
            validate_file_size(file)
        except ValidationError as e:
            raise ValidationError(f"File validation error: {str(e)}")
        return ext

    def load_data(self, file, ext):
        """
        Load data from the file into a DataFrame.
        """
        try:
            if ext == ".csv":
                return pd.read_csv(file)
            elif ext in [".xls", ".xlsx", ".xlsm"]:
                return pd.read_excel(file, engine="openpyxl")
            else:
                raise ValidationError("Unsupported file format.")
        except Exception as e:
            logger.exception(f"Failed to read file {file}: {e}")
            raise ValidationError("Unable to read the file.")

    def validate(self, attrs: dict):
        """
        Validate the file and data_set, then load and process the file.
        """
        try:
            model = apps.get_model("data", attrs.get("file_type"))
            ext = self.validate_file(attrs.get("ordinary_data"))
            self.df = self.load_data(attrs.get("ordinary_data"), ext)
            headers: list = validate_headers(self.df, model().expected_fields)
            attrs.update({"headers": headers, "ext": ext})
        except Exception as e:
            raise ValidationError(f"Error processing file: {str(e)}")

        return attrs

    def save_file(self, validated_data: dict):
        """
        Save the uploaded file to the media/data/ directory with a unique UUID and timestamp-based name.
        """
        try:
            file_upload = FileUpload.objects.create(**validated_data)
        except Exception as e:
            raise ValidationError(f"Error saving file: {str(e)}")

        return file_upload
