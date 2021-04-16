import sqlite3
import locker

create_table_ratings_sqlite = '''
                                CREATE TABLE IF NOT EXISTS RATINGS (
                                userID INTEGER,
                                isbn VARCHAR(20),
                                bookRating INTEGER NOT NULL,
                                email VARCHAR(40),
                                PRIMARY KEY (userID, isbn),
                                FOREIGN KEY (isbn) REFERENCES BOOK (isbn),
                                FOREIGN KEY (userID) REFERENCES PERSON (ID),
                                FOREIGN KEY (email) REFERENCES PERSON (email)
                                );'''
create_table_locker_sqlite = '''CREATE TABLE IF NOT EXISTS LOCKER (
                                ID INTEGER PRIMARY KEY
                                );'''
create_table_drawer_sqlite = '''CREATE TABLE IF NOT EXISTS DRAWER (
                                ID INTEGER PRIMARY KEY,
                                ID_LOCKER INTEGER,
                                current_capacity UNSIGNED CHECK ( current_capacity >= 0 ),
                                max_capacity INTEGER,
                                FOREIGN KEY (ID_LOCKER) REFERENCES LOCKER (ID)
                                );'''
create_table_book_sqlite = '''  CREATE TABLE IF NOT EXISTS BOOK (
                                ID INTEGER UNIQUE,
                                ID_DRAWER INTEGER,
                                title VARCHAR(160) NOT NULL,
                                author VARCHAR(160) NOT NULL,
                                isbn VARCHAR(20),
                                original_owner_ID INTEGER NOT NULL,
                                current_owner_ID INTEGER,
                                date_of_loan DATE,
                                date_of_reserve DATE,
                                PRIMARY KEY (isbn, original_owner_ID),
                                FOREIGN KEY (ID_DRAWER) REFERENCES DRAWER (ID),
                                FOREIGN KEY (original_owner_ID) REFERENCES PERSON (ID),
                                FOREIGN KEY (current_owner_ID) REFERENCES PERSON (ID)
                                );'''
create_table_person_sqlite = '''CREATE TABLE IF NOT EXISTS PERSON (
                                ID INTEGER PRIMARY KEY,
                                name VARCHAR(40) NOT NULL,
                                email VARCHAR(40)
                                );'''

config_drawer_sqlite = '''  INSERT INTO DRAWER
                            SELECT 0, 1, 5, 5
                            WHERE NOT EXISTS (SELECT * FROM DRAWER)'''

get_drawer_id_free_sqlite = '''    SELECT ID FROM DRAWER
                            WHERE current_capacity > 0
                            '''

get_person_sqlite = '''SELECT * FROM PERSON WHERE ID = ?;'''

get_book_sqlite = '''SELECT * FROM BOOK WHERE isbn = ?;'''

get_book_from_title_sqlite = '''SELECT * FROM BOOK WHERE title LIKE ?;'''

reduce_current_capacity_sqlite = '''UPDATE DRAWER SET current_capacity = (current_capacity - 1) WHERE ID = ?;'''
add_book_sqlite = '''   INSERT INTO BOOK (ID, ID_DRAWER, title, author, isbn, original_owner_ID)
                        VALUES ((SELECT IFNULL(MAX(ID), 0) + 1 FROM BOOK) , ?, ?, ?,
                        ?, ?);'''

take_id_book_to_reserve_sqlite = '''SELECT ID FROM BOOK
                                    WHERE title LIKE ? AND current_owner_ID IS NULL
                                    LIMIT 1;'''
reserve_book_from_previous_id_sqlite = '''  UPDATE BOOK
                                            SET current_owner_ID = ?, date_of_reserve = date('now')
                                            WHERE ID =  ?'''

add_client_sqlite = '''INSERT INTO PERSON VALUES (?, ?, ?);'''

get_reserved_books_sqlite = ''' SELECT ID_DRAWER, title, author, isbn, ID
                                FROM BOOK
                                WHERE current_owner_ID = ? AND date_of_reserve <= date('now')
                                AND date_of_loan IS NULL;'''

set_book_taken_sqlite = '''UPDATE BOOK SET date_of_loan = date('now') WHERE ID = ?;'''

add_rating_sqlite = '''INSERT INTO RATINGS VALUES (?, ?, ?, ?);'''

get_books_to_return_sqlite = '''SELECT ID, title, isbn FROM BOOK WHERE current_owner_ID = ?;'''

set_books_to_return_sqlite = '''UPDATE BOOK
                                SET current_owner_ID = NULL, date_of_loan = NULL, date_of_reserve = NULL
                                WHERE ID = ?'''

get_id_drawer_from_book_sqlite = '''SELECT ID_DRAWER FROM BOOK WHERE ID = ?'''

get_isbn_from_book_id_sqlite = '''SELECT isbn FROM BOOK WHERE ID = ?'''

get_email_from_user_id_sqlite = '''SELECT email FROM PERSON WHERE ID = ?'''

update_rating_sqlite = '''update RATINGS set bookRating=? where (userID=? and isbn=?)'''


class SqliteLocker(locker.Locker):
    def reserve_book(self, client_id, book_id) -> bool:
        pass

    def __init__(self, filename):
        super().__init__(filename)
        self.connection = sqlite3.connect(self.filename, check_same_thread=False)
        self.cursor = self.connection.cursor()

        self.cursor.execute(create_table_locker_sqlite)
        self.cursor.execute(create_table_drawer_sqlite)
        self.cursor.execute(create_table_book_sqlite)
        self.cursor.execute(create_table_person_sqlite)
        self.cursor.execute(create_table_ratings_sqlite)
        self.connection.commit()
        self.cursor.execute(config_drawer_sqlite)
        self.connection.commit()

    def reserve_book_from_title(self, client_id, title) -> bool:
        try:
            if len(self.get_client(client_id)) == 0:
                return False
            self.cursor.execute(take_id_book_to_reserve_sqlite, ("%" + title + "%",))
            rows = self.cursor.fetchone()
            if rows:
                book_id = rows[0]
                self.cursor.execute(reserve_book_from_previous_id_sqlite, (client_id, book_id))
                self.connection.commit()
                return True
            else:
                return False
        except sqlite3.Error:
            return False

    def set_book_taken(self, book_id) -> bool:
        try:
            self.cursor.execute(set_book_taken_sqlite, (book_id,))
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def add_client(self, client_id, name, email) -> bool:
        params = (client_id, name, email)
        try:
            self.cursor.execute(add_client_sqlite, params)
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def add_book(self, book, owner_id):
        self.cursor.execute(get_drawer_id_free_sqlite)
        rows = self.cursor.fetchall()
        if not rows:
            return None
        else:
            id_drawer = rows[0][0]
        params = (id_drawer, book.title, book.authors, book.isbn, owner_id)
        self.cursor.execute(reduce_current_capacity_sqlite, (id_drawer,))
        self.cursor.execute(add_book_sqlite, params)
        self.connection.commit()
        return id_drawer

    def check_book(self, isbn) -> bool:
        self.cursor.execute(get_book_sqlite, (isbn,))
        rows = self.cursor.fetchone()
        if rows:
            return True
        else:
            return False

    def check_book_from_title(self, title) -> bool:
        self.cursor.execute(get_book_from_title_sqlite, ("%" + title + "%",))
        rows = self.cursor.fetchone()
        if rows:
            return True
        else:
            return False

    def check_free_space(self) -> bool:
        self.cursor.execute(get_drawer_id_free_sqlite)
        rows = self.cursor.fetchone()
        if rows:
            return True
        else:
            return False

    def get_reserved_books(self, client_id) -> list:
        self.cursor.execute(get_reserved_books_sqlite, (client_id,))
        rows = self.cursor.fetchall()
        if not rows:
            return []
        else:
            return rows

    def get_client(self, client_id) -> tuple:
        self.cursor.execute(get_person_sqlite, (client_id,))
        rows = self.cursor.fetchone()
        if not rows:
            return ()
        else:
            return rows

    def get_isbn_from_book_id(self, book_id):
        self.cursor.execute(get_isbn_from_book_id_sqlite, (book_id,))
        row = self.cursor.fetchone()
        if not row:
            return ()
        else:
            return row[0]
        pass

    def get_email_from_user_id(self, client_id):
        self.cursor.execute(get_email_from_user_id_sqlite, (client_id,))
        row = self.cursor.fetchone()
        if not row:
            return ()
        else:
            return row[0]
        pass

    def add_rating(self, user_id, book_id, bookRating) -> bool:
        isbn = self.get_isbn_from_book_id(book_id)
        email = self.get_email_from_user_id(user_id)
        params = (user_id, isbn, bookRating, email)
        try:
            self.cursor.execute(add_rating_sqlite, params)
            self.connection.commit()
            return True
        except sqlite3.Error:
            self.cursor.execute(update_rating_sqlite, (bookRating, user_id, isbn))
            self.connection.commit()
            return True

    def get_books_to_return(self, client_id):
        self.cursor.execute(get_books_to_return_sqlite, (client_id,))
        rows = self.cursor.fetchall()
        if not rows:
            return ()
        else:
            return rows

    def set_books_to_return(self, book_id):
        try:
            self.cursor.execute(set_books_to_return_sqlite, (book_id,))
            self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def get_id_drawer_from_book(self, book_id):
        self.cursor.execute(get_id_drawer_from_book_sqlite, (book_id,))
        row = self.cursor.fetchone()
        if not row:
            return ()
        else:
            return row[0]

    def __del__(self):
        self.connection.commit()
        self.connection.close()
