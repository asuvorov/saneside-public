from accounts.forms import LoginForm


def signin_form(request):
    """Docstring."""
    signin_form = LoginForm()

    return {
        "signin_form":  signin_form,
    }
