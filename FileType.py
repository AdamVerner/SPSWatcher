from hashlib import sha256
import os
import logging


class PDF(object):

    def __init__(self, name: str, data: bytes, path: str):
        self.name = name
        self.data = data
        self.path = path

        self.pdf_name = name + '.pdf'

        self.save_path = os.path.dirname(self.path) + '/'
        self.save_path += os.path.dirname(self.name) + '/'
        self.save_path += self.get_hex() + '.pdf'

    def get_hex(self):
        s = sha256()
        s.update(self.data)
        return s.hexdigest()

    def save(self):

        logging.info('saving self to %s', self.save_path)

        if not os.path.exists(os.path.dirname(self.save_path)):
            os.mkdir(os.path.dirname(self.save_path))

        with open(self.save_path, 'wb') as wfile:
            wfile.write(self.data)

    def is_new(self) -> bool:
        return not os.path.exists(self.save_path)


def main():
    logging.basicConfig(level=logging.DEBUG)
    p = PDF('testfile', b'BULLSHIT PDF', './temp')

    print(bool(p))

    print(p.is_new())
    p.save()
    print(p.is_new())


if __name__ == '__main__':
    main()
