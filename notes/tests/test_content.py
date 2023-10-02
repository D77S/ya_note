from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()
AUTHOR_USERNAME = 'Лев Толстой'
READER_USERNAME = 'Читатель простой'


class TestDetailNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=AUTHOR_USERNAME)
        cls.reader = User.objects.create(username=READER_USERNAME)
        cls.note = Note.objects.create(
            title='Тестовая_заметка',
            text='Просто текст.',
            author=cls.author
        )
        cls.editnote_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)
        )

    def test_anonymous_client_has_no_editform(self):
        '''Проверяет, что анонимусу НЕ видна
        страница редактирования заметки.
        '''
        response = self.client.get(self.editnote_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_client_has_editform(self):
        '''Проверяет, что автору видна
        форма редактирования заметки.
        '''
        self.client.force_login(self.author)
        response = self.client.get(self.editnote_url)
        self.assertIn('form', response.context)

    def test_note_in_list_for_different_users(self):
        '''
        Проверяет, что заметки:
        - свои доступны,
        - а чужие нет.'''
        user_sees_note = {
            (self.author, True),
            (self.reader, False)
        }
        url_to = reverse('notes:list')
        for user, note_in_list in user_sees_note:
            self.client.force_login(user)
            with self.subTest(user=user):
                response = self.client.get(url_to)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        '''
        Проверяет, что форма передается на:
        - страницу добавления,
        - страницу редактирования.'''
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
