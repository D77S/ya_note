from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.Note_test = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author
            )

    def test_pages_availability(self):

        # При обращении к страницам редактирования и удаления записи
        users_statuses = (
            (self.author, HTTPStatus.OK),  # автор должен получить ответ OK,
            (self.reader, HTTPStatus.NOT_FOUND),  # а читатель - NOT_FOUND.
        )

        # Проверки для авторизованного юзера, но любого.
        self.client.force_login(self.author)
        for name, args in (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None)
        ):
            with self.subTest(user=self.author, name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверки для неавторизованного юзера.
        # Итерируемся по внешнему кортежу
        # и распаковываем содержимое вложенных кортежей:
        for name, args in (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверки для авторизованного юзера и именного нужного.
        for user, status in users_statuses:
            #  Логиним пользователя в клиенте:
            self.client.force_login(user)
            #  Для каждой пары "пользователь - ожидаемый ответ"
            #  перебираем имена тестируемых страниц:
            for name, args in (
                ('notes:edit', (self.Note_test.slug,)),
                ('notes:detail', (self.Note_test.slug,)),
                ('notes:delete', (self.Note_test.slug,)),
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # def test_redirect_for_anonymous_client(self):
        # Сохраняем адрес страницы логина:
        # login_url = reverse('users:login')
        # print('адрес страницы логина: ', login_url)
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        # for name in ('news:edit', 'news:delete'):
        #     with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
        #         url = reverse(name, args=(self.comment.id,))
        #         print('адрес страницы редактирования или удаления комментария: ', url)
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
        #         redirect_url = f'{login_url}?next={url}'
        #         print('ожидаемый адрес страницы логина, на который будет перенаправлен пользователь: ', redirect_url)
        #         response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
        #         self.assertRedirects(response, redirect_url)
