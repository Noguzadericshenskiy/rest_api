import logging
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple

DATA = [
    {'id': 0, 'title': 'A Byte of Python', 'author': 1},
    {'id': 1, 'title': 'Moby-Dick; or, The Whale', 'author': 2},
    {'id': 3, 'title': 'War and Peace', 'author': 3},
]

AUTHORS = [
    {"id": 1, "name_author": "Swaroop C. H.", "fill_name": "SCW"},
    {"id": 2, "name_author": "Herman Melville", "fill_name": "HM"},
    {"id": 3, "name_author": "Leo Tolstoy", "fill_name": "LT"},
]

BOOKS_TABLE_NAME = 'books'
AUTHOR_TABLE_NAME = 'authors'

log = logging.Logger("--models--")
logging.basicConfig(level='INFO')


@dataclass
class Book:
    title: str
    author_id: int
    id: Optional[int] = None

    def __getitem__(self, item: str) -> Union[int, str]:
        return getattr(self, item)


@dataclass
class Author:
    name_author: str
    fill_name: Optional[str] = ''
    id: Optional[int] = None

    def __getitem__(self, item) -> Union[str]:
        return getattr(self, item)


def init_db(initial_records: List[dict], authors: List[str]) -> None:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' AND name='{BOOKS_TABLE_NAME}';"
        )
        exists = cursor.fetchone()
        # now in `exist` we have tuple with table name if table really exists in DB
        if not exists:

            cursor.executescript(
                f"""CREATE TABLE `{BOOKS_TABLE_NAME}` (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                title TEXT, 
                author_id INTEGER NOT NULL,
                FOREIGN KEY (author_id) REFERENCES {AUTHOR_TABLE_NAME} (id) ON DELETE CASCADE
                );"""
            )

            cursor.executescript(
                f"""CREATE TABLE '{AUTHOR_TABLE_NAME}' (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    name_author TEXT VARCHAR(50),
                    fill_name TEXT                     
                    );"""
            )

            cursor.executemany(
                f'INSERT INTO `{BOOKS_TABLE_NAME}` '
                '(title, author_id) VALUES (?, ?)',
                [(item['title'], item['author']) for item in initial_records]
            )

            cursor.executemany(
                f"""INSERT INTO '{AUTHOR_TABLE_NAME}'
                 (name_author, fill_name) VALUES (?,?);""",
                [(item['name_author'], item['fill_name']) for item in authors]
            )


def _get_book_obj_from_row(row: Tuple) -> Book:
    return Book(id=row[0], title=row[1], author_id=row[2])


def _get_author_obj(row: Tuple) -> Author:
    print(row)
    return Author(id=row[0], name_author=row[1], fill_name=row[2])


def get_all_books() -> List[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM `{BOOKS_TABLE_NAME}`')
        all_books = cursor.fetchall()
        return [_get_book_obj_from_row(row) for row in all_books]


def add_book(book: Book) -> Book:

    if get_author_by_id(book.author_id) is None:
        add_author_by_name(book.author_id)

    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            INSERT INTO `{BOOKS_TABLE_NAME}` 
            (title, author_id) VALUES (?, ?)
            """,
            (book.title, book.author_id)
        )
        book.id = cursor.lastrowid
        return book


def get_book_by_id(book_id: int) -> Optional[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM `{BOOKS_TABLE_NAME}` WHERE id = "%s"' % book_id)
        book = cursor.fetchone()
        if book:
            return _get_book_obj_from_row(book)


def get_books_by_author_id(author_id: int):
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        # cursor.execute(f'SELECT id, title,  FROM `{BOOKS_TABLE_NAME}` WHERE author = "%s";' %name)
        cursor.execute(f"""
        SELECT *
        FROM `{BOOKS_TABLE_NAME}`
        WHERE author_id = ?
        ;""",
        (author_id,))
        books = cursor.fetchall()
        if books:
            return [_get_book_obj_from_row(row) for row in books]


def update_book_by_id(book: Book) -> None:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE {BOOKS_TABLE_NAME}
            SET title = ? ,
                author = ?
            WHERE id = ?
            """, (book.title, book.author, book.id)
        )
        conn.commit()


def delete_book_by_id(book_id: int) -> None:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            DELETE FROM {BOOKS_TABLE_NAME}
            WHERE id = ?;
            """, (book_id,)
        )
        conn.commit()

def delete_book_by_title(title: str) -> None:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            DELETE FROM {BOOKS_TABLE_NAME}
            WHERE title = ?;
            """, (title,)
        )
        conn.commit()


def get_book_by_title(book_title: str) -> Optional[Book]:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT * FROM `{BOOKS_TABLE_NAME}` WHERE title = "%s"' % book_title
        )
        book = cursor.fetchone()
        if book:
            return _get_book_obj_from_row(book)


def get_all_authors() -> List[Author]:
    with sqlite3.connect('table_books.db') as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT id, name_author, fill_name FROM `{AUTHOR_TABLE_NAME}`;""")
        authors = cur.fetchall()
        return [_get_author_obj(row) for row in authors]


def add_author_by_name(author: Author) -> Author:
    with sqlite3.connect('table_books.db') as conn:
        cur = conn.cursor()
        cur.execute(
            f"""INSERT INTO {AUTHOR_TABLE_NAME} (name_author, fill_name) VALUES (?, ?);""",
            (author.name_author, author.fill_name)
        )
        author.id = cur.lastrowid
        return author


def get_author_by_id(author_id: int) -> Optional[Author]:
    with sqlite3.connect('table_books.db') as conn:
        cur = conn.cursor()
        cur.execute(f"""
        SELECT id, name_author, fill_name 
        FROM {AUTHOR_TABLE_NAME} 
        WHERE id = ?;""",  (author_id,))

        author = cur.fetchone()
        log.info(f"author--{author}")
        if author:
            return _get_author_obj(author)


def get_author_by_name(author: str) -> Optional[Author]:
    with sqlite3.connect('table_books.db') as conn:
        cur = conn.cursor()
        cur.execute(f"""SELECT id, name_author, fill_name FROM {AUTHOR_TABLE_NAME} WHERE name_author = '%s';""" % author)
        authore = cur.fetchone()
        log.info(f"author--{authore}")
        if authore:
            return _get_author_obj(authore)


def update_author_by_id(author: Author, id: int) -> None:
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""
            UPDATE {AUTHOR_TABLE_NAME}
            SET name_author = ?, fill_name = ?  
            WHERE id = ?
            """, (author.name_author, author.fill_name, id)
        )
        conn.commit()


def delete_author(id):
    with sqlite3.connect('table_books.db') as conn:
        cur = conn.cursor()
        cur.execute(
            f"""DELETE FROM {AUTHOR_TABLE_NAME} WHERE id = ?;""",
            (id,)
        )
        conn.commit()


def delete_books_author(author_id):
    with sqlite3.connect('table_books.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(f"""
        DELETE FROM {AUTHOR_TABLE_NAME}
        WHERE id = ?
        """,
        (author_id,))

        # cursor.execute(
        #     f"""
        #     DELETE FROM {BOOKS_TABLE_NAME}
        #     WHERE author = ?;
        #     """, (author_id,)
        # )
        # cursor.execute(
        #     f"""DELETE FROM {AUTHOR_TABLE_NAME} WHERE name_author = ?;""",
        #     (author_id,)
        # )

        conn.commit()
