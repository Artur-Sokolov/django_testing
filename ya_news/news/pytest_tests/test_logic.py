from http import HTTPStatus

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


FORM_DATA = {'text': 'Текст комментария'}
NEW_FORM_DATA = {'text': 'Обновлённый комментарий'}
BAD_WORDS_DATA = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


def test_anonymous_user_cant_create_comment(client, detail_url):
    initial_count = Comment.objects.count()
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == initial_count


def test_user_can_create_comment(
    author_client,
    detail_url,
    news,
    author
):
    Comment.objects.all().delete()
    response = author_client.post(detail_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{detail_url}#comments'
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    initial_count = Comment.objects.count()
    response = author_client.post(detail_url, data=BAD_WORDS_DATA)
    assert Comment.objects.count() == initial_count
    assert response.context['form'].errors['text'] == [WARNING]


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    initial_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    assert Comment.objects.count() == initial_count - 1


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    initial_count = Comment.objects.count()
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count


def test_author_can_edit_comment(author_client, edit_url,
                                 url_to_comments, comment):
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == NEW_FORM_DATA['text']
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_user_cant_edit_comment_of_another_user(reader_client,
                                                edit_url,
                                                comment
                                                ):
    response = reader_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news
