import inspect

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import papertrail

from termcolor import colored


# -----------------------------------------------------------------------------
# --- SEND TEMPLATED EMAIL.
# -----------------------------------------------------------------------------
def send_templated_email(
        to,
        template_subj, template_text, template_html=None,
        template_id=None, substitutions={},
        from_email=settings.EMAIL_SENDER, headers={}, cc=[], bcc=[]):
    """Send templated Email.

    This is new Version, which uses SendGrid HTML Template to be sent.
    """
    print colored("***" * 27, "green")
    print colored("*** INSIDE `%s`" % inspect.stack()[0][3], "green")

    try:
        # ---------------------------------------------------------------------
        # Prepare Email to be sent
        subj_content = render_to_string(
            template_subj["name"],
            template_subj["context"],
        )
        subj_content = "".join(subj_content.splitlines())

        text_content = render_to_string(
            template_text["name"],
            template_text["context"],
        )

        mail = EmailMultiAlternatives(
            subject=subj_content,
            body=text_content,
            from_email=from_email,
            to=to,
            cc=cc,
            bcc=bcc,
            headers=headers,
        )

        # ---------------------------------------------------------------------
        # --- 1. Add Template ID
        # --- 2. Replace Substitutions in SendGrid Template
        if template_id:
            mail.template_id = template_id
            mail.substitutions = substitutions

        # ---------------------------------------------------------------------
        # --- Attach Alternative
        if template_html:
            html_content = render_to_string(
                template_html["name"],
                template_html["context"],
            )
            mail.attach_alternative(html_content, "text/html")

        # ---------------------------------------------------------------------
        # --- Send Email
        mail.send()

        return True

    except Exception as e:
        print colored("###" * 27, "white", "on_red")
        print colored("### EXCEPTION @ `{module}`: {msg}".format(
            module=inspect.stack()[0][3],
            msg=str(e),
            ), "white", "on_red")

        # ---------------------------------------------------------------------
        # --- Save the Log
        papertrail.log(
            event_type="exception-send-templated-email",
            message="Exception: Send templated Email",
            data={
                "to":           to,
                "from":         from_email,
                "message":      str(e),
            },
            # timestamp=timezone.now(),
            targets={},
            )

    return False
