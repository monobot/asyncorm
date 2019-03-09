from asyncorm.serializers import ModelSerializer
from tests.app_1.models import Book


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = ["name", "content"]
