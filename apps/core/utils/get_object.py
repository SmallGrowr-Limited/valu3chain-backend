from django.http import Http404


def get_object_or_404_using(model, db_alias, **kwargs):
    """
    Fetch an object from a specific database using get_object_or_404.

    :param model: The model to query.
    :param db_alias: The database alias (e.g., 'default', 'secondary').
    :param kwargs: The query parameters for filtering.
    :return: The retrieved object or raises Http404.
    """
    queryset = model.objects.using(db_alias)
    try:
        return queryset.get(**kwargs)
    except model.DoesNotExist:
        raise Http404(f"{model._meta.object_name} does not exist.")
