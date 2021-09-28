from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UsersFormTests(TestCase):
    def setUp(self):
        """Создаем клиент гостя."""
        self.guest_client = Client()

    def test_create_user(self):
        """Создание нового прользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Никита',
            'last_name': 'Чалых',
            'username': 'NikitaChalykh',
            'email': 'Wizardus@list.ru',
            'password1': 'passworD1234_!',
            'password2': 'passworD1234_!'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        user = User.objects.last()
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(user.username, form_data['username'])
        self.assertEqual(user.first_name, form_data['first_name'])
        self.assertEqual(user.last_name, form_data['last_name'])
