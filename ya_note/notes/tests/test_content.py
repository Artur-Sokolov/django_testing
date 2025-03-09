from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.note1 = Note.objects.create(
            title='Зметка пользователя 1',
            text='Просто текст1.',
            author=cls.user1,
            slug='note1',
        )
        cls.note2 = Note.objects.create(
            title='Зметка пользователя 2',
            text='Просто текст2.',
            author=cls.user2,
            slug='note2',
        )
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note1.slug,))
        cls.client_user1 = cls.client_class()
        cls.client_user2 = cls.client_class()


class TestDetailPage(BaseTestCase):
    def test_note_appears_in_object_notes(self):
        """Проверяем заметку - отображается в object_notes у своего автора."""
        self.client_user1.force_login(self.user1)
        response = self.client_user1.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_notes = response.context['object_list']
        self.assertIn(self.note1, object_notes)
        self.assertNotIn(self.note2, object_notes)

    def test_user_see_only_his_own_notes(self):
        """Проверяем, что пользователь видит только свои заметки."""
        self.client_user2.force_login(self.user2)
        response = self.client_user2.get(self.list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object_notes = response.context['object_list']
        self.assertIn(self.note2, object_notes)
        self.assertNotIn(self.note1, object_notes)

    def test_authorized_client_has_form(self):
        self.client_user1.force_login(self.user1)

        with self.subTest():
            response_add = self.client_user1.get(self.add_url)
            self.assertIn('form', response_add.context)
            self.assertIsInstance(response_add.context['form'], NoteForm)

        with self.subTest():
            response_edit = self.client_user1.get(self.edit_url)
            self.assertIn('form', response_edit.context)
            self.assertIsInstance(response_edit.context['form'], NoteForm)
