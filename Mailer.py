import smtplib
from FileType import PDF

TO = 'toimen21@gmail.com'
SUBJECT = 'TEST MAIL'
TEXT = 'Here is a message from python.'


def construct_mail(pdf: PDF, recipient: str):
    pass

# Gmail Sign In
import os

print(os.listdir(os.path.abspath(os.path.curdir)))
with open('creds', 'r') as cred:
    gmail_sender = cred.readlines(1)[0].replace('\n', '')
    gmail_passwd = cred.readlines(1)[0].replace('\n', '')

print('singing to server')
server = smtplib.SMTP('smtp.gmail.com', 587)

print('saying ehlo')
# server.ehlo()
server.starttls()

print('logging in')
server.login(gmail_sender, gmail_passwd)

BODY = '\r\n'.join(['To: %s' % TO,
                    'From: %s' % gmail_sender,
                    'Subject: %s' % SUBJECT,
                    '', TEXT])

try:
    server.sendmail(gmail_sender, [TO], BODY)
    print('email sent')
except:
    print('error sending mail')

server.close()
