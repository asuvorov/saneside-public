import datetime
import inspect
import json
import urlparse

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.test import (
    Client,
    TestCase,
    LiveServerTestCase,
)

import mock
import requests as request
import unittest

from lxml import html
from termcolor import colored, cprint

from challenges.choices import (
    CHALLENGE_STATUS, challenge_status_choices,
    CHALLENGE_MODE, application_choices,
    CHALLENGE_CATEGORY, challenge_category_choices,
    CHALLENGE_COLORS, challenge_category_colors,
    CHALLENGE_ICONS, challenge_category_icons,
    PARTICIPATION_REMOVE_MODE,
    PARTICIPATION_STATUS, participation_status_choices,
    RECURRENCE, recurrence_choices,
    MONTH, month_choices,
    DAY_OF_WEEK, day_of_week_choices,
    day_of_month_choices,
    )
from challenges.forms import (
    CreateEditChallengeForm,
    RoleForm,
    RoleFormSet,
    )
from challenges.models import (
    Challenge,
    Role,
    Participation
    )
from organizations.models import (
    Organization,
    OrganizationStaff,
    OrganizationGroup,
    )


client = Client(
    HTTP_USER_AGENT="Mozilla/5.0",
    enforce_csrf_checks=True,
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ MOCKS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ MODELS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChallengeCreateModelTestCase(TestCase):

    """Challenge create Test Case.

        COVERS:
                Create Challenge    (default)
                                    without Author
                                    without Name
                                    without Avatar
                                    with    Organization
    """

    fixtures = [
        "test_accounts.json",
        "test_core_addr_acc.json",
        "test_core_addr_org.json",
        "test_organizations_private.json",
        "test_organizations_public.json",
    ]

    def setUp(self):
        """Set up."""
        print colored("***" * 27, "green")
        print colored("*** TEST > CHALLENGES > MODELS > CREATE", "green")

        # ---------------------------------------------------------------------
        # --- Fake

        # ---------------------------------------------------------------------
        # --- Initials

        # --- Users
        self.test_user_1 = User.objects.get(id=1)
        self.test_user_2 = User.objects.get(id=2)
        self.test_user_3 = User.objects.get(id=3)
        self.test_user_4 = User.objects.get(id=4)

        # --- Organizations
        self.test_private_org_1 = Organization.objects.get(id=31)
        self.test_private_org_3 = Organization.objects.get(id=33)

        self.test_public_org_2 = Organization.objects.get(id=32)
        self.test_public_org_4 = Organization.objects.get(id=34)

    def test_challenge_defaults(self):
        """Challenge create. Defaults."""
        print colored("[---  INFO   ---] Challenge create. Defaults...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        challenge = Challenge.objects.create(
            author=self.test_user_1,
            # avatar=,
            name="Challenge #1",
            # description="Description of the Challenge #1",
            # slug=,
            # tags=,
            # hashtag=,
            # category=,
            # status=,
            # application=,
            # addressless=,
            # address=,
            # duration=,
            # recurrence=,
            # month=,
            # day_of_week=,
            # day_of_month=,
            # start_date=,
            # start_time=,
            # start_tz=,
            # start_date_time_tz=,
            # is_alt_person=,
            # alt_person_fullname=,
            # alt_person_email=,
            # alt_person_phone=,
            # organization=,
            # closed_reason=,
            # is_newly_created=,
            # allow_reenter=,
            # accept_automatically=,
            # acceptance_text=,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            challenge.author,
            self.test_user_1,
            colored("[---  ERROR  ---] Wrong Author", "white", "on_red"))

        self.assertIsNotNone(
            challenge.name,
            colored("[---  ERROR  ---] Wrong Name", "white", "on_red"))
        self.assertIsNone(
            challenge.description,
            colored("[---  ERROR  ---] Wrong default Value of Description", "white", "on_red"))
        self.assertIsNotNone(
            challenge.slug,
            colored("[---  ERROR  ---] Wrong Slug", "white", "on_red"))

        """
        self.assertIsNone(
            challenge.tags,
            colored("[---  ERROR  ---] Wrong default Value of Tags", "white", "on_red"))
        """
        self.assertIsNone(
            challenge.hashtag,
            colored("[---  ERROR  ---] Wrong default Value of Hashtag", "white", "on_red"))
        self.assertIsNone(
            challenge.category,
            colored("[---  ERROR  ---] Wrong default Value of Category", "white", "on_red"))

        self.assertEqual(
            challenge.status,
            CHALLENGE_STATUS.UPCOMING,
            colored("[---  ERROR  ---] Wrong default Value of Status", "white", "on_red"))
        self.assertEqual(
            challenge.application,
            CHALLENGE_MODE.FREE_FOR_ALL,
            colored("[---  ERROR  ---] Wrong default Value of Application", "white", "on_red"))

        self.assertFalse(
            challenge.addressless,
            colored("[---  ERROR  ---] Wrong default Value of Addressless", "white", "on_red"))
        self.assertIsNone(
            challenge.address,
            colored("[---  ERROR  ---] Wrong default Value of Address", "white", "on_red"))

        self.assertEqual(
            challenge.duration,
            1,
            colored("[---  ERROR  ---] Wrong default Value of Duration", "white", "on_red"))

        self.assertEqual(
            challenge.recurrence,
            RECURRENCE.ONCE,
            colored("[---  ERROR  ---] Wrong default Value of Recurrence", "white", "on_red"))
        self.assertIsNone(
            challenge.month,
            colored("[---  ERROR  ---] Wrong default Value of Month", "white", "on_red"))
        self.assertIsNone(
            challenge.day_of_week,
            colored("[---  ERROR  ---] Wrong default Value of Day of Week", "white", "on_red"))
        self.assertIsNone(
            challenge.day_of_month,
            colored("[---  ERROR  ---] Wrong default Value of Day of Month", "white", "on_red"))

        """
        self.assertIsNone(
            challenge.start_date,
            colored("[---  ERROR  ---] Wrong default Value of Start Date", "white", "on_red"))
        self.assertIsNone(
            challenge.start_time,
            colored("[---  ERROR  ---] Wrong default Value of Start Time", "white", "on_red"))
        self.assertEqual(
            challenge.start_tz,
            settings.TIME_ZONE,
            colored("[---  ERROR  ---] Wrong default Value of Start TZ", "white", "on_red"))
        self.assertIsNone(
            challenge.start_date_time_tz,
            colored("[---  ERROR  ---] Wrong default Value of Start Date/Time with TZ", "white", "on_red"))
        """

        self.assertFalse(
            challenge.is_alt_person,
            colored("[---  ERROR  ---] Wrong default Value of Alt Person", "white", "on_red"))
        self.assertIsNone(
            challenge.alt_person_fullname,
            colored("[---  ERROR  ---] Wrong default Value of Alt Person full Name", "white", "on_red"))
        self.assertIsNone(
            challenge.alt_person_email,
            colored("[---  ERROR  ---] Wrong default Value of Alt Person Email", "white", "on_red"))
        self.assertIsNone(
            challenge.alt_person_phone,
            colored("[---  ERROR  ---] Wrong default Value of Alt Person Phone", "white", "on_red"))

        self.assertIsNone(
            challenge.organization,
            colored("[---  ERROR  ---] Wrong default Value of Organization", "white", "on_red"))

        self.assertIsNone(
            challenge.closed_reason,
            colored("[---  ERROR  ---] Wrong default Value of closed Reason", "white", "on_red"))

        self.assertTrue(
            challenge.is_newly_created,
            colored("[---  ERROR  ---] Wrong default Value of newly created", "white", "on_red"))

        self.assertTrue(
            challenge.allow_reenter,
            colored("[---  ERROR  ---] Wrong default Value of allow Reenter", "white", "on_red"))

        self.assertFalse(
            challenge.accept_automatically,
            colored("[---  ERROR  ---] Wrong default Value of accept automatically", "white", "on_red"))
        self.assertIsNone(
            challenge.acceptance_text,
            colored("[---  ERROR  ---] Wrong default Value of Acceptance Text", "white", "on_red"))

    def test_challenge_wo_author(self):
        """Challenge create. Without Author."""
        print colored("[---  INFO   ---] Challenge create. Without Author...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request

        # ---------------------------------------------------------------------
        # --- Test Response
        with self.assertRaises(IntegrityError):
            Challenge.objects.create(
                # author=self.test_user_1,
                # avatar=,
                name="Challenge #1",
                )

    @unittest.skip("Skip the Test")
    def test_challenge_wo_name(self):
        """Challenge create. Without Name."""
        print colored("[---  INFO   ---] Challenge create. Without Name...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request

        # ---------------------------------------------------------------------
        # --- Test Response
        with self.assertRaises(IntegrityError):
            Challenge.objects.create(
                author=self.test_user_1,
                # avatar=,
                # name="Challenge #1",
                )

    @unittest.skip("Skip the Test")
    def test_challenge_wo_avatar(self):
        """Challenge create. Without Avatar."""
        print colored("[---  INFO   ---] Challenge create. Without Avatar...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request

        # ---------------------------------------------------------------------
        # --- Test Response
        with self.assertRaises(IntegrityError):
            Challenge.objects.create(
                author=self.test_user_1,
                # avatar=,
                name="Challenge #1",
                )

    def test_challenge_w_organization(self):
        """Challenge create. With Organization."""
        print colored("[---  INFO   ---] Challenge create. With Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        challenge = Challenge.objects.create(
            author=self.test_user_1,
            # avatar=,
            name="Challenge #1",
            organization=self.test_private_org_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            challenge.organization,
            self.test_private_org_1,
            colored("[---  ERROR  ---] Wrong Organization", "white", "on_red"))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ VIEWS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChallengeListViewTestCase(TestCase):

    """Challenge List Test Case.

        COVERS:
                USER                        CHALLENGE
                --------------------------- -----------------------------------
                NOT logged in

                    Logged in               Upcoming Chl of pub Org
                                            Auth  of Chl of prv Org
                                            Staff Member or prv Org
                                            Group Member of prv Org
                                            Auth  of Chl &  Staff Member of prv Org
                                            Auth  of Chl &  Group Member of prv Org
    """

    fixtures = [
        "test_accounts.json",
        "test_challenges_completed.json",
        "test_challenges_dateless.json",
        "test_challenges_draft.json",
        "test_challenges_pastdue.json",
        "test_challenges_upcoming.json",
        "test_core_addr_acc.json",
        "test_core_addr_chl.json",
        "test_core_addr_org.json",
        "test_organizations_private.json",
        "test_organizations_public.json",
    ]

    def setUp(self):
        """Set up."""
        print colored("***" * 27, "green")
        print colored("*** TEST > CHALLENGES > VIEWS > LIST", "green")

        # ---------------------------------------------------------------------
        # --- Fake

        # ---------------------------------------------------------------------
        # --- Initials
        self.url = reverse("challenge-list")

        # --- Users
        self.test_author_1 = User.objects.get(id=1)
        self.test_author_3 = User.objects.get(id=3)

        self.test_user_2 = User.objects.get(id=2)
        self.test_user_4 = User.objects.get(id=4)

        # --- Challenges
        self.test_draft_chl_11 = Challenge.objects.get(id=211)
        self.test_draft_chl_21 = Challenge.objects.get(id=221)

        self.test_upcoming_private_chl_12 = Challenge.objects.get(id=212)
        self.test_upcoming_private_chl_32 = Challenge.objects.get(id=232)

        self.test_upcoming_public_chl_22 = Challenge.objects.get(id=222)
        self.test_upcoming_public_chl_42 = Challenge.objects.get(id=242)

        self.test_completed_chl_13 = Challenge.objects.get(id=213)
        self.test_completed_chl_23 = Challenge.objects.get(id=223)

        self.test_pastdue_chl_24 = Challenge.objects.get(id=224)
        self.test_pastdue_chl_44 = Challenge.objects.get(id=244)

        self.test_dateless_chl_15 = Challenge.objects.get(id=215)
        self.test_dateless_chl_25 = Challenge.objects.get(id=225)

        # --- Organizations
        self.test_private_org_1 = Organization.objects.get(id=31)
        self.test_private_org_3 = Organization.objects.get(id=33)

        self.test_public_org_2 = Organization.objects.get(id=32)
        self.test_public_org_4 = Organization.objects.get(id=34)

    def test_user_not_logged_in(self):
        """Challenge List. User NOT logged in."""
        print colored("[---  INFO   ---] Test Challenge List. User NOT logged in...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False),
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))

        for challenge in response.context["challenges"]:
            if challenge.organization:
                self.assertFalse(
                    challenge.organization.is_hidden,
                    colored("[---  ERROR  ---] Wrong Status of the Challenge", "white", "on_red"))

    def test_user_logged_in(self):
        """Challenge List. User logged in. Simple Case."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in. Simple Case...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False),
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))

        for challenge in response.context["challenges"]:
            self.assertFalse(
                challenge.organization.is_hidden,
                colored("[---  ERROR  ---] Wrong Status of the Challenge", "white", "on_red"))

    def test_user_logged_in_and_author_of_private_org(self):
        """Challenge List. User logged in, and the Author of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and the Author of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_12,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_staff_member_of_private_org(self):
        """Challenge List. User logged in, and the Staff Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and the Staff Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Staff Member of the private Organization
        OrganizationStaff.objects.create(
            author=self.test_author_3,
            organization=self.test_private_org_3,
            member=self.test_user_2,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_3,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_32,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_group_member_of_private_org(self):
        """Challenge List. User logged in, and the Group Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and the Group Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Group Member of the private Organization
        org_group = OrganizationGroup.objects.create(
            author=self.test_author_3,
            name="Test Group",
            organization=self.test_private_org_3,
        )
        org_group.members.add(self.test_user_2)
        org_group.save()

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_3,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_32,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_author_and_staff_member_of_private_org(self):
        """Challenge List. User logged in, and Author and the Staff Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and Author and the Staff Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Staff Member of the private Organization
        OrganizationStaff.objects.create(
            author=self.test_author_3,
            organization=self.test_private_org_3,
            member=self.test_author_1,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ) |
                Q(
                    author=self.test_author_3,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_12,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_32,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_author_and_group_member_of_private_org(self):
        """Challenge List. User logged in, and Author the Group Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and Author the Group Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Group Member of the private Organization
        org_group = OrganizationGroup.objects.create(
            author=self.test_author_3,
            name="Test Group",
            organization=self.test_private_org_3,
        )
        org_group.members.add(self.test_author_1)
        org_group.save()

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ) |
                Q(
                    author=self.test_author_3,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
            ).exclude(
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_12,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))
        self.assertIn(
            self.test_upcoming_private_chl_32,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))


class ChallengeDatelessListViewTestCase(TestCase):

    """Challenge List Test Case.

        COVERS:
                USER                        CHALLENGE
                --------------------------- -----------------------------------
                NOT logged in

                    Logged in               Dateless Chl of pub Org
                                            Auth  of Chl of prv Org
                                            Staff Member or prv Org
                                            Group Member of prv Org
                                            Auth  of Chl &  Staff Member of prv Org
                                            Auth  of Chl &  Group Member of prv Org
    """

    fixtures = [
        "test_accounts.json",
        "test_challenges_completed.json",
        "test_challenges_dateless.json",
        "test_challenges_draft.json",
        "test_challenges_pastdue.json",
        "test_challenges_upcoming.json",
        "test_core_addr_acc.json",
        "test_core_addr_chl.json",
        "test_core_addr_org.json",
        "test_organizations_private.json",
        "test_organizations_public.json",
    ]

    def setUp(self):
        """Set up."""
        print colored("***" * 27, "green")
        print colored("*** TEST > CHALLENGES > VIEWS > LIST", "green")

        # ---------------------------------------------------------------------
        # --- Fake

        # ---------------------------------------------------------------------
        # --- Initials
        self.url = reverse("challenge-dateless-list")

        # --- Users
        self.test_author_1 = User.objects.get(id=1)
        self.test_author_3 = User.objects.get(id=3)

        self.test_user_2 = User.objects.get(id=2)
        self.test_user_4 = User.objects.get(id=4)

        # --- Challenges
        self.test_draft_chl_11 = Challenge.objects.get(id=211)
        self.test_draft_chl_21 = Challenge.objects.get(id=221)

        self.test_upcoming_private_chl_12 = Challenge.objects.get(id=212)
        self.test_upcoming_private_chl_32 = Challenge.objects.get(id=232)

        self.test_upcoming_public_chl_22 = Challenge.objects.get(id=222)
        self.test_upcoming_public_chl_42 = Challenge.objects.get(id=242)

        self.test_completed_chl_13 = Challenge.objects.get(id=213)
        self.test_completed_chl_23 = Challenge.objects.get(id=223)

        self.test_pastdue_chl_24 = Challenge.objects.get(id=224)
        self.test_pastdue_chl_44 = Challenge.objects.get(id=244)

        self.test_dateless_chl_15 = Challenge.objects.get(id=215)
        self.test_dateless_chl_25 = Challenge.objects.get(id=225)

        # --- Organizations
        self.test_private_org_1 = Organization.objects.get(id=31)
        self.test_private_org_3 = Organization.objects.get(id=33)

        self.test_public_org_2 = Organization.objects.get(id=32)
        self.test_public_org_4 = Organization.objects.get(id=34)

    def test_user_not_logged_in(self):
        """Challenge List. User NOT logged in."""
        print colored("[---  INFO   ---] Test Challenge List. User NOT logged in...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False),
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))

        for challenge in response.context["challenges"]:
            if challenge.organization:
                self.assertFalse(
                    challenge.organization.is_hidden,
                    colored("[---  ERROR  ---] Wrong Status of the Challenge", "white", "on_red"))

    def test_user_logged_in(self):
        """Challenge List. User logged in. Simple Case."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in. Simple Case...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False),
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))

        for challenge in response.context["challenges"]:
            self.assertFalse(
                challenge.organization.is_hidden,
                colored("[---  ERROR  ---] Wrong Status of the Challenge", "white", "on_red"))

    def test_user_logged_in_and_author_of_private_org(self):
        """Challenge List. User logged in, and the Author of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and the Author of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_15,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_staff_member_of_private_org(self):
        """Challenge List. User logged in, and the Staff Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and the Staff Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Staff Member of the private Organization
        OrganizationStaff.objects.create(
            author=self.test_author_1,
            organization=self.test_private_org_1,
            member=self.test_user_2,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_15,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_group_member_of_private_org(self):
        """Challenge List. User logged in, and the Group Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and the Group Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Group Member of the private Organization
        org_group = OrganizationGroup.objects.create(
            author=self.test_author_1,
            name="Test Group",
            organization=self.test_private_org_1,
        )
        org_group.members.add(self.test_user_2)
        org_group.save()

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_15,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_author_and_staff_member_of_private_org(self):
        """Challenge List. User logged in, and Author and the Staff Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and Author and the Staff Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Staff Member of the private Organization
        OrganizationStaff.objects.create(
            author=self.test_author_3,
            organization=self.test_private_org_3,
            member=self.test_author_1,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ) |
                Q(
                    author=self.test_author_3,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_15,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_25,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))

    def test_user_logged_in_and_author_and_group_member_of_private_org(self):
        """Challenge List. User logged in, and Author the Group Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge List. User logged in, and Author the Group Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Group Member of the private Organization
        org_group = OrganizationGroup.objects.create(
            author=self.test_author_3,
            name="Test Group",
            organization=self.test_private_org_3,
        )
        org_group.members.add(self.test_author_1)
        org_group.save()

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["challenges"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_list.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            len(response.context["challenges"]),
            len(Challenge.objects.filter(
                Q(organization=None) |
                Q(organization__is_hidden=False) |
                Q(
                    author=self.test_author_1,
                    organization__is_hidden=True,
                ) |
                Q(
                    author=self.test_author_3,
                    organization__is_hidden=True,
                ),
                status=CHALLENGE_STATUS.UPCOMING,
                start_date__gte=datetime.date.today(),
                recurrence=RECURRENCE.DATELESS,
            )),
            colored("[---  ERROR  ---] Wrong Amount of Challenges returned", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_15,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))
        self.assertIn(
            self.test_dateless_chl_25,
            response.context["challenges"],
            colored("[---  ERROR  ---] Target Challenge is not returned in the List", "white", "on_red"))


class ChallengeCreateViewTestCase(TestCase):

    """Challenge create Test Case.

        COVERS:
                USER                        CHALLENGE
                --------------------------- -----------------------------------
                NOT logged in

                    Logged in
    """

    fixtures = [
        "test_accounts.json",
        "test_core_addr_acc.json",
    ]

    def setUp(self):
        """Set up."""
        print colored("***" * 27, "green")
        print colored("*** TEST > CHALLENGES > VIEWS > CREATE", "green")

        # ---------------------------------------------------------------------
        # --- Fake

        # ---------------------------------------------------------------------
        # --- Initials
        self.url = reverse("challenge-create")
        self.login_url = reverse("login")

        # --- Users
        self.test_user_1 = User.objects.get(id=1)
        self.test_user_3 = User.objects.get(id=3)
        self.test_user_2 = User.objects.get(id=2)
        self.test_user_4 = User.objects.get(id=4)

    def test_user_not_logged_in(self):
        """Challenge create. User NOT logged in."""
        print colored("[---  INFO   ---] Test Challenge create. User NOT logged in...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.login_url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "accounts/account_login.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        if response.redirect_chain:
            # -----------------------------------------------------------------
            path, status_code = response.redirect_chain[0]

            self.assertTrue(
                self.url in path,
                "[---  ERROR  ---] %s NOT in URL Path..." % self.url)
            self.assertEqual(
                status_code, 301,
                "[---  ERROR  ---] Wrong Status Code...")

            # -----------------------------------------------------------------
            path, status_code = response.redirect_chain[1]

            self.assertTrue(
                "?next=" in path,
                "[---  ERROR  ---] '?next=' NOT in URL Path...")
            self.assertEqual(
                status_code, 302,
                "[---  ERROR  ---] Wrong Status Code...")

    def test_user_logged_in(self):
        """Challenge create. User logged in."""
        print colored("[---  INFO   ---] Test Challenge create. User logged in...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        response = client.get(
            self.url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            self.url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_create.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))


class ChallengeDetailsViewTestCase(TestCase):

    """Challenge Details Test Case.

        COVERS:
                USER                        CHALLENGE
                --------------------------- -----------------------------------
                NOT logged in               Upcoming Chl of pub Org
                                            Upcoming Chl of prv Org
                                            Draft    Chl
                                            Complete Chl
                                            Past due Chl
                                            Dateless Chl

                    Logged in               Upcoming Chl of pub Org
                                            Upcoming Chl of pub Org, waiting   4  Conf
                                            Upcoming Chl of pub Org, confirmed
                                            Upcoming Chl of pub Org, canceled  by Adm
                                            Upcoming Chl of pub Org, canceled  by Usr,    reenter
                                            Upcoming Chl of pub Org, canceled  by Usr, NO reenter
                                            Upcoming Chl of pub Org, waiting   4  selfreflection
                                            Upcoming Chl of pub Org, waiting   4  acknowledgment
                                            Upcoming Chl of pub Org, acknowledged
    """

    fixtures = [
        "test_accounts.json",
        "test_accounts_privacy_basic.json",
        "test_challenges_completed.json",
        "test_challenges_dateless.json",
        "test_challenges_draft.json",
        "test_challenges_pastdue.json",
        "test_challenges_upcoming.json",
        "test_core_addr_acc.json",
        "test_core_addr_chl.json",
        "test_core_addr_org.json",
        "test_organizations_private.json",
        "test_organizations_public.json",
    ]

    def setUp(self):
        """Set up."""
        print colored("***" * 27, "green")
        print colored("*** TEST > CHALLENGES > VIEWS > DETAILS", "green")

        # ---------------------------------------------------------------------
        # --- Fake

        # ---------------------------------------------------------------------
        # --- Initials

        # --- Users
        self.test_author_1 = User.objects.get(id=1)
        self.test_author_3 = User.objects.get(id=3)

        self.test_user_2 = User.objects.get(id=2)
        self.test_user_4 = User.objects.get(id=4)

        # --- Challenges
        self.test_draft_chl_11 = Challenge.objects.get(id=211)
        self.test_draft_chl_21 = Challenge.objects.get(id=221)

        self.test_upcoming_private_chl_12 = Challenge.objects.get(id=212)
        self.test_upcoming_private_chl_32 = Challenge.objects.get(id=232)

        self.test_upcoming_public_chl_22 = Challenge.objects.get(id=222)
        self.test_upcoming_public_chl_42 = Challenge.objects.get(id=242)

        self.test_completed_chl_13 = Challenge.objects.get(id=213)
        self.test_completed_chl_23 = Challenge.objects.get(id=223)

        self.test_pastdue_chl_24 = Challenge.objects.get(id=224)
        self.test_pastdue_chl_44 = Challenge.objects.get(id=244)

        self.test_dateless_chl_15 = Challenge.objects.get(id=215)
        self.test_dateless_chl_25 = Challenge.objects.get(id=225)

        # --- Organizations
        self.test_private_org_1 = Organization.objects.get(id=31)
        self.test_private_org_3 = Organization.objects.get(id=33)

        self.test_public_org_2 = Organization.objects.get(id=32)
        self.test_public_org_4 = Organization.objects.get(id=34)

    def test_user_not_logged_in_chl_of_public_org(self):
        """Challenge Details. User NOT logged in. Challenge of the public Organization."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge of the public Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_22.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_22,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertIsNone(
            response.context["participation"],
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_not_logged_in_chl_of_private_org(self):
        """Challenge Details. User NOT logged in. Challenge of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_private_chl_12.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_not_logged_in_chl_draft(self):
        """Challenge Details. User NOT logged in. Challenge Draft."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge Draft...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_draft_chl_21.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_not_logged_in_chl_completed(self):
        """Challenge Details. User NOT logged in. Challenge completed."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge completed...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_completed_chl_23.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_not_logged_in_chl_pastdue(self):
        """Challenge Details. User NOT logged in. Challenge past due."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge past due...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_pastdue_chl_24.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_not_logged_in_chl_dateless(self):
        """Challenge Details. User NOT logged in. Challenge dateless."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge dateless...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_dateless_chl_25.slug,
            })
        data = {}

        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_dateless_chl_25,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertIsNone(
            response.context["participation"],
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org(self):
        """Challenge Details. User logged in. Challenge of the public Organization."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_42.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_42,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertIsNone(
            response.context["participation"],
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_waiting(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Participation waiting for Confirmation."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Participation waiting for Confirmation...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_2,
            challenge=self.test_upcoming_public_chl_42,
            # role=,
            status=PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_42.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_42,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_confirmed(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Participation confirmed."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Participation confirmed...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_2,
            challenge=self.test_upcoming_public_chl_42,
            # role=,
            status=PARTICIPATION_STATUS.CONFIRMED,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_42.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_42,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_canceled_by_admin(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Participation canceled by Admin."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Participation canceled by Admin...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_2,
            challenge=self.test_upcoming_public_chl_42,
            # role=,
            status=PARTICIPATION_STATUS.CANCELLED_BY_ADMIN,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_42.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_42,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_canceled_by_user_reenter_allowed(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Participation canceled by User. Reenter allowed."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Participation canceled by User. Reenter allowed...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_2,
            challenge=self.test_upcoming_public_chl_42,
            # role=,
            status=PARTICIPATION_STATUS.CANCELLED_BY_USER,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_42.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_42,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_canceled_by_user_reenter_not_allowed(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Participation canceled by User. Reenter NOT allowed."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Participation canceled by User. Reenter NOT allowed...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_4.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_4,
            challenge=self.test_upcoming_public_chl_22,
            # role=,
            status=PARTICIPATION_STATUS.CANCELLED_BY_USER,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_22.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_22,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_waiting_for_selfreflection(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Waiting for Selfreflection."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Waiting for Selfreflection...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_4.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_4,
            challenge=self.test_upcoming_public_chl_22,
            # role=,
            status=PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_22.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_22,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_waiting_for_acknowledgment(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Waiting for Acknowledgment."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Waiting for Acknowledgment...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_4.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_4,
            challenge=self.test_upcoming_public_chl_22,
            # role=,
            status=PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_22.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_22,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_public_org_acknowledged(self):
        """Challenge Details. User logged in. Challenge of the public Organization. Acknowledged."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the public Organization. Acknowledged...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_4.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Participant of the Challenge
        participation = Participation.objects.create(
            user=self.test_user_4,
            challenge=self.test_upcoming_public_chl_22,
            # role=,
            status=PARTICIPATION_STATUS.ACKNOWLEDGED,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_public_chl_22.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_public_chl_22,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertEqual(
            response.context["participation"],
            participation,
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertTrue(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_chl_of_private_org(self):
        """Challenge Details. User logged in. Challenge of the Private Organization."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge of the Private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_private_chl_12.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    # TODO

    def test_user_logged_in_chl_draft(self):
        """Challenge Details. User logged in. Challenge Draft."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge Draft...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_4.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_draft_chl_21.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_logged_in_chl_completed(self):
        """Challenge Details. User logged in. Challenge completed."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. Challenge completed...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_4.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_completed_chl_23.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_not_logged_in_chl_pastdue(self):
        """Challenge Details. User NOT logged in. Challenge past due."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge past due...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_pastdue_chl_24.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            404,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "404.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

    def test_user_not_logged_in_chl_dateless(self):
        """Challenge Details. User NOT logged in. Challenge dateless."""
        print colored("[---  INFO   ---] Test Challenge Details. User NOT logged in. Challenge dateless...", "cyan")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_dateless_chl_25.slug,
            })
        data = {}

        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_dateless_chl_25,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertIsNone(
            response.context["participation"],
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    # TODO

    def test_user_logged_in_and_author_of_upcoming_chl(self):
        """Challenge Details. User logged in, and the Author of the upcoming Challenge."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in, and the Author of the upcoming Challenge...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_author_1.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        data = {}
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_upcoming_private_chl_12.slug,
            })
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["challenge"],
            self.test_upcoming_private_chl_12,
            colored("[---  ERROR  ---] Wrong Challenge returned", "white", "on_red"))
        self.assertIsNone(
            response.context["participation"],
            colored("[---  ERROR  ---] Wrong Participation returned", "white", "on_red"))
        self.assertTrue(
            response.context["is_admin"],
            colored("[---  ERROR  ---] Wrong `is_admin` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_withdraw_form"],
            colored("[---  ERROR  ---] Wrong `show_withdraw_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_signup_form"],
            colored("[---  ERROR  ---] Wrong `show_signup_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_selfreflection_form"],
            colored("[---  ERROR  ---] Wrong `show_selfreflection_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_not_participated_form"],
            colored("[---  ERROR  ---] Wrong `show_not_participated_form` returned", "white", "on_red"))
        self.assertFalse(
            response.context["show_rate_form"],
            colored("[---  ERROR  ---] Wrong `show_rate_form` returned", "white", "on_red"))

    def test_user_logged_in_and_staff_member_of_private_org(self):
        """Challenge Details. User logged in, and the Staff Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in, and the Staff Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Staff Member of the private Organization
        OrganizationStaff.objects.create(
            author=self.test_author_3,
            organization=self.test_private_org_3,
            member=self.test_user_2,
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_private_org_3.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["organization"],
            self.test_private_org_3,
            colored("[---  ERROR  ---] Wrong Organization returned", "white", "on_red"))

    def test_user_logged_in_and_group_member_of_private_org(self):
        """Challenge Details. User logged in, and the Group Member of the private Organization."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in, and the Group Member of the private Organization...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Group Member of the private Organization
        org_group = OrganizationGroup.objects.create(
            author=self.test_author_3,
            name="Test Group",
            organization=self.test_private_org_3,
        )
        org_group.members.add(self.test_user_2)
        org_group.save()

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_private_org_3.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["organization"],
            self.test_private_org_3,
            colored("[---  ERROR  ---] Wrong Organization returned", "white", "on_red"))

    def test_user_logged_in_not_subscriber(self):
        """Challenge Details. User logged in. NOT an Organization Subscriber."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. NOT an Organization Subscriber...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_public_org_4.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["organization"],
            self.test_public_org_4,
            colored("[---  ERROR  ---] Wrong Organization returned", "white", "on_red"))
        self.assertFalse(
            response.context["is_subscribed"],
            colored("[---  ERROR  ---] Wrong subscribed Information returned", "white", "on_red"))

    def test_user_logged_in_subscriber(self):
        """Challenge Details. User logged in. An Organization Subscriber."""
        print colored("[---  INFO   ---] Test Challenge Details. User logged in. An Organization Subscriber...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_2.username,
            password="test"
        )
        # print colored("[---  DUMP   ---] LOGIN            : %s" % result, "yellow")

        # ---------------------------------------------------------------------
        # --- Make User a Subscribed of the Organization
        self.test_public_org_4.subscribers.add(self.test_user_2)
        self.test_public_org_4.save()

        # ---------------------------------------------------------------------
        # --- Send Request
        url = reverse("challenge-details", kwargs={
            "slug":     self.test_public_org_4.slug,
            })
        data = {}
        response = client.get(
            url,
            data=data,
            follow=True)

        # print colored("[---  DUMP   ---] CONTEXT          : %s" % response.context["organizations"], "yellow")
        # print colored("[---  DUMP   ---] REQUEST          : %s" % response.request, "yellow")
        # print colored("[---  DUMP   ---] STATUS           : %s" % response.status_code, "yellow")
        # print colored("[---  DUMP   ---] TEMPLATES        : %s" % response.templates, "yellow")
        # print colored("[---  DUMP   ---] CONTENT          : %s" % response.content, "yellow")
        # print colored("[---  DUMP   ---] REDIRECT CHAIN   : %s" % response.redirect_chain, "yellow")

        # ---------------------------------------------------------------------
        # --- Test Response
        self.assertEqual(
            response.request["PATH_INFO"],
            url,
            colored("[---  ERROR  ---] Wrong Path", "white", "on_red"))
        self.assertEqual(
            response.status_code,
            200,
            colored("[---  ERROR  ---] Wrong Status Code", "white", "on_red"))
        self.assertTemplateUsed(
            response,
            "challenges/challenge_details.html",
            colored("[---  ERROR  ---] Wrong Template used", "white", "on_red"))

        self.assertEqual(
            response.context["organization"],
            self.test_public_org_4,
            colored("[---  ERROR  ---] Wrong Organization returned", "white", "on_red"))
        self.assertTrue(
            response.context["is_subscribed"],
            colored("[---  ERROR  ---] Wrong subscribed Information returned", "white", "on_red"))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ AJAX
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ TEMPLATES
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ FORMS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ChallengeCreateFormTestCase(TestCase):

    """Challenge create Test Case."""

    fixtures = [
        "test_accounts.json",
        "test_core_addr_acc.json",
    ]

    def setUp(self):
        """Set up."""
        print colored("***" * 27, "green")
        print colored("*** TEST > CHALLENGES > FORMS > CREATE", "green")

        # ---------------------------------------------------------------------
        # --- Fake

        # ---------------------------------------------------------------------
        # --- Initials
        self.login_url = reverse("login")

        # --- Users
        self.test_user_1 = User.objects.get(id=1)
        self.test_user_3 = User.objects.get(id=3)
        self.test_user_2 = User.objects.get(id=2)
        self.test_user_4 = User.objects.get(id=4)

    def test_create_chl_success(self):
        """Challenge create. Success."""
        print colored("[---  INFO   ---] Test Challenge create. Success...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                "name":                 "Testing Challenge #1",
                "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                "tags":                 "testing,challenge",
                "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.ONCE,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                "start_date":           "2017-12-31",
                "start_time":           "00:00",
                "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertTrue(
            form.is_valid())

        # self.assertEqual(form.clean_id_number(),"0000528989")
        # self.assertIn(u"Invalid Action",form.errors["__all__"])

    def test_create_chl_no_avatar(self):
        """Challenge create. No Avatar."""
        print colored("[---  INFO   ---] Test Challenge create. No Avatar...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                "name":                 "Testing Challenge #1",
                "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                "tags":                 "testing,challenge",
                "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.ONCE,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                "start_date":           "2017-12-31",
                "start_time":           "00:00",
                "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                # "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertFalse(
            form.is_valid())

    def test_create_chl_no_name_no_description(self):
        """Challenge create. No Name, no Description."""
        print colored("[---  INFO   ---] Test Challenge create. No Name, no Description...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                # "name":                 "Testing Challenge #1",
                # "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                "tags":                 "testing,challenge",
                "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.ONCE,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                "start_date":           "2017-12-31",
                "start_time":           "00:00",
                "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertFalse(
            form.is_valid())
        self.assertIn(
            "name",
            form.errors.as_json())
        self.assertNotIn(
            "description",
            form.errors.as_json())

    def test_create_chl_no_tags(self):
        """Challenge create. No Tags."""
        print colored("[---  INFO   ---] Test Challenge create. No Tags...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )

        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                "name":                 "Testing Challenge #1",
                "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                # "tags":                 "testing,challenge",
                # "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.ONCE,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                "start_date":           "2017-12-31",
                "start_time":           "00:00",
                "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertTrue(
            form.is_valid())
        self.assertNotIn(
            "tags",
            form.errors.as_json())
        self.assertNotIn(
            "hashtag",
            form.errors.as_json())

    def test_create_chl_dateless(self):
        """Challenge create. Dateless."""
        print colored("[---  INFO   ---] Test Challenge create. Dateless...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )

        # ---------------------------------------------------------------------
        # --- Successful
        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                "name":                 "Testing Challenge #1",
                "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                "tags":                 "testing,challenge",
                "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.DATELESS,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                # "start_date":           "2017-12-31",
                # "start_time":           "00:00",
                # "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertTrue(
            form.is_valid())

        # --- Save Form
        instance = form.save()

        self.assertEqual(
            instance.recurrence,
            RECURRENCE.DATELESS)

        self.assertIn(
            MONTH.NONE,
            instance.month)
        self.assertIn(
            DAY_OF_WEEK.NONE,
            instance.day_of_week)
        self.assertIn(
            "0",
            instance.day_of_month)

        self.assertIsNone(instance.start_date)
        self.assertIsNone(instance.start_time)

        self.assertIsNotNone(instance.start_tz)

    def test_create_chl_once(self):
        """Challenge create. Once. Success."""
        print colored("[---  INFO   ---] Test Challenge create. Once...", "cyan")

        # ---------------------------------------------------------------------
        # --- Log in
        result = client.login(
            username=self.test_user_1.username,
            password="test"
        )

        # ---------------------------------------------------------------------
        # --- Successful
        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                "name":                 "Testing Challenge #1",
                "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                "tags":                 "testing,challenge",
                "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.ONCE,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                "start_date":           "2017-12-31",
                "start_time":           "00:00",
                "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertTrue(
            form.is_valid())

        # --- Save Form
        instance = form.save()

        self.assertEqual(
            instance.recurrence,
            RECURRENCE.ONCE)

        self.assertIn(
            MONTH.NONE,
            instance.month)
        self.assertIn(
            DAY_OF_WEEK.NONE,
            instance.day_of_week)
        self.assertIn(
            "0",
            instance.day_of_month)

        self.assertIsNotNone(instance.start_date)
        self.assertIsNotNone(instance.start_time)

        self.assertIsNotNone(instance.start_tz)

        # ---------------------------------------------------------------------
        # --- No Date/Time
        # ---------------------------------------------------------------------
        # --- Send Request
        form = CreateEditChallengeForm(
            data={
                "name":                 "Testing Challenge #1",
                "description":          "Description for the testing Challenge #1",
                "category":             CHALLENGE_CATEGORY.ANIMALS,
                "tags":                 "testing,challenge",
                "hashtag":              "testing-challenge",
                "duration":             8,
                "addressless":          False,
                "is_alt_person":        False,
                "contact":              "me",
                "alt_person_fullname":  "",
                "alt_person_email":     "",
                "alt_person_phone":     "",
                "recurrence":           RECURRENCE.ONCE,
                "month":                MONTH.NONE,
                "day_of_week":          DAY_OF_WEEK.NONE,
                "day_of_month":         "0",
                # "start_date":           "2017-12-31",
                # "start_time":           "00:00",
                # "start_tz":             "America/Los_Angeles",
                "organization":         None,
                "application":          CHALLENGE_MODE.FREE_FOR_ALL,
                "allow_reenter":        True,
                "accept_automatically": True,
                "acceptance_text":      "Great Job",
            },
            files={
                "avatar":               File(open("static/img/tests/challenge-test.jpg", "rb")),
            },
            user=self.test_user_1,
            )

        # ---------------------------------------------------------------------
        # --- Test Response
        form.is_valid()
        print colored("[--- ERRORS ---] %s" % form.errors.as_json(), "white", "on_red")

        self.assertFalse(
            form.is_valid())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ UTILS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""
    self.assertEqual                /               self.assertNotEqual
    self.assertGreater
    self.assertGreaterEqual
    self.assertLess
    self.assertLessEqual
    self.assertTrue                 /               self.assertFalse
    self.assertIs                   /               self.assertIsNot
    self.assertIsNone               /               self.assertIsNotNone
    self.assertIn                   /               self.assertNotIn
    self.assertIsInstance           /               self.assertNotIsInstance
    self.assertRegexpMatches        /               self.assertNotRegexpMatches
    self.assertRaises
    self.assertRaisesRegexp

    self.assertDictContainsSubset

    self.assertContains             /               self.assertNotContains
    self.assertTemplateUsed         /               self.assertTemplateNotUsed
    self.assertInHTML
    self.assertJSONEqual            /               self.assertJSONNotEqual
"""
