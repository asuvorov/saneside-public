import datetime
import inspect

from django.conf import settings

import papertrail

from apscheduler.schedulers.background import BackgroundScheduler
from haystack.management.commands import (
    rebuild_index,
    update_index,
    )
from termcolor import colored


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
# --- System Ping
# -----------------------------------------------------------------------------
# @background_scheduler.scheduled_job("interval", minutes=1)
def system_ping():
    """Docstring."""
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    now = datetime.datetime.now()

    print colored("[---  INFO   ---] NOW : %s" % now, "cyan")

    """
    try:
        mail = EmailMultiAlternatives(
            subject="SYSTEM PING",
            body="SANESIDE PING",
            from_email=settings.EMAIL_SENDER,
            to=[
                "artem.suvorov@gmail.com",
            ],
            cc=[],
            bcc=[],
        )
        mail.send()

    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}\n{details}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            details=e.read(),
            ), "white", "on_red")
    """


# -----------------------------------------------------------------------------
# --- Rebuild Search Indexes.
#     A periodic Task that runs every 3 Hours at 0 Minutes.
# -----------------------------------------------------------------------------
@background_scheduler.scheduled_job("interval", hours=3)
def rebuild_search_indexes():
    """Rebuild/update Search Indexes.

    https://stackoverflow.com/questions/4358771/updating-a-haystack-search-index-with-django-celery
    """
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    print colored("[---   LOG   ---] Going to rebuild Search Indexes...", "green")

    try:
        rebuild_index.Command().handle(
            age=4,
            batchsize=1000,
            workers=0,
            max_retries=5,
            interactive=False,
            remove=True,
            verbosity=2,
            using=["default", ])
        """
        update_index.Command().handle(
            age=4,
            interactive=False,
            remove=True,
            verbosity=2,
            using=["default", ])
        """

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
print colored("[---   LOG   ---] Going to start the `CORE` Tasks", "green")

start_all()
