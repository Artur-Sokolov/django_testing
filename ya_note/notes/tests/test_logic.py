from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .test_base import BaseTestCase

User = get_user_model()


class TestNoteLogic(BaseTestCase):
    def test_anonymus_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        note_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.note_data)
        expected_redirect = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Note.objects.count(), note_count_before)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        note_count_before = Note.objects.count()
        response = self.auth_client.post(self.add_url, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), note_count_before + 1)
        new_note = Note.objects.get(slug=self.NEW_NOTE_SLUG)
        self.assertEqual(new_note.title, self.note_data['title'])
        self.assertEqual(new_note.text, self.note_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_user_cant_create_note_with_duplicate_slug(self):
        """Пользователь не может создать заметку с уже существующим slug."""
        note_count_before = Note.objects.count()
        response = self.auth_client.post(
            self.add_url,
            data=self.duplicate_note_data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), note_count_before)
        expected_error = (f'{self.DUPLICATE_SLUG}{WARNING}')
        self.assertFormError(response, 'form', 'slug', expected_error)

    def test_slug_is_generated_if_empty(self):
        """Если slug не заполнен, он создаётся автоматически."""
        Note.objects.all().delete()
        responce = self.auth_client.post(
            self.add_url,
            data=self.note_data_empty_slug
        )
        self.assertEqual(responce.status_code, HTTPStatus.FOUND)
        expected_slug = slugify(self.note_data_empty_slug['title'])
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, expected_slug)

    def test_user_can_delete_own_note(self):
        """Клиент может удалять свои заметки."""
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            Note.objects.count(),
            notes_count_before - self.NOTE_COUNT
        )
        with self.assertRaises(Note.DoesNotExist):
            Note.objects.get(id=self.note.id)

    def test_user_cant_edit_or_delete_others_notes(self):
        """Клиент не может редактировать и удалять чужие заметки."""
        with self.subTest('Test user cannot edit others note'):
            response = self.other_client.post(
                self.edit_url,
                data=self.note_data
            )
            self.assertEqual(response.status_code, HTTPStatus.FOUND)
            note_after = Note.objects.get(id=self.note.id)
            self.assertEqual(note_after.title, self.note.title)
            self.assertEqual(note_after.text, self.note.text)
            self.assertEqual(note_after.slug, self.note.slug)
            self.assertEqual(note_after.author, self.note.author)

        with self.subTest('Test user cannot delete others note'):
            notes_count_before = Note.objects.count()
            response = self.other_client.post(self.delete_url)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
            self.assertEqual(Note.objects.count(), notes_count_before)

    def test_user_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        response = self.auth_client.post(self.edit_url,
                                         data=self.edit_note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, 'initial-slug')
        self.assertEqual(self.note.author, self.author)
