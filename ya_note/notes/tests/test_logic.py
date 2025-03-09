from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class BaseTestCase(TestCase):
    NOTE_COUNT = 1
    NEW_NOTE_TITLE = 'Новая заметка'
    NEW_NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_SLUG = 'new-note'
    DUPLICATE_SLUG = 'unique-slug'

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1')
        cls.author = User.objects.create_user(username='author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.user1)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='initial-slug'
        )
        cls.note_with_dublicate_slug = Note.objects.create(
            title='Заголовок',
            text='Текст2',
            author=cls.author,
            slug=cls.DUPLICATE_SLUG
        )

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.login_url = reverse('users:login')

        cls.note_data = {
            'title': 'Новая заметка',
            'text': 'Какой-то текст',
            'slug': cls.NEW_NOTE_SLUG
        }
        cls.duplicate_note_data = {
            'title': 'Дубликат',
            'text': 'Текст заметки',
            'slug': cls.DUPLICATE_SLUG
        }
        cls.note_data_empty_slug = {
            'title': 'Новая заметка',
            'text': 'Какой-то текст',
            'slug': ''
        }
        cls.edit_note_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }


class TestNoteLogic(BaseTestCase):
    def test_anonymus_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        note_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.note_data)
        login_url = reverse('users:login')
        expected_redirect = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Note.objects.count(), note_count_before)

    def test_user_cant_create_note_with_duplicate_slug(self):
        """Пользователь не может создать заметку с уже существующим slug."""
        response = self.auth_client.post(
            self.add_url,
            data=self.duplicate_note_data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Note.objects.filter(slug=self.DUPLICATE_SLUG).count(),
            self.NOTE_COUNT
        )
        expected_error = (
            'unique-slug - такой slug уже существует, '
            'придумайте уникальное значение!'
        )
        self.assertFormError(response, 'form', 'slug', expected_error)

    def test_slug_is_generated_if_empty(self):
        """Если slug не заполнен, он создаётся автоматически."""
        responce = self.auth_client.post(
            self.add_url,
            data=self.note_data_empty_slug
        )
        self.assertEqual(responce.status_code, HTTPStatus.FOUND)
        expected_slug = slugify(self.note_data_empty_slug['title'])
        self.assertTrue(Note.objects.filter(slug=expected_slug).exists())

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
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
            note_after = Note.objects.get(id=self.note.id)
            self.assertEqual(note_after.title, self.note.title)
            self.assertEqual(note_after.text, self.note.text)
            self.assertEqual(note_after.slug, self.note.slug)

        with self.subTest('Test user cannot delete others note'):
            notes_count_before = Note.objects.count()
            response = self.other_client.post(self.delete_url)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
            self.assertEqual(Note.objects.count(), notes_count_before)
