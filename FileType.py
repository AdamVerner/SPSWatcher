from hashlib import sha256
import os
import logging
import PDFProcessor
import datetime
import re


class PDF(object):

    def __init__(self, name: str, data: bytes, path: str, logger):
        self.name = name
        self.data = data
        self.path = os.path.dirname(path)
        self.log = logger

        self.save_path = self.path + '/'
        self.save_path += self.name + '/'
        self.save_path += self.get_hex() + '.pdf'

    def get_hex(self):
        s = sha256()
        s.update(self.data)
        return s.hexdigest()

    def save(self):

        self.log.info('saving self to %s', self.save_path)

        if not os.path.exists(os.path.dirname(self.save_path)):
            os.mkdir(os.path.dirname(self.save_path))

        with open(self.save_path, 'wb') as wfile:
            wfile.write(self.data)

    def is_new(self) -> bool:
        return not os.path.exists(self.save_path)

    def get_version(self)-> int:
        try:
            files_in_dir = set(os.listdir(os.path.dirname(self.save_path)))
            files_in_dir.add(self.get_hex() + '.pdf')
        except FileNotFoundError:
            return 1
        return len(files_in_dir)

    def get_as_image(self):
        pages = PDFProcessor.convert_pdf(self.data, 250)
        unified = PDFProcessor.unify_pages(pages)
        return unified

    def get_day_name(self, lang='CZ')->str:
        """
        TODO change to use locale settings, not translation table
        :param lang: {CZ|EN}
        :return: name of the day
        """

        translation = {
            'EN': [
                'Sunday',
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday'
                ],
            'CZ': [
                'Pondělí',
                'Úterý',
                'Středa',
                'Čtvrtek',
                'Pátek',
                'Sobota',
                'Neděle'
                ]
            }

        # generate datetime Object from filename (foramt e.g.: 09082018)
        dtobj = datetime.datetime.strptime(self.name, '%d%m%Y')

        # strftimes %w returns number of weekday starting from sunday
        name = translation[lang][int(dtobj.strftime('%w'))]
        return name

    def get_author(self)->str:
        try:
            re_author = re.compile('/Author\((.*)\)>>endobj')
            author = re_author.findall("".join(map(chr, self.data)))[0]
        except IndexError:
            return 'Unknown'

        return author






def main():
    logging.basicConfig(level=logging.DEBUG)
    p = PDF('testfile', b'BULLSHIT PDF', './temp')


if __name__ == '__main__':
    main()
