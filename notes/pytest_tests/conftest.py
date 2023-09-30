import pytest

# Импортируем модель заметки, чтобы создать экземпляр.
from notes.models import Note


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуры автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def note(author):
    ''''
    Возвращает ОБЪЕКТ МОДЕЛИ, заметку note.'''
    note = Note.objects.create(  # Создаем объект заметки.
        title='Заголовок',
        text='Текст заметки',
        slug='note-slug',
        author=author,
    )
    return note


@pytest.fixture
def slug_for_args(note):
    return (note.slug,)


@pytest.fixture
def form_data():
    '''
    Возвращает СЛОВАРЬ, еще одну заметку, другую чем ранее.'''
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
        'slug': 'new-slug'
    }
