from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('name', ['home', 'login', 'logout', 'signup'])
def test_pages_availability(client, name, urls, detail_url):
    url = urls[name] if name != 'detail' else detail_url
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('reverse_url, parametrized_client, status', [
    (lambda comment: reverse('news:edit', args=(comment.id,)),
     'author_client', HTTPStatus.OK),
    (lambda comment: reverse('news:edit', args=(comment.id,)),
     'reader_client', HTTPStatus.NOT_FOUND),
    (lambda comment: reverse('news:delete', args=(comment.id,)),
     'author_client', HTTPStatus.OK),
    (lambda comment: reverse('news:delete', args=(comment.id,)),
     'reader_client', HTTPStatus.NOT_FOUND),
])
def test_availability_for_comment_edit_and_delete(
    reverse_url,
    parametrized_client,
    status,
    comment,
    request
):
    client = request.getfixturevalue(parametrized_client)
    url = reverse_url(comment)
    response = client.get(url)
    assert response.status_code == status
