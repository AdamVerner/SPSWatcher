from datetime import datetime, timedelta
import urllib3
import os
import logging
from typing import Union
from time import sleep

from FileType import PDF


class SPSCrawler(object):

    save_folder = './sups/'
    look_forward = 3

    sps_url = 'https://is.sps-prosek.cz/suplovani/prosek/'

    def __init__(self):

        self.l = logging.getLogger(__name__)

        self.http = urllib3.PoolManager()

        self.l.info('current day is %s', datetime.now().isoformat())
        self.l.info('saving to folder : %s', os.path.abspath(self.save_folder))
        self.l.info('lookforward set to %d days', self.look_forward)

    def _worker(self):
        look = [(datetime.now() + timedelta(days=x)).strftime('%d%m%Y.pdf') for x in range(self.look_forward)]

        for f in look:
            self.l.debug('working with : %s', f)
            p = self.get_pdf(f)
            if p:
                if p.is_new():
                    self.report_new_file(p)
                    p.save()

    def get_pdf(self, name: str) -> Union[bool, PDF]:

        url = self.sps_url + name

        self.l.debug('trying to download file: %s', url)

        r = self.http.request('GET', url)

        self.l.info('page status = %d', r.status)

        if r.status != 200:
            return False
        pdf = PDF(name, r.data, self.save_folder)
        self.l.debug('file found with hex: %s', pdf.get_hex())
        return pdf

    def report_new_file(self, p: PDF):
        print('*' * 50)
        print('NEW FILE FOUND:', p.name, p.get_hex())
        print('*' * 50)


def main():
    logging.basicConfig(level=logging.DEBUG)
    sc = SPSCrawler()
    sc._worker()


if __name__ == '__main__':
    main()
