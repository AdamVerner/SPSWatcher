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
from hashlib import sha256

from FileType import PDF


class Mailer(object):

    recipients = ['toimen21@gmail.com']
    smtp_login = None
    smtp_psswd = None

    def __init__(self, sender: str):
        self.log = logging.getLogger(__name__)
        self.sender = sender

        with open('recipients', 'r') as rcps:
            for r in rcps.readlines():
                r = r.replace('\n', '')
                self.log.info('adding %s to recipients', repr(r))
                self.recipients.append(r)

        with open('creds', 'r') as cred:
            creds = cred.readlines()
            if self.smtp_login is None:
                self.smtp_login = creds[0].replace('\n', '')
                self.log.info('smtp_login = %s', self.smtp_login)

            if self.smtp_psswd is None:
                self.smtp_psswd = creds[1].replace('\n', '')

                # do not log plaintext password
                s = sha256()
                s.update(self.smtp_psswd)
                self.log.info('sha256(smtp_psswd) = "%s"', s.hexdigest())

        if self.sender != self.smtp_login:
            self.log.warning('sender is different from authorization email')

    def send_mail(self, pdfs: List[PDF]=None):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.recipients)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = 'New file on sps-prosek.cz'

        msg.attach(MIMEText('new file found, what else do you need to know?'))

        # attach all pdfs to mail body
        for p in pdfs or []:
            part = MIMEApplication(p.data, name=p.name)

            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(p.name)
            msg.attach(part)

        # open connection to server and send the mail
        self.log.debug('opening connection to SMTP server and sending emails')
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(self.smtp_login, self.smtp_psswd)
            smtp.sendmail(self.sender, self.recipients, msg.as_string())

        self.log.info('emails sucessfully sent')
