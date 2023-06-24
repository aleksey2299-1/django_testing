import pytest
from django.conf import settings
from django.urls import reverse

from ..forms import CommentForm

HOME_URL = 'news:home'
DETAIL_URL = 'news:detail'


@pytest.mark.django_db
def test_news_count_and_sorted(client, many_news):
    url = reverse(HOME_URL)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_sorted(admin_client, pk_for_args_new, many_comments):
    url = reverse(DETAIL_URL, args=pk_for_args_new)
    response = admin_client.get(url)
    assert 'news' in response.context
    new = response.context['news']
    comments = new.comment_set.all()
    assert len(comments) > 1
    all_dates = [comment.created for comment in comments]
    sorted_dates = sorted(all_dates)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, is_form_allowed',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        (DETAIL_URL, pytest.lazy_fixture('pk_for_args_new')),
    )
)
def test_pages_contains_form(parametrized_client, name, args, is_form_allowed):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert ('form' in response.context) == is_form_allowed
    if is_form_allowed:
        assert type(response.context['form']) == CommentForm
