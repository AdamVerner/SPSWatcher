"""
TODO logging
TODO message body
TODO hide psswd from ram, or at least somehow encrypt it
"""

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formatdate
from email.utils import make_msgid
from email.message import EmailMessage
from typing import List
import mimetypes
import logging

from FileType import PDF
import auth


class Mailer(object):

    def __init__(self, logger: logging.getLogger):
        self.log = logger

    def send_mail(self, pdf: PDF=None):
        msg = EmailMessage()
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'New file on sps-prosek.cz'
        msg['Reply-To'] = auth.Smtp.reply_to

        # set the plain text body
        msg.set_content('This is a plain text body.')

        # now create a Content-ID for the image
        # image_cid looks like <long.random.number@xyz.com>
        # to use it as the img src, we don't need `<` or `>`
        # so we use [1:-1] to strip them off
        image_cid = make_msgid()[1:-1]
        # if `domain` argument isn't provided, it will
        # use your computer's name

        # set an alternative html body

        with open('email-template.html', 'r') as email_template:
            email_message = email_template.read()

        email_message = email_message.replace('{version_number}', str(pdf.get_version()))
        email_message = email_message.replace('{day_name}',      pdf.get_day_name())
        email_message = email_message.replace('{image_cid}',     image_cid)
        email_message = email_message.replace('{author_name}',   pdf.get_author())

        msg.add_alternative(email_message, subtype='html')

        # attach it
        msg.get_payload()[1].add_related(pdf.get_as_image(), maintype='image', subtype='png', cid=image_cid)

        # open connection to server and send the mail
        self.log.debug('opening connection to SMTP server and sending emails')
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(auth.Smtp.login, auth.Smtp.password)
            smtp.sendmail(auth.Smtp.sender, self.get_recipients(), msg.as_string())

        self.log.info('emails successfully sent')

    def get_recipients(self)-> List[str]:
        recipients = list()
        with open('recipients', 'r') as rcps:
            for r in rcps.readlines():
                r = r.replace('\n', '')
                self.log.info('adding %s to recipients', repr(r))
                recipients.append(r)

        return recipients
