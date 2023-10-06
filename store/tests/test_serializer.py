from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksSerialiserTEstCase(TestCase):
    def test_get(self):
        self.user = User.objects.create(username='test_username')
        book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        book_2 = Book.objects.create(name='Test book 2', price=242, author_name='Author 2', owner=self.user)
        data = BooksSerializer([book_1, book_2], many=True).data
        # Данные которые мы ожидаем!
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': 25.00,
                'author_name': 'Author 1',
                'owner': 'test_username',
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': 242.00,
                'author_name': 'Author 2',
                'owner': 'test_username',
            }
        ]
        print(expected_data)
        print(data)
        self.assertEqual(expected_data, data)
