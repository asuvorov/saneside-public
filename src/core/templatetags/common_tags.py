# -*- coding: utf-8
import email
import json
import quopri
import re

from django import template
from django.db.models.query import QuerySet
from django.forms import CheckboxInput
from django.template.base import Variable
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def is_checkbox(item):
    """Docstring."""
    return isinstance(item.field.widget, CheckboxInput)


@register.filter
def highlight(text, query):
    """Docstring."""
    regex = re.compile(smart_unicode(query), re.IGNORECASE | re.UNICODE)
    i = 0
    output = ""
    m = False

    for m in regex.finditer(text):
        output += "".join(
            [text[i:m.start()],
            "<span class='highlighted'>",
            text[m.start():m.end()],
            "</span>"])
        i = m.end()

    if m:
        return mark_safe("".join([output, text[m.end():]]))
    else:
        return mark_safe(text)


@register.filter
def textbreaker(text, action, breaker="<!-- break -->", more_symbols=" ..."):
    """Docstring."""
    if action == "split":
        try:
            pos = text.index(breaker)
        except:
            return mark_safe(text)

        return mark_safe(text[:pos].rstrip())+more_symbols
    else:
        return mark_safe(text.replace(breaker, ""))


@register.filter
def invert(value):
    """Docstring."""
    if value == 1:
        value = 0
    elif value == 0:
        value = 1

    return value


@register.filter
def number_format(number, decimals=0, dec_point=".", thousands_sep=","):
    """Docstring."""
    try:
        number = round(float(number), decimals)
    except ValueError:
        return number

    neg = number < 0
    integer, fractional = str(abs(number)).split(".")
    m = len(integer) % 3

    if m:
        parts = [integer[:m]]
    else:
        parts = []

    parts.extend([integer[m+t:m+t+3] for t in xrange(0, len(integer[m:]), 3)])

    if decimals:
        return "%s%s%s%s" % (
            neg and "-" or "",
            thousands_sep.join(parts),
            dec_point,
            fractional.ljust(decimals, "0")[:decimals]
        )
    else:
        return "%s%s" % (neg and "-" or "", thousands_sep.join(parts))


@register.filter
def parse_str(str, val):
    """Docstring."""
    return str % val


@register.filter
def placeholder(value, token):
    """Docstring."""
    value.field.widget.attrs["placeholder"] = token

    return value


@register.filter
def htmlattributes(value, arg):
    """Docstring."""
    attrs = value.field.widget.attrs
    data = arg
    kvs = data.split(",")

    for string in kvs:
        kv = string.split(":")
        attrs[kv[0]] = kv[1]

    rendered = str(value)

    return rendered


@register.filter
def encode_mime(text, text_only=False):
    """Docstring."""
    text_body = ""

    text = quopri.decodestring(text)

    msg = email.message_from_string(text)

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue

        if part.get_content_subtype() == "text":
            text_body = part.get_payload(decode=True)

        if part.get_content_subtype() == "html":
            return part.get_payload(decode=True)

        if text_only and part.get_content_maintype() == "text":
            return part.get_payload(decode=True)

    return text_body


@register.filter
def http(text):
    """Docstring."""
    if text.startswith("http://"):
        return text
    else:
        return "http://%s" % text


@register.filter
def limit(val, length):
    """Docstring."""
    if len(val) > length:
        return val[:length] + "..."
    else:
        return val


def render_get_params(context):
    """Docstring."""
    req = Variable("request").resolve(context)
    data = req.GET.copy().urlencode()

    if data:
        return "?%s" % data
    else:
        return ""

register.simple_tag(render_get_params, takes_context=True)


@register.filter
def percent(value):
    """Docstring."""
    try:
        p = float(value) * 100

        return "%.2f %%" % p
    except ValueError:
        return "-"


@register.filter
def dict_get(d, key):
    """Docstring."""
    try:
        return d.get(key, "")
    except AttributeError:
        return ""


@register.filter
def round_up(value):
    """Docstring."""
    try:
        value = float(value)
        digits = len(str(value).split(".")[0]) - 1

        return round(value, -digits)
    except TypeError:
        return None


@register.filter
def divide_by(value, divide):
    """Docstring."""
    try:
        if divide:
            return value/divide
        else:
            return value
    except TypeError:
        return None


@register.filter
def multiply_by(value, multiply):
    """Docstring."""
    try:
        return value * multiply
    except TypeError:
        return None


@register.filter
def sub(value, sub):
    """Docstring."""
    try:
        return value - sub
    except TypeError:
        return None


@register.filter
def str_add(value, add):
    """Docstring."""
    return str(value) + str(add)


@register.filter
def get(instance, attr, default=None):
    """Docstring."""
    if type(instance) == dict:
        x = instance.get(attr, default)
    elif type(instance) == list or isinstance(instance, QuerySet):
        try:
            x = instance[attr]
        except IndexError:
            x = None
    else:
        x = getattr(instance, attr, default)

    if callable(x):
        return x()
    else:
        return x


@register.filter(name="max")
def list_max(l, key=None):
    """Docstring."""
    if not l:
        return None

    if key:
        x = max(l, key=lambda i: get(i, key))

        if callable(x):
            return x()
        else:
            return x
    else:
        return max(l)


@register.filter(name="min")
def list_min(l, key=None):
    """Docstring."""
    if not l:
        return None

    if key:
        x = min(l, key=lambda i: get(i, key))

        if callable(x):
            return x()
        else:
            return x
    else:
        return min(l)


@register.filter("truncate_chars")
def truncate_chars(value, max_length):
    """Docstring."""
    if len(value) <= max_length:
        return value

    truncd_val = value[:max_length]

    if value[max_length] != " ":
        rightmost_space = truncd_val.rfind(" ")

        if rightmost_space != -1:
            truncd_val = truncd_val[:rightmost_space]

    return truncd_val + "..."


@register.filter
def is_ie(request):
    """Docstring."""
    if request:
        if "MSIE" in request.META["HTTP_USER_AGENT"]:
            return True

    return False


class RawNode(template.Node):

    """Docstring."""

    def __init__(self, bits):
        """Docstring."""
        self.bits = bits

    def render(self, context):
        """Docstring."""
        return self.bits


@register.tag
def raw(parser, token):
    """Docstring."""
    params = " ".join(token.split_contents()[1:])

    return RawNode(params)


@register.filter
def to_json(data):
    """Docstring."""
    return json.dumps(data)
