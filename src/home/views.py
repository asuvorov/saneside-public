import inspect

from itertools import chain
from operator import attrgetter

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip import GeoIP
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
    )
from django.views.decorators.cache import cache_page

from termcolor import colored

from accounts.models import (
    Team,
    TeamMember,
    )
from blog.models import Post
from challenges.models import Challenge
from core.utils import get_client_ip
from home.forms import (
    ContactUsForm,
    CreateEditFAQForm,
    )
from home.models import (
    Partner,
    Section,
    FAQ,
    )
from organizations.models import Organization


# -----------------------------------------------------------------------------
# --- Index
# -----------------------------------------------------------------------------
@cache_page(60 * 60)
def index(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    g = GeoIP()
    ip = get_client_ip(request)
    # ip = "108.162.209.69"
    country = g.country(ip)
    city = g.city(ip)

    print colored("[---  DUMP   ---] COUNTRY : %s" % country, "yellow")
    print colored("[---  DUMP   ---] CITY    : %s" % city, "yellow")

    timeline_qs = []
    timeline_qs = sorted(
        chain(
            Post.objects.all(),
            Challenge.objects.get_upcoming(),
            Organization.objects.filter(
                is_hidden=False,
                is_deleted=False,
            )
        ),
        key=attrgetter("created"))[:10]

    return render(
        request, "home/index.html", {
            "timeline_qs":  timeline_qs,
        })


@cache_page(60 * 60 * 24)
def privacy_policy(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(
        request, "home/privacy-policy.html", {})


@cache_page(60 * 60 * 24)
def user_agreement(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(
        request, "home/user-agreement.html", {})


@cache_page(60 * 60 * 24)
def our_team(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    teams = Team.objects.all()
    members = TeamMember.objects.all()

    return render(
        request, "home/our-team.html", {
            "teams":    teams,
            "members":  members,
        })


@cache_page(60 * 60 * 24)
def our_partners(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    partners = Partner.objects.all()

    print ">>> PARTNERS : %s" % partners

    return render(
        request, "home/our-partners.html", {
            "partners":     partners,
        })


@cache_page(60 * 60 * 24)
def about_us(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(
        request, "home/about-us.html", {})


def contact_us(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    # --- Form is being sent via POST Request.
    form = ContactUsForm(
        request.POST or None, request.FILES or None)

    return render(
        request, "home/contact-us.html", {
            "form":     form,
        })


# -----------------------------------------------------------------------------
# --- FAQ
# -----------------------------------------------------------------------------
@cache_page(60 * 5)
def faq(request):
    """List of FAQs."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Sections
    # -------------------------------------------------------------------------
    sections = Section.objects.all()

    return render(
        request, "home/faq-list.html", {
            "sections":     sections,
        })


@login_required
@staff_member_required
def faq_create(request):
    """Create FAQ."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    form = CreateEditFAQForm(
        request.POST or None, request.FILES or None,
        user=request.user)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(
                reverse("faq"))

    return render(
        request, "home/faq-create.html", {
            "form":     form,
        })


@login_required
@staff_member_required
def faq_edit(request, faq_id):
    """Edit FAQ."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve FAQ
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    faq = get_object_or_404(
        FAQ,
        id=faq_id,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    form = CreateEditFAQForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=faq,
        )

    if request.method == "POST":
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(
                reverse("faq"))

    return render(
        request, "home/faq-edit.html", {
            "form":     form,
            "faq":      faq,
        })


# -----------------------------------------------------------------------------
# --- Feature Test
# -----------------------------------------------------------------------------
@login_required
@staff_member_required
def feature(request):
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    return render(
        request, "home/feature.html", {})
