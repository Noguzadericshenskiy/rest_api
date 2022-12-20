import logging
# from dataclasses import asdict
from typing import Tuple, List, Dict

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from flasgger import APISpec, Swagger
from flask import Flask, request
from flask_restful import Api, Resource
from marshmallow import ValidationError, INCLUDE
from werkzeug.serving import WSGIRequestHandler

from models import (DATA, AUTHORS, init_db, get_all_books, add_book, get_book_by_id, delete_book_by_id,
                    Book, update_book_by_id, get_all_authors, add_author_by_name, get_author_by_id, delete_author,
                    get_books_by_author_id, update_author_by_id, delete_books_author, delete_book_by_title)
from schemas import BookSchema, AuthorSchema

log = logging.getLogger("routes.py")
logging.basicConfig(level='INFO')


app = Flask(__name__)
api = Api(app)

spec = APISpec(
    title='BooksList',
    version='1.0.0',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)


class BookList(Resource):
    def get(self) -> Tuple[List[Dict], int]:
        """
        Описание метода.....
        ---
        tags:
          - books
        responses:
          200:
            description: Books data
            schema:
             type: array
             items:
        """

        schema = BookSchema()
        return schema.dump(get_all_books(), many=True), 200

    def post(self) -> Tuple[Dict, int]:
        """Add book in db"""
        data = request.json
        schema = BookSchema()

        try:
            book = schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        book = add_book(book)
        return schema.dump(book), 201

    def delete(self):
        """Delet book by title"""
        title = request.json['title']
        log.info(title)
        delete_book_by_title(title)
        return "Book delete"


class BookGUD(Resource):
    def get(self, id):
        schema = BookSchema()
        return schema.dump(get_book_by_id(id),), 200

    def put(self, id: int):
        json_date = request.json
        schema = BookSchema()
        json_date["id"] = id
        # объявление в самом классе схема или так
        # book = schema.load(json_date, unknown=INCLUDE)
        book = schema.load(json_date)
        update_book_by_id(book)

        return schema.dump(get_book_by_id(id), ), 200

    def delete(self, id):
        delete_book_by_id(id)
        return "Book delete"


class AuthorList(Resource):
    def get(self) -> Tuple[List[Dict], int]:
        """
        Список всех авторов
        ---
        tags:
          - authors
        responses:
          200:
            description: Authors data
            schema:
                type: array
                items:
                  $ref: '#/definitions/Author'
        """

        schema = AuthorSchema()
        return schema.dump(get_all_authors(), many=True), 200

    def post(self) -> Tuple[Dict, int]:
        """
        Создает нового автора
        ---
        tags:
          - authors
        parameters:
          - in: body
            name: new author params
            schema:
              $ref: '#/definitions/Author'
        responses:
          201:
            description: Создан новый автор
            schema:
              $ref: '#/definitions/Author'
          400:
            description: BAD REQUEST
        """
        data = request.json
        schema = AuthorSchema()

        try:
            author = schema.load(data)

        except ValidationError as err:
            return err.messages, 400

        author = add_author_by_name(author)
        res = schema.dump(author)

        return res, 200


class AuthorGUD(Resource):
    def get(self, id):
        """
        This method gets information about the author by authot ID
        ---
        tags:
          - authors
        parameters:
          - in: path
            name: id
        responses:
          201:
            description: Author info
            schema:
              $ref: '#/definitions/Author'

        """
        schema = AuthorSchema()
        return schema.dump(get_author_by_id(id),), 200

    def put(self, id):
        """
        Метод изменяет информацию об авторе
        ---
        tags:
          - authors
        responses:
          202:
            description: Информация успешно обновлена
            schema:
              $ref: '#/definitions/Author'
          400:
            description: BAD REQUEST

        """
        json_date = request.json
        schema = AuthorSchema()
        author = schema.load(json_date)
        update_author_by_id(author, id)
        return schema.dump(get_author_by_id(id),), 202

    def delete(self, id):
        """
        Удаляет автора из базы
        ---
        tags:
          - xz
        parameters:
          - in: path
            name: id
        responses:
          200:
            description: OK
          400:
            description: BAD
        """
        delete_author(id)
        return f"Author {id} destroyed", 200


class AutorAndBook(Resource):
    def get(self, author_id):
        schema = BookSchema()
        return schema.dump(get_books_by_author_id(author_id), many=True), 200

    def delete(self, author_id):
        delete_books_author(author_id)
        return 'ok', 200


template = spec.to_flasgger(app, definitions=[BookSchema, AuthorSchema])
swagger = Swagger(app, template=template)

api.add_resource(BookList, '/api/books')
api.add_resource(BookGUD, '/api/books/<int:id>')
api.add_resource(AuthorList, '/api/authors')
api.add_resource(AuthorGUD, '/api/author/<int:id>')
api.add_resource(AutorAndBook, '/api/authors/<int:author_id>/books')

# Simple
if __name__ == '__main__':
    init_db(initial_records=DATA, authors=AUTHORS)
    app.run('0.0.0.0', debug=True)

# Session
# if __name__ == '__main__':
#     init_db(initial_records=DATA, authors=AUTHORS)
#     WSGIRequestHandler.protocol_version = "HTTP/1.1"
#     app.run('0.0.0.0', debug=True)
