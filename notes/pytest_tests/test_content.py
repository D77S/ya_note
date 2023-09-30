from django.urls import reverse
import pytest

@pytest.mark.parametrize(
        'parametrized_client, note_in_list',
        (
            (pytest.lazy_fixture('author_client'), True),
            (pytest.lazy_fixture('admin_client'), False),
        )
)
def test_note_in_list_for_different_users(note, parametrized_client, note_in_list):
    url = reverse('notes:list')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    assert (note in object_list) is note_in_list


def test_note_not_in_list_for_another_user(note, admin_client):
    url = reverse('notes:list')
    response = admin_client.get(url)
    object_list = response.context['object_list']
    assert note not in object_list
