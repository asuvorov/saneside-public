from django.utils.translation import ugettext_lazy as _

from core import enum


# -----------------------------------------------------------------------------
# --- CHALLENGE CHOICES
# -----------------------------------------------------------------------------
CHALLENGE_STATUS = enum(
    DRAFT="0",
    UPCOMING="1",
    COMPLETE="2",
    EXPIRED="4",
    CLOSED="8",
    )
challenge_status_choices = [
    (CHALLENGE_STATUS.DRAFT,    _("Draft")),
    (CHALLENGE_STATUS.UPCOMING, _("Upcoming")),
    (CHALLENGE_STATUS.COMPLETE, _("Complete")),
    (CHALLENGE_STATUS.EXPIRED,  _("Expired")),
    (CHALLENGE_STATUS.CLOSED,   _("Closed")),
    ]

CHALLENGE_MODE = enum(
    FREE_FOR_ALL="0",
    CONFIRMATION_REQUIRED="1",
    )
application_choices = [
    (CHALLENGE_MODE.FREE_FOR_ALL,
        _("Anyone can participate.")),
    (CHALLENGE_MODE.CONFIRMATION_REQUIRED,
        _("Participate only after a confirmed Application")),
    ]


# -----------------------------------------------------------------------------
# --- CHALLENGE CATEGORY CHOICES
# -----------------------------------------------------------------------------
CHALLENGE_CATEGORY = enum(
    ANIMALS="0",
    ARTS="1",
    YOUTH="2",
    COMMUNITY="4",
    EDUCATION="8",
    ENVIRONMENT="16",
    HEALTH="32",
    RECREATION="64",
    SENIOURS="128",
    )
challenge_category_choices = [
    (CHALLENGE_CATEGORY.ANIMALS,        _("Animals")),
    (CHALLENGE_CATEGORY.ARTS,           _("Arts & Culture")),
    (CHALLENGE_CATEGORY.YOUTH,          _("Children & Youth")),
    (CHALLENGE_CATEGORY.COMMUNITY,      _("Community")),
    (CHALLENGE_CATEGORY.EDUCATION,      _("Education & Literacy")),
    (CHALLENGE_CATEGORY.ENVIRONMENT,    _("Environment")),
    (CHALLENGE_CATEGORY.HEALTH,         _("Health & Wellness")),
    (CHALLENGE_CATEGORY.RECREATION,     _("Sports & Recreation")),
    (CHALLENGE_CATEGORY.SENIOURS,       _("Veterans & Seniors")),
    ]

CHALLENGE_COLORS = enum(
    ANIMALS="0",
    ARTS="1",
    YOUTH="2",
    COMMUNITY="4",
    EDUCATION="8",
    ENVIRONMENT="16",
    HEALTH="32",
    RECREATION="64",
    SENIOURS="128",
    )
challenge_category_colors = [
    (CHALLENGE_COLORS.ANIMALS,      "DarkKhaki"),
    (CHALLENGE_COLORS.ARTS,         "LightSteelBlue"),
    (CHALLENGE_COLORS.YOUTH,        "SlateBlue"),
    (CHALLENGE_COLORS.COMMUNITY,    "DarkOrange"),
    (CHALLENGE_COLORS.EDUCATION,    "#DEB887"),
    (CHALLENGE_COLORS.ENVIRONMENT,  "Green"),
    (CHALLENGE_COLORS.HEALTH,       "Red"),
    (CHALLENGE_COLORS.RECREATION,   "LightSeaGreen"),
    (CHALLENGE_COLORS.SENIOURS,     "SaddleBrown"),
    ]

CHALLENGE_ICONS = enum(
    ANIMALS="0",
    ARTS="1",
    YOUTH="2",
    COMMUNITY="4",
    EDUCATION="8",
    ENVIRONMENT="16",
    HEALTH="32",
    RECREATION="64",
    SENIOURS="128",
    )
challenge_category_icons = [
    (CHALLENGE_ICONS.ANIMALS,       "fa fa-paw fa-fw"),
    (CHALLENGE_ICONS.ARTS,          "fa fa-wrench fa-fw"),
    (CHALLENGE_ICONS.YOUTH,         "fa fa-child fa-fw"),
    (CHALLENGE_ICONS.COMMUNITY,     "fa fa-users fa-fw"),
    (CHALLENGE_ICONS.EDUCATION,     "fa fa-book fa-fw"),
    (CHALLENGE_ICONS.ENVIRONMENT,   "fa fa-tree fa-fw"),
    (CHALLENGE_ICONS.HEALTH,        "fa fa-heartbeat fa-fw"),
    (CHALLENGE_ICONS.RECREATION,    "fa fa-bicycle fa-fw"),
    (CHALLENGE_ICONS.SENIOURS,      "fa fa-home fa-fw"),
    ]


CHALLENGE_IMAGES = enum(
    ANIMALS="0",
    ARTS="1",
    YOUTH="2",
    COMMUNITY="4",
    EDUCATION="8",
    ENVIRONMENT="16",
    HEALTH="32",
    RECREATION="64",
    SENIOURS="128",
    )
challenge_category_images = [
    (CHALLENGE_IMAGES.ANIMALS,       "/img/challenge-categories/1-animals.jpeg"),
    (CHALLENGE_IMAGES.ARTS,          "/img/challenge-categories/2-arts-and-culture.jpeg"),
    (CHALLENGE_IMAGES.YOUTH,         "/img/challenge-categories/3-children-and-youth.jpeg"),
    (CHALLENGE_IMAGES.COMMUNITY,     "/img/challenge-categories/4-community.jpeg"),
    (CHALLENGE_IMAGES.EDUCATION,     "/img/challenge-categories/5-education-and-literacy.jpeg"),
    (CHALLENGE_IMAGES.ENVIRONMENT,   "/img/challenge-categories/6-environment-2.jpeg"),
    (CHALLENGE_IMAGES.HEALTH,        "/img/challenge-categories/7-health-and-wellness.jpeg"),
    (CHALLENGE_IMAGES.RECREATION,    "/img/challenge-categories/8-sports-and-recreation.jpeg"),
    (CHALLENGE_IMAGES.SENIOURS,      "/img/challenge-categories/9-veterans-and-seniors.jpeg"),
    ]


# -----------------------------------------------------------------------------
# --- CHALLENGE PARTICIPATION CHOICES
# -----------------------------------------------------------------------------
PARTICIPATION_REMOVE_MODE = enum(
    REMOVE_APPLICATION="0",
    REJECT_APPLICATION="1",
    REJECT_SELFREFLECTION="2",
    ACKNOWLEDGE="4",
    )

PARTICIPATION_STATUS = enum(
    WAITING_FOR_CONFIRMATION="0",
    CONFIRMATION_DENIED="1",
    CONFIRMED="2",
    CANCELLED_BY_ADMIN="4",
    CANCELLED_BY_USER="8",
    WAITING_FOR_SELFREFLECTION="16",
    WAITING_FOR_ACKNOWLEDGEMENT="32",
    ACKNOWLEDGED="64",
    )
participation_status_choices = [
    (PARTICIPATION_STATUS.WAITING_FOR_CONFIRMATION,
        _("Waiting for Confirmation")),
    (PARTICIPATION_STATUS.CONFIRMATION_DENIED,
        _("You were not accepted to this Challenge")),
    (PARTICIPATION_STATUS.CONFIRMED,
        _("Signed up")),
    (PARTICIPATION_STATUS.CANCELLED_BY_ADMIN,
        _("The Organizer removed you from this Challenge")),
    (PARTICIPATION_STATUS.CANCELLED_BY_USER,
        _("You withdrew your Participation to this Challenge")),
    (PARTICIPATION_STATUS.WAITING_FOR_SELFREFLECTION,
        _("Please, write your Experience Report")),
    (PARTICIPATION_STATUS.WAITING_FOR_ACKNOWLEDGEMENT,
        _("Waiting for Acknowledgment")),
    (PARTICIPATION_STATUS.ACKNOWLEDGED,
        _("Report acknowledged")),
    ]


# -----------------------------------------------------------------------------
# --- RECURRENCE CHOICES
# -----------------------------------------------------------------------------
RECURRENCE = enum(
    DATELESS="0",
    ONCE="1",
)
recurrence_choices = [
    (RECURRENCE.DATELESS,   _("Dateless")),
    (RECURRENCE.ONCE,       _("Once")),
    ]

MONTH = enum(
    NONE="",
    JANUARY="1",
    FEBRUARY="2",
    MARCH="3",
    APRIL="4",
    MAY="5",
    JUNE="6",
    JULY="7",
    AUGUST="8",
    SEPTEMBER="9",
    OCTOBER="10",
    NOVEMBER="11",
    DECEMBER="12",
)
month_choices = [
    (MONTH.NONE,            _("----------")),
    (MONTH.JANUARY,         _("January")),
    (MONTH.FEBRUARY,        _("February")),
    (MONTH.MARCH,           _("March")),
    (MONTH.APRIL,           _("April")),
    (MONTH.MAY,             _("May")),
    (MONTH.JUNE,            _("June")),
    (MONTH.JULY,            _("July")),
    (MONTH.AUGUST,          _("August")),
    (MONTH.SEPTEMBER,       _("September")),
    (MONTH.OCTOBER,         _("October")),
    (MONTH.NOVEMBER,        _("November")),
    (MONTH.DECEMBER,        _("December")),
    ]

DAY_OF_WEEK = enum(
    NONE="",
    SUNDAY="0",
    MONDAY="1",
    TUESDAY="2",
    WEDNESDAY="3",
    THURSDAY="4",
    FRIDAY="5",
    SATURDAY="6",
    )
day_of_week_choices = [
    (DAY_OF_WEEK.NONE,          _("----------")),
    (DAY_OF_WEEK.SUNDAY,        _("Sunday")),
    (DAY_OF_WEEK.MONDAY,        _("Monday")),
    (DAY_OF_WEEK.TUESDAY,       _("Tuesday")),
    (DAY_OF_WEEK.WEDNESDAY,     _("Wednesday")),
    (DAY_OF_WEEK.THURSDAY,      _("Thursday")),
    (DAY_OF_WEEK.FRIDAY,        _("Friday")),
    (DAY_OF_WEEK.SATURDAY,      _("Saturday")),
    ]

day_of_month_choices = [(str(day), str(day)) for day in range(0, 32)]
day_of_month_choices[0] = ("", _("----------"))
day_of_month_choices.append(("32", _("Last Day of Month")))
