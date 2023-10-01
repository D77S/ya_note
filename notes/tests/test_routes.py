from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.Note_test = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author
        )

    def test_pages_availability(self):
        '''
        Проверяет доступность разных страниц, что:
        - анонимусу доступно:
            - главная,
            - логин,
            - логаут,
            - рега,
        - авторизованному читателю доступно:
            - добавления новой заметки,
            - список заметок,
            - страница успешного добавления,
        - автору доступно:
            - редактирование,
            - детализированная каждая отдельная,
            - удаления.'''
        users_statuses = (
            (self.author, HTTPStatus.OK),  # автор должен получить ответ OK,
            (self.reader, HTTPStatus.NOT_FOUND),  # а читатель - NOT_FOUND.
        )
        urls_for_anonymous = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        urls_for_authorized = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None)
        )
        urls_for_author = (
            ('notes:edit', (self.Note_test.slug,)),
            ('notes:detail', (self.Note_test.slug,)),
            ('notes:delete', (self.Note_test.slug,)),
        )

        # Проверки для анонимуса.
        for name, args in urls_for_anonymous:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверки для читателя.
        for name, args in urls_for_authorized:
            with self.subTest(user=self.reader, name=name):
                url = reverse(name, args=args)
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверки для автора.
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls_for_author:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        '''
        Проверяет редиректы со страниц,
        с которых он должен быть для анонимуса.'''
        login_url = reverse('users:login')
        urls_for_redirect = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:edit', (self.Note_test.slug,)),
            ('notes:detail', (self.Note_test.slug,)),
            ('notes:delete', (self.Note_test.slug,)),
        )
        for name, args in urls_for_redirect:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
