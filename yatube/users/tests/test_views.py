from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

User = get_user_model()


class UsersViewTests(TestCase):
    def setUp(self):
        """Создаем клиент зарегистрированного пользователя."""
        self.user = User.objects.create_user(
            username='new_author'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_signup_page_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
