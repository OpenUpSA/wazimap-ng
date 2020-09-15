from wazimap_ng.utils import get_objects_for_user


from ..models import Dataset


def get_datasets_with_permission(user, permission):
    datasets = Dataset.objects.all()

    if user.is_superuser:
        return datasets

    datasets = get_objects_for_user(user, permission, Dataset)
    return datasets
