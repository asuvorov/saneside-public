import inspect
import json
import mimetypes

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
    )
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

import papertrail

from annoying.functions import get_object_or_None
from termcolor import colored

from app.management.commands import clear_cache
from core.models import (
    AttachedDocument,
    AttachedImage,
    AttachedUrl,
    AttachedVideoUrl,
    Comment,
    Complaint,
    Rating,
    TemporaryFile,
    )


# -----------------------------------------------------------------------------
# --- HANDLERS
# -----------------------------------------------------------------------------
def handler400(request):
    """400 Handler."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(request, "error-pages/400.html", status=404)


def handler403(request):
    """403 Handler."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(request, "error-pages/403.html", status=404)


def handler404(request):
    """404 Handler."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(request, "error-pages/404.html", status=404)


def handler500(request):
    """500 Handler."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    try:
        clear_cache.Command().handle()

        # ---------------------------------------------------------------------
        # --- Save the Log
        papertrail.log(
            event_type="500-exception",
            message="Cache cleared",
            data={
                "success":      True,
            },
            # timestamp=timezone.now(),
            targets={},
            )

    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

    return render(request, "error-pages/500.html", status=500)


# -----------------------------------------------------------------------------
# --- ATTACHMENTS
# -----------------------------------------------------------------------------
@login_required
@require_http_methods(["POST", ])
def tmp_upload(request):
    """Upload temporary File."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    if not request.FILES:
        return HttpResponseBadRequest(
            _("No Files attached."))

    tmp_file = TemporaryFile.objects.create(
        file=request.FILES["file"],
        name=request.FILES["file"].name
    )

    result = {
        "name":         tmp_file.file.name,
        "type":         mimetypes.guess_type(tmp_file.file.name)[0] or "image/png",
        "size":         tmp_file.file.size,
        "tmp_file_id":  tmp_file.id
    }

    return HttpResponse(
        json.dumps({
            "files":    [result]
        }),
        content_type="application/json"
        )


@login_required
@require_http_methods(["POST", ])
def remove_upload(request):
    """Remove uploaded File."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    found = False

    upload_type = request.POST.get("type")
    upload_id = request.POST.get("id")

    print colored("[---  DUMP   ---] UPLOAD TYPE : %s" % upload_type, "yellow")
    print colored("[---  DUMP   ---] UPLOAD ID   : %s" % upload_id, "yellow")

    if upload_type and upload_id:
        if upload_type == "document":
            instance = get_object_or_None(
                AttachedDocument,
                id=upload_id,
                )
        elif upload_type == "image":
            instance = get_object_or_None(
                AttachedImage,
                id=upload_id,
                )
        elif upload_type == "temp":
            instance = get_object_or_None(
                TemporaryFile,
                id=upload_id,
                )

        if instance:
            try:
                instance.file.delete()
            except:
                pass

            instance.delete()
            found = True

    print colored("[---  DUMP   ---] DELETED     : %s" % found, "yellow")

    return HttpResponse(
        json.dumps({
            "deleted":  found,
        }),
        content_type="application/json"
        )


@login_required
@require_http_methods(["POST", ])
def remove_link(request):
    """Remove Link."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    found = False

    upload_type = request.POST.get("type")
    upload_id = request.POST.get("id")

    print colored("[---  DUMP   ---] UPLOAD TYPE : %s" % upload_type, "yellow")
    print colored("[---  DUMP   ---] UPLOAD ID   : %s" % upload_id, "yellow")

    if upload_type and upload_id:
        if upload_type == "regular":
            instance = get_object_or_None(
                AttachedUrl,
                id=upload_id,
                )
        elif upload_type == "video":
            instance = get_object_or_None(
                AttachedVideoUrl,
                id=upload_id,
                )

        if instance:
            instance.delete()
            found = True

    print colored("[---  DUMP   ---] DELETED     : %s" % found, "yellow")

    return HttpResponse(
        json.dumps({
            "deleted":  found,
        }),
        content_type="application/json"
        )
