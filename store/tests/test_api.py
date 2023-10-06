import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=242, author_name='Author 2')
        self.book_3 = Book.objects.create(name='Test book Author 1', price=25, author_name='Author 3')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        # Сравниваем что пришло с запроса и с сериалайзера
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 25.00})
        # Сравниваем что пришло с запроса и с сериалайзера
        serializer_data = BooksSerializer([self.book_1, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})
        # Сравниваем что пришло с запроса и с сериалайзера
        serializer_data = BooksSerializer([self.book_1, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        # Сравниваем что пришло с запроса и с сериалайзера
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_name_models(self):
        self.assertEqual(str(self.book_1), self.book_1.__str__())

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {"name": "Programming in Python 3.12",
                "price": 231,
                "author_name": "Alex Chavlytko"}
        json_data = json.dumps(data)
        # Обход авторизации для пост запроса
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса и с сериалайзера

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 555,
                "author_name": self.book_1.author_name}
        json_data = json.dumps(data)
        # Обход авторизации для пут запроса
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса и с сериалайзера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(555, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 555,
                "author_name": self.book_1.author_name}
        json_data = json.dumps(data)
        # Обход авторизации для пут запроса
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса и с сериалайзера
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.book_1.refresh_from_db()
        self.assertEqual(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"name": self.book_1.name,
                "price": 555,
                "author_name": self.book_1.author_name}
        json_data = json.dumps(data)
        # Обход авторизации для пут запроса
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса и с сериалайзера
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.book_1.refresh_from_db()
        self.assertEqual(555, self.book_1.price)

    def test_delete(self):

        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"id": self.book_1.id}
        json_data = json.dumps(data)
        # Обход авторизации для delete запроса
        self.client.force_login(self.user)
        response = self.client.delete(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        def book_exist(book):
            try:
                book.refresh_from_db()
            except:
                return False

        self.assertEqual(book_exist(self.book_1), Book.objects.filter(id=self.book_1.id).exists())

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"id": self.book_1.id}
        json_data = json.dumps(data)
        # Обход авторизации для delete запроса
        self.client.force_login(self.user2)
        response = self.client.delete(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        def book_exist(book):
            try:
                book.refresh_from_db()
            except:
                return False

    def test_delete_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {"id": self.book_1.id}
        json_data = json.dumps(data)
        # Обход авторизации для delete запроса
        self.client.force_login(self.user2)
        response = self.client.delete(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        def book_exist(book):
            try:
                book.refresh_from_db()
            except:
                return False

        self.assertEqual(book_exist(self.book_1), Book.objects.filter(id=self.book_1.id).exists())


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', price=25, author_name='Author 1', owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2', price=242, author_name='Author 2')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {"like": True,
                }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        """При пут передается весь объект, а при патч передается одно поле"""
        response = self.client.patch(url, data=json_data, content_type='application/json')
        # Сравниваем что пришло с запроса и с сериалайзера
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

        data = {"in_bookmarks": True,
                }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {"rate": 3,
                }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        """При пут передается весь объект, а при патч передается одно поле"""
        response = self.client.patch(url, data=json_data, content_type='application/json')

        # Сравниваем что пришло с запроса и с сериалайзера
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_worng(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {"rate": 6,
                }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        """При пут передается весь объект, а при патч передается одно поле"""
        response = self.client.patch(url, data=json_data, content_type='application/json')

        # Сравниваем что пришло с запроса и с сериалайзера
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)

        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)



