from asyncorm.serializers import ModelSerializer, SerializerMethod
from library.models import Book


class BookSerializer(ModelSerializer):
    book_type = SerializerMethod(method_name="my_book_type")

    @staticmethod
    def my_book_type(instance):
        return instance.book_type_display()

    class Meta:
        model = Book
        fields = ["id", "name", "synopsis", "book_type", "pages", "date_created"]
