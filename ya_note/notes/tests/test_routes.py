from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'slug'
HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
SUCCES_URL = reverse('notes:success')
ADD_URL = reverse('notes:add')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))


class TestPagesAvailability(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Чтец')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title='Заголовок', text='Текст', slug=SLUG, author=cls.author,
        )
        cls.events = (
            (HOME_URL, Client(), HTTPStatus.OK),
            (LOGIN_URL, Client(), HTTPStatus.OK),
            (LOGOUT_URL, Client(), HTTPStatus.OK),
            (SIGNUP_URL, Client(), HTTPStatus.OK),
            (DETAIL_URL, cls.reader_client, HTTPStatus.NOT_FOUND),
            (EDIT_URL, cls.reader_client, HTTPStatus.NOT_FOUND),
            (DELETE_URL, cls.reader_client, HTTPStatus.NOT_FOUND),
            (LIST_URL, cls.reader_client, HTTPStatus.OK),
            (SUCCES_URL, cls.reader_client, HTTPStatus.OK),
            (ADD_URL, cls.reader_client, HTTPStatus.OK),
            (LOGIN_URL, cls.reader_client, HTTPStatus.OK),
            (LOGOUT_URL, cls.reader_client, HTTPStatus.OK),
            (SIGNUP_URL, cls.reader_client, HTTPStatus.OK),
            (DETAIL_URL, cls.author_client, HTTPStatus.OK),
            (EDIT_URL, cls.author_client, HTTPStatus.OK),
            (DELETE_URL, cls.author_client, HTTPStatus.OK),
            (LOGIN_URL, cls.author_client, HTTPStatus.OK),
            (LOGOUT_URL, cls.author_client, HTTPStatus.OK),
            (SIGNUP_URL, cls.author_client, HTTPStatus.OK),
        )

    def test_pages_availability_for_different_users(self):
        for name, user_client, expected_status in self.events:
            with self.subTest(name=name):
                response = user_client.get(name)
                self.assertEqual(response.status_code, expected_status)


class TestRedirects(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.notes = Note.objects.create(
            title='Заголовок', text='Текст', slug=SLUG, author=cls.author,
        )
        cls.urls = (
            LIST_URL,
            SUCCES_URL,
            ADD_URL,
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
        )

    def test_redirect_for_anonymous_client(self):
        for name in self.urls:
            with self.subTest(name=name):
                redirect_url = f'{LOGIN_URL}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
