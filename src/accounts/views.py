import datetime
import inspect

from django.conf import settings
from django.contrib.auth import (
    authenticate,
    login,
    )
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import (
    default_token_generator as token_generator
    )
from django.contrib.auth.views import (
    auth_login,
    logout,
    )
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geoip import GeoIP
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
    )
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    )
from django.shortcuts import (
    get_object_or_404,
    render,
    )
from django.utils.http import (
    base36_to_int,
    int_to_base36,
    )
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

import papertrail

from termcolor import colored

from accounts.forms import (
    LoginForm,
    ResetPasswordForm,
    UserForm,
    UserPrivacyAdminsForm,
    UserPrivacyGeneralForm,
    UserPrivacyMembersForm,
    UserProfileEditForm,
    UserProfileForm,
    )
from accounts.models import (
    UserLogin,
    UserPrivacyAdmins,
    UserPrivacyGeneral,
    UserPrivacyMembers,
    UserProfile,
    )
from accounts.utils import (
    get_admin_challenges,
    get_participations_intersection,
    )
from challenges.choices import (
    CHALLENGE_STATUS,
    RECURRENCE,
    PARTICIPATION_STATUS,
    )
from challenges.models import Participation
from core.forms import (
    AddressForm,
    PhoneForm,
    SocialLinkFormSet,
    )
from core.helpers import form_field_error_list
from core.models import SocialLink
from core.utils import (
    get_client_ip,
    make_json_cond,
    render_to_pdf,
    )
from organizations.models import OrganizationStaff


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ HELPERS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _retrieve_account_list_with_privacy(request):
    """Docstring."""
    accounts = User.objects.filter(
        is_active=True,
        privacy_general__hide_profile_from_list=False,
    ).exclude(
        id=request.user.id,
    )

    return accounts


def is_profile_complete(user):
    """Docstring."""
    return user.profile.is_completed


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ DESKTOP
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -----------------------------------------------------------------------------
# --- ACCOUNT LIST
# -----------------------------------------------------------------------------
@cache_page(60 * 5)
def account_list(request):
    """List of the Members."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    accounts = _retrieve_account_list_with_privacy(request)

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(
        accounts,
        settings.MAX_MEMBERS_PER_PAGE)

    page = request.GET.get("page")

    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        accounts = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        accounts = paginator.page(paginator.num_pages)

    return render(
        request, "accounts/account-list.html", {
            "accounts":     accounts,
            "page_title":   _("All Members"),
            "page_total":   paginator.num_pages,
            "page_number":  accounts.number,
        })


@cache_page(60 * 5)
def account_near_you_list(request):
    """List of the Members."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    g = GeoIP()
    ip = get_client_ip(request)
    # ip = "108.162.209.69"
    country = g.country(ip)
    city = g.city(ip)

    print colored("[---  DUMP   ---] COUNTRY : %s" % country, "yellow")
    print colored("[---  DUMP   ---] CITY    : %s" % city, "yellow")

    accounts = _retrieve_account_list_with_privacy(request)

    # -------------------------------------------------------------------------
    # --- Members near.
    #     According to the last log-in Location.
    # -------------------------------------------------------------------------
    members_logins = UserLogin.objects.filter(
        user__is_active=True,
    )

    if city:
        if city["country_code"]:
            members_logins = members_logins.filter(
                city__icontains=make_json_cond(
                    "country_code", city["country_code"]),
            )

        if city["region"]:
            members_logins = members_logins.filter(
                city__icontains=make_json_cond(
                    "region", city["region"]),
            )

        if city["area_code"]:
            members_logins = members_logins.filter(
                city__icontains=make_json_cond(
                    "area_code", city["area_code"]),
            )

    members_user_ids = list(set(
        members_logins.values_list(
            "user__id", flat=True
        ).distinct()))
    members_near = accounts.filter(
        id__in=members_user_ids,
    )

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(
        members_near,
        settings.MAX_MEMBERS_PER_PAGE)

    page = request.GET.get("page")

    try:
        members_near = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        members_near = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        members_near = paginator.page(paginator.num_pages)

    return render(
        request, "accounts/account-list.html", {
            "accounts":     members_near,
            "page_title":   _("Members near you"),
            "page_total":   paginator.num_pages,
            "page_number":  members_near.number,
        })


@cache_page(60 * 5)
def account_might_know_list(request):
    """List of the Members."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    accounts = _retrieve_account_list_with_privacy(request)

    # -------------------------------------------------------------------------
    # --- Members might know.
    #     According to the Location, specified in the User Profile.
    # -------------------------------------------------------------------------
    members_might_know = accounts.filter()

    if request.user.is_authenticated() and request.user.profile.address:
        # ---------------------------------------------------------------------
        # --- Filter by Country and City.
        if (
                request.user.profile.address.country and
                request.user.profile.address.city):
            members_might_know = members_might_know.filter(
                profile__address__country=request.user.profile.address.country,
                profile__address__city=request.user.profile.address.city,
                )
        # ---------------------------------------------------------------------
        # --- Filter by Province and Zip Code.
        elif (
                request.user.profile.address.province and
                request.user.profile.address.zip_code):
            members_might_know = members_might_know.filter(
                profile__address__province=request.user.profile.address.province,
                profile__address__zip_code=request.user.profile.address.zip_code,
                )
        else:
            members_might_know = []

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(
        members_might_know,
        settings.MAX_MEMBERS_PER_PAGE)

    page = request.GET.get("page")

    try:
        members_might_know = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        members_might_know = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        members_might_know = paginator.page(paginator.num_pages)

    return render(
        request, "accounts/account-list.html", {
            "accounts":     members_might_know,
            "page_title":   _("Members you might know"),
            "page_total":   paginator.num_pages,
            "page_number":  members_might_know.number,
        })


@cache_page(60 * 5)
def account_new_list(request):
    """List of the Members."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    accounts = _retrieve_account_list_with_privacy(request)

    # -------------------------------------------------------------------------
    # --- New Members.
    #     Date joined is less than 1 Day ago.
    # -------------------------------------------------------------------------
    time_threshold = datetime.datetime.now() - datetime.timedelta(days=1)
    members_new = accounts.filter(
        date_joined__gte=time_threshold,
    )

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(
        members_new,
        settings.MAX_MEMBERS_PER_PAGE)

    page = request.GET.get("page")

    try:
        members_new = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        members_new = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        members_new = paginator.page(paginator.num_pages)

    return render(
        request, "accounts/account-list.html", {
            "accounts":     members_new,
            "page_title":   _("New Members"),
            "page_total":   paginator.num_pages,
            "page_number":  members_new.number,
        })


@cache_page(60 * 5)
def account_online_list(request):
    """List of the Members."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    accounts = _retrieve_account_list_with_privacy(request)

    # -------------------------------------------------------------------------
    # --- Members on-line.
    #     Last login was less than 1 Hour ago.
    # -------------------------------------------------------------------------
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=1)
    members_online = accounts.filter(
        last_login__gte=time_threshold,
    )

    # -------------------------------------------------------------------------
    # --- Paginate QuerySet.
    # -------------------------------------------------------------------------
    paginator = Paginator(
        members_online,
        settings.MAX_MEMBERS_PER_PAGE)

    page = request.GET.get("page")

    try:
        members_online = paginator.page(page)
    except PageNotAnInteger:
        # ---------------------------------------------------------------------
        # --- If Page is not an integer, deliver first Page.
        members_online = paginator.page(1)
    except EmptyPage:
        # ---------------------------------------------------------------------
        # --- If Page is out of Range (e.g. 9999), deliver last Page of the
        #     Results.
        members_online = paginator.page(paginator.num_pages)

    return render(
        request, "accounts/account-list.html", {
            "accounts":     members_online,
            "page_title":   _("Members online"),
            "page_total":   paginator.num_pages,
            "page_number":  members_online.number,
        })


# -----------------------------------------------------------------------------
# --- ACCOUNT REGISTRATION
# -----------------------------------------------------------------------------
def account_signup(request):
    """Sign up."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    g = GeoIP()
    ip = get_client_ip(request)
    country_code = g.country_code(ip)

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    uform = UserForm(
        request.POST or None, request.FILES or None)
    pform = UserProfileForm(
        request.POST or None, request.FILES or None)
    """
    aform = AddressForm(
        request.POST or None, request.FILES or None,
        country_code=country_code)
    nform = PhoneForm(
        request.POST or None, request.FILES or None)
    """

    if request.method == "GET":
        if request.user.is_authenticated():
            return HttpResponseRedirect(
                reverse("my-profile-view"))

    if request.method == "POST":
        # if (
        #         uform.is_valid() and pform.is_valid() and
        #         aform.is_valid() and nform.is_valid()):
        if uform.is_valid() and pform.is_valid():
            # -----------------------------------------------------------------
            # --- Create User.
            user = uform.save(commit=False)
            user.is_active = False
            user.save()
            user.set_password(uform.cleaned_data["password"])
            user.save()

            # -----------------------------------------------------------------
            # --- Create User Profile.
            profile = pform.save(commit=False)
            profile.user = user
            # profile.address = aform.save(commit=True)
            # profile.phone_number = nform.save(commit=True)
            profile.save()

            # -----------------------------------------------------------------
            # --- Create User Privacy.
            UserPrivacyGeneral.objects.create(
                user=user)
            UserPrivacyMembers.objects.create(
                user=user)
            UserPrivacyAdmins.objects.create(
                user=user)

            """
            user.backend = "django.contrib.auth.backends.ModelBackend"
            auth_login(request, user)

            return HttpResponseRedirect(reverse("index"))
            """

            uidb36 = int_to_base36(user.id)
            token = token_generator.make_token(user)

            DOMAIN_NAME = request.get_host()
            url = reverse(
                "signup-confirm", kwargs={
                    "uidb36":   uidb36,
                    "token":    token,
                })
            confirmation_link = "http://{domain}{url}".format(
                domain=DOMAIN_NAME,
                url=url,
                )

            # -----------------------------------------------------------------
            # --- Send Email Notification(s).
            profile.email_notify_signup_confirmation(
                request=request,
                url=confirmation_link)

            # -----------------------------------------------------------------
            # --- Save the Log.
            papertrail.log(
                event_type="new-user-signed-up",
                message="New User has signed up",
                data={
                    "user":         user.email,
                },
                # timestamp=timezone.now(),
                targets={
                    "user":         user,
                    "profile":      profile,
                },
                )

            # -----------------------------------------------------------------
            # --- Save the Log.
            papertrail.log(
                event_type="user-sign-up-submitted",
                message="User sign up submitted",
                data={
                    "ip":           ip,
                    "country":      g.country(ip),
                    "city":         g.city(ip),
                    "uform":        form_field_error_list(uform),
                    "pform":        form_field_error_list(pform),
                    # "aform":        form_field_error_list(aform),
                    # "nform":        form_field_error_list(nform),
                },
                # timestamp=timezone.now(),
                targets={},
                )

            return render(
                request,
                "accounts/account-signup-confirmation-email-sent.html", {
                    "email":    user.email,
                })

        # ---------------------------------------------------------------------
        # --- Failed to sign up.
        # --- Save the Log.
        papertrail.log(
            event_type="user-sign-up-failed",
            message="User sign up failed",
            data={
                "ip":           ip,
                "country":      g.country(ip),
                "city":         g.city(ip),
                "uform":        form_field_error_list(uform),
                "pform":        form_field_error_list(pform),
                # "aform":        form_field_error_list(aform),
                # "nform":        form_field_error_list(nform),
            },
            # timestamp=timezone.now(),
            targets={},
            )

    return render(
        # request, "accounts/account_signup_all.html", {
        request, "accounts/account-signup.html", {
            "uform":    uform,
            "pform":    pform,
            # "aform":    aform,
            # "nform":    nform,
        })


def account_signup_confirm(request, uidb36=None, token=None):
    """Sign up confirm."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    assert uidb36 is not None and token is not None

    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(
            id=uid_int
        )
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        # ---------------------------------------------------------------------
        # --- Instant log-in after confirmation.
        user.is_active = True
        user.save()

        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth_login(request, user)

        DOMAIN_NAME = request.get_host()
        url = reverse(
            "login", kwargs={})
        login_link = "http://{domain}{url}".format(
            domain=DOMAIN_NAME,
            url=url,
            )

        # ---------------------------------------------------------------------
        # --- Send Email Notification(s).
        user.profile.email_notify_signup_confirmed(
            request=request,
            url=login_link)

        # ---------------------------------------------------------------------
        # --- Save the Log.
        papertrail.log(
            event_type="new-user-sign-up-confirmed",
            message="New User sign up was confirmed",
            data={
                "user":         user.email,
            },
            # timestamp=timezone.now(),
            targets={
                "user":         user,
                "profile":      user.profile,
            },
            )

        """
        return render(
            request,
            "accounts/account-signup-confirmation-success.html", {})
        """
        return HttpResponseRedirect(
            reverse("my-profile-edit"))
    else:
        # ---------------------------------------------------------------------
        # --- Save the Log.
        papertrail.log(
            event_type="new-user-sign-up-confirm-failed",
            message="New User sign up confirm failed",
            data={
                "user_id":      base36_to_int(uidb36),
            },
            # timestamp=timezone.now(),
            targets={},
            )

        return render(
            request,
            "accounts/account-signup-confirmation-error.html", {})


@csrf_exempt
def account_login(request):
    """Log in."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    g = GeoIP()
    ip = get_client_ip(request)

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    form = LoginForm(
        request.POST or None)
    redirect_to = request.GET.get("next", "")

    print colored("[---  DUMP   ---] NEXT : %s" % redirect_to, "yellow")

    if request.method == "GET":
        if request.user.is_authenticated():
            if redirect_to:
                return HttpResponseRedirect(redirect_to)

            return HttpResponseRedirect(
                reverse("my-profile-view"))

    if request.method == "POST":
        if form.is_valid():
            # if not redirect_to:
            #     redirect_to = settings.LOGIN_REDIRECT_URL

            data = form.cleaned_data
            user = authenticate(
                username=data["username"],
                password=data["password"],
            )

            if user:
                login(request, user)

                if data["remember_me"]:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                else:
                    request.session.set_expiry(0)
                # return HttpResponseRedirect(redirect_to)

                # -------------------------------------------------------------
                # --- Track IP.
                UserLogin.objects.insert(
                    request=request)

                # -------------------------------------------------------------
                # --- Save the Log.
                papertrail.log(
                    event_type="user-logged-in",
                    message="User logged in",
                    data={
                        "ip":           ip,
                        "country":      g.country(ip),
                        "city":         g.city(ip),
                        "user":         user.email,
                        "data":         data,
                    },
                    # timestamp=timezone.now(),
                    targets={
                        "user":         user,
                        "profile":      user.profile
                    },
                    )

                if redirect_to:
                    return HttpResponseRedirect(redirect_to)

                return HttpResponseRedirect(
                    reverse("my-profile-view"))
            else:
                form.add_non_field_error(
                    _("Sorry, you have entered wrong Email or Password"))

        # ---------------------------------------------------------------------
        # --- Failed to log in
        # --- Save the Log
        papertrail.log(
            event_type="user-login-failed",
            message="user login failed",
            data={
                "form":     form_field_error_list(form),
            },
            # timestamp=timezone.now(),
            targets={},
            )

    return render(
        request, "accounts/account-login.html", {
            "form":     form,
            "next":     redirect_to,
        })


@login_required
def account_logout(request, next_page):
    """Log out."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    response = logout(request, next_page=next_page)

    return response


# -----------------------------------------------------------------------------
# --- MY PROFILE
# -----------------------------------------------------------------------------
@login_required
def my_profile_view(request):
    """My Profile."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Get or create User's Profile.
    # -------------------------------------------------------------------------
    try:
        profile = request.user.profile
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        profile = UserProfile.objects.create(
            user=request.user,
        )

    # -------------------------------------------------------------------------
    # --- Get or create User's Privacy Settings.
    # -------------------------------------------------------------------------
    try:
        privacy_general, created = UserPrivacyGeneral.objects.get_or_create(
            user=request.user,
            )
        privacy_members, created = UserPrivacyMembers.objects.get_or_create(
            user=request.user,
            )
        privacy_admins, created = UserPrivacyAdmins.objects.get_or_create(
            user=request.user,
            )
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        # ---------------------------------------------------------------------
        # --- Save the Log.
        papertrail.log(
            event_type="exception-create-user-privacy",
            message="Exception: Create User Privacy Entries",
            data={
                "user":         request.user.email,
                "message":      str(e),
            },
            # timestamp=timezone.now(),
            targets={
                "user":         request.user,
            },
            )

    # -------------------------------------------------------------------------
    # --- Retrieve the Profile Social Links.
    # -------------------------------------------------------------------------
    social_links = SocialLink.objects.filter(
        content_type=ContentType.objects.get_for_model(profile),
        object_id=profile.id
    )

    # ---------------------------------------------------------------------
    # --- Retrieve the List of Organizations, created by User.
    created_organizations = request.user.created_organizations.all()

    # ---------------------------------------------------------------------
    # --- Retrieve the List of Organizations, where the User is
    #     a Staff Member.
    staff_member_organizations =\
        request.user.profile.staff_member_organizations.all()

    # ---------------------------------------------------------------------
    # --- Retrieve the List of Organizations, where the User is
    #     a Group Member.
    group_member_organizations =\
        request.user.profile.group_member_organizations.all()

    # ---------------------------------------------------------------------
    # --- Related Organizations.
    related_organizations = staff_member_organizations | group_member_organizations
    related_organizations = related_organizations.exclude(
        id__in=created_organizations
    )

    # -------------------------------------------------------------------------
    # --- Prepare Response.
    show_no_email_popup_modal = False

    if (
            not request.user.email and
            "show_no_email_popup_modal" not in request.COOKIES):
        show_no_email_popup_modal = True

    response = HttpResponse(render(
        request, "accounts/my-profile-info.html", {
            "created_organizations":                created_organizations,
            "related_organizations":                related_organizations,
            "show_no_email_popup_modal":            show_no_email_popup_modal,
            "social_links":                         social_links,
        }))

    # -------------------------------------------------------------------------
    # --- Get/set Cookie(s).
    print colored("[---  DUMP   ---] REQUEST COOKIES : %s" % request.COOKIES, "yellow")

    response.set_cookie("show_no_email_popup_modal", "")

    if "show_no_email_popup_modal" in request.COOKIES:
        response.set_cookie("show_no_email_popup_modal", "")

    return response


@login_required
def my_profile_invitations(request):
    """My Profile."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Get or create User's Profile.
    # -------------------------------------------------------------------------
    try:
        assert request.user.profile
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        UserProfile.objects.create(
            user=request.user,
        )

    return render(
        request, "accounts/my-profile-invitations.html", {})


@login_required
def my_profile_participations(request):
    """My Profile."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Get or create User's Profile.
    # -------------------------------------------------------------------------
    try:
        assert request.user.profile
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        UserProfile.objects.create(
            user=request.user,
        )

    return render(
        request, "accounts/my-profile-participations.html", {})


@login_required
def my_profile_challenges(request):
    """My Profile."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Get or create User's Profile.
    # -------------------------------------------------------------------------
    try:
        assert request.user.profile
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        UserProfile.objects.create(
            user=request.user,
        )

    return render(
        request, "accounts/my-profile-challenges.html", {})


@login_required
def my_profile_edit(request):
    """Edit Profile."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    pform = UserProfileEditForm(
        request.POST or None, request.FILES or None,
        user=request.user, instance=request.user.profile)
    aform = AddressForm(
        request.POST or None, request.FILES or None,
        instance=request.user.profile.address)
    nform = PhoneForm(
        request.POST or None, request.FILES or None,
        instance=request.user.profile.phone_number)

    formset_social = SocialLinkFormSet(
        request.POST or None, request.FILES or None,
        prefix="socials",
        queryset=SocialLink.objects.filter(
            content_type=ContentType.objects.get_for_model(request.user.profile),
            object_id=request.user.profile.id
            ))

    if request.method == "POST":
        print colored("[---  DUMP   ---]  FORM           : %s" % pform.is_valid(), "yellow")
        print colored("[---  DUMP   ---] AFORM           : %s" % aform.is_valid(), "yellow")
        print colored("[---  DUMP   ---] AFORM           : %s" % nform.is_valid(), "yellow")
        print colored("[---  DUMP   ---]  FORMSET SOCIAL : %s" % formset_social.is_valid(), "yellow")

        if (
                pform.is_valid() and aform.is_valid() and nform.is_valid() and
                formset_social.is_valid()):
            request.user.profile.address = aform.save()
            request.user.profile.phone_number = nform.save()
            request.user.profile.save()

            request.user.first_name = pform.cleaned_data["first_name"]
            request.user.last_name = pform.cleaned_data["last_name"]
            request.user.save()

            pform.save()

            # -----------------------------------------------------------------
            # --- Save Social Links.
            social_links = formset_social.save(commit=True)

            for social_link in social_links:
                social_link.content_type = ContentType.objects.get_for_model(request.user.profile)
                social_link.object_id = request.user.profile.id
                social_link.save()

            return HttpResponseRedirect(
                reverse("my-profile-view"))

        # ---------------------------------------------------------------------
        # --- Failed to save the Profile.
        # --- Save the Log.
        papertrail.log(
            event_type="user-profile-save-failed",
            message="User Profile save failed",
            data={
                "pform":    form_field_error_list(pform),
                "aform":    form_field_error_list(aform),
                "nform":    form_field_error_list(nform),
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
                "profile":  request.user.profile,
            },
            )

    # -------------------------------------------------------------------------
    # --- Is newly created?
    #     If so, show the pop-up Overlay.
    # -------------------------------------------------------------------------
    is_newly_created = False

    if request.user.profile.is_newly_created:
        is_newly_created = True

        request.user.profile.is_newly_created = False
        request.user.profile.save()

    return render(
        request, "accounts/my-profile-edit.html", {
            "pform":            pform,
            "aform":            aform,
            "nform":            nform,
            "formset_social":   formset_social,
            "is_newly_created": is_newly_created,
        })


@login_required
def my_profile_delete(request):
    """Delete Profile."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    if request.method == "POST":
        response = account_logout(request, "/")
        request.user.delete()

        # ---------------------------------------------------------------------
        # --- Save the Log.
        papertrail.log(
            event_type="user-account-deleted",
            message="User's Account was deleted",
            data={
                "user":         request.user.email,
            },
            # timestamp=timezone.now(),
            targets={},
            )

        return response

    return render(
        request, "accounts/my-profile-delete.html", {})


@login_required
def my_profile_privacy(request):
    """Profile Privacy Settings."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Get or create User's Privacy Settings.
    # -------------------------------------------------------------------------
    try:
        privacy_general, created = UserPrivacyGeneral.objects.get_or_create(
            user=request.user,
            )
        privacy_members, created = UserPrivacyMembers.objects.get_or_create(
            user=request.user,
            )
        privacy_admins, created = UserPrivacyAdmins.objects.get_or_create(
            user=request.user,
            )
    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        # ---------------------------------------------------------------------
        # --- Save the Log.
        papertrail.log(
            event_type="exception-create-user-privacy",
            message="Exception: Create User Privacy Entries",
            data={
                "user":         request.user.email,
                "message":      str(e),
            },
            # timestamp=timezone.now(),
            targets={
                "user":         request.user,
            },
            )

    # -------------------------------------------------------------------------
    # --- Prepare Form(s).
    # -------------------------------------------------------------------------
    privacy_general_form = UserPrivacyGeneralForm(
        request.POST or None, request.FILES or None,
        instance=privacy_general,
        prefix="general")
    privacy_members_form = UserPrivacyMembersForm(
        request.POST or None, request.FILES or None,
        instance=privacy_members,
        prefix="members")
    privacy_admins_form = UserPrivacyAdminsForm(
        request.POST or None, request.FILES or None,
        instance=privacy_admins,
        prefix="admins")

    if request.method == "POST":
        if (
                privacy_general_form.is_valid() and
                privacy_members_form.is_valid() and
                privacy_admins_form.is_valid()):
            privacy_general_form.save()
            privacy_members_form.save()
            privacy_admins_form.save()

            if "submit-stay" in request.POST:
                return HttpResponseRedirect(
                    reverse("my-profile-privacy"))

            return HttpResponseRedirect(
                reverse("my-profile-view"))

        # ---------------------------------------------------------------------
        # --- Failed to save the Profile Privacy.
        # --- Save the Log.
        papertrail.log(
            event_type="user-profile-privacy-save-failed",
            message="User Profile Privacy save failed",
            data={
                "pform":    form_field_error_list(privacy_general_form),
                "aform":    form_field_error_list(privacy_members_form),
                "nform":    form_field_error_list(privacy_admins_form),
            },
            # timestamp=timezone.now(),
            targets={
                "user":     request.user,
                "profile":  request.user.profile,
            },
            )

    return render(
        request, "accounts/my-profile-privacy.html", {
            "privacy_general_form":     privacy_general_form,
            "privacy_members_form":     privacy_members_form,
            "privacy_admins_form":      privacy_admins_form,
        })


# -----------------------------------------------------------------------------
# --- FOREIGN PROFILE
# -----------------------------------------------------------------------------
@cache_page(60 * 5)
def profile_view(request, user_id):
    """Foreign Profile Info."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------
    is_complained = False
    show_complain_form = False

    # -------------------------------------------------------------------------
    # --- Retrieve the User Account.
    # -------------------------------------------------------------------------
    account = get_object_or_404(
        User,
        pk=user_id,
    )

    if account == request.user:
        return HttpResponseRedirect(
            reverse("my-profile-view"))

    # -------------------------------------------------------------------------
    # --- Retrieve the Account Social Links.
    # -------------------------------------------------------------------------
    social_links = SocialLink.objects.filter(
        content_type=ContentType.objects.get_for_model(account.profile),
        object_id=account.profile.id
    )

    # -------------------------------------------------------------------------
    # --- Get QuerySet of Admin Challenges with
    #     the Organization Privacy Settings:
    #     1. Organization is not set;
    #     2. Organization is set to Public;
    #     3. Organization is set to Private, and:
    #        a) User is the Organization Staff Member (and/or Author);
    #        b) User is the Organization Group Member.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        # ---------------------------------------------------------------------
        # --- Check, if the User has already complained to the Account.
        is_complained = account.profile.is_complained_by_user(request.user)

        if not is_complained:
            # -----------------------------------------------------------------
            # --- Check, if the registered User participated in the same
            #     Challenge(s), as the Account.
            if len(get_participations_intersection(request.user, account)) > 0:
                show_complain_form = True

    # -------------------------------------------------------------------------
    # --- Get QuerySet of Organizations with the Organization Privacy Settings:
    #     1. Organization is set to Public;
    #     2. Organization is set to Private, and:
    #        a) User is the Organization Staff Member (and/or Author);
    #        b) User is the Organization Group Member.
    # -------------------------------------------------------------------------
    # --- Retrieve the List of Organizations, where the User is
    #     a Staff Member.
    staff_member_organizations = account.profile.staff_member_organizations.all()

    # -------------------------------------------------------------------------
    # --- Retrieve the List of Organizations, where the User is
    #     a Group Member.
    group_member_organizations = account.profile.group_member_organizations.all()

    if request.user.is_authenticated():
        # ---------------------------------------------------------------------
        # --- Retrieve the List of Organizations, created by User.
        created_organizations = account.created_organizations.filter(
            Q(is_hidden=False) |
            Q(
                Q(pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )) |
                Q(pk__in=request.user
                    .organization_group_members
                    .all().values_list(
                        "organization_id", flat=True
                    )),
                is_hidden=True,
            ),
            is_deleted=False,
        )

        # ---------------------------------------------------------------------
        # --- Related Organizations.
        related_organizations = staff_member_organizations | group_member_organizations
        related_organizations = related_organizations.filter(
            Q(is_hidden=False) |
            Q(
                Q(pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )) |
                Q(pk__in=request.user
                    .organization_group_members
                    .all().values_list(
                        "organization_id", flat=True
                    )),
                is_hidden=True,
            ),
            is_deleted=False,
        )
    else:
        # ---------------------------------------------------------------------
        # --- Retrieve the List of Organizations, created by User.
        created_organizations = account.created_organizations.filter(
            is_hidden=False,
            is_deleted=False,
        )

        # ---------------------------------------------------------------------
        # --- Related Organizations.
        related_organizations = staff_member_organizations | group_member_organizations
        related_organizations = related_organizations.filter(
            is_hidden=False,
            is_deleted=False,
        )

    related_organizations = related_organizations.exclude(
        id__in=created_organizations
    )

    # -------------------------------------------------------------------------
    # --- Increment Views Counter.
    # -------------------------------------------------------------------------
    account.profile.increase_views_count(request)

    return render(
        request, "accounts/foreign-profile-info.html", {
            "account":                      account,
            "created_organizations":        created_organizations,
            "related_organizations":        related_organizations,
            "social_links":                 social_links,
            "show_complain_form":           show_complain_form,
        })


@cache_page(60 * 5)
def profile_participations(request, user_id):
    """Foreign Profile Participations."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # --- Retrieve the User Account.
    # -------------------------------------------------------------------------
    account = get_object_or_404(
        User,
        pk=user_id,
    )

    if account == request.user:
        return HttpResponseRedirect(
            reverse("my-profile-view"))

    # -------------------------------------------------------------------------
    # --- Get QuerySet of Challenges (Participations) with
    #     the Organization Privacy Settings:
    #     1. Organization is not set;
    #     2. Organization is set to Public;
    #     3. Organization is set to Private, and:
    #        a) User is the Organization Staff Member (and/or Author);
    #        b) User is the Organization Group Member.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        participations = Participation.objects.filter(
            Q(challenge__organization=None) |
            Q(challenge__organization__is_hidden=False) |
            Q(
                Q(challenge__organization__pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )) |
                Q(challenge__organization__pk__in=request.user
                    .organization_group_members
                    .all().values_list(
                        "organization_id", flat=True
                    )),
                challenge__organization__is_hidden=True,
            ),
            user=account,
        )
    else:
        participations = Participation.objects.filter(
            Q(challenge__organization=None) |
            Q(challenge__organization__is_hidden=False),
            user=account,
        )

    # -------------------------------------------------------------------------
    # --- Get QuerySet of upcoming Challenges (Participations).
    # -------------------------------------------------------------------------
    upcoming_participations = participations.filter(
        challenge__status=CHALLENGE_STATUS.UPCOMING,
        status__in=[
            PARTICIPATION_STATUS.CONFIRMED,
            PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
        ],
    )

    # -------------------------------------------------------------------------
    # --- Get QuerySet of completed Challenges (Participations).
    # -------------------------------------------------------------------------
    completed_participations = participations.filter(
        challenge__status=CHALLENGE_STATUS.COMPLETE,
        status__in=[
            PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
            PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
            PARTICIPATION_STATUS.ACKNOWLEDGED,
        ],
    )

    # -------------------------------------------------------------------------
    # --- Get QuerySet of canceled Challenges (Participations).
    # -------------------------------------------------------------------------
    cancelled_participations = participations.filter(
        challenge__status__in=[
            CHALLENGE_STATUS.UPCOMING,
            CHALLENGE_STATUS.COMPLETE,
        ],
        status__in=[
            PARTICIPATION_STATUS.CANCELLED_BY_USER,
        ],
    )

    # -------------------------------------------------------------------------
    # --- Get QuerySet of rejected Challenges (Participations).
    # -------------------------------------------------------------------------
    rejected_participations = participations.filter(
        challenge__status__in=[
            CHALLENGE_STATUS.UPCOMING,
            CHALLENGE_STATUS.COMPLETE,
        ],
        status__in=[
            PARTICIPATION_STATUS.CONFIRMATION_DENIED,
            PARTICIPATION_STATUS.CANCELLED_BY_ADMIN,
        ],
    )

    # -------------------------------------------------------------------------
    # --- Increment Views Counter.
    # -------------------------------------------------------------------------
    account.profile.increase_views_count(request)

    return render(
        request, "accounts/foreign-profile-participations.html", {
            "account":                      account,
            "upcoming_participations":      upcoming_participations,
            "completed_participations":     completed_participations,
            "cancelled_participations":     cancelled_participations,
            "rejected_participations":      rejected_participations,
        })


@cache_page(60 * 5)
def profile_challenges(request, user_id):
    """Foreign Profile Challenges."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    # -------------------------------------------------------------------------
    # --- Initials.
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # --- Retrieve the User Account.
    # -------------------------------------------------------------------------
    account = get_object_or_404(
        User,
        pk=user_id,
    )

    if account == request.user:
        return HttpResponseRedirect(
            reverse("my-profile-view"))

    # -------------------------------------------------------------------------
    # --- Get QuerySet of Admin Challenges with
    #     the Organization Privacy Settings:
    #     1. Organization is not set;
    #     2. Organization is set to Public;
    #     3. Organization is set to Private, and:
    #        a) User is the Organization Staff Member (and/or Author);
    #        b) User is the Organization Group Member.
    # -------------------------------------------------------------------------
    if request.user.is_authenticated():
        admin_challenges = get_admin_challenges(account).filter(
            Q(organization=None) |
            Q(organization__is_hidden=False) |
            Q(
                Q(organization__pk__in=OrganizationStaff
                    .objects.filter(
                        member=request.user,
                    ).values_list(
                        "organization_id", flat=True
                    )) |
                Q(organization__pk__in=request.user
                    .organization_group_members
                    .all().values_list(
                        "organization_id", flat=True
                    )),
                organization__is_hidden=True,
            ),
        )
    else:
        admin_challenges = get_admin_challenges(account).filter(
            Q(organization=None) |
            Q(organization__is_hidden=False),
        )

    # -------------------------------------------------------------------------
    # --- Increment Views Counter.
    # -------------------------------------------------------------------------
    account.profile.increase_views_count(request)

    return render(
        request, "accounts/foreign-profile-challenges.html", {
            "account":                      account,
            "admin_challenges":             admin_challenges,
        })


# -----------------------------------------------------------------------------
# --- EXPORT to PDF (Freiwilligenausweis)
# -----------------------------------------------------------------------------
def my_profile_challenges_export(request):
    """Export the List of the completed Challenges to PDF."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    completed_participations = Participation.objects.filter(
        user=request.user,
        challenge__status=CHALLENGE_STATUS.COMPLETE,
        status__in=[
            PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
            PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
            PARTICIPATION_STATUS.ACKNOWLEDGED,
        ]
    )

    # -------------------------------------------------------------------------
    # --- Prepare Data.
    template = "accounts/export/my-profile-completed-challenges-export.html"
    payload = {
        "completed_participations":     completed_participations,
    }

    return render_to_pdf(
        template,
        payload,
        )


# -----------------------------------------------------------------------------
# --- PASSWORD
# -----------------------------------------------------------------------------
def password_renew(request, uidb36=None, token=None):
    """Renew Password."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    assert uidb36 is not None and token is not None

    try:
        uid_int = base36_to_int(uidb36)
        user = User.objects.get(
            id=uid_int,
            )
    except (ValueError, User.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        # ---------------------------------------------------------------------
        # --- Instant log-in after confirmation.
        user.backend = "django.contrib.auth.backends.ModelBackend"
        auth_login(request, user)

        return HttpResponseRedirect(
            reverse("password-reset"))
    else:
        info = _("An Error has occurred.")

        return render(
            request, "common/error.html", {
                "information":  info,
            })


@login_required
def password_reset(request):
    """Reset Password."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    form = ResetPasswordForm(
        request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            request.user.set_password(form.cleaned_data["password"])
            request.user.save()

            DOMAIN_NAME = request.get_host()
            url = reverse("login", kwargs={})
            login_link = "http://{domain}{url}".format(
                domain=DOMAIN_NAME,
                url=url,
                )

            # -----------------------------------------------------------------
            # --- Send Email Notification(s).
            request.user.profile.email_notify_password_reset(
                request=request,
                url=login_link)

            return HttpResponseRedirect(
                reverse("my-profile-view"))

    return render(
        request, "accounts/account-password-reset.html", {
            "form":     form,
        })
