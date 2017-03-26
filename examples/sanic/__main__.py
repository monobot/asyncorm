import asyncio

from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView

from asyncorm import configure_orm
from asyncorm. exceptions import QuerysetError
from library.models import Book

app = Sanic(name=__name__)


@app.listener('before_server_start')
def orm_configure(sanic, loop):
    db_config = {'database': 'sanic_example',
                 'host': 'localhost',
                 'user': 'sanicdbuser',
                 'password': 'sanicDbPass',
                 }

    loop = asyncio.get_event_loop()
    # configure_orm receives a dictionary with:
    # the database configuration
    # the application/s where the models are defined
    orm_app = configure_orm({'loop': loop,  # always use the sanic loop!
                             'db_config': db_config,
                             'modules': ['library', ],  # list of apps
                             })

    # this should be run only once, recomend to do that as external command
    # it creates the tables in the database!!!!
    # orm_app.sync_db()


# now the propper sanic workflow
class BooksView(HTTPMethodView):

    async def get(self, request):
        books = await Book.objects.all()
        return json({'method': request.method,
                     'status': 200,
                     'results': [book.asDict() for book in books] or None,
                     'count': len(books),
                     })

    async def post(self, request):
        # populate the book with the data in te request
        book = Book(**request.json)

        # and await on save
        await book.save()

        return json({'method': request.method,
                     'status': 201,
                     'results': book.asDict(),
                     })


class BookView(HTTPMethodView):
    async def get_object(self, request, book_id):
        # we have to await on getting the book info
        try:
            book = await Book.objects.get(**{'id': book_id})
        except QuerysetError as e:
            return e
        return book

    async def get(self, request, book_id):
        book = await self.get_object(request, book_id)

        if isinstance(book, Exception):
            return json({'status': 400,
                         'method': request.method,
                         'error_msg': book.args[0]
                         })
        return json({'method': request.method,
                     'status': 200,
                     'results': book.asDict(),
                     })

    async def put(self, request, book_id):
        book = await self.get_object(request, book_id)

        if isinstance(book, Exception):
            return json(
                {'status': 400,
                 'method': request.method,
                 'error_msg': book.args[0]
                 }
            )

        await book.save(**request.json)

        return json({'method': request.method,
                     'status': 200,
                     'results': book.asDict(),
                     })

    async def patch(self, request, book_id):
        book = await self.get_object(request, book_id)

        if isinstance(book, Exception):
            return json(
                {'status': 400,
                 'method': request.method,
                 'error_msg': book.args[0]
                 }
            )

        await book.save(**request.json)

        return json({'method': request.method,
                     'status': 200,
                     'results': book.asDict(),
                     })

    async def delete(self, request, book_id):
        book = await self.get_object(request, book_id)

        if isinstance(book, Exception):
            return json(
                {'status': 400,
                 'method': request.method,
                 'error_msg': book.args[0]
                 }
            )

        # await on its deletion
        await book.delete()
        return json({'status': 200, 'method': request.method})


app.add_route(BooksView.as_view(), '/books/')
app.add_route(BookView.as_view(), '/books/<book_id:int>/')

if __name__ == '__main__':
    app.run()
