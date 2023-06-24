from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

NOTE_TEXT = 'Текст'
NOTE_TITLE = 'Заголовок'
NOTE_SLUG = 'note-slug'
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCES_URL = reverse('notes:success')
EDIT_URL = reverse('notes:edit', args=[NOTE_SLUG])
DELETE_URL = reverse('notes:delete', args=[NOTE_SLUG])


class TestNoteCreation(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': NOTE_SLUG,
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(ADD_URL, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCES_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.title, NOTE_TITLE)
        self.assertEqual(note.slug, NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_unique_slug(self):
        Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=self.user,
        )
        slug_data = {
            'title': 'титель',
            'text': 'текстель',
            'slug': NOTE_SLUG,
        }
        response = self.auth_client.post(ADD_URL, data=slug_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(Note.objects.get().slug + WARNING),
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        slug_data = {
            'title': 'титель',
            'text': 'текстель',
        }
        response = self.auth_client.post(ADD_URL, data=slug_data)
        self.assertRedirects(response, SUCCES_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        expected_slug = slugify(slug_data['title'])
        self.assertEqual(note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NEW_NOTE_TEXT = 'Обновлённая заметка'
    NEW_NOTE_TITLE = 'Обновленный заголовок'
    NEW_NOTE_SLUG = 'new-note-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(DELETE_URL)
        self.assertRedirects(response, SUCCES_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.slug, NOTE_SLUG)

    def test_author_can_edit_note(self):
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCES_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, NOTE_TITLE)
        self.assertEqual(self.note.text, NOTE_TEXT)
        self.assertEqual(self.note.slug, NOTE_SLUG)
