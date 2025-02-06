import os

from pandas.core.frame import DataFrame
from rest_framework import serializers


def validate_file_extension(file) -> str:
    """Validate file extension

    Args:
        file (UploadedFile): File object uploaded by the user

    Raises:
        serializers.ValidationError: Only Excel files (.xls, .xlsx, .xlsm, .csv) are allowed.

    Returns:
        str: File extension
    """
    ext = os.path.splitext(file.name)[1].lower()  # Get file extension

    valid_extensions = [
        ".xls",
        ".xlsx",
        ".xlsm",
        ".csv",
    ]  # Valid file extensions
    if ext not in valid_extensions:
        raise serializers.ValidationError(
            "Only Excel files (.xls, .xlsx, .xlsm, .csv) are allowed."
        )
    return ext


def validate_file_size(file):
    """Validate file size is not more than 20 MB

    Args:
        file (UploadedFile): File object uploaded by the user

    Raises:
        serializers.ValidationError: File size too large. Max size is 20 MB.
    """
    max_size = 20 * 1024 * 1024  # 20 MB in bytes
    if file.size > max_size:
        raise serializers.ValidationError("File size too large. Max size is 20 MB.")


def validate_headers(df: DataFrame, fields: set) -> str:
    """Validate file headers

    Args:
        df (DataFrame): pandas DataFrame
        fields (set): Expected fields from the file header

    Raises:
        serializers.ValidationError: If required fields are missing in the Excel file headers.

    Returns:
        str: Headers present in the file
    """
    try:

        headers = set(["_".join(h.strip().lower().split(" ")) for h in df.columns])

        missing_fields = fields - headers

        if missing_fields:
            raise serializers.ValidationError(
                f"The following fields are missing in the Excel file headers: {', '.join(missing_fields)}"
            )
        return list(headers)
    except Exception as e:
        raise serializers.ValidationError(f"Error validating headers: {str(e)}")
