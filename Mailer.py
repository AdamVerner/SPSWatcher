# smtplib module send mail

import smtplib

TO = 'toimen21@gmail.com'
SUBJECT = 'TEST MAIL'
TEXT = 'Here is a message from python.'

# Gmail Sign In
gmail_sender = 'user@localhost'
gmail_passwd = 'Password123'

print('singing to server')
server = smtplib.SMTP('smtp.gmail.com', 587)

print('saying ehlo')
server.ehlo()
server.starttls()
server.ehlo()

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
