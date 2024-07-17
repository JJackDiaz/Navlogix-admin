from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    def decorator(view_func):
        decorated_view_func = user_passes_test(in_groups, login_url='no_permission')(view_func)
        return decorated_view_func

    return decorator
