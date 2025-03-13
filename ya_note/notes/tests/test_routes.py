from http import HTTPStatus

from django.contrib.auth import get_user_model
from .test_base import BaseTestCase

User = get_user_model()


class TestRoutes(BaseTestCase):
    def test_pages_availability_without_auth(self):
        """Тест доступности страниц без авторизации"""
        for url, expected_status in self.urls_anonymous:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_pages_availability(self):
        """Тест доступности страниц c авторизацией"""
        for url, expected_status in self.urls_authorized_author:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_availability_for_different_users(self):
        pages = [
            url for url, name in self.urls_redirect_anonymous
            if name in ('notes:edit', 'notes:delete', 'notes:detail')
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа неавторизованного пользователя"""
        for url, _ in self.urls_redirect_anonymous:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_are_accessible(self):
        for url, expected_status in self.urls_authorized_author:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, expected_status)
