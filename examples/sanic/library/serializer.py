from asyncorm.models import ModelSerializer, SerializerMethod
from library.models import Book


class BookSerializer(ModelSerializer):
    book_type = SerializerMethod()

    @staticmethod
    def get_book_type(instance):
        return instance.book_type_display()

    class Meta():
        model = Book
        fields = [
            'id', 'name', 'synopsis', 'book_type', 'pages', 'date_created'
        ]
