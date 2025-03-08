import pytest
from http import HTTPStatus


from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize('name, args', [
    ('news:home', None),
    ('news:detail', None),
    ('users:login', None),
    ('users:logout', None),
    ('users:signup', None),
])
def test_pages_availability(client, news, name, args):
    if name == 'news:detail':
        args = (news.id,)
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize('client_fixture, expected_status', [
    ('author_client', HTTPStatus.OK),
    ('reader_client', HTTPStatus.NOT_FOUND),
])
@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_availability_for_comment_edit_and_delete(
    client_fixture,
    name,
    comment,
    expected_status,
    request
):
    client = request.getfixturevalue(client_fixture)
    url = reverse(name, args=(comment.id,))
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ['news:edit', 'news:delete'])
def test_redirect_for_anonymous_client(client, comment, name):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
