from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author(db, django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def reader(db, django_user_model):
    return django_user_model.objects.create(username='Reader')


@pytest.fixture
def author_client(db, author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(db, reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(db, news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def news_list(db):
    now = timezone.now()
    for i in range(10):
        News.objects.create(
            title=f'Тестовая новость {i}',
            text='Просто текст.',
            date=now - timedelta(days=i)
        )


@pytest.fixture
def comments_for_news(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def url_to_comments(detail_url):
    return f'{detail_url}#comments'


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def urls():
    return {
        'detail': reverse('news:detail', args=(1,)),
        'login': reverse('users:login'),
        'logout': reverse('users:logout'),
        'signup': reverse('users:signup'),
    }
