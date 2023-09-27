from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm, WARNING
from notes.models import Note

User = get_user_model()

NOTE_TITLE = 'Заголовок заметки'
NOTE_TEXT = 'Текст заметки'
NOTE_SLUG = 'AnySlug'


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Адрес страницы создания новой заметки.
        cls.url = reverse('notes:add', args=None)
        # Создаём юзера и его клиент, логинимся в клиенте.
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        # Данные для POST-запроса при создании заметки.
        cls.form_data = {
            'title': NOTE_TITLE,
            'text': NOTE_TEXT,
            'slug': NOTE_SLUG,
            'author': cls.user,
        }

    def test_anonymous_user_cant_create_note(self):
        '''Проверка, что что анонимный пользователь не может создать заметку.
        Для этого достаточно проверить, что при отправке POST-запроса
        на URL 'add/' в системе не появилось новых заметок.
        При запуске тестов создаётся пустая база данных, так что проверим,
        что после отправки запроса число объектов модели Note
        останется равным нулю.
        '''
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом заметки.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество заметок.
        notes_count = Note.objects.count()
        # Ожидаем, что заметок в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        '''Проверка, что залогиненный пользователь может создать заметку:
        отправим POST-запрос через авторизованный клиент.
        Затем посчитаем количество заметок в системе: база была пустая,
        так что число заметок должно стать равным единице.
        После этого проверим, что поля заметки
        содержат корректную информацию.
        '''
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл куда надо.
        self.assertRedirects(response, reverse('notes:success'))
        # Считаем количество заметок в базе.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть одна заметка.
        self.assertEqual(notes_count, 1)
        # Получаем объект заметки из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты созданной заметки
        # совпадают с ожидаемыми.
        self.assertEqual(note.title, NOTE_TITLE)
        self.assertEqual(note.text, NOTE_TEXT)
        self.assertEqual(note.author, self.user)

    def test_user_cant_repeat_slug(self):
        '''Проверка, что пользователь не может использовать повторяющийся
        слаг заметки при ее создании.
        '''
        # Отправляем два подряд запроса через авторизованный клиент
        # с гарантированно одинаковыми слагами.
        response = self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, есть ли в последнем (втором) ответе ошибка формы.
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=NOTE_SLUG + WARNING
        )
        # Дополнительно убедимся, что вторая заметка не была создана.
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestNoteEditDelete(TestCase):
    '''Класс для тестирования
    возможности редактировать и удалить свою запись,
    невозможности редактировать и удалить чужую запись.
    '''
    NOTE_NEW_TEXT = 'Обновлённый текст записи'

    @classmethod
    def setUpTestData(cls):
        # Создаём автора и его клиент,
        # читателя и его клиент
        # логиним их попарно.
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        # Создаем первому свою запись.
        cls.Note_author = Note.objects.create(
            title=NOTE_TITLE,
            text=NOTE_TEXT,
            slug=NOTE_SLUG,
            author=cls.author,
        )
        # URL для редактирования записи.
        cls.edit_url = reverse('notes:edit', args=(cls.Note_author.slug,))
        # URL для удаления записи.
        cls.delete_url = reverse('notes:delete', args=(cls.Note_author.slug,))
        # Формируем данные для POST-запроса по обновлению записи.
        cls.form_data = {'text': cls.NOTE_NEW_TEXT}

    def test_author_can_delete_note(self):
        '''Проверим, что автор может удалить свой комментарий.
        '''
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        # От имени автора заметки отправляем DELETE-запрос на удаление.
        response = self.author_client.delete(self.delete_url)
        # Проверяем, что редирект верный.
        # Заодно проверим статус-коды ответов.
        self.assertRedirects(response, reverse('notes:success', args=None))
        # Считаем количество комментариев в системе.
        notes_count = Note.objects.count()
        # Ожидаем ноль комментариев в системе.
        self.assertEqual(notes_count, 0)
