import asyncio

from sanic import Sanic
from sanic.response import json
from sanic.views import HTTPMethodView

from asyncorm import configure_orm
from library.models import Book

app = Sanic(name=__name__)
loop = asyncio.get_event_loop()

db_config = {
    'database': 'sanic_example',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
}

# configure_orm receives a dictionary with:
# the database configuration and the application/s where the models are defined
orm_app = configure_orm({
    'loop': loop,  # always use the same loop as sanic!
    'db_config': db_config,
    'modules': ['library', ],
})

# this should be run only once, since it creates the tables in the database!!!!
orm_app.sync_db()


# now the propper sanic workflow
class BooksView(HTTPMethodView):

    async def get(self, request):
        books = await Book.objects.all()

        return json({'method': request.method,
                     'status': 200,
                     'results': books or None,
                     'count': len(books),
                     })

    async def post(self, request):
        # populate the book with the data in te request
        book = Book(request.json)

        # and await on save
        await book.save()

        return json({'method': request.method,
                     'status': 201,
                     'results': book,
                     })


class BookView(HTTPMethodView):
    async def get(self, request, book_id):
        # we have to await on getting the book info
        book = await Book.objects.get(**{'id': book_id})

        return json({'method': request.method,
                     'status': 200,
                     'results': book,
                     })

    async def put(self, request, book_id):
        # we have to await on getting the book info
        book = await Book.objects.get(**{'id': book_id})

    async def delete(self, request, book_id):
        # we have to await on getting the book info
        book = await Book.objects.get(**{'id': book_id})
        # and also await on its deletion
        await book.delete()
        return json({'status': 200, 'method': request.method})


app.add_route(BookView.as_view(), '/books/<book_id:int>/')
app.add_route(BooksView.as_view(), '/books/')

if __name__ == '__main__':
    app.run(loop=loop)
