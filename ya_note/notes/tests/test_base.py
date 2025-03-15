from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND


class BaseTestCase(TestCase):

    NOTE_COUNT = 1
    NEW_NOTE_TITLE = 'Новая заметка'
    NEW_NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_SLUG = 'new-note'
    DUPLICATE_SLUG = 'unique-slug'

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create(username='user2')
        cls.author = User.objects.create_user(username='author')
        cls.reader = User.objects.create(username='Читатель простой')

        cls.note1 = Note.objects.create(
            title='Заметка пользователя 1',
            text='Просто текст1.',
            author=cls.user1,
            slug='note1',
        )

        cls.note2 = Note.objects.create(
            title='Заметка пользователя 2',
            text='Просто текст2.',
            author=cls.user2,
            slug='note2',
        )

        cls.note = Note.objects.create(
            title='Новая заметка',
            text='Текст комментария',
            author=cls.author,
            slug='initial-slug'
        )
        cls.note_with_dublicate_slug = Note.objects.create(
            title='Заголовок',
            text='Текст2',
            author=cls.author,
            slug=cls.DUPLICATE_SLUG
        )

        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.login_url = reverse('users:login')
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

        cls.client_user1 = cls.client_class()
        cls.client_user1.force_login(cls.user1)
        cls.client_user2 = cls.client_class()
        cls.client_user2.force_login(cls.user2)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.user1)
        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)

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

        cls.home_url = reverse('notes:home')
        cls.detail_url = reverse('notes:detail', args=[cls.note.slug])
        cls.success_url = reverse('notes:success')
        cls.urls_anonymous = (
            (cls.home_url, OK),
            (cls.list_url, FOUND),
            (cls.detail_url, FOUND),
            (cls.add_url, FOUND),
            (cls.edit_url, FOUND),
            (cls.delete_url, FOUND),
            (cls.success_url, FOUND),
        )

        cls.urls_authorized_author = (
            (cls.list_url, OK),
            (cls.detail_url, OK),
            (cls.add_url, OK),
            (cls.edit_url, OK),
            (cls.delete_url, OK),
            (cls.success_url, OK),
        )

        cls.urls_redirect_anonymous = (
            (cls.edit_url, 'notes:edit'),
            (cls.delete_url, 'notes:delete'),
            (cls.detail_url, 'notes:detail'),
            (cls.add_url, 'notes:add'),
            (cls.success_url, 'notes:success'),
            (cls.list_url, 'notes:list'),
        )
