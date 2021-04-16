from abc import abstractmethod


class Locker:
    def __init__(self, filename):
        self.filename = filename
        # part of the implementation in subclasses

    # These operations have to be implemented in subclasses.
    @abstractmethod
    def add_client(self, client_id, name, email) -> bool:
        pass

    @abstractmethod
    def add_book(self, book, owner_id) -> int:
        pass

    @abstractmethod
    def check_book(self, book_id) -> bool:
        pass

    @abstractmethod
    def reserve_book(self, client_id, book_id) -> bool:
        pass

    @abstractmethod
    def check_free_space(self) -> bool:
        pass

    @abstractmethod
    def get_client(self, client_id) -> tuple:
        pass

    @abstractmethod
    def set_book_taken(self, client_id) -> tuple:
        pass

    @abstractmethod
    def get_reserved_books(self, client_id) -> tuple:
        pass

    @abstractmethod
    def __del__(self):
        pass
