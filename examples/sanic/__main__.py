from asyncorm.application.configure import configure_orm
from asyncorm.exceptions import QuerysetError
from library.models import Book
from library.serializer import BookSerializer
from sanic import Sanic
from sanic.exceptions import NotFound, URLBuildError
from sanic.response import json
from sanic.views import HTTPMethodView

app = Sanic(name=__name__)


@app.listener("before_server_start")
def orm_configure(sanic, loop):
    # configure_orm defaults to the asyncorm.ini in same directory
    # the loop is required tho
    orm = configure_orm(loop=loop)
    orm.sync_db()


# for all the 404 lets handle the exceptions
@app.exception(NotFound)
def ignore_404s(request, exception):
    return json(
        {"error": exception.args[0], "method": request.method, "results": None, "status": exception.status_code}
    )


@app.exception(URLBuildError)
def ignore_urlbuilderrors(request, exception):
    return json(
        {"error": exception.args[0], "method": request.method, "results": None, "status": exception.status_code}
    )


# now the propper sanic workflow
class BooksView(HTTPMethodView):
    async def get(self, request):
        filtered_by = request.raw_args

        if filtered_by:
            try:
                q_books = Book.objects.filter(**filtered_by)
            except AttributeError as e:
                raise URLBuildError(e.args[0])
        else:
            q_books = Book.objects.all()

        books = []
        async for book in q_books:
            books.append(BookSerializer.serialize(book))

        return json({"method": request.method, "status": 200, "results": books or None, "count": len(books)})

    async def post(self, request):
        # populate the book with the data in the request
        book = Book(**request.json)

        # and await on save
        await book.save()

        return json({"method": request.method, "status": 201, "results": BookSerializer.serialize(book)})


class BookView(HTTPMethodView):
    async def get_object(self, request, book_id):
        try:
            # await on database consults
            book = await Book.objects.get(**{"id": book_id})
        except QuerysetError as e:
            raise NotFound(e.args[0])
        return book

    async def get(self, request, book_id):
        # await on database consults
        book = await self.get_object(request, book_id)

        return json({"method": request.method, "status": 200, "results": BookSerializer.serialize(book)})

    async def put(self, request, book_id):
        # await on database consults
        book = await self.get_object(request, book_id)
        # await on save
        await book.save(**request.json)

        return json({"method": request.method, "status": 200, "results": BookSerializer.serialize(book)})

    async def patch(self, request, book_id):
        # await on database consults
        book = await self.get_object(request, book_id)
        # await on save
        await book.save(**request.json)

        return json({"method": request.method, "status": 200, "results": BookSerializer.serialize(book)})

    async def delete(self, request, book_id):
        # await on database consults
        book = await self.get_object(request, book_id)
        # await on its deletion
        await book.delete()

        return json({"method": request.method, "status": 200, "results": None})


app.add_route(BooksView.as_view(), "/books/")
app.add_route(BookView.as_view(), "/books/<book_id:int>/")

if __name__ == "__main__":
    app.run(port=9000, debug=True)
