from http import HTTPStatus

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    [
        (pytest.lazy_fixture('home_url'), 'client', HTTPStatus.OK),
        (pytest.lazy_fixture('detail_url'), 'client', HTTPStatus.OK),
        (reverse('users:login'), 'client', HTTPStatus.OK),
        (reverse('users:logout'), 'client', HTTPStatus.OK),
        (reverse('users:signup'), 'client', HTTPStatus.OK),
    ]
)
def test_pages_availability(
    reverse_url,
    parametrized_client,
    expected_status,
    request
):
    client = request.getfixturevalue(parametrized_client)
    response = client.get(reverse_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status',
    [
        (pytest.lazy_fixture('edit_url'),
         'author_client', HTTPStatus.OK),
        (pytest.lazy_fixture('edit_url'),
         'reader_client', HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('delete_url'),
         'author_client', HTTPStatus.OK),
        (pytest.lazy_fixture('delete_url'),
         'reader_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_availability_for_comment_edit_and_delete(
    reverse_url, parametrized_client, expected_status, request
):
    client = request.getfixturevalue(parametrized_client)
    response = client.get(reverse_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'reverse_url',
    [
        pytest.lazy_fixture('edit_url'),
        pytest.lazy_fixture('delete_url'),
    ]
)
def test_redirect_for_anonymous_user(reverse_url, client):
    redirect_url = f"{reverse('users:login')}?next={reverse_url}"
    response = client.get(reverse_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
