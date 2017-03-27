from asyncorm.model import ModelSerializer, SerializerMethod
from library.models import Book


class BookSerializer(ModelSerializer):
    book_type = SerializerMethod()
    # date_created = SerializerMethod()

    def get_book_type(self, instance):
        return instance.book_type_display()

    # def get_date_created(self, instance):
    #     return instance.date_created.strftime('%Y-%m-%d')

    class Meta():
        model = Book
        fields = [
            'id', 'name', 'synopsis', 'book_type', 'pages', 'date_created'
        ]
