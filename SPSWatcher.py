#!/usr/bin/env python3

from datetime import datetime, timedelta
import urllib3
import os
import logging
from typing import Union
from time import sleep

from FileType import PDF
from Mailer import Mailer

from datetime import datetime

class SPSCrawler(object):

    save_folder = './sups/'
    look_forward = 3

    sps_url = 'https://is.sps-prosek.cz/suplovani/prosek/'

    def __init__(self):

        self.log = logging.getLogger(__name__)

        self.http = urllib3.PoolManager()

        if not os.path.exists(os.path.dirname(self.save_folder)):
            os.mkdir(os.path.dirname(self.save_folder))

        self.log.info('current day is %s', datetime.now().isoformat())
        self.log.info('saving to folder : %s', os.path.abspath(self.save_folder))
        self.log.info('look_forward set to %d days', self.look_forward)

        self.mailer = Mailer('vernead15@sps-prosek.cz', self.log)

    def _worker(self):
        look = [(datetime.now() + timedelta(days=x)).strftime('%d%m%Y.pdf') for x in range(self.look_forward)]

        new = []

        for f in look:
            self.log.debug('working with : %s', f)
            p = self.get_pdf(f)
            if p:
                if p.is_new():
                    self.log.debug('file is NEW')
                    new.append(p)
                    p.save()

        if new:
            self.mailer.send_mail(new)

    def get_pdf(self, name: str) -> Union[bool, PDF]:

        url = self.sps_url + name

        self.log.debug('trying to download file: %s', url)

        r = self.http.request('GET', url)

        self.log.info('page status = %d', r.status)

        if r.status != 200:
            return False
        pdf = PDF(name.replace('.pdf', ''), r.data, self.save_folder, self.log)
        self.log.debug('file found with hex: %s', pdf.get_hex())
        return pdf


def main():
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    sc = SPSCrawler()
    while True:
        try:
            sc._worker()
        except Exception as ex:
            print(ex)
        finally:
            # minutes to quarter
            mtq = 15 - (datetime.now().minute % 15)
            sc.log.info('going to sleep for %d minutes', mtq)
            sleep(mtq * 60)


if __name__ == '__main__':
    main()
