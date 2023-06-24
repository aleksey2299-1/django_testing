from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

SLUG = 'note-slug'
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
EDIT_URL = reverse('notes:edit', args=[SLUG])


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Чтец')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=SLUG,
            author=cls.author,
        )

    def test_notes_list(self):
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_not_for_author(self):
        response = self.reader_client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_author_client_has_form(self):
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertEqual(type(response.context['form']), NoteForm)
