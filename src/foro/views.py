import inspect

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
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

from foro.forms import (
    CreateEditForumForm,
    CreateEditTopicForm,
    CreateEditTopicPostForm,
    )
from foro.models import (
    Section,
    Forum,
    Topic,
    Post,
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ DESKTOP
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -----------------------------------------------------------------------------
# --- Forums
# -----------------------------------------------------------------------------
@cache_page(60 * 5)
def forum_list(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Sections
    # -------------------------------------------------------------------------
    sections = Section.objects.all()

    return render(
        request, "forum/forum-list.html", {
            "sections":     sections,
        })


@staff_member_required
def forum_create(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditForumForm(
        request.POST or None, request.FILES or None,
        user=request.user,
        )

    if request.method == "POST":
        if form.is_valid():
            forum = form.save(commit=False)
            forum.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="new-forum-created",
                message="New Forum was created",
                data={
                    "author":   forum.author.email,
                    "title":    forum.title,
                },
                # timestamp=timezone.now(),
                targets={
                    "author":   forum.author,
                    "forum":    forum,
                },
                )

            return redirect("forum-list")

    return render(
        request, "forum/forum-create.html", {
            "form":     form,
        })


@staff_member_required
def forum_edit(request, forum_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Forum
    # -------------------------------------------------------------------------
    forum = get_object_or_404(
        Forum,
        id=forum_id,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditForumForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=forum,
        )

    if request.method == "POST":
        if form.is_valid():
            forum = form.save(commit=False)
            forum.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="forum-edited",
                message="Forum was edited",
                data={
                    "user":     request.user.email,
                    "author":   forum.author.email,
                    "title":    forum.title,
                },
                # timestamp=timezone.now(),
                targets={
                    "user":     request.user,
                    "author":   forum.author,
                    "forum":    forum,
                },
                )

            return redirect("forum-list")

    return render(
        request, "forum/forum-edit.html", {
            "forum":    forum,
            "form":     form,
        })


# -----------------------------------------------------------------------------
# --- Topics
# -----------------------------------------------------------------------------
@cache_page(60 * 5)
def topic_list(request, forum_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Forum
    # -------------------------------------------------------------------------
    forum = get_object_or_404(
        Forum,
        id=forum_id,
    )

    # -------------------------------------------------------------------------
    # --- Retrieve Forum Topics
    # -------------------------------------------------------------------------
    topics = Topic.objects.filter(
        forum=forum,
    ).order_by("-created")

    return render(
        request, "forum/topic-list.html", {
            "forum":    forum,
            "topics":   topics,
        })


@login_required
def topic_create(request, forum_id):
    """Docstring."""
    # -------------------------------------------------------------------------
    # --- Retrieve Forum
    # -------------------------------------------------------------------------
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Forum
    # -------------------------------------------------------------------------
    forum = get_object_or_404(
        Forum,
        id=forum_id,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditTopicForm(
        request.POST or None, request.FILES or None,
        user=request.user, forum=forum)

    if request.method == "POST":
        if form.is_valid():
            topic = form.save(commit=False)
            topic.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="forum-topic-created",
                message="Forum Topic was created",
                data={
                    "author":   topic.author.email,
                    "title":    topic.title,
                },
                # timestamp=timezone.now(),
                targets={
                    "author":   topic.author,
                    "forum":    forum,
                    "topic":    topic,
                },
                )

            return HttpResponseRedirect(
                reverse("topic-list", kwargs={
                    "forum_id":     forum.id,
                }))

    return render(
        request, "forum/topic-create.html", {
            "forum":    forum,
            "form":     form,
        })


@staff_member_required
def topic_edit(request, forum_id, topic_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Topic
    # -------------------------------------------------------------------------
    topic = get_object_or_404(
        Topic,
        id=topic_id,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditTopicForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=topic)

    if request.method == "POST":
        if form.is_valid():
            topic = form.save(commit=False)
            topic.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="forum-topic-edited",
                message="Forum Topic was edited",
                data={
                    "user":     request.user.email,
                    "author":   topic.author.email,
                    "title":    topic.title,
                },
                # timestamp=timezone.now(),
                targets={
                    "user":     request.user,
                    "author":   topic.author,
                    "forum":    topic.forum,
                    "topic":    topic,
                },
                )

            return HttpResponseRedirect(
                reverse("topic-list", kwargs={
                    "forum_id":     forum_id,
                }))

    return render(
        request, "forum/topic-edit.html", {
            "topic":    topic,
            "form":     form,
        })


# -----------------------------------------------------------------------------
# --- Posts
# -----------------------------------------------------------------------------
@cache_page(60 * 5)
def topic_post_list(request, forum_id, topic_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Topic
    # -------------------------------------------------------------------------
    topic = get_object_or_404(
        Topic,
        id=topic_id,
    )

    # -------------------------------------------------------------------------
    # --- Retrieve Posts
    # -------------------------------------------------------------------------
    posts = Post.objects.filter(
        topic=topic,
        level=0,
    ).order_by("created")

    return render(
        request, "forum/topic-post-list.html", {
            "topic":    topic,
            "nodes":    posts,
        })


@login_required
def topic_post_create(request, forum_id, topic_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Topic
    # -------------------------------------------------------------------------
    topic = get_object_or_404(
        Topic,
        id=topic_id,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditTopicPostForm(
        request.POST or None, request.FILES or None,
        user=request.user, topic=topic)

    if request.method == "POST":
        if form.is_valid():
            topic_post = form.save(commit=False)
            topic_post.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="forum-topic-post-created",
                message="Forum Topic Post was created",
                data={
                    "author":   topic_post.author.email,
                    "title":    topic_post.title,
                },
                # timestamp=timezone.now(),
                targets={
                    "author":   topic_post.author,
                    "forum":    topic.forum,
                    "topic":    topic,
                    "post":     topic_post,
                },
                )

            return HttpResponseRedirect(
                reverse("topic-post-list", kwargs={
                    "forum_id":     forum_id,
                    "topic_id":     topic.id,
                }))

    return render(
        request, "forum/topic-post-create.html", {
            "topic":    topic,
            "form":     form,
        })


@staff_member_required
def topic_post_edit(request, topic_post_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Topic
    # -------------------------------------------------------------------------
    topic = get_object_or_404(
        Topic,
        id=topic_post_id,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditTopicForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=topic)

    if request.method == "POST":
        if form.is_valid():
            topic = form.save(commit=False)
            topic.save()

            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="forum-topic-post-edited",
                message="Forum Topic Post was edited",
                data={
                    "user":     request.user.email,
                    "author":   topic.author.email,
                    "title":    topic.title,
                },
                # timestamp=timezone.now(),
                targets={
                    "user":     request.user,
                    "author":   topic.author,
                    "forum":    topic.forum,
                    "topic":    topic,
                    "post":     topic,
                },
                )

            return HttpResponseRedirect(
                reverse("topic-list", kwargs={
                    "forum_id":     topic.forum_id,
                }))

    return render(
        request, "forum/topic-post-edit.html", {
            "topic":    topic,
            "form":     form,
        })


@login_required
def topic_post_reply(request, forum_id, topic_id, topic_post_id):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Topic
    # -------------------------------------------------------------------------
    topic = get_object_or_404(
        Topic,
        id=topic_id,
    )

    # -------------------------------------------------------------------------
    # --- Retrieve Post
    # -------------------------------------------------------------------------
    topic_post = get_object_or_404(
        Post,
        id=topic_post_id,
    )

    # -------------------------------------------------------------------------
    # --- Limit the Depth (Level) of the nested Entries
    if topic_post.level >= 5:
        raise Http404

    # -------------------------------------------------------------------------
    # --- Prepare Form(s)
    # -------------------------------------------------------------------------
    form = CreateEditTopicPostForm(
        request.POST or None, request.FILES or None,
        user=request.user, topic=topic, parent=topic_post)

    if request.method == "POST":
        if form.is_valid():
            topic_post = form.save(commit=False)
            topic_post.save()

            return HttpResponseRedirect(
                reverse("topic-post-list", kwargs={
                    "forum_id":     forum_id,
                    "topic_id":     topic.id,
                }))

    return render(
        request, "forum/topic-post-create.html", {
            "topic":    topic,
            "form":     form,
        })
