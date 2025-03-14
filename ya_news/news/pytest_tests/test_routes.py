from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture as lf


pytestmark = pytest.mark.django_db


OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND
FOUND = HTTPStatus.FOUND


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, expected_status, precomputed_key',
    [
        (lf('home_url'), 'client', OK, None),
        (lf('detail_url'), 'client', OK, None),
        (lf('precomputed_urls'), 'client', OK, 'login'),
        (lf('precomputed_urls'), 'client', OK, 'logout'),
        (lf('precomputed_urls'), 'client', OK, 'signup'),
        (lf('edit_url'), 'author_client', OK, None),
        (lf('edit_url'), 'reader_client', NOT_FOUND, None),
        (lf('delete_url'), 'author_client', OK, None),
        (lf('delete_url'), 'reader_client', NOT_FOUND, None),
    ]
)
def test_pages_availability(
    reverse_url, parametrized_client, expected_status, request,
    precomputed_key
):
    client = request.getfixturevalue(parametrized_client)
    url = reverse_url[precomputed_key] if precomputed_key else reverse_url
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'reverse_url',
    [
        lf('edit_url'),
        lf('delete_url'),
    ]
)
def test_redirect_for_anonymous_user(reverse_url, client,
                                     redirect_url_for_anonymous):
    response = client.get(reverse_url)
    assert response.status_code == FOUND
    assert response.url == redirect_url_for_anonymous(reverse_url)
