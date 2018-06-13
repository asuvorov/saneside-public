from core.decorators import exception


@exception
def form_field_error_list(form):
    form_errors = []

    for field in form:
        if field.errors:
            for error in field.errors:
                form_errors.append(
                    u"{label} : {value} : {error}".format(
                        label=field.label,
                        value=field.value(),
                        error=error,
                    )
                )
        else:
            form_errors.append(
                u"{label} : {value}".format(
                    label=field.label,
                    value=field.value(),
                )
            )

    return form_errors
