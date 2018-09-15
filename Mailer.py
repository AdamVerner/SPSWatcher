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
from email.utils import formatdate
from typing import List
import logging

from FileType import PDF
import auth


class Mailer(object):

    def __init__(self, logger: logging.getLogger):
        self.log = logger

    def send_mail(self, pdfs: List[PDF]=None):
        msg = MIMEMultipart()
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'New file on sps-prosek.cz'
        msg['Reply-To'] = auth.Smtp.reply_to

        msg.attach(MIMEText('new file found, what else do you need to know?'))

        # attach all pdfs to mail body
        for p in pdfs or []:
            p_name = p.name
            if p_name[-4:] is not '.pdf':
                p_name = p_name + '.pdf'
            part = MIMEApplication(p.data, name=p_name)

            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(p_name)
            msg.attach(part)

        recipients = []
        with open('recipients', 'r') as rcps:
            for r in rcps.readlines():
                r = r.replace('\n', '')
                self.log.info('adding %s to recipients', repr(r))
                recipients.append(r)

        # open connection to server and send the mail
        self.log.debug('opening connection to SMTP server and sending emails')
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(auth.Smtp.login, auth.Smtp.password)
            smtp.sendmail(auth.Smtp.sender, recipients, msg.as_string())

        self.log.info('emails sucessfully sent')
