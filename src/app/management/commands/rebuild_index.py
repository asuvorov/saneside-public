import inspect

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

from termcolor import colored
from haystack.management.commands import (
    rebuild_index,
    update_index,
    )


class Command(BaseCommand):
    """Rebuild/update Search Indexes.

    https://stackoverflow.com/questions/4358771/updating-a-haystack-search-index-with-django-celery
    """

    help = "Rebuild/update Search Indexes."

    def handle(self, *args, **kwargs):
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        print colored("[---   LOG   ---] Going to rebuild Search Indexes...", "green")

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

        self.stdout.write("!!! Successfully rebuilt Indexes !!!\n")
