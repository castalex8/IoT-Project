import socket
import time

import tqdm
import os
import pandas as pd
import sqlite3

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # send 4096 bytes each time step
# the ip address or hostname of the server, the receiver
host = "100.86.245.218"
# the port, let's use 5001
port = 5001


def generate_csv_from_db(db_name: str, books_filename: str, ratings_filename: str):
    conn = sqlite3.connect(db_name, isolation_level=None, detect_types=sqlite3.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM BOOK", conn)
    db_df.to_csv(books_filename, index=False, sep=';')
    db_df = pd.read_sql_query("SELECT * FROM RATINGS", conn)
    db_df.to_csv(ratings_filename, index=False, sep=';')


def send_file(filename: str):
    # get the file size
    filesize = os.path.getsize(filename)

    # create the client socket
    s = socket.socket()

    print(f"\n[Bridge] Connecting to cloud {host}:{port}")
    s.connect((host, port))
    print("[Bridge] Connected!")

    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    time.sleep(0.5)

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                progress.close()
                break
            # we use sendall to assure transmission in busy networks
            s.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    # close the socket
    s.close()


class Sender:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def send_all(self):
        books_filename = f'Book_{self.db_name}.csv'
        ratings_filename = f'Ratings_{self.db_name}.csv'
        generate_csv_from_db(self.db_name, books_filename, ratings_filename)

        send_file(books_filename)
        time.sleep(1)
        send_file(ratings_filename)
