import pytest

from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.models import Comment, News
from news.forms import WARNING, BAD_WORDS


@pytest.mark.django_db
def test_user_can_create_comment(
    new, author_client, author, form_data, pk_for_args_new
):
    url = reverse('news:detail', args=pk_for_args_new)
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
    url = reverse('news:detail', args=pk_for_args_new)
    client.post(url, data=form_data)
    assert Comment.objects.count() == 0


def test_bad_text(author_client, pk_for_args_new, form_data):
    url = reverse('news:detail', args=pk_for_args_new)
    form_data['text'] = BAD_WORDS[0]
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=(WARNING))
    assert Comment.objects.count() == 0


def test_author_can_edit_note(author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    redirect = reverse(
        'news:detail', args=(News.objects.get().id,)
    ) + '#comments'
    assertRedirects(response, redirect)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_note(admin_client, form_data, comment):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, pk_for_args_comment):
    url = reverse('news:delete', args=pk_for_args_comment)
    response = author_client.post(url)
    redirect = reverse(
        'news:detail', args=(News.objects.get().id,)
    ) + '#comments'
    assertRedirects(response, redirect)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(admin_client, pk_for_args_comment):
    url = reverse('news:delete', args=pk_for_args_comment)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
