from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm, WARNING
from notes.models import Note

User = get_user_model()