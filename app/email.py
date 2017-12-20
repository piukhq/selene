import smtplib
import settings

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64


def send_email(agent, partner_name, content, attachments=''):
    to_email = settings.EMAIL_TARGETS
    server_name = settings.EMAIL_HOST
    username = settings.EMAIL_USERNAME
    password = settings.EMAIL_PASSWORD
    port = settings.EMAIL_PORT

    subject = '{} MID files for on-boarding with {}'.format(agent.title(), partner_name)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(attachments, 'rb').read())
    encode_base64(part)

    # Create the message
    msg = MIMEMultipart(content)
    msg['To'] = ", ".join(to_email)
    msg['From'] = username
    msg['Subject'] = subject

    filename = attachments.split('/')[-1]

    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
    msg.attach(part)

    server = smtplib.SMTP(host=server_name, port=port)
    try:
        server.set_debuglevel(True)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection

        server.login(username, password)
        server.sendmail(username, to_email, msg.as_string())
    finally:
        server.quit()
