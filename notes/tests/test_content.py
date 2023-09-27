# Тестировать ли количество заметок на одной странице?
# Так пагинатора вообще ж нет никакого.
# Не тестируем.

# Тестировать ли сортировку заметок? Так не по чем сортировать,
# в модели нет ни одного поля даты/времени.
# Не тестируем.

# Тестируем ли форму редактирования заметки (по /edit/<slug:slug>/)?
# То, что она видна лишь авторизованному пользователю.
# Да, это можем. Тестируем.
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.test import TestCase
from notes.models import Note
from django.urls import reverse

User = get_user_model()


class TestDetailNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем автора тестовой заметки.
        cls.author = User.objects.create(username='Автор тестовой заметки')
        # Создаем тестовую заметку
        cls.note = Note.objects.create(
            title='Тестовая_заметка',
            text='Просто текст.',
            author=cls.author
        )
        # локатор редактирования заметки
        cls.editnote_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)  # type: ignore
        )  # type: ignore
        print(cls.editnote_url)

    def test_anonymous_client_has_no_editform(self):
        '''Проверка, что анонимусу НЕ видна страинца редактирования заметки.
        '''
        response = self.client.get(self.editnote_url)
        print('response.status_code=', response.status_code)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_client_has_editform(self):
        '''Проверка, что автору видна форма редактирования заметки.
        '''
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.editnote_url)
        # print('response.context=', response.context)
        self.assertIn('form', response.context)
