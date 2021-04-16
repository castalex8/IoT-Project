import cv2 as cv
import logging
import time
from bridge import Bridge
from microcontroller import Microcontroller
from locker_sqlite import SqliteLocker
from utils import read_code, Book

# set the following variables for the abstract bridge
timeout_value = 20

welcome_string = """
-----------------------------------------------------------------------------------
WELCOME TO BOOK SHARING
Share your books with the community!
scan book's barcode to share it and put your book in the library

I'm ready to scan!
-----------------------------------------------------------------------------------
"""

logging.getLogger('bridge.locker')


class LockerBridge(Bridge):
    def __init__(self, state, region, bridge_id, db_name, video_source):
        super().__init__(state, region, bridge_id)

        self.db_name = db_name
        self.video_source = video_source

        logging.info(f'I am the bridge: {bridge_id} [{state}/{region}/{bridge_id}])')

        self.locker = SqliteLocker(db_name)
        self.microcontroller = Microcontroller()
        logging.debug(f'All locker structure are build ({db_name} OK)')

    def bring_back_book(self, client_code):
        books = self.locker.get_books_to_return(client_code)
        print('The books you can return:\n')
        if not books:
            print('No books to return')
            return 1
        for book in books:
            print(f'ID: {book[0]} - title: {book[1]} - isbn {book[2]}\n')

        print('Do you want to return a book?')
        response = input()
        if response.lower() in ['y', 'ye', 'yes']:
            print('Write id book to return!')
            book_id = 0
            while True:
                try:
                    book_id = int(input())
                    break
                except:
                    print('Retry')
            if type(book_id) is not int or book_id < 0:
                return 2
            self.locker.set_books_to_return(book_id)
            drawer = self.locker.get_id_drawer_from_book(book_id)

            print('Rate your book!')
            print('From 1 to 10!')

            rate = 0
            while True:
                try:
                    rate = int(input())
                    break
                except:
                    print('Retry')

            if rate < 0:
                rate = 0
            elif rate > 10:
                rate = 10

            self.locker.add_rating(client_code, book_id, rate)

            print(f'You can deposit into drawer {drawer}')
            self.microcontroller.send_command(drawer.to_bytes(1, 'big'))
            print('OK')

    def loop(self):
        camera = cv.VideoCapture(self.video_source)
        if not camera.isOpened():
            msg = f'Cannot open camera {self.video_source}'
            logging.critical(msg)
            raise IOError(msg)

        logging.info(f'Start to read from camera {self.video_source}')

        print(welcome_string)

        current_client_code = None
        state = 'qrcode'
        last_time = time.time()
        while True:
            # Capture frame-by-frame
            ret, frame = camera.read()
            # if frame is read correctly ret is True
            if not ret:
                msg = f"Can't receive frame, camera.read() returned {ret}"
                logging.error(msg)
                raise IOError(msg)

            # Operations on the frame come here
            code = read_code(state, frame)

            if state == 'qrcode' and code is not None:
                last_time = time.time()
                current_client_code = code
                logging.info(f'Read the qrcode: {code}')
                # check client information (respect QR code read) and do what client wants
                client_info = self.locker.get_client(current_client_code)
                if not client_info:
                    continue

                msg = f'Client {client_info[0]} {client_info[1]} {client_info[2]}'
                logging.info(msg)
                print('Hi! ' + msg)

                # check if client want to bring back a book and rating it
                self.bring_back_book(current_client_code)

                # check if client want to get books (if client has booked a book in app)
                reserved_books = self.locker.get_reserved_books(current_client_code)
                if reserved_books:
                    msg = f'{len(reserved_books)} books reserved'
                    logging.info(msg)
                    print(msg)
                    for book in reserved_books:
                        print(f'{book[1]} {book[2]} {book[3]} is inside the drawer {book[0]}')
                        print('You can pick it')
                        self.microcontroller.send_command(book[0].to_bytes(1, 'big'))
                        self.locker.set_book_taken(book[4])
                        time.sleep(8)

                print('Now, if you want, scan barcode of the book to share!')

                state = 'barcode'
                continue

            if state == 'barcode' and code is not None:
                time.sleep(1)
                isbn = code
                # check timeout to return in state 'qrcode'
                last_time = time.time()

                logging.info(f'Read the isbn: {isbn}')
                book = Book(isbn)
                print(book)

                id_drawer = self.locker.add_book(book, current_client_code)
                if id_drawer is None:
                    logging.info('Locker full!!')
                    print('Locker full!!')
                else:
                    print(f'Please insert book  at drawer {id_drawer}')
                    # add a book in Locker physically
                    self.microcontroller.send_command(int(id_drawer).to_bytes(1, 'big'))
                    print('OK!')

                # a small break before scanning again
                time.sleep(2)

            if state == 'barcode' and (time.time() - last_time > timeout_value):
                state = 'qrcode'
                logging.info(f'barcode timeout')

            cv.imshow('Barcode reader', frame)
            if cv.waitKey(15) == 27:
                break

        camera.release()
        cv.destroyAllWindows()
        return
