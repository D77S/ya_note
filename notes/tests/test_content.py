# Пока непонятно, что из контента будем тестировать.

# Количество заметок на одной странице? Так пагинатора вообще ж нет никакого.

# Сортировку заметок? Так не по чем сортировать,
# нет ни одного поля даты/времени.

# Разве что, потестим что форма редактирования заметки (по /edit/<slug:slug>/)
# видна лишь авторизованному пользователю.
from django.contrib.auth import get_user_model
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

    # def test_anonymous_client_has_no_editform(self):
    #     '''Проверка, что анонимусу НЕ видна форма редактирования заметки.
    #     '''
    #     response = self.client.get(self.editnote_url)
    #     print('response.context=', response.context)
    #     # self.assertNotIn('form', response.context)

    def test_authorized_client_has_editform(self):
        '''Проверка, что автору видна форма редактирования заметки.
        '''
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        response = self.client.get(self.editnote_url)
        # print('response.context=', response.context)
        self.assertIn('form', response.context)
