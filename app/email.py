import smtplib
import settings

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64


def send_email(agent, partner_name, content, attachment=None):
    to_email = settings.EMAIL_TARGETS
    server_name = settings.EMAIL_HOST
    username = settings.EMAIL_USERNAME
    password = settings.EMAIL_PASSWORD
    port = settings.EMAIL_PORT

    subject = '{} MID files for on-boarding with {}'.format(agent.title(), partner_name)

    # Create the message
    msg = MIMEMultipart()
    msg['To'] = to_email.get(agent)
    msg['From'] = username
    msg['Subject'] = subject

    body = MIMEText(content, 'html')
    msg.attach(body)

    if attachment:
        part = MIMEBase('application', "octet-stream")
        with open(attachment, 'rb') as file:
            part.set_payload(file.read())

        encode_base64(part)
        filename = attachment.split('/')[-1]
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
        server.sendmail(username, to_email.get(agent), msg.as_string())
    finally:
        server.quit()
