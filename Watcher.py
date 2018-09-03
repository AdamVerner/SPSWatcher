from datetime import datetime, timedelta
import urllib3
import os
from hashlib import sha256
import logging
from time import sleep
from threading import Thread

class PDF(object):

    def __init__(self, name: str, data: bytes):
        self.name = name
        self.data = data

        self.pdf_name = name + '.pdf'

    def get_hex(self):
        s = sha256()
        s.update(self.data)
        return s.hexdigest()


class SPSCrawler(object):

    save_folder = './sups/'
    look_forward = 3

    sps_url = 'https://is.sps-prosek.cz/suplovani/prosek/'

    stop_flag = False

    def __init__(self):

        self.l = logging.getLogger(__name__)

        self.http = urllib3.PoolManager()

        self.l.info('current day is %s', datetime.now().isoformat())
        self.l.info('saving to folder : %s', os.path.abspath(self.save_folder))
        self.l.info('lookforward set to %d days', self.look_forward)

    def _worker(self):
        while not self.stop_flag:
            look = [(datetime.now() + timedelta(days=x)).strftime('%d%m%Y.pdf') for x in range(self.look_forward)]

            for f in look:
                self.l.debug('working with : %s', f)
                p = self.get_pdf(f)
                if p[0]:
                    if self.is_new(p[1]):
                        self.report_new_file(p[1])
                        self.save_file(p[1])
            sleep(60)

    @staticmethod
    def list_files(path):
        return os.listdir(path)

    def is_new(self, pdf: PDF) -> bool:
        return not os.path.exists(self.pdf_to_path(pdf))

    def get_pdf(self, name: str) -> (bool, PDF):

        url = self.sps_url + name

        self.l.debug('trying to download file: %s', url)

        r = self.http.request('GET', url)

        self.l.info('page status = %d', r.status)

        if r.status != 200:
            return False, PDF
        pdf = PDF(name, r.data)

        self.l.debug('file found with hex: %s', pdf.get_hex())
        pdf = PDF(name, r.data)
        return True, pdf

    def report_new_file(self, p: PDF):
        print('*' * 50)
        print('NEW FILE FOUND:', p.name, p.get_hex())
        print('*' * 50)

    def pdf_to_path(self, pdf:PDF):
        path = os.path.abspath(self.save_folder)
        path += '/'
        path += pdf.name.strip('.pdf')
        path += '/'
        path += pdf.get_hex()
        path += '.pdf'
        return path

    def save_file(self, p: PDF):
        path = self.pdf_to_path(p)
        logging.info('saving %s to %s', p.get_hex(), path)

        if not os.path.exists(path):
            os.mkdir(os.path.dirname(path))

        with open(path, 'wb') as wfile:
            wfile.write(p.data)


def main():
    logging.basicConfig(level=logging.DEBUG)
    sc = SPSCrawler()
    sc._worker()


if __name__ == '__main__':
    main()
