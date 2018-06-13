default_app_config = "core.apps.CoreConfig"


def enum(**args):
    """Enum."""
    return type("Enum", (), args)
