from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='test-slug'
        )

        cls.anonymous_client = cls.client_class()
        cls.author_client = cls.client_class()
        cls.reader_client = cls.client_class()

        cls.login_url = reverse('users:login')

        cls.urls_anonymous = (
            ('notes:home', None, HTTPStatus.OK),
            ('notes:list', None, HTTPStatus.FOUND),
            ('notes:detail', (cls.note.slug,), HTTPStatus.FOUND),
            ('notes:add', None, HTTPStatus.FOUND),
            ('notes:edit', (cls.note.slug,), HTTPStatus.FOUND),
            ('notes:delete', (cls.note.slug,), HTTPStatus.FOUND),
            ('notes:success', None, HTTPStatus.FOUND),
        )

        cls.urls_authorized_author = (
            ('notes:list', None, HTTPStatus.OK),
            ('notes:detail', (cls.note.slug,), HTTPStatus.OK),
            ('notes:add', None, HTTPStatus.OK),
            ('notes:edit', (cls.note.slug,), HTTPStatus.OK),
            ('notes:delete', (cls.note.slug,), HTTPStatus.OK),
            ('notes:success', None, HTTPStatus.OK),
        )

        cls.urls_redirect_anonymous = (
            'notes:edit',
            'notes:delete',
            'notes:detail',
            'notes:add',
            'notes:success',
            'notes:list',
        )

        cls.urls_auth_pages = (
            ('users:login', None, HTTPStatus.OK),
            ('users:logout', None, HTTPStatus.OK),
            ('users:signup', None, HTTPStatus.OK),
        )

    def setUp(self):
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)


class TestRoutes(BaseTestCase):
    def test_pages_availability_without_auth(self):
        """Тест доступности страниц без авторизации"""
        for name, args, expected_status in self.urls_anonymous:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.anonymous_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_pages_availability(self):
        """Тест доступности страниц c авторизацией"""
        for name, args, expected_status in self.urls_authorized_author:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_availability_for_different_users(self):
        pages = ('notes:edit', 'notes:delete', 'notes:detail')
        for name in pages:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа неавторизованного пользователя"""
        for name in self.urls_redirect_anonymous:
            with self.subTest(name=name):
                args = (self.note.slug,) if name in (
                    'notes:edit', 'notes:delete', 'notes:detail') else None
                url = reverse(name, args=args)
                redirect_url = f'{self.login_url}?next={url}'
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_are_accessible(self):
        for name, args, expected_status in self.urls_authorized_author:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, expected_status)
