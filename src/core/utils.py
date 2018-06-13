import cStringIO as StringIO
import inspect
import json
import os
import re
import uuid

from HTMLParser import HTMLParser
from urlparse import (
    parse_qs,
    urlparse,
    )

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponse
from django.template.loader import render_to_string

import MySQLdb
import requests

from ipware.ip import (
    get_ip,
    get_real_ip,
    )

from BeautifulSoup import BeautifulSoup
from cgi import escape
from termcolor import colored
from xhtml2pdf import pisa


URL_VALIDATOR = URLValidator()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~
# ~~~ HELPERS
# ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MLStripper(HTMLParser):
    """Docstring."""

    def __init__(self):
        """Docstring."""
        self.reset()
        self.fed = []

    def handle_data(self, d):
        """Docstring."""
        self.fed.append(d)

    def get_data(self):
        """Docstring."""
        return "".join(self.fed)


def escape_html(html):
    """Escape HTML Code."""
    try:
        s = MLStripper()
        s.feed(html)

        return s.get_data()

    except:
        pass

    return ""


def escape_string(string):
    """Escape String for MySQL."""
    return MySQLdb.escape_string(
        get_purified_str(
            re.sub("[^a-zA-Z0-9 \n\.,]", " ", string)
            ))
    # return MySQLdb.escape_string(unicode(string, "utf-8"))


def get_client_ip(request):
    """Get Client IP Address."""
    # -------------------------------------------------------------------------
    # --- If Web Server is publicly accessible on the Internet, get the `real`
    #     IP Address of the Client.
    #
    #    `Real IP` = an IP Address, that is route-able on the Internet.
    ip = get_real_ip(request)

    if ip:
        # ---------------------------------------------------------------------
        # --- We have a real, public IP Address for User
        return ip

    # -------------------------------------------------------------------------
    # --- If Web Server is NOT publicly accessible on the Internet, get the
    #     `best matched` IP Address of the Client.
    #
    #     `Best Matched IP` = The first matched Public IP if found,
    #                         else the first matched non-public IP.
    ip = get_ip(request)

    return ip


def make_json_cond(name, value):
    """Docstring."""
    cond = json.dumps({
        name:   value
    })[1:-1]  # remove "{" and "}"

    return " " + cond  # avoid '\"'


def get_youtube_video_id(yt_url):
    """Return "video_id" from YouTube Video URL.

    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    Source: http://stackoverflow.com/a/7936523
    """
    query = urlparse(yt_url)

    if query.hostname == "youtu.be":
        return query.path[1:]

    if query.hostname in ("www.youtube.com", "youtube.com"):
        if query.path == "/watch":
            p = parse_qs(query.query)

            return p["v"][0]

        if query.path[:7] == "/embed/":
            return query.path.split("/")[2]

        if query.path[:3] == "/v/":
            return query.path.split("/")[2]

    return None


def validate_url(url, try_harder=True):
    """Validate URL."""
    try:
        URL_VALIDATOR(url)
    except ValidationError:
        if try_harder:
            url = "http://" + url
            # Recursive run to check correctness of modified url.
            return validate_url(url, try_harder=False)
        else:
            return False

    return url


def get_website_title(url):
    """Get Website Title."""
    try:
        r = requests.get(url)
    except (
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema):
        try:
            r = requests.get("http://" + url)
        except:
            return None
    except:
        return None

    if r.status_code != 200:
        return None

    try:
        soup = BeautifulSoup(r.text)
        title = soup.title.string.strip()
    except:
        return None

    return title


def get_unique_hashname():
    """Get unique Hash Name."""
    return "%s" % uuid.uuid4()


def get_unique_filename(filename):
    """Get unique File Name."""
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)

    return filename


def get_purified_str(string=""):
    """Purify String."""
    # -------------------------------------------------------------------------
    # --- Remove special Characters

    # --- TODO: Had to comment out this Line, because it removes mutated
    #           Unicode Characters.
    #           Figure out the Way to remove special Characters, but keep
    #           printable Unicode Characters.
    # string = re.sub("[^a-zA-Z0-9 \n\.,]", " ", string)

    # -------------------------------------------------------------------------
    # --- Remove duplicated and trailing Spaces
    # -------------------------------------------------------------------------
    try:
        string = re.sub(" +", " ", string.strip())
    except:
        pass

    return string


# -----------------------------------------------------------------------------
# --- RENDER PDF
# -----------------------------------------------------------------------------
def link_callback(uri, rel):
    """Convert HTML URIs to absolute system Paths.

    So `xhtml2pdf` can access those Resources.
    """
    # -------------------------------------------------------------------------
    # --- Use short Variable Names
    # -------------------------------------------------------------------------
    try:
        sUrl = settings.STATIC_URL    # /static/
        sRoot = settings.STATIC_ROOT  # /home/userX/project_static/
        mUrl = settings.MEDIA_URL     # /static/media/
        mRoot = settings.MEDIA_ROOT   # /home/userX/project_static/media/

        print colored("[---  DUMP   ---] URI  : %s" % uri, "yellow")
        print colored("[---  DUMP   ---] REL  : %s" % rel, "yellow")

        # -------------------------------------------------------------------------
        # --- Convert URIs to absolute system Paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        print colored("[---  DUMP   ---] PATH : %s" % path, "yellow")

        # -------------------------------------------------------------------------
        # --- Make sure, that File exists
        if not os.path.isfile(path):
            raise Exception(
                "media URI must start with %s or %s" % (sUrl, mUrl)
            )

        return path

    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")


def render_to_pdf(template_src, context_dict):
    """Render HTML Template to PDF."""
    # -------------------------------------------------------------------------
    # --- Prepare Data
    # -------------------------------------------------------------------------
    # template = get_template(template_src)
    # html = template.render(context_dict)
    html = render_to_string(template_src, context_dict)

    # -------------------------------------------------------------------------
    # --- Convert to PDF
    # -------------------------------------------------------------------------
    # result = StringIO.StringIO()
    # pdf = pisa.pisaDocument(
    #     StringIO.StringIO(
    #         html.encode("UTF-8")),
    #     dest=result,
    #     link_callback=link_callback
    #     )
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(
        StringIO.StringIO(
            html.encode("UTF-8")),
        dest=result,
        link_callback=link_callback
        )

    if not pdf.err:
        return HttpResponse(
            result.getvalue(),
            content_type="application/pdf")

    return HttpResponse("We had some errors<pre>%s</pre>" % escape(html))
