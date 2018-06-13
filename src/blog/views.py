import inspect
import json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
    )
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    )
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
    )
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods

import papertrail

from termcolor import colored

from blog.choices import POST_STATUS
from blog.forms import CreateEditPostForm
from blog.models import Post
from core.helpers import form_field_error_list


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ DESKTOP
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@cache_page(60 * 5)
def post_list(request):
    """List of the all Blog Posts."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Blog Posts
    # -------------------------------------------------------------------------
    if request.user.is_staff:
        posts = Post.objects.filter(
            status__in=[
                POST_STATUS.VISIBLE,
                POST_STATUS.DRAFT,
            ]
        )
    else:
        posts = Post.objects.filter(
            status__in=[
                POST_STATUS.VISIBLE,
            ]
        )

    # -------------------------------------------------------------------------
    # --- Filter QuerySet by Tag ID
    # -------------------------------------------------------------------------
    tag_id = request.GET.get("tag", None)

    if tag_id:
        try:
            posts = posts.filter(
                tags__id=tag_id,
            ).distinct()
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

    # -------------------------------------------------------------------------
    # --- Slice the Post List
    # -------------------------------------------------------------------------
    posts = posts[:settings.MAX_POSTS_PER_QUERY]

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet
    # -------------------------------------------------------------------------
    paginator = Paginator(posts, settings.MAX_POSTS_PER_PAGE)

    page = request.GET.get("page")

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If page is our of range (e.g. 9999), deliver last page of
        #     results.
        posts = paginator.page(paginator.num_pages)

    return render(
        request, "blog/post-list.html", {
            "posts":        posts,
            "page_total":   paginator.num_pages,
            "page_number":  posts.number,
        })


@staff_member_required
def post_create(request):
    """Create the Post."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditPostForm(
        request.POST or None, request.FILES or None,
        user=request.user)

    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()

            # -----------------------------------------------------------------
            # --- Render HTML Email Content
            if "post-draft" in request.POST:
                post.status = POST_STATUS.DRAFT
                # -------------------------------------------------------------
                # --- TODO: Send confirmation Email
            else:
                post.status = POST_STATUS.VISIBLE
                # -------------------------------------------------------------
                # --- TODO: Send confirmation Email

            post.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="new-post-created",
                message="New Post created",
                data={
                    "author":   post.author.email,
                    "title":    post.title,
                    "status":   post.status,
                },
                # timestamp=timezone.now(),
                targets={
                    "author":   post.author,
                    "post":     post,
                },
                )

            return redirect("post-list")

        # ---------------------------------------------------------------------
        # --- Failed to create the Post
        # --- Save the Log
        papertrail.log(
            event_type="post-create-failed",
            message="Post create failed",
            data={
                "form":     form_field_error_list(form),
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
            },
            )

    return render(
        request, "blog/post-create.html", {
            "form":     form,
        })


@cache_page(60 * 1)
def post_details(request, slug):
    """Post Details."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Blog Post
    # -------------------------------------------------------------------------
    post = get_object_or_404(
        Post,
        slug=slug,
    )

    if post.is_closed:
        raise Http404

    # -------------------------------------------------------------------------
    # --- Increment Views Counter
    # -------------------------------------------------------------------------
    post.increase_views_count(request)

    return render(
        request, "blog/post-details.html", {
            "post":     post,
        })


@staff_member_required
def post_edit(request, slug):
    """Edit the Post."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Blog Post
    # -------------------------------------------------------------------------
    post = get_object_or_404(
        Post,
        slug=slug,
    )

    if post.is_closed:
        raise Http404

    form = CreateEditPostForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=post)

    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()

            # -----------------------------------------------------------------
            # --- TODO: Send confirmation Email

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="post-edited",
                message="Post was edited",
                data={
                    "user":     request.user.email,
                    "author":   post.author.email,
                    "title":    post.title,
                    "status":   post.status,
                },
                # timestamp=timezone.now(),
                targets={
                    "user":     request.user,
                    "author":   post.author,
                    "post":     post,
                },
                )

            return HttpResponseRedirect(
                reverse("post-details", kwargs={
                    "slug":     post.slug,
                }))

        # ---------------------------------------------------------------------
        # --- Failed to save the Post
        # --- Save the Log
        papertrail.log(
            event_type="post-save-failed",
            message="Post save failed",
            data={
                "form":     form_field_error_list(form),
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
                "post":     post,
            },
            )

    return render(
        request, "blog/post-edit.html", {
            "form":     form,
            "post":     post,
        })
