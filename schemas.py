from typing import Dict

from flasgger import Schema, fields, ValidationError
from marshmallow import validates, post_load, INCLUDE

from models import get_book_by_title, get_author_by_id, get_author_by_name, Book, Author


class BookSchema(Schema):

    class Meta:
        unknown = INCLUDE

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author_id = fields.Int(required=True)
    author_name = fields.Str()

    # @validates('title')
    # def validate_title(self, title: str) -> None:
    #     if get_book_by_title(title) is not None:
    #         raise ValidationError(
    #             'Book with title "{title}" already exists, '
    #             'please use a different title.'.format(title=title)
    #         )

    @validates('author_id')
    def validate_author(self, author_id: int) -> None:
        if get_author_by_id(author_id) is None:
            raise ValidationError(f"Автора с ID: {author_id} нет")

    @post_load
    def create_book(self, data: Dict, **kwargs) -> Book:
        return Book(**data)


class AuthorSchema(Schema):

    id = fields.Int(dump_only=True)
    name_author = fields.Str(required=True)
    fill_name = fields.Str()

    @validates('name_author')
    def validate_name(self, name_author: str) -> None:
        if not isinstance(name_author, str):
            raise ValidationError('Имя автора- строка')
        # if get_author_by_name(name_author) is not None:
        #     raise ValidationError("Уже есть такой автор, хватит и одного")


    @post_load
    def create_author(self, data: Dict, **kwargs) -> Author:
        return Author(**data)


# class BookAndAutorShema(Schema):

