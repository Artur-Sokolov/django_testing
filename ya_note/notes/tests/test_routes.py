from http import HTTPStatus

from django.contrib.auth import get_user_model
from .test_base import BaseTestCase

User = get_user_model()


NOT_FOUND = HTTPStatus.NOT_FOUND


class TestRoutes(BaseTestCase):
    def test_pages_availability_without_auth(self):
        """Тест доступности страниц без авторизации"""
        for url, expected_status in self.urls_anonymous:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_pages_availability(self):
        """Тест доступности страниц c авторизацией"""
        for url, expected_status in self.urls_authorized_author:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_availability_for_different_users(self):
        restricted_urls = [
            self.edit_url,
            self.delete_url,
            self.detail_url,
        ]
        for url in restricted_urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        """Тест редиректа неавторизованного пользователя"""
        for url, _ in self.urls_redirect_anonymous:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
