from functools import wraps

from django.db.models.signals import (
    pre_save,
    post_save,
    pre_delete,
    post_delete,
    m2m_changed
    )

import papertrail


# Original Idea: http://djangosnippets.org/snippets/2124/
def autoconnect(cls):
    """Class Decorator.

    Automatically connects pre_save / post_save signals on a model class to its
    pre_save() / post_save() methods.
    """
    def connect(signal, func):
        cls.func = staticmethod(func)

        @wraps(func)
        def wrapper(sender, **kwargs):
            return func(kwargs.get("instance"), **kwargs)

        signal.connect(wrapper, sender=cls)

        return wrapper

    if hasattr(cls, "pre_save"):
        cls.pre_save = connect(pre_save, cls.pre_save)

    if hasattr(cls, "post_save"):
        cls.post_save = connect(post_save, cls.post_save)

    if hasattr(cls, "pre_delete"):
        cls.pre_delete = connect(pre_delete, cls.pre_delete)

    if hasattr(cls, "post_delete"):
        cls.post_delete = connect(post_delete, cls.post_delete)

    if hasattr(cls, "m2m_changed"):
        cls.m2m_changed = connect(m2m_changed, cls.m2m_changed)

    return cls


def exception(func):
    """A Decorator.

    Wraps the passed in Function, and logs Exceptions should one occur.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # -----------------------------------------------------------------
            # --- Save the Log
            papertrail.log(
                event_type="runtime-exception",
                message="There was an exception in " + func.__name__,
                data={
                    "success":      False,
                    "origin":       func.__name__,
                    "response":     str(e),
                },
                # timestamp=timezone.now(),
                targets={},
                )

            # -----------------------------------------------------------------
            # --- Re-raise the Exception
            raise

    return wrapper
