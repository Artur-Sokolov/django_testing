from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        cls.edit_url = reverse('notes:edit', args=(cls.note1.slug,))

        cls.client_user1 = cls.client_class()
        cls.client_user1.force_login(cls.user1)
        cls.client_user2 = cls.client_class()
        cls.client_user2.force_login(cls.user2)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.other_client = Client()
        cls.other_client.force_login(cls.user1)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)
        cls.anonymous_client = cls.client_class()

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

        cls.urls_anonymous = (
            (reverse('notes:home'), HTTPStatus.OK),
            (reverse('notes:list'), HTTPStatus.FOUND),
            (reverse('notes:detail', args=['initial-slug']), HTTPStatus.FOUND),
            (reverse('notes:add'), HTTPStatus.FOUND),
            (reverse('notes:edit', args=['initial-slug']), HTTPStatus.FOUND),
            (reverse('notes:delete', args=['initial-slug']), HTTPStatus.FOUND),
            (reverse('notes:success'), HTTPStatus.FOUND),
        )

        cls.urls_authorized_author = (
            (reverse('notes:list'), HTTPStatus.OK),
            (reverse('notes:detail', args=['initial-slug']), HTTPStatus.OK),
            (reverse('notes:add'), HTTPStatus.OK),
            (reverse('notes:edit', args=['initial-slug']), HTTPStatus.OK),
            (reverse('notes:delete', args=['initial-slug']), HTTPStatus.OK),
            (reverse('notes:success'), HTTPStatus.OK),
        )

        cls.urls_redirect_anonymous = (
            (reverse('notes:edit', args=['initial-slug']), 'notes:edit'),
            (reverse('notes:delete', args=['initial-slug']), 'notes:delete'),
            (reverse('notes:detail', args=['initial-slug']), 'notes:detail'),
            (reverse('notes:add'), 'notes:add'),
            (reverse('notes:success'), 'notes:success'),
            (reverse('notes:list'), 'notes:list'),
        )
