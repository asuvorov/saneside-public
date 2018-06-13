import datetime
import inspect
import logging
import mimetypes

from django.conf import settings
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
    )
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geoip import GeoIP
from django.core.files import File
from django.core.files.storage import default_storage as storage
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
    )
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
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import papertrail

from annoying.functions import get_object_or_None
from termcolor import colored
from url_tools.helper import UrlHelper

from accounts.utils import is_challenge_admin
from accounts.views import is_profile_complete
from challenges.choices import (
    CHALLENGE_STATUS,
    CHALLENGE_MODE,
    PARTICIPATION_STATUS,
    RECURRENCE,
    )
from challenges.decorators import (
    challenge_access_check_required,
    challenge_org_staff_member_required,
    )
from challenges.forms import (
    CreateEditChallengeForm,
    AddChallengeMaterialsForm,
    RoleFormSet,
    FilterChallengeForm,
    )
from challenges.helpers import get_challenge_list
from challenges.models import (
    Category,
    Challenge,
    Participation,
    Role,
    )
from core.forms import (
    AddressForm,
    SocialLinkFormSet,
    )
from core.helpers import form_field_error_list
from core.models import (
    AttachedDocument,
    AttachedImage,
    AttachedUrl,
    AttachedVideoUrl,
    Rating,
    SocialLink,
    )
from core.utils import (
    get_client_ip,
    get_website_title,
    get_youtube_video_id,
    validate_url,
    )


logger = logging.getLogger("py.warnings")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE LIST
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@cache_page(60 * 5)
def challenge_list(request):
    """List of the all Challenges."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve Data from the Request.
    # -------------------------------------------------------------------------
    category_slug = request.GET.get("cat", None)

    print colored("[---  DUMP   ---] CATEGORY SLUG : %s" % category_slug, "yellow")

    # -------------------------------------------------------------------------
    # --- Retrieve Challenge List.
    # -------------------------------------------------------------------------
    challenges = get_challenge_list(request).filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=datetime.date.today(),
    ).exclude(
        recurrence=RECURRENCE.DATELESS,
    )

    if category_slug:
        category = get_object_or_None(
            Category,
            slug=category_slug,
            )

        if category:
            challenges = challenges.filter(
                category=category.category,
                )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    filter_form = FilterChallengeForm(
        request.GET or None, request.FILES or None,
        qs=challenges)

    # -------------------------------------------------------------------------
    # --- Filter QuerySet by Tag ID.
    # -------------------------------------------------------------------------
    tag_id = request.GET.get("tag", None)

    if tag_id:
        try:
            challenges = challenges.filter(
                tags__id=tag_id,
            ).distinct()
        except Exception as e:
            print colored("###" * 27, "white", "on_red")
            print colored("### EXCEPTION @ `{module}`: {msg}".format(
                module=inspect.stack()[0][3],
                msg=str(e),
                ), "white", "on_red")

    # -------------------------------------------------------------------------
    # --- Slice the Challenge List.
    # -------------------------------------------------------------------------
    challenges = challenges[:settings.MAX_CHALLENGES_PER_QUERY]

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(
        challenges,
        settings.MAX_CHALLENGES_PER_PAGE)

    page = request.GET.get("page")

    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        challenges = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        challenges = paginator.page(paginator.num_pages)

    return render(
        request, "challenges/challenge-list.html", {
            "challenges":   challenges,
            "page_title":   _("All Challenges"),
            "page_total":   paginator.num_pages,
            "page_number":  challenges.number,
            "filter_form":  filter_form,
        })


@cache_page(60 * 5)
def challenge_near_you_list(request):
    """List of the Challenges, near the User."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    g = GeoIP()
    ip = get_client_ip(request)
    # ip = "108.162.209.69"
    country = g.country(ip)
    city = g.city(ip)

    print colored("[---  DUMP   ---] COUNTRY : %s" % country, "yellow")
    print colored("[---  DUMP   ---] CITY    : %s" % city, "yellow")

    # -------------------------------------------------------------------------
    # --- Retrieve Challenge List.
    # -------------------------------------------------------------------------
    challenges = get_challenge_list(request).filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=datetime.date.today(),
    ).exclude(
        recurrence=RECURRENCE.DATELESS,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    filter_form = FilterChallengeForm(
        request.GET or None, request.FILES or None,
        qs=challenges)

    # -------------------------------------------------------------------------
    # --- Challenges near.
    #     According to the Location, specified in the User Profile.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated() and request.user.profile.address:
        # ---------------------------------------------------------------------
        # --- Filter by Country and City
        if (
                request.user.profile.address.country and
                request.user.profile.address.city):
            challenges = challenges.filter(
                address__country=request.user.profile.address.country,
                address__city__icontains=request.user.profile.address.city,
                )
        # ---------------------------------------------------------------------
        # --- Filter by Province and Zip Code
        elif (
                request.user.profile.address.province and
                request.user.profile.address.zip_code):
            challenges = challenges.filter(
                address__province__icontains=request.user.profile.address.province,
                address__zip_code=request.user.profile.address.zip_code,
                )
        else:
            challenges = []
    elif city:
        # ---------------------------------------------------------------------
        # --- Filter by Country and City
        if city["country_code"]:
            challenges = challenges.filter(
                address__country=city["country_code"],
            )

        if city["city"]:
            challenges = challenges.filter(
                address__city__icontains=city["city"],
            )
    else:
        challenges = []

    # -------------------------------------------------------------------------
    # --- Filter QuerySet by Tag ID.
    # -------------------------------------------------------------------------
    tag_id = request.GET.get("tag", None)

    if tag_id:
        try:
            challenges = challenges.filter(
                tags__id=tag_id,
            ).distinct()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # --- Slice the Challenge List.
    # -------------------------------------------------------------------------
    challenges = challenges[:settings.MAX_CHALLENGES_PER_QUERY]

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(challenges, settings.MAX_CHALLENGES_PER_PAGE)

    page = request.GET.get("page")

    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        challenges = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        challenges = paginator.page(paginator.num_pages)

    return render(
        request, "challenges/challenge-list.html", {
            "challenges":   challenges,
            "page_title":   _("Challenges near you"),
            "page_total":   paginator.num_pages,
            "page_number":  challenges.number,
            "filter_form":  filter_form,
        })


@cache_page(60 * 5)
def challenge_new_list(request):
    """List of the new Challenges."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- New Challenges.
    #     Date created is less than 1 Day ago.
    # -------------------------------------------------------------------------
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=1)

    challenges = get_challenge_list(request).filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=datetime.date.today(),
        created__gte=time_threshold,
    ).exclude(
        recurrence=RECURRENCE.DATELESS,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    filter_form = FilterChallengeForm(
        request.GET or None, request.FILES or None,
        qs=challenges)

    # -------------------------------------------------------------------------
    # --- Filter QuerySet by Tag ID.
    # -------------------------------------------------------------------------
    tag_id = request.GET.get("tag", None)

    if tag_id:
        try:
            challenges = challenges.filter(
                tags__id=tag_id,
            ).distinct()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # --- Slice the Challenge List.
    # -------------------------------------------------------------------------
    challenges = challenges[:settings.MAX_CHALLENGES_PER_QUERY]

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(challenges, settings.MAX_CHALLENGES_PER_PAGE)

    page = request.GET.get("page")

    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        challenges = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        challenges = paginator.page(paginator.num_pages)

    return render(
        request, "challenges/challenge-list.html", {
            "challenges":   challenges,
            "page_title":   _("New Challenges"),
            "page_total":   paginator.num_pages,
            "page_number":  challenges.number,
            "filter_form":  filter_form,
        })


@cache_page(60 * 5)
def challenge_dateless_list(request):
    """List of the dateless Challenges."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    challenges = get_challenge_list(request).filter(
        status=CHALLENGE_STATUS.UPCOMING,
        recurrence=RECURRENCE.DATELESS,
        )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    filter_form = FilterChallengeForm(
        request.GET or None, request.FILES or None,
        qs=challenges)

    # -------------------------------------------------------------------------
    # --- Filter QuerySet by Tag ID.
    # -------------------------------------------------------------------------
    tag_id = request.GET.get("tag", None)

    if tag_id:
        try:
            challenges = challenges.filter(
                tags__id=tag_id,
            ).distinct()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # --- Slice the Challenge List.
    # -------------------------------------------------------------------------
    challenges = challenges[:settings.MAX_CHALLENGES_PER_QUERY]

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(challenges, settings.MAX_CHALLENGES_PER_PAGE)

    page = request.GET.get("page")

    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        challenges = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        challenges = paginator.page(paginator.num_pages)

    return render(
        request, "challenges/challenge-dateless-list.html", {
            "challenges":   challenges,
            "page_title":   _("Dateless Challenges"),
            "page_total":   paginator.num_pages,
            "page_number":  challenges.number,
            "filter_form":  filter_form,
        })


@cache_page(60 * 5)
def challenge_featured_list(request):
    """List of the featured Challenges."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    challenges = get_challenge_list(request).filter(
        status=CHALLENGE_STATUS.UPCOMING,
        start_date__gte=datetime.date.today(),
    ).exclude(
        recurrence=RECURRENCE.DATELESS,
    )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    filter_form = FilterChallengeForm(
        request.GET or None, request.FILES or None,
        qs=challenges)

    # -------------------------------------------------------------------------
    # --- Filter QuerySet by Tag ID.
    # -------------------------------------------------------------------------
    tag_id = request.GET.get("tag", None)

    if tag_id:
        try:
            challenges = challenges.filter(
                tags__id=tag_id,
            ).distinct()
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # --- Slice the Challenge List.
    # -------------------------------------------------------------------------
    challenges = challenges[:settings.MAX_CHALLENGES_PER_QUERY]

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(challenges, settings.MAX_CHALLENGES_PER_PAGE)

    page = request.GET.get("page")

    try:
        challenges = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        challenges = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        challenges = paginator.page(paginator.num_pages)

    return render(
        request, "challenges/challenge-list.html", {
            "challenges":   challenges,
            "page_title":   _("Featured Challenges"),
            "page_total":   paginator.num_pages,
            "page_number":  challenges.number,
            "filter_form":  filter_form,
        })


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE CATEGORY LIST
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@cache_page(60 * 5)
def challenge_category_list(request):
    """List of the all Challenge Categories."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # ---- Retrieve Category List.
    # -------------------------------------------------------------------------
    categories = Category.objects.all()

    return render(
        request, "challenges/challenge-category-list.html", {
            "categories":   categories,
        })


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE CREATE
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@login_required
@user_passes_test(is_profile_complete, login_url="/accounts/my-profile/")
def challenge_create(request):
    """Create the Challenge."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------
    url = UrlHelper(request.get_full_path())
    query_dict = dict(url.query_dict)

    print colored("[---  DUMP   ---] URL HELPER : %s" % dict(url.query_dict), "yellow")

    # -------------------------------------------------------------------------
    # --- Retrieve the Data from the GET Request.
    # -------------------------------------------------------------------------
    organization_ids = map(int, query_dict.get("organization", []))

    print colored("[---  DUMP   ---] ORGANIZATION : %s" % organization_ids, "yellow")

    # -------------------------------------------------------------------------
    # --- Geo IP.
    # -------------------------------------------------------------------------
    g = GeoIP()
    ip = get_client_ip(request)
    country_code = g.country_code(ip)

    tz_name = request.session.get("django_timezone")

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    form = CreateEditChallengeForm(
        request.POST or None, request.FILES or None,
        user=request.user, organization_ids=organization_ids, tz_name=tz_name)
    aform = AddressForm(
        request.POST or None, request.FILES or None,
        required=False if request.POST.get("addressless", False) else True,
        country_code=country_code)

    formset_roles = RoleFormSet(
        request.POST or None, request.FILES or None,
        prefix="roles",
        queryset=Role.objects.none())
    formset_social = SocialLinkFormSet(
        request.POST or None, request.FILES or None,
        prefix="socials",
        queryset=SocialLink.objects.none())

    if request.method == "POST":
        print colored("[---  DUMP   ---]  FORM           : %s" % form.is_valid(), "yellow")
        print colored("[---  DUMP   ---] AFORM           : %s" % aform.is_valid(), "yellow")
        print colored("[---  DUMP   ---]  FORMSET ROLES  : %s" % formset_roles.is_valid(), "yellow")
        print colored("[---  DUMP   ---]  FORMSET SOCIAL : %s" % formset_social.is_valid(), "yellow")

        if (
                form.is_valid() and
                aform.is_valid() and
                formset_roles.is_valid() and
                formset_social.is_valid()):
            challenge = form.save(commit=False)
            challenge.address = aform.save(commit=True)
            challenge.save()

            form.save_m2m()

            # -----------------------------------------------------------------
            # --- Save Roles.
            roles = formset_roles.save(commit=True)
            for role in roles:
                role.challenge = challenge
                role.save()

            # -----------------------------------------------------------------
            # --- Save Social Links.
            social_links = formset_social.save(commit=True)
            for social_link in social_links:
                social_link.content_type = ContentType.objects.get_for_model(challenge)
                social_link.object_id = challenge.id
                social_link.save()

            if "chl-draft" in request.POST:
                challenge.status = CHALLENGE_STATUS.DRAFT
                challenge.save()

                # -------------------------------------------------------------
                # --- Send Email Notification(s).
                challenge.email_notify_admin_chl_drafted(request)
            else:
                # -------------------------------------------------------------
                # --- Send Email Notification(s).
                challenge.email_notify_admin_chl_created(request)
                challenge.email_notify_alt_person_chl_created(request)
                challenge.email_notify_org_subscribers_chl_created(request)

            # -----------------------------------------------------------------
            # --- Save the Log.
            papertrail.log(
                event_type="new-challenge-created",
                message="New Challenge was created",
                data={
                    "author":       challenge.author.email,
                    "name":         challenge.name,
                    "status":       str(challenge.stat_status_name),
                },
                # timestamp=timezone.now(),
                targets={
                    "author":       challenge.author,
                    "challenge":    challenge,
                },
                )

            return HttpResponseRedirect(
                reverse("challenge-details", kwargs={
                    "slug":     challenge.slug,
                }))

        # ---------------------------------------------------------------------
        # --- Failed to create the Challenge
        # --- Save the Log
        papertrail.log(
            event_type="challenge-create-failed",
            message="Challenge create failed",
            data={
                "form":     form_field_error_list(form),
                "aform":    form_field_error_list(aform),
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
            },
            )

    return render(
        request, "challenges/challenge-create.html", {
            "form":             form,
            "aform":            aform,
            "formset_roles":    formset_roles,
            "formset_social":   formset_social,
        })


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE DETAILS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@cache_page(60 * 1)
@challenge_access_check_required
def challenge_details(request, slug):
    """Challenge Details."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------
    is_admin = False
    is_rated = False
    is_complained = False
    participation = None
    show_withdraw_form = False
    show_signup_form = False
    show_selfreflection_form = False
    show_not_participated_form = False
    show_rate_form = False
    show_complain_form = False

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge.
    # -------------------------------------------------------------------------
    challenge = get_object_or_404(
        Challenge,
        slug=slug,
    )

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge Social Links.
    # -------------------------------------------------------------------------
    social_links = SocialLink.objects.filter(
        content_type=ContentType.objects.get_for_model(challenge),
        object_id=challenge.id
    )

    # -------------------------------------------------------------------------
    # --- Only authenticated Users may sign up to the Challenge.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        # ---------------------------------------------------------------------
        # --- Check, if the User is a Challenge Admin.
        is_admin = is_challenge_admin(
            request.user,
            challenge)

        print colored("[---  DUMP   ---] IS ADMIN : %s" % is_admin, "yellow")

        if challenge.is_closed and not is_admin:
            raise Http404

        # ---------------------------------------------------------------------
        # --- Check, if the User has already rated the Challenge.
        is_rated = challenge.is_rated_by_user(
            request.user)

        # ---------------------------------------------------------------------
        # --- Check, if the User has already complained to the Challenge.
        is_complained = challenge.is_complained_by_user(
            request.user)

        # ---------------------------------------------------------------------
        # --- Retrieve User's Participation to the Challenge.
        participation = get_object_or_None(
            Participation,
            user=request.user,
            challenge=challenge,
        )

        if participation:
            # -----------------------------------------------------------------
            # --- If User already signed up for the Challenge, show withdraw
            #     the Participation Form.
            if (
                    participation.is_confirmed or
                    participation.is_waiting_for_confirmation):
                show_withdraw_form = True

            # -----------------------------------------------------------------
            # --- If User canceled the Participation, and it's allowed
            #     to apply again to the Challenge, show sign-up Form.
            if participation.is_cancelled_by_user and challenge.allow_reenter:
                show_signup_form = True

            if (
                    participation.is_waiting_for_selfreflection or
                    participation.is_selfreflection_rejected):
                show_selfreflection_form = True

            if participation.is_waiting_for_selfreflection:
                show_not_participated_form = True

            if (
                    not is_rated and (
                        participation.is_waiting_for_acknowledgement or
                        participation.is_acknowledged)):
                show_rate_form = True

            if (
                    not is_complained and (
                        participation.is_waiting_for_selfreflection or
                        participation.is_waiting_for_acknowledgement or
                        participation.is_acknowledged)):
                show_complain_form = True
        else:
            # -----------------------------------------------------------------
            # --- If the Participation isn't found, return sign-up Form.
            if not is_admin:
                show_signup_form = True

        # ---------------------------------------------------------------------
        # --- Lookup for submitted Forms.
        if request.method == "POST":
            # -----------------------------------------------------------------
            # --- Silent Refresh.
            return HttpResponseRedirect(
                reverse("challenge-details", kwargs={
                    "slug":     challenge.slug,
                }))
    else:
        # ---------------------------------------------------------------------
        # --- NOT authenticated Users are not allowed to view the Challenge
        #     Details Page, if the Challenge is:
        #     - Draft;
        #     - Complete;
        #     - Past due.
        if challenge.is_draft or challenge.is_happened or challenge.is_closed:
            raise Http404

    # -------------------------------------------------------------------------
    # --- Prepare the Challenge Roles Breakdown.
    # -------------------------------------------------------------------------
    roles_breakdown = []

    if challenge.challenge_roles.all():
        for role in challenge.challenge_roles.all():
            roles_breakdown.append({
                "name":         role.name,
                "required":     role.quantity,
                "applied":      role.role_participations.filter(
                    status__in=[
                        PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
                        PARTICIPATION_STATUS.CONFIRMATION_DENIED,
                        PARTICIPATION_STATUS.CONFIRMED,
                    ],
                ).count(),
                "rejected":     role.role_participations.filter(
                    status=PARTICIPATION_STATUS.CONFIRMATION_DENIED,
                ).count(),
                "confirmed":    role.role_participations.filter(
                    status=PARTICIPATION_STATUS.CONFIRMED,
                ).count(),
            })

    # -------------------------------------------------------------------------
    # --- Is newly created?
    #     If so, show the pop-up Overlay.
    # -------------------------------------------------------------------------
    is_newly_created = False

    if (
            challenge.author == request.user and
            challenge.status == CHALLENGE_STATUS.UPCOMING and
            challenge.is_newly_created):
        is_newly_created = True

        challenge.is_newly_created = False
        challenge.save()

    # -------------------------------------------------------------------------
    # --- Increment Views Counter.
    # -------------------------------------------------------------------------

    return render(
        request, "challenges/challenge-details-info.html", {
            "challenge":                    challenge,
            "participation":                participation,
            "is_admin":                     is_admin,
            "show_withdraw_form":           show_withdraw_form,
            "show_signup_form":             show_signup_form,
            "show_selfreflection_form":     show_selfreflection_form,
            "show_not_participated_form":   show_not_participated_form,
            "show_rate_form":               show_rate_form,
            "show_complain_form":           show_complain_form,
            "is_newly_created":             is_newly_created,
            "roles_breakdown":              roles_breakdown,
            "social_links":                 social_links,
        })


@cache_page(60 * 1)
@challenge_access_check_required
def challenge_confirm(request, slug):
    """Challenge Details."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------
    is_admin = False

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge.
    # -------------------------------------------------------------------------
    challenge = get_object_or_404(
        Challenge,
        slug=slug,
    )

    # -------------------------------------------------------------------------
    # --- Only authenticated Users may sign up to the Challenge.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        # ---------------------------------------------------------------------
        # --- Check, if the User is a Challenge Admin.
        is_admin = is_challenge_admin(
            request.user,
            challenge)

        print colored("[---  DUMP   ---] IS ADMIN : %s" % is_admin, "yellow")

    return render(
        request, "challenges/challenge-details-confirm.html", {
            "challenge":    challenge,
            "is_admin":     is_admin,
        })


@cache_page(60 * 1)
@challenge_access_check_required
def challenge_acknowledge(request, slug):
    """Challenge Details."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------
    is_admin = False

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge.
    # -------------------------------------------------------------------------
    challenge = get_object_or_404(
        Challenge,
        slug=slug,
    )

    # -------------------------------------------------------------------------
    # --- Only authenticated Users may sign up to the Challenge.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        # ---------------------------------------------------------------------
        # --- Check, if the User is a Challenge Admin.
        is_admin = is_challenge_admin(
            request.user,
            challenge)

        print colored("[---  DUMP   ---] IS ADMIN : %s" % is_admin, "yellow")

    return render(
        request, "challenges/challenge-details-acknowledge.html", {
            "challenge":    challenge,
            "is_admin":     is_admin,
        })


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ CHALLENGE EDIT
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@login_required
@challenge_org_staff_member_required
def challenge_edit(request, slug):
    """Edit Challenge."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge.
    # -------------------------------------------------------------------------
    challenge = get_object_or_404(
        Challenge,
        slug=slug,
    )

    # -------------------------------------------------------------------------
    # --- Completed or closed (deleted) Challenges cannot be modified.
    # -------------------------------------------------------------------------
    if challenge.is_complete or challenge.is_closed:
        raise Http404

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    form = CreateEditChallengeForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=challenge)
    aform = AddressForm(
        request.POST or None, request.FILES or None,
        required=False if request.POST.get("addressless", False) else True,
        instance=challenge.address)

    formset_roles = RoleFormSet(
        request.POST or None, request.FILES or None,
        prefix="roles",
        queryset=Role.objects.filter(
            challenge=challenge,
            ))
    formset_social = SocialLinkFormSet(
        request.POST or None, request.FILES or None,
        prefix="socials",
        queryset=SocialLink.objects.filter(
            content_type=ContentType.objects.get_for_model(challenge),
            object_id=challenge.id
            ))

    # print colored("[---  DUMP   ---] REQUEST POST : %s" % request.POST, "yellow")

    if request.method == "POST":
        print colored("[---  DUMP   ---]  FORM           : %s" % form.is_valid(), "yellow")
        print colored("[---  DUMP   ---] AFORM           : %s" % aform.is_valid(), "yellow")
        print colored("[---  DUMP   ---]  FORMSET ROLES  : %s" % formset_roles.is_valid(), "yellow")
        print colored("[---  DUMP   ---]  FORMSET SOCIAL : %s" % formset_social.is_valid(), "yellow")

        if (
                form.is_valid() and
                aform.is_valid() and
                formset_roles.is_valid() and
                formset_social.is_valid()):
            form.save()
            form.save_m2m()

            challenge.address = aform.save(commit=True)
            challenge.save()

            # -----------------------------------------------------------------
            # --- Save Roles.
            roles = formset_roles.save(commit=True)
            for role in roles:
                role.challenge = challenge
                role.save()

            # -----------------------------------------------------------------
            # --- Save Social Links.
            social_links = formset_social.save(commit=True)
            for social_link in social_links:
                social_link.content_type = ContentType.objects.get_for_model(challenge)
                social_link.object_id = challenge.id
                social_link.save()

            # -----------------------------------------------------------------
            # --- Move temporary Files to real Challenge Images/Documents.
            for tmp_file in form.cleaned_data["tmp_files"]:
                mime_type = mimetypes.guess_type(tmp_file.file.name)[0]

                if mime_type in settings.UPLOADER_SETTINGS["images"]["CONTENT_TYPES"]:
                    AttachedImage.objects.create(
                        name=tmp_file.name,
                        image=File(storage.open(tmp_file.file.name, "rb")),
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )
                elif mime_type in settings.UPLOADER_SETTINGS["documents"]["CONTENT_TYPES"]:
                    AttachedDocument.objects.create(
                        name=tmp_file.name,
                        document=File(storage.open(tmp_file.file.name, "rb")),
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )

                tmp_file.delete()

            # -----------------------------------------------------------------
            # --- Save URLs and Video URLs and pull their Titles.
            for link in request.POST["tmp_links"].split():
                url = validate_url(link)

                if get_youtube_video_id(link):
                    AttachedVideoUrl.objects.create(
                        url=link,
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )
                elif url:
                    AttachedUrl.objects.create(
                        url=url,
                        title=get_website_title(url) or "",
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )

            # -----------------------------------------------------------------
            # --- Send Email Notification(s).
            challenge.email_notify_admin_chl_edited(request)
            challenge.email_notify_alt_person_chl_edited(request)

            # -----------------------------------------------------------------
            # --- Is Date/Time changed?
            if (
                    "start_date" in form.changed_data or
                    "start_time" in form.changed_data):
                Participation.email_notify_participants_datetime_chl_edited(
                    request=request,
                    challenge=challenge)

            # -----------------------------------------------------------------
            # --- Is Application changed?
            if (
                    "application" in form.changed_data and
                    challenge.is_free_for_all):
                Participation.email_notify_participants_application_chl_edited(
                    request=request,
                    challenge=challenge)

            # -----------------------------------------------------------------
            # --- Is Location changed?
            if (
                    "address_1" in form.changed_data or
                    "address_2" in form.changed_data or
                    "city" in form.changed_data or
                    "zip_code" in form.changed_data or
                    "province" in form.changed_data or
                    "country" in form.changed_data):
                Participation.email_notify_participants_location_chl_edited(
                    request=request,
                    challenge=challenge)

            # -----------------------------------------------------------------
            # --- Save the Log.
            papertrail.log(
                event_type="challenge-edited",
                message="Challenge was edited",
                data={
                    "admin":        request.user.email,
                    "author":       challenge.author.email,
                    "name":         challenge.name,
                    "status":       str(challenge.stat_status_name),
                },
                # timestamp=timezone.now(),
                targets={
                    "admin":        request.user,
                    "author":       challenge.author,
                    "challenge":    challenge,
                },
                )

            return HttpResponseRedirect(
                reverse("challenge-details", kwargs={
                    "slug":     challenge.slug,
                }))

        # ---------------------------------------------------------------------
        # --- Failed to edit the Challenge
        # --- Save the Log
        papertrail.log(
            event_type="challenge-edit-failed",
            message="Challenge edit failed",
            data={
                "form":     form_field_error_list(form),
                "aform":    form_field_error_list(aform),
            },
            # timestamp=timezone.now(),
            targets={
                "user":         request.user,
                "challenge":    challenge,
            },
            )

    return render(
        request, "challenges/challenge-edit.html", {
            "form":             form,
            "aform":            aform,
            "formset_roles":    formset_roles,
            "formset_social":   formset_social,
            "challenge":        challenge,
        })


@login_required
@challenge_org_staff_member_required
def challenge_reporting_materials(request, slug):
    """Add Challenge reporting Materials."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Retrieve the Challenge.
    # -------------------------------------------------------------------------
    challenge = get_object_or_404(
        Challenge,
        slug=slug,
    )

    # -------------------------------------------------------------------------
    # --- Organizer can add reporting Materials only if Challenge is completed.
    #     Closed (deleted) Challenge cannot be modified.
    # -------------------------------------------------------------------------
    if not challenge.is_complete or challenge.is_closed:
        raise Http404

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    form = AddChallengeMaterialsForm(
        request.POST or None, request.FILES or None,
        instance=challenge)

    # print colored("[---  DUMP   ---] REQUEST POST : %s" % request.POST, "yellow")

    if request.method == "POST":
        print colored("[---  DUMP   ---]  FORM           : %s" % form.is_valid(), "yellow")

        if form.is_valid():
            form.save()
            form.save_m2m()

            # -----------------------------------------------------------------
            # --- Move temporary Files to real Challenge Images/Documents.
            for tmp_file in form.cleaned_data["tmp_files"]:
                mime_type = mimetypes.guess_type(tmp_file.file.name)[0]

                if mime_type in settings.UPLOADER_SETTINGS["images"]["CONTENT_TYPES"]:
                    AttachedImage.objects.create(
                        name=tmp_file.name,
                        image=File(storage.open(tmp_file.file.name, "rb")),
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )
                elif mime_type in settings.UPLOADER_SETTINGS["documents"]["CONTENT_TYPES"]:
                    AttachedDocument.objects.create(
                        name=tmp_file.name,
                        document=File(storage.open(tmp_file.file.name, "rb")),
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )

                tmp_file.delete()

            # -----------------------------------------------------------------
            # --- Save URLs and Video URLs and pull their Titles.
            for link in request.POST["tmp_links"].split():
                url = validate_url(link)

                if get_youtube_video_id(link):
                    AttachedVideoUrl.objects.create(
                        url=link,
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )
                elif url:
                    AttachedUrl.objects.create(
                        url=url,
                        title=get_website_title(url) or "",
                        content_type=ContentType.objects.get_for_model(challenge),
                        object_id=challenge.id,
                        )

            # -----------------------------------------------------------------
            # --- Send Email Notification(s).
            challenge.email_notify_admin_chl_edited(request)
            challenge.email_notify_alt_person_chl_edited(request)

            Participation.email_notify_participants_chl_reporting_materials(
                request=request,
                challenge=challenge)

            # -----------------------------------------------------------------
            # --- Save the Log.
            papertrail.log(
                event_type="challenge-edited",
                message="Challenge was edited",
                data={
                    "admin":        request.user.email,
                    "author":       challenge.author.email,
                    "name":         challenge.name,
                    "status":       str(challenge.stat_status_name),
                },
                # timestamp=timezone.now(),
                targets={
                    "admin":        request.user,
                    "author":       challenge.author,
                    "challenge":    challenge,
                },
                )

            return HttpResponseRedirect(
                reverse("challenge-details", kwargs={
                    "slug":     challenge.slug,
                }))

        # ---------------------------------------------------------------------
        # --- Failed to edit the Challenge
        # --- Save the Log
        papertrail.log(
            event_type="challenge-edit-failed",
            message="Challenge edit failed",
            data={
                "form":     form_field_error_list(form),
            },
            # timestamp=timezone.now(),
            targets={
                "user":         request.user,
                "challenge":    challenge,
            },
            )

    return render(
        request, "challenges/challenge-reporting-materials.html", {
            "form":             form,
            "challenge":        challenge,
        })
