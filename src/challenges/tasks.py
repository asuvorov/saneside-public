import datetime
import inspect

from django.conf import settings
from django.utils.translation import ugettext as _

import papertrail

from apscheduler.schedulers.background import BackgroundScheduler
from termcolor import colored

from api.sendgrid_api import send_templated_email
from challenges.models import Challenge


background_scheduler = BackgroundScheduler()


# -----------------------------------------------------------------------------
# --- Start all the scheduled Tasks
# -----------------------------------------------------------------------------
def start_all():
    """Start all of the Cron Tasks."""
    background_scheduler.start()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ TASKS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# -----------------------------------------------------------------------------
# --- Notify Admins about overdue Challenges.
#     A periodic Task that runs every Midnight.
# -----------------------------------------------------------------------------
@background_scheduler.scheduled_job(
    "cron", hour="0", minute="0", day_of_week="*")
def challenge_overdue_notify_admin():
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    try:
        upcoming_challenges = Challenge.objects.get_upcoming()

        for challenge in upcoming_challenges:
            if challenge.is_overdue:
                # -------------------------------------------------------------
                # --- Render HTML Email Content
                greetings = _(
                    "Dear, %(user)s.") % {
                        "user":     challenge.author.first_name,
                    }
                htmlbody = _(
                    "<p>Your Challenge \"<a href=\"%(url)s\">%(name)s</a>\" is overdue!</p>"
                    "<p>If this Challenge has taken place as planned, please, mark it as completed.</p>"
                    "<p>Remember to remove all Participants from the Challenge, who did not show up to help, so the Challenge will not appear on their Profiles.</p>") % {
                        "url":      challenge.public_url(),
                        "name":     challenge.name,
                    }

                # -------------------------------------------------------------
                # --- Send Notification to Challenge Admin
                send_templated_email(
                    template_subj={
                        "name":     "challenges/emails/challenge_overdue_subject.txt",
                        "context":  {},
                    },
                    template_text={
                        "name":     "challenges/emails/challenge_overdue.txt",
                        "context": {
                            "admin":            challenge.author,
                            "challenge":        challenge,
                            "challenge_link":   challenge.public_url(),
                        },
                    },
                    template_html={
                        "name":     "emails/base.html",
                        "context": {
                            "greetings":    greetings,
                            "htmlbody":     htmlbody,
                        },
                    },
                    from_email=settings.EMAIL_SENDER,
                    to=[
                        challenge.author.email,
                    ],
                    headers=None,
                )

        # ---------------------------------------------------------------------
        # --- Save the Log
        papertrail.log(
            event_type="periodic-task-ran",
            message="Periodic Task `%s` executed" % inspect.stack()[0][3],
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

        # ---------------------------------------------------------------------
        # --- Save the Log
        papertrail.log(
            event_type="periodic-task-failed",
            message="Periodic Task `%s` failed" % inspect.stack()[0][3],
            data={
                "success":      False,
                "response":     str(e),
            },
            # timestamp=timezone.now(),
            targets={},
            )

    return True


# -----------------------------------------------------------------------------
# --- Notify Challenge Participants about upcoming Challenges.
#     A periodic Task that runs every 1am.
# -----------------------------------------------------------------------------
@background_scheduler.scheduled_job(
    "cron", hour="0", minute="0", day_of_week="*")
def challenge_upcoming_notify():
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    try:
        upcoming_challenges = Challenge.objects.get_upcoming()

        for challenge in upcoming_challenges:
            days_delta = (challenge.start_date - datetime.date.today()).days

            if days_delta > 0 and days_delta <= 2:
                for participation in challenge.challenge_participations.confirmed():
                    # ---------------------------------------------------------
                    # --- Render HTML Email Content
                    greetings = _(
                        "Dear, %(user)s.") % {
                            "user":     participation.user.first_name,
                        }
                    htmlbody = _(
                        "<p>Don\'t forget that you are signed up for the Challenge \"<a href=\"%(url)s\">%(name)s</a>\" on %(start_date)s at %(start_time)s.</p>"
                        "<p>Please, don\'t forget to show up!</p>") % {
                            "url":          challenge.public_url(),
                            "name":         challenge.name,
                            "start_date":   challenge.get_start_date,
                            "start_time":   challenge.get_start_time,
                        }

                    # ---------------------------------------------------------
                    # --- Send Notification to the Challenge Participants
                    send_templated_email(
                        template_subj={
                            "name":     "challenges/emails/challenge_upcoming_subject.txt",
                            "context":  {},
                        },
                        template_text={
                            "name":     "challenges/emails/challenge_upcoming.txt",
                            "context": {
                                "user":             participation.user,
                                "challenge":        challenge,
                                "challenge_link":   challenge.public_url(),
                            },
                        },
                        template_html={
                            "name":     "emails/base.html",
                            "context": {
                                "greetings":    greetings,
                                "htmlbody":     htmlbody,
                            },
                        },
                        from_email=settings.EMAIL_SENDER,
                        to=[
                            participation.user.email,
                        ],
                        headers=None,
                    )

        # ---------------------------------------------------------------------
        # --- Save the Log
        papertrail.log(
            event_type="periodic-task-ran",
            message="Periodic Task `%s` executed" % inspect.stack()[0][3],
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

        # ---------------------------------------------------------------------
        # --- Save the Log
        papertrail.log(
            event_type="periodic-task-failed",
            message="Periodic Task `%s` failed" % inspect.stack()[0][3],
            data={
                "success":      False,
                "response":     str(e),
            },
            # timestamp=timezone.now(),
            targets={},
            )

    return True


# -----------------------------------------------------------------------------
# --- Call the `main` Function.
# -----------------------------------------------------------------------------
print colored("[---   LOG   ---] Going to start the `CHALLENGES` Tasks", "green")

start_all()
