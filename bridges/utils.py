from pyzbar import pyzbar
import json
import requests


def read_code(type_code, frame):
    codes = pyzbar.decode(frame)
    codes_read = []
    for code in codes:
        x, y, w, h = code.rect
        if type_code == 'qrcode' and code.type == 'QRCODE':
            return code.data.decode('utf-8')
        elif type_code == 'barcode' and (code.type == 'EAN13' or code.type == 'EAN14' or code.type == 'ISBN13'
                                         or code.type == 'ISBN14'):
            return code.data.decode('utf-8')
        else:
            return None


class Book:
    def get_info_from_isbn(self, isbn) -> tuple:
        params = {'q': 'isbn:' + str(isbn)}
        r = requests.get('https://www.googleapis.com/books/v1/volumes', params=params)

        if r.status_code == 200:
            r_dict = json.loads(r.text)
            if r_dict['kind'] == 'books#volumes' and r_dict['totalItems'] == 1:
                volume_info_dict = r_dict['items'][0]['volumeInfo']

                self.title, self.authors, self.publishedDate = \
                    volume_info_dict['title'], volume_info_dict['authors'][0], volume_info_dict['publishedDate']

    def __init__(self, isbn):
        self.isbn = isbn
        self.title = 'No title'
        self.authors = 'No authors'
        self.publishedDate = 'No published date'
        self.get_info_from_isbn(isbn)

    def __str__(self):
        description_string = f"""title: {self.title}\nauthors: {self.authors}\npublished date: {self.publishedDate}"""
        return description_string
