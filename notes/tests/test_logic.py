from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

NOTE_TITLE = 'Заголовок заметки'
NOTE_TEXT = 'Текст заметки'
NOTE_SLUG = 'AnySlug'


class TestNoteCreation(TestCase):
    '''
    Класс для тестирования, что:
    - создать заметку:
        - анонимус не может,
        - а логированный может,
    - слаг при создании заметки:
        - нельзя повторять,
        - можно не указывать.'''

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add', args=None)
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': NOTE_SLUG,
            # 'author': cls.user,
        }

    def test_anonymous_user_cant_create_note(self):
        '''
        Проверяет, что анонимус
        не может создать заметку.'''
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)  # Ноль штук.

    def test_user_can_create_note(self):
        '''
        Проверяет, что залогиненный
        может создать заметку.'''
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)  # Оппа, одна появилась.
        note = Note.objects.get()
        self.assertEqual(note.title, NOTE_TITLE)
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_user_cant_repeat_slug(self):
        '''
        Проверяет, что нельзя использовать повторяющийся
        слаг при создании заметки.
        '''
        response = self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=NOTE_SLUG + WARNING
        )  # Ошибка формы при НЕпервом запросе с одинаковыми слагами.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)  # Всего одна, не две.

    def test_empty_slug(self):
        '''
        Проверяет, что если забыли/не стали вводить слаг
        при создании заметки,
        то он сам собой транслитерируется из ее названия.'''
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    '''
    Класс для тестирования:
    - для своей записи:
        - возможности редактировать,
        - возможности удалить,
    - для чужой записи:
        - невозможности редактировать,
        - невозможности удалить.'''

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.Note_author = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.Note_author.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.Note_author.slug,))
        cls.NOTE_NEW_TITLE = 'Обновлённый заголовок записи'
        cls.NOTE_NEW_TEXT = 'Обновлённый текст записи'
        cls.NOTE_NEW_SLUG = 'new-slug'
        cls.form_data = {
            'title': cls.NOTE_NEW_TITLE,
            'text': cls.NOTE_NEW_TEXT,
            'slug': cls.NOTE_NEW_SLUG
        }

    def test_author_can_delete_note(self):
        '''
        Проверяет, что автор может удалить свою заметку.'''
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success', args=None))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)  # Оппа, уже ноль, а не одна.

    def test_user_cant_delete_note_of_another_user(self):
        '''
        Проверяет, что читатель не может удалить чужую заметку.'''
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)  # Оппа, а она не удалилась.

    def test_author_can_edit_comment(self):
        '''
        Проверяет, что автор может редактировать свою заметку.'''
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.Note_author.refresh_from_db()
        self.assertEqual(self.Note_author.text, self.NOTE_NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        '''
        Проверяет, что читатель не может редактировать чужую заметку.'''
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.Note_author.refresh_from_db()
        self.assertEqual(self.Note_author.text, NOTE_TEXT)
