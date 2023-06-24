from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment, News
from news.forms import WARNING, BAD_WORDS

DETAIL_URL = 'news:detail'
EDIT_URL = 'news:edit'
DELETE_URL = 'news:delete'


@pytest.mark.django_db
def test_user_can_create_comment(
    new, author_client, author, form_data, pk_for_args_new
):
    url = reverse(DETAIL_URL, args=pk_for_args_new)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == new
    assert new_comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, pk_for_args_new
):
    url = reverse(DETAIL_URL, args=pk_for_args_new)
    assert Comment.objects.count() == 0
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_bad_text(author_client, pk_for_args_new, form_data):
    url = reverse(DETAIL_URL, args=pk_for_args_new)
    form_data['text'] = BAD_WORDS[0]
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_edit_note(author_client, form_data, comment, author):
    url = reverse(EDIT_URL, args=(comment.id,))
    response = author_client.post(url, form_data)
    redirect = reverse(
        DETAIL_URL, args=(News.objects.get().id,)
    ) + '#comments'
    assertRedirects(response, redirect)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news == News.objects.get()
    assert comment.author == author


def test_other_user_cant_edit_note(admin_client, form_data, comment):
    url = reverse(EDIT_URL, args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, pk_for_args_comment):
    url = reverse(DELETE_URL, args=pk_for_args_comment)
    assert Comment.objects.count() == 1
    response = author_client.post(url)
    redirect = reverse(
        DETAIL_URL, args=(News.objects.get().id,)
    ) + '#comments'
    assertRedirects(response, redirect)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(
        admin_client, pk_for_args_comment, author
):
    url = reverse(DELETE_URL, args=pk_for_args_comment)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == 'Текст комментария'
    assert Comment.objects.get().news == News.objects.get()
    assert Comment.objects.get().author == author
