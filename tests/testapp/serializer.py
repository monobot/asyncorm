from asyncorm.model import ModelSerializer
from .models import Book


class BookSerializer(ModelSerializer):

    class Meta:
        model = Book
        fields = ['name', 'content', 'kks']


class BookSerializer2(ModelSerializer):

    class Meta:
        model = Book
        fields = ['name', 'content', ]
