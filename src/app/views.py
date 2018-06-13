from django.http import HttpResponse


def permission_denied_handler(request):
    """Permission denied Handler."""
    return HttpResponse("You have no Permissions!")


def resource_access_handler(request, resource):
    """Callback for resource access.

    Determines who can see the documentation for which API.
    """
    # -------------------------------------------------------------------------
    # --- Superusers and Staff can see whatever they want
    if request.user.is_superuser or request.user.is_staff:
        return True

    return False
