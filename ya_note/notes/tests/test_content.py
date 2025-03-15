from http import HTTPStatus

from notes.forms import NoteForm
from .test_base import BaseTestCase

OK = HTTPStatus.OK


class TestDetailPage(BaseTestCase):
    def test_note_appears_in_object_notes(self):
        """Проверяем заметку - отображается в object_notes у своего автора."""
        response = self.client_user1.get(self.list_url)
        self.assertEqual(response.status_code, OK)
        object_notes = response.context['object_list']
        self.assertIn(self.note1, object_notes)
        self.assertNotIn(self.note2, object_notes)

    def test_user_see_only_his_own_notes(self):
        """Проверяем, что пользователь видит только свои заметки."""
        response = self.client_user2.get(self.list_url)
        self.assertEqual(response.status_code, OK)
        object_notes = response.context['object_list']
        self.assertIn(self.note2, object_notes)
        self.assertNotIn(self.note1, object_notes)

    def test_authorized_client_has_form(self):
        urls = [
            (self.add_url, 'add_page'),
            (self.edit_url, 'edit_page')
        ]
        for url, page_name in urls:
            with self.subTest(page=page_name):
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
