import inspect

from importlib import import_module

from django.apps import AppConfig

from termcolor import colored


class CoreConfig(AppConfig):
    """Docstring."""

    name = "core"

    def ready(self):
        """Docstring."""
        print colored("***" * 27, "green")
        print colored("*** INSIDE `%s.%s`" % (self.__class__.__name__, inspect.stack()[0][3]), "green")

        import_module("core.tasks")
