import pytest

from datetime import datetime, timedelta
from django.conf import settings
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def new():
    new = News.objects.create(
        title='Текст заголовка',
        text='Текст новости',
        date=datetime.utcnow(),
    )
    return new


@pytest.fixture
def comment(author, new):
    comment = Comment.objects.create(
        text='Текст комментария',
        created=datetime.utcnow(),
        author=author,
        news=new,
    )
    return comment


@pytest.fixture
def pk_for_args_new(new):
    return new.id,


@pytest.fixture
def pk_for_args_comment(comment):
    return comment.id,


@pytest.fixture(scope='function')
def many_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture(scope='function')
def many_comments(new, author):
    now = datetime.utcnow()
    all_comments = [
        Comment(
            text=f'Просто текст. {index}',
            created=now - timedelta(hours=index),
            news=new,
            author=author,
        )
        for index in range(5)
    ]
    Comment.objects.bulk_create(all_comments)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }
