from challenges.choices import (
    CHALLENGE_STATUS, challenge_status_choices,
    CHALLENGE_MODE, application_choices,
    CHALLENGE_CATEGORY, challenge_category_choices,
    CHALLENGE_COLORS, challenge_category_colors,
    CHALLENGE_ICONS, challenge_category_icons,
    CHALLENGE_IMAGES, challenge_category_images,
    PARTICIPATION_REMOVE_MODE,
    PARTICIPATION_STATUS, participation_status_choices,
    RECURRENCE, recurrence_choices,
    MONTH, month_choices,
    DAY_OF_WEEK, day_of_week_choices,
    day_of_month_choices,
    )


def pb_challenge_choices(request):
    """Docstring."""
    return {
        "CHALLENGE_STATUS":             CHALLENGE_STATUS,
        "CHALLENGE_MODE":               CHALLENGE_MODE,
        "CHALLENGE_CATEGORY":           CHALLENGE_CATEGORY,
        "challenge_category_choices":   challenge_category_choices,
        "CHALLENGE_COLORS":             CHALLENGE_COLORS,
        "challenge_category_colors":    challenge_category_colors,
        "CHALLENGE_ICONS":              CHALLENGE_ICONS,
        "challenge_category_icons":     challenge_category_icons,
        "CHALLENGE_IMAGES":             CHALLENGE_IMAGES,
        "challenge_category_images":    challenge_category_images,
    }


def pb_participation_choices(request):
    """Docstring."""
    return {
        "PARTICIPATION_STATUS":         PARTICIPATION_STATUS,
        "PARTICIPATION_REMOVE_MODE":    PARTICIPATION_REMOVE_MODE,
        "participation_status_choices": participation_status_choices,
    }


def pb_recurrence_choices(request):
    """Docstring."""
    return {
        "RECURRENCE":                   RECURRENCE,
        "recurrence_choices":           recurrence_choices,
        "MONTH":                        MONTH,
        "month_choices":                month_choices,
        "DAY_OF_WEEK":                  DAY_OF_WEEK,
        "day_of_week_choices":          day_of_week_choices,
        "day_of_month_choices":         day_of_month_choices,
    }
