from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

HOME_URL = 'news:home'
DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'
LOGIN_URL = 'users:login'
LOGOUT_URL = 'users:logout'
SIGNUP_URL = 'users:signup'
lazy_new = pytest.lazy_fixture('pk_for_args_new')
lazy_comment = pytest.lazy_fixture('pk_for_args_comment')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'clients, name, args, expected_status',  # как ли сделать args внутри name?
    [
        (pytest.lazy_fixture('client'), HOME_URL, None, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), DETAIL_URL, lazy_new, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), LOGIN_URL, None, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), LOGOUT_URL, None, HTTPStatus.OK),
        (pytest.lazy_fixture('client'), SIGNUP_URL, None, HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'),
         EDIT_URL, lazy_comment, HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('admin_client'),
         DELETE_URL, lazy_comment, HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'),
         EDIT_URL, lazy_comment, HTTPStatus.OK),
        (pytest.lazy_fixture('author_client'),
         DELETE_URL, lazy_comment, HTTPStatus.OK),
    ]
)
def test_pages_availability_for_different_users(
        clients, name, args, expected_status,
):
    url = reverse(name, args=args)
    response = clients.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        (EDIT_URL, lazy_comment),
        (DELETE_URL, lazy_comment),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse(LOGIN_URL)
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
